from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from utils.exceptions import TradingError

__all__ = [
    "app",
]

app: FastAPI

async def trading_error_handler(request: Request, exc: TradingError): ...

async def http_exception_handler(request: Request, exc: HTTPException): ...

async def root() -> Dict[str, Any]: ... 