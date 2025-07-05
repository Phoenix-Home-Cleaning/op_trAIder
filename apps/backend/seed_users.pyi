from typing import Any, Dict, List
import asyncpg

__all__ = [
    "hash_password",
    "create_users_table",
    "seed_demo_user",
    "verify_users",
    "main",
]

def hash_password(password: str) -> str: ...

async def create_users_table(conn: asyncpg.Connection) -> None: ...

async def seed_demo_user(conn: asyncpg.Connection, user_data: Dict[str, Any]) -> None: ...

async def verify_users(conn: asyncpg.Connection) -> None: ...

async def main() -> None: ... 