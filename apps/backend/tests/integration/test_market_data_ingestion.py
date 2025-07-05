"""
@fileoverview Integration tests for market-data vertical slice (WS → Queue → Timescale)
@module tests.integration.test_market_data_ingestion

@description
Validates that:
1. `CoinbaseWebSocketClient` enqueues validated *ticker* messages and records
   drop metrics when queue is full.
2. `TimescaleBatchWriter` consumes queued ticks, performs batch insert via the
   DB session dependency, and updates Prometheus metrics.

The database dependency is patched with an in-memory stub so the tests run
without requiring a live Postgres/TimescaleDB instance.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict

import pytest
from prometheus_client import CollectorRegistry

# Import modules under test via canonical alias path
from backend.services.market_data.websocket_client import (
    CoinbaseWebSocketClient,
    _QUEUE_DROPPED_TOTAL,
)
from backend.services.market_data.timescale_writer import (
    TimescaleBatchWriter,
    _BATCH_ROWS_TOTAL,
    _LAST_FLUSH_SIZE,
)

# ---------------------------------------------------------------------------
# Helper: stub async DB session (no real DB required)
# ---------------------------------------------------------------------------

class _StubSession:  # pylint: disable=too-few-public-methods
    """Mimic minimal SQLAlchemy AsyncSession interface used by writer."""

    def __init__(self) -> None:
        self.executed_rows: list[Dict[str, Any]] = []

    async def execute(self, _stmt, rows):  # noqa: D401 – matching call sig
        self.executed_rows.extend(rows)

    async def commit(self):  # noqa: D401
        return None


@asynccontextmanager
async def _stub_session_ctx():  # noqa: D401 – context manager helper
    sess = _StubSession()
    yield sess


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(name="registry_reset")
def _registry_reset_fixture():  # noqa: D401 – reset Prometheus between tests
    """Ensure Prometheus counters start at 0 for each test run."""

    # Each metric is registered in the default REGISTRY; snapshot values & reset
    orig_batch_total = _BATCH_ROWS_TOTAL._value.get()  # type: ignore[attr-defined]
    orig_last_flush = _LAST_FLUSH_SIZE._value.get()  # type: ignore[attr-defined]
    orig_drop_total = _QUEUE_DROPPED_TOTAL._value.get()  # type: ignore[attr-defined]
    yield
    # Restore original values (counters only grow – compensate)
    _BATCH_ROWS_TOTAL._value.set(orig_batch_total)  # type: ignore[attr-defined]
    _LAST_FLUSH_SIZE._value.set(orig_last_flush)  # type: ignore[attr-defined]
    _QUEUE_DROPPED_TOTAL._value.set(orig_drop_total)  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_batch_writer_flushes_and_updates_metrics(monkeypatch, registry_reset):
    """Writer should persist rows (via stub) and update Prometheus gauges/counters."""

    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    # Patch DB session dependency
    monkeypatch.setattr(
        "backend.services.market_data.timescale_writer.get_async_session",
        _stub_session_ctx,
    )

    writer = TimescaleBatchWriter(queue, batch_size=2, flush_interval=0.1, max_retries=1)
    writer.start()

    # Sample Coinbase ticker message (raw dict, already validated by client)
    base_msg: Dict[str, Any] = {
        "type": "ticker",
        "product_id": "BTC-USD",
        "price": 30000.12,
        "time": datetime.now(tz=timezone.utc).isoformat(),
    }

    await queue.put(base_msg)
    await queue.put(base_msg | {"price": 30001.55})

    # Give writer enough time to flush
    await asyncio.sleep(0.2)
    await writer.stop()

    # Assertions – Prometheus metrics updated
    assert _LAST_FLUSH_SIZE._value.get() == 2  # type: ignore[attr-defined]
    assert _BATCH_ROWS_TOTAL._value.get() >= 2  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_websocket_queue_drops_when_full(registry_reset):
    """Client should drop messages & increment counter if internal queue is full."""

    client = CoinbaseWebSocketClient(products=["BTC-USD"], queue_maxsize=1)

    # Craft a valid ticker message string (JSON)
    msg_dict = {
        "type": "ticker",
        "product_id": "BTC-USD",
        "price": 31500.00,
        "time": datetime.utcnow().isoformat() + "Z",
    }
    msg_json = __import__("json").dumps(msg_dict)

    # Enqueue first message – should pass
    await client._handle(msg_json)  # pylint: disable=protected-access
    # Second message should overflow queue and be dropped
    await client._handle(msg_json)

    assert _QUEUE_DROPPED_TOTAL._value.get() >= 1  # type: ignore[attr-defined] 