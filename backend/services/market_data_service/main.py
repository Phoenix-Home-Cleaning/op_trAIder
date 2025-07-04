#!/usr/bin/env python3
"""
@fileoverview Market Data Microservice (read-only)
@module backend.services.market_data_service.main

@description
Standalone FastAPI service exposing query-only endpoints for market data.
Designed for phased decoupling of the monolithic backend. Runs under its own
process/container but reuses shared `database` and `models` modules. All
endpoints are idempotent and side-effect-free, ensuring zero risk to trading
state.

@performance
- Latency target: ≤ 5 ms internal processing per request
- Throughput: 500 req/s on commodity VM

@risk
- Failure impact: MEDIUM — system can fall back to monolith endpoints
- Recovery: Kubernetes auto-restart; health probe `/health/live`

@compliance
- Audit: All requests logged via shared structured logger
- Data retention: logs 90 days
"""
from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, desc

from utils.logging import setup_logging, get_logger
from utils.monitoring import MetricsCollector
from database import get_database_connection
from models.market_data import MarketData

# ---------------------------------------------------------------------------
# Service Setup
# ---------------------------------------------------------------------------
ENV = os.getenv("PYTHON_ENV", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

setup_logging()
logger = get_logger("market_data_service")
metrics = MetricsCollector("market_data_service")

app = FastAPI(title="TRAIDER Market Data Service", version="1.0.0-alpha")

# CORS (allow internal dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"]
)


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------
async def db_dep():
    async with get_database_connection() as conn:
        yield conn


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health/live", tags=["Health"])
async def liveness() -> Dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/health/ready", tags=["Health"])
async def readiness(conn=Depends(db_dep)) -> Dict[str, str]:
    """Readiness probe checks DB connectivity."""
    _ = await conn.execute(select(1))
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/market-data/{symbol}", tags=["Market Data"])
async def latest_market_data(
    symbol: str,
    limit: int = Query(1, ge=1, le=1000, description="Number of recent rows to return"),
    conn=Depends(db_dep),
):
    """Return the latest *limit* market-data rows for a symbol."""
    start = time.perf_counter()
    try:
        stmt = (
            select(MarketData)
            .where(MarketData.symbol == symbol.upper())
            .order_by(desc(MarketData.timestamp))
            .limit(limit)
        )
        result = await conn.execute(stmt)
        rows = result.scalars().all()
        if not rows:
            raise HTTPException(status_code=404, detail="Symbol not found")
        data = [row.to_dict() for row in rows]
        return {"data": data}
    finally:
        duration = time.perf_counter() - start
        metrics.request_duration.labels("GET", "/market-data", 200).observe(duration)


@app.get("/metrics", include_in_schema=False)
async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    return JSONResponse(content=metrics.get_prometheus_metrics(), media_type="text/plain") 