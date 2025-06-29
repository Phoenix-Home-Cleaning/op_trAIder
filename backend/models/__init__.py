"""
@fileoverview Database models package for TRAIDER V1
@module backend.models

@description
SQLAlchemy ORM models for institutional-grade trading platform.
Includes user authentication, market data, and trading record models
with TimescaleDB optimizations for time-series data.

@performance
- Optimized indexes for trading queries
- TimescaleDB hypertables for market data
- Async-compatible model definitions

@risk
- Failure impact: CRITICAL - No data persistence
- Recovery strategy: Database migration rollback

@compliance
- Audit requirements: All model changes tracked
- Data retention: Market data 7 years, trades indefinitely

@see {@link docs/architecture/database-schema.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

from .user import User
from .market_data import MarketData, OrderBookLevel2
from .position import Position
from .trade import Trade
from .signal import Signal

__all__ = [
    "User",
    "MarketData", 
    "OrderBookLevel2",
    "Position",
    "Trade",
    "Signal",
] 