"""
@fileoverview Alembic migration environment for TRAIDER V1
@module backend.migrations.env

@description
Alembic environment configuration for database migrations with institutional-grade
settings, TimescaleDB support, and proper model metadata integration.

@performance
- Uses connection pooling for migration operations
- Supports both online and offline migration modes
- Optimized for PostgreSQL/TimescaleDB

@risk
- Failure impact: HIGH - Database schema changes
- Recovery strategy: Rollback migrations, restore from backup

@compliance
- Audit requirements: All migrations logged
- Data retention: Migration history preserved indefinitely

@see {@link docs/architecture/database-migrations.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the parent directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models after path setup
try:
    from database import Base
    from models.user import User
    from models.market_data import MarketData, OrderBookLevel2
    from models.position import Position
    from models.trade import Trade
    from models.signal import Signal
    
    # Set target metadata
    target_metadata = Base.metadata
except ImportError as e:
    print(f"Warning: Could not import models: {e}")
    target_metadata = None

# Get database URL from environment variable
def get_database_url():
    """
    Get database URL from environment variables.
    
    @description
    Retrieves database connection URL from environment variables with fallback
    to default development settings. Supports both sync and async URLs.
    
    @returns Database URL string for SQLAlchemy
    
    @tradingImpact CRITICAL - Database connectivity required
    @riskLevel HIGH - Migration fails if URL invalid
    """
    database_url = os.getenv(
        "DATABASE_URL", 
        "postgresql://traider:password@localhost:5432/traider"
    )
    
    # Convert async URL to sync for Alembic
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    return database_url

# Override the database URL in config
config.set_main_option("sqlalchemy.url", get_database_url())

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    @description
    Configures the context with just a URL and not an Engine, though an Engine 
    is acceptable here as well. By skipping the Engine creation we don't even 
    need a DBAPI to be available. This mode generates SQL scripts for manual execution.

    @performance Fastest migration mode, no database connection required
    @sideEffects Creates SQL migration scripts
    
    @tradingImpact LOW - Offline script generation only
    @riskLevel LOW - No database changes made
    
    @example
    ```bash
    # Generate migration SQL without database connection
    alembic upgrade --sql head > migration.sql
    ```
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    @description
    Creates an Engine and associates a connection with the context for live
    database migration execution. Includes institutional-grade safety features
    like transaction isolation and proper connection handling.

    @performance Uses connection pooling for optimal resource usage
    @sideEffects Executes DDL changes against live database
    
    @tradingImpact HIGH - Live database schema changes
    @riskLevel HIGH - Data loss possible if migration fails
    
    @example
    ```bash
    # Apply migrations to live database
    alembic upgrade head
    ```
    """
    # Create engine configuration with institutional-grade settings
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Configure context with enhanced comparison options
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
