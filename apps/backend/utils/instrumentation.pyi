from typing import Any, Dict, Callable

__all__ = [
    "instrument",
]


def instrument(func: Callable[..., Any]) -> Callable[..., Any]: ... 