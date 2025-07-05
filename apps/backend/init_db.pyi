from typing import Any, Dict
import asyncpg
from datetime import datetime, timezone

__all__ = [
    "create_database_if_not_exists",
    "setup_timescaledb_extensions",
    "create_tables",
    "create_hypertables",
    "create_indexes",
    "seed_initial_data",
    "verify_setup",
    "main",
]

async def create_database_if_not_exists() -> None: ...

async def setup_timescaledb_extensions() -> None: ...

async def create_tables() -> None: ...

async def create_hypertables() -> None: ...

async def create_indexes() -> None: ...

async def seed_initial_data() -> None: ...

async def verify_setup() -> None: ...

async def main() -> None: ... 