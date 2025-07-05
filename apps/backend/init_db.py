#!/usr/bin/env python3
"""
@fileoverview Database initialization script for TRAIDER V1
@module backend.init_db

@description
Creates database tables, indexes, and TimescaleDB hypertables for the
TRAIDER trading platform. Handles initial schema setup and data seeding.

@performance
- Batch table creation for optimal setup time
- Pre-optimized indexes for trading queries
- TimescaleDB hypertables for time-series data

@risk
- Failure impact: CRITICAL - No database schema
- Recovery strategy: Drop and recreate database

@compliance
- Audit requirements: Schema changes logged
- Data retention: Setup logs preserved

@see {@link docs/architecture/database-setup.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Base, get_database_connection
from models.user import User
from models.market_data import MarketData, OrderBookLevel2
from models.position import Position
from models.trade import Trade
from models.signal import Signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://traider:password@localhost:5432/traider")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "traider")
DB_USER = os.getenv("DB_USER", "traider")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")


async def create_database_if_not_exists():
    """
    Create the database if it doesn't exist.
    
    @description
    Connects to PostgreSQL server and creates the TRAIDER database
    if it doesn't already exist. Uses administrative connection.
    
    @performance Database creation typically <5 seconds
    @sideEffects Creates database on PostgreSQL server
    
    @tradingImpact CRITICAL - No system without database
    @riskLevel MEDIUM - Administrative database operation
    """
    
    try:
        # Connect to PostgreSQL server (not specific database)
        admin_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
        
        conn = await asyncpg.connect(admin_url)
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", DB_NAME
        )
        
        if not exists:
            logger.info(f"Creating database: {DB_NAME}")
            await conn.execute(f'CREATE DATABASE "{DB_NAME}"')
            logger.info(f"Database {DB_NAME} created successfully")
        else:
            logger.info(f"Database {DB_NAME} already exists")
        
        await conn.close()
        
    except Exception as exc:
        logger.error(f"Failed to create database: {exc}")
        raise


async def setup_timescaledb_extensions():
    """
    Set up TimescaleDB extensions and configurations.
    
    @description
    Installs TimescaleDB extension and configures database for
    high-performance time-series data storage and querying.
    
    @performance Extension setup <10 seconds
    @sideEffects Installs TimescaleDB extension
    
    @tradingImpact HIGH - Time-series performance critical
    @riskLevel MEDIUM - Database extension installation
    """
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Install TimescaleDB extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
        logger.info("TimescaleDB extension installed")
        
        # Set up timezone
        await conn.execute("SET timezone = 'UTC';")
        logger.info("Database timezone set to UTC")
        
        await conn.close()
        
    except Exception as exc:
        logger.error(f"Failed to setup TimescaleDB: {exc}")
        raise


async def create_tables():
    """
    Create all database tables using SQLAlchemy.
    
    @description
    Creates all tables defined in the SQLAlchemy models with proper
    indexes, constraints, and relationships for trading operations.
    
    @performance Table creation <30 seconds
    @sideEffects Creates all database tables
    
    @tradingImpact CRITICAL - No data storage without tables
    @riskLevel HIGH - Schema creation operation
    """
    
    try:
        # Create async engine for table creation
        engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("All database tables created successfully")
        
        await engine.dispose()
        
    except Exception as exc:
        logger.error(f"Failed to create tables: {exc}")
        raise


async def create_hypertables():
    """
    Convert time-series tables to TimescaleDB hypertables.
    
    @description
    Converts market_data and trades tables to TimescaleDB hypertables
    for optimized time-series data storage and querying performance.
    
    @performance Hypertable creation <15 seconds
    @sideEffects Converts tables to hypertables
    
    @tradingImpact HIGH - Time-series query performance
    @riskLevel MEDIUM - Table structure modification
    """
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Create hypertable for market data (partitioned by timestamp)
        try:
            await conn.execute("""
                SELECT create_hypertable('market_data', 'timestamp', 
                                       chunk_time_interval => INTERVAL '1 hour',
                                       if_not_exists => TRUE);
            """)
            logger.info("Market data hypertable created")
        except Exception as e:
            logger.warning(f"Market data hypertable creation failed: {e}")
        
        # Create hypertable for trades (partitioned by executed_at)
        try:
            await conn.execute("""
                SELECT create_hypertable('trades', 'executed_at', 
                                       chunk_time_interval => INTERVAL '1 day',
                                       if_not_exists => TRUE);
            """)
            logger.info("Trades hypertable created")
        except Exception as e:
            logger.warning(f"Trades hypertable creation failed: {e}")
        
        await conn.close()
        
    except Exception as exc:
        logger.error(f"Failed to create hypertables: {exc}")
        raise


async def create_indexes():
    """
    Create additional indexes for optimal trading performance.
    
    @description
    Creates specialized indexes for trading queries including symbol lookups,
    time-range queries, and user-specific data access patterns.
    
    @performance Index creation <20 seconds
    @sideEffects Creates database indexes
    
    @tradingImpact HIGH - Query performance optimization
    @riskLevel LOW - Index creation operation
    """
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Market data indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_data_symbol_time 
            ON market_data (symbol, timestamp DESC);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_data_exchange 
            ON market_data (exchange, timestamp DESC);
        """)
        
        # Trade indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_trades_user_symbol 
            ON trades (user_id, symbol, executed_at DESC);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_trades_status 
            ON trades (status, executed_at DESC);
        """)
        
        # Position indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_positions_user_active 
            ON positions (user_id, is_active, updated_at DESC);
        """)
        
        # Signal indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_signals_strategy_time 
            ON signals (strategy, generated_at DESC);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_signals_symbol_confidence 
            ON signals (symbol, confidence DESC, generated_at DESC);
        """)
        
        logger.info("All trading indexes created successfully")
        
        await conn.close()
        
    except Exception as exc:
        logger.error(f"Failed to create indexes: {exc}")
        raise


async def seed_initial_data():
    """
    Seed database with initial administrative data.
    
    @description
    Creates initial admin user and system configuration data
    required for platform operation and testing.
    
    @performance Data seeding <5 seconds
    @sideEffects Inserts initial data
    
    @tradingImpact MEDIUM - Initial system setup
    @riskLevel LOW - Data insertion operation
    """
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Create admin user if not exists
        admin_exists = await conn.fetchval(
            "SELECT 1 FROM users WHERE username = 'admin'"
        )
        
        if not admin_exists:
            # Note: In production, use proper password hashing
            await conn.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active, created_at)
                VALUES ('admin', 'admin@traider.local', '$2b$12$dummy.hash.for.development', 
                        'admin', true, $1)
            """, datetime.now(timezone.utc))
            
            logger.info("Admin user created")
        else:
            logger.info("Admin user already exists")
        
        await conn.close()
        
    except Exception as exc:
        logger.error(f"Failed to seed initial data: {exc}")
        raise


async def verify_setup():
    """
    Verify database setup by running basic queries.
    
    @description
    Performs basic connectivity and functionality tests to ensure
    database is properly configured and ready for trading operations.
    
    @performance Verification <5 seconds
    @sideEffects Reads from database tables
    
    @tradingImpact LOW - Setup verification only
    @riskLevel LOW - Read-only operations
    """
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Test basic connectivity
        version = await conn.fetchval("SELECT version()")
        logger.info(f"PostgreSQL version: {version}")
        
        # Test TimescaleDB
        try:
            ts_version = await conn.fetchval("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'")
            logger.info(f"TimescaleDB version: {ts_version}")
        except:
            logger.warning("TimescaleDB extension not found")
        
        # Test table creation
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        table_names = [row['table_name'] for row in tables]
        logger.info(f"Created tables: {', '.join(table_names)}")
        
        # Test user creation
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        logger.info(f"Users in database: {user_count}")
        
        await conn.close()
        
        logger.info("Database setup verification completed successfully")
        
    except Exception as exc:
        logger.error(f"Database verification failed: {exc}")
        raise


async def main():
    """
    Main database initialization workflow.
    
    @description
    Executes complete database setup workflow including database creation,
    extension setup, table creation, and initial data seeding.
    
    @performance Complete setup <60 seconds
    @sideEffects Full database initialization
    
    @tradingImpact CRITICAL - System initialization
    @riskLevel HIGH - Complete database setup
    """
    
    logger.info("Starting TRAIDER database initialization...")
    
    try:
        # Step 1: Create database
        await create_database_if_not_exists()
        
        # Step 2: Set up TimescaleDB
        await setup_timescaledb_extensions()
        
        # Step 3: Create tables
        await create_tables()
        
        # Step 4: Create hypertables
        await create_hypertables()
        
        # Step 5: Create indexes
        await create_indexes()
        
        # Step 6: Seed initial data
        await seed_initial_data()
        
        # Step 7: Verify setup
        await verify_setup()
        
        logger.info("✅ Database initialization completed successfully!")
        logger.info("TRAIDER V1 database is ready for trading operations.")
        
    except Exception as exc:
        logger.error(f"❌ Database initialization failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 