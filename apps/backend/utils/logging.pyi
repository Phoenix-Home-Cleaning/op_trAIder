from typing import Any, Dict, Optional
import logging

__all__ = [
    "setup_logging",
    "get_logger",
    "StructuredAdapter",
]


def setup_logging(level: int = ...) -> None: ...


def get_logger(name: Optional[str] = ...) -> logging.Logger: ...


class StructuredAdapter(logging.LoggerAdapter):
    def process(self, msg: Any, kwargs: Dict[str, Any]) -> Any: ... 