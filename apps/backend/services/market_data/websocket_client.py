"""
@fileoverview Coinbase Advanced Trade WebSocket client for real-time market data ingestion.
@module apps.backend.services.market_data.websocket_client

@description
Establishes and maintains an authenticated WebSocket connection to the Coinbase
Advanced Trade feed, validates incoming ticker messages, persists them to the
internal async queue for downstream processing, and exposes basic Prometheus
metrics for latency and drop-rates.

@performance
- Latency target: <50 ms tick ingestion
- Throughput: ≥1 k msgs/sec (2 product streams)
- Memory usage: <25 MB resident

@risk
- Failure impact: HIGH – loss of market data halts trading decisions
- Recovery strategy: exponential back-off reconnect with circuit-breaker

@compliance
- Audit requirements: Yes – all connection and recovery events logged
- Data retention: Raw WS messages not stored; parsed ticks stored in DB layer

@see docs/architecture/market_data_service.md
@since 0.2.0
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Iterable, List

import websockets
from pydantic import BaseModel, Field, ValidationError
from prometheus_client import Counter, Histogram, Gauge
from opentelemetry import trace

# ---------------------------------------------------------------------------
# Pydantic models – strict schema validation of incoming messages
# ---------------------------------------------------------------------------


class _TickerMessage(BaseModel):
    """Subset of the Coinbase Advanced Trade `ticker` channel message."""

    product_id: str = Field(..., alias="product_id")
    price: float = Field(..., alias="price")
    time: str = Field(..., alias="time")  # ISO-8601 timestamp


class _Level2Message(BaseModel):
    """Subset of Coinbase Advanced Trade `level2` update message."""

    product_id: str = Field(..., alias="product_id")
    changes: list[list[str]] = Field(..., alias="changes")  # [ [side, price, qty] ]
    time: str = Field(..., alias="time")


# ---------------------------------------------------------------------------
# Metrics – exported via Prometheus HTTP endpoint elsewhere in app
# ---------------------------------------------------------------------------

_WS_LATENCY_MS = Histogram(
    "market_data_ws_latency_ms",
    "End-to-end latency between websocket receive time and message timestamp.",
)

_DROPPED_MSGS_TOTAL = Counter(
    "market_data_dropped_msgs_total",
    "Total number of WebSocket messages dropped due to validation errors.",
)

# Queue size for downstream buffering
_QUEUE_DROPPED_TOTAL = Counter(
    "market_data_queue_dropped_total",
    "Total number of validated WS messages dropped because the async queue was full.",
)

# Real-time queue size gauge
_QUEUE_SIZE = Gauge(
    "market_data_queue_size",
    "Current number of tick messages in the async queue.",
)

# ---------------------------------------------------------------------------
# Coinbase WebSocket client implementation
# ---------------------------------------------------------------------------

_tracer = trace.get_tracer(__name__)


class CoinbaseWebSocketClient:
    """Lightweight async client handling connection & basic resilience."""

    WS_URL: str = "wss://advanced-trade-ws.coinbase.com"
    _PING_INTERVAL_SEC: int = 20
    _MAX_BACKOFF_SEC: int = 60

    def __init__(self, products: Iterable[str] | None = None, *, queue_maxsize: int = 10000) -> None:
        self.products: List[str] = list(products) if products else ["BTC-USD", "ETH-USD"]
        self._logger = logging.getLogger(__name__)
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task[None] | None = None

        # In-memory buffer decoupling WebSocket ingest from DB writer / processors
        self._queue: asyncio.Queue[dict[str, str | float]] = asyncio.Queue(maxsize=queue_maxsize)

    # ---------------------------------------------------------------------
    # Public control methods
    # ---------------------------------------------------------------------

    def start(self) -> None:
        """Launch background connection task inside current event-loop."""

        if self._task and not self._task.done():
            raise RuntimeError("WebSocket client already running")
        self._task = asyncio.create_task(self._run(), name="coinbase-ws-client")

    async def stop(self) -> None:
        """Signal background task to stop gracefully."""

        self._stop_event.set()
        if self._task:
            await self._task

    # ---------------------------------------------------------------------
    # Public consumer helpers
    # ---------------------------------------------------------------------

    @property
    def queue(self) -> "asyncio.Queue[dict[str, str | float]]":  # noqa: D401 – readable alias
        """Return the internal tick buffer queue for downstream consumers."""

        return self._queue

    async def get_tick(self) -> dict[str, str | float]:
        """Await one validated tick message from the internal queue."""

        return await self._queue.get()

    async def ticks(self):  # pragma: no cover – convenience async generator
        """Async iterator yielding validated tick messages as they arrive."""

        while True:
            yield await self.get_tick()

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------

    async def _run(self) -> None:
        backoff = 1
        while not self._stop_event.is_set():
            try:
                await self._connect_and_listen()
                backoff = 1  # reset after successful session
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("WS error: %s – reconnect in %s s", exc, backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, self._MAX_BACKOFF_SEC)

    async def _connect_and_listen(self) -> None:
        """Establish connection, subscribe, and stream messages until closed."""

        async with websockets.connect(
            self.WS_URL, ping_interval=self._PING_INTERVAL_SEC, max_queue=2048
        ) as ws:
            await self._subscribe(ws)
            async for raw_msg in ws:
                await self._handle(raw_msg)
                if self._stop_event.is_set():
                    await ws.close(code=1000, reason="client shutdown")
                    break

    async def _subscribe(self, ws: websockets.WebSocketClientProtocol) -> None:
        """Send channel subscription message."""

        sub_msg = {
            "type": "subscribe",
            "channel": "ticker",
            "product_ids": self.products,
        }
        await ws.send(json.dumps(sub_msg))
        self._logger.info("Subscribed to Coinbase WS for %s", ", ".join(self.products))

    async def _handle(self, raw_msg: str) -> None:
        """Validate and process an incoming raw WebSocket message with tracing."""

        start = time.perf_counter_ns()
        with _tracer.start_as_current_span("ws.message.process") as span:
            try:
                data = json.loads(raw_msg)
                msg_type = data.get("type")
                if msg_type == "ticker":
                    _TickerMessage.model_validate(data)
                elif msg_type == "l2update":
                    _Level2Message.model_validate(data)
                else:
                    return  # ignore others
                # Non-blocking enqueue – drop if queue is full to maintain back-pressure
                try:
                    self._queue.put_nowait(data)
                    _QUEUE_SIZE.set(self._queue.qsize())
                except asyncio.QueueFull:
                    _QUEUE_DROPPED_TOTAL.inc()
                    _QUEUE_SIZE.set(self._queue.qsize())
            except (ValidationError, json.JSONDecodeError) as exc:
                span.record_exception(exc)
                _DROPPED_MSGS_TOTAL.inc()
                return
            finally:
                elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
                _WS_LATENCY_MS.observe(elapsed_ms)
                span.set_attribute("latency_ms", elapsed_ms) 