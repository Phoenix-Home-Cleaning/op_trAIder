from typing import Optional, AsyncGenerator, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
import asyncpg

__all__ = [
    "create_database_engine",
    "create_connection_pool",
    "get_database_connection",
    "close_database_connection",
    "test_database_connectivity",
    "get_async_session",
    "get_raw_connection",
    "get_db_session",
    "check_database_health",
]

async def create_database_engine() -> AsyncEngine: ...

async def create_connection_pool() -> asyncpg.pool.Pool: ...

async def get_database_connection() -> None: ...

async def close_database_connection() -> None: ...

async def test_database_connectivity() -> None: ...

async def get_async_session() -> AsyncGenerator[AsyncSession, None]: ...

async def get_raw_connection() -> asyncpg.Connection: ...

async def get_db_session() -> AsyncGenerator[AsyncSession, None]: ...

async def check_database_health() -> dict[str, Any]: ...

# Re-export for ORM base
class Base: ... 