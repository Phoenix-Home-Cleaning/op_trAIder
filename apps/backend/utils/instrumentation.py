"""
@fileoverview Function-level instrumentation utilities
@module backend.utils.instrumentation

@description
Provides a lightweight decorator (`@instrument`) to measure latency, count
success/failure, and emit Prometheus/OpenTelemetry metrics via the shared
`MetricsCollector`. Designed to be applied to service-boundary functions (e.g.
order executors, market-data processors) and FastAPI route handlers.

@performance
- <50µs overhead per call (timer + label lookup)

@risk
- Failure impact: LOW — metrics only

@since 1.0.0-alpha
"""

from functools import wraps
from time import perf_counter
from typing import Any, Callable, Coroutine, TypeVar, Union, overload, Awaitable

from .monitoring import get_metrics_collector

F = TypeVar("F", bound=Callable[..., Any])


def _get_default_labels(func: Callable[..., Any]) -> dict[str, str]:
    """Generate default Prometheus labels from function metadata."""
    module = func.__module__ or "unknown"
    name = func.__name__ or "anonymous"
    return {"module": module, "function": name}


@overload
def instrument(func: F) -> F:  # Decorator used without arguments
    ...


@overload
def instrument(**labels: str) -> Callable[[F], F]:  # Decorator with custom labels
    ...


def instrument(func: Union[F, None] = None, **custom_labels: str):  # type: ignore[override]
    """Decorator that records latency and success/failure metrics.

    Example
    -------
    ```python
    @instrument
    async def fetch_price(symbol: str):
        ...

    @instrument(operation="order_execute", venue="coinbase")
    def place_order(...):
        ...
    ```
    """

    def decorator(fn: F) -> F:  # type: ignore[override]
        metrics = get_metrics_collector()
        labels = _get_default_labels(fn)
        labels.update(custom_labels)

        @wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any):
            start = perf_counter()
            try:
                result = fn(*args, **kwargs)
                # Handle coroutine functions transparently
                if isinstance(result, Coroutine):  # type: ignore
                    async def _async_handler(coro: Awaitable[Any]):
                        try:
                            value = await coro
                            return value
                        finally:
                            duration = perf_counter() - start
                            if metrics:
                                metrics.request_duration.labels(
                                    "ASYNC", labels.get("function", "unknown"), 200
                                ).observe(duration)
                    return _async_handler(result)  # type: ignore
                return result
            except Exception as exc:  # pylint: disable=broad-except
                duration = perf_counter() - start
                if metrics:
                    metrics.error_count.labels(type(exc).__name__, labels.get("function", "unknown")).inc()
                    metrics.request_duration.labels(
                        "SYNC", labels.get("function", "unknown"), 500
                    ).observe(duration)
                raise
            finally:
                if not isinstance(result, Coroutine):  # type: ignore
                    duration = perf_counter() - start
                    if metrics:
                        metrics.request_duration.labels(
                            "SYNC", labels.get("function", "unknown"), 200
                        ).observe(duration)
        return sync_wrapper  # type: ignore

    # If decorator used without parentheses: @instrument
    if func and callable(func):
        return decorator(func)

    # If decorator used with params: @instrument(operation="x")
    return decorator  # type: ignore


# Example usage removed to keep library importable without syntax errors.

# @instrument(operation="order_execute", venue="coinbase")
# def place_order(...):
#     # Implementation of place_order function
#     pass 