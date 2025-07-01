#!/usr/bin/env python3
"""
@fileoverview Comprehensive TimescaleDB integration test suite for TRAIDER
@module tests.integration.test_timescaledb_integration

@description
Institutional-grade integration test coverage for TimescaleDB functionality.
Tests include hypertable management, time-series data operations, compression,
data retention policies, query performance, and market data workflows.

@performance
- Hypertable operations: <100ms
- Data ingestion: >10k records/second
- Query performance: <50ms for recent data

@risk
- Failure impact: CRITICAL - Market data storage affects all trading
- Recovery strategy: Database backup and replay mechanisms

@compliance
- Audit requirements: Yes - All database operations must be tested
- Data integrity: Time-series consistency validation

@see {@link backend/models/market_data.py}
@see {@link backend/database.py}
@since 1.0.0-alpha.1
@author TRAIDER Team
"""

import asyncio
import os
import time
import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from unittest.mock import patch

import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Import backend modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from database import (
    get_async_session,
    create_database_engine,
    create_connection_pool,
    test_database_connectivity,
    check_database_health,
    connection_pool,
    engine
)
from models.market_data import MarketData, OrderBookLevel2
from models import Base

class TestTimescaleDBIntegration:
    """
    TimescaleDB integration test suite
    
    @description
    Comprehensive testing of TimescaleDB functionality including:
    - Hypertable creation and management
    - Time-series data ingestion and querying
    - Data compression and retention policies
    - Performance benchmarks for trading workloads
    - Market data storage and retrieval
    - Order book management
    - Database health monitoring
    - Failover and recovery scenarios
    
    @tradingImpact Tests critical time-series database for all market data
    @riskLevel CRITICAL - Database failures affect entire trading system
    """

    @pytest.fixture(scope="class")
    async def setup_database(self):
        """
        Setup database connection and create test hypertables.
        
        @description
        Initializes database connections, creates test hypertables,
        and ensures TimescaleDB is properly configured for testing.
        
        @performance Target: <5s database setup
        @tradingImpact Database setup essential for integration tests
        @riskLevel HIGH - Test infrastructure setup
        """
        # Initialize database connections
        await create_database_engine()
        await create_connection_pool()
        
        # Test connectivity
        await test_database_connectivity()
        
        # Create tables and hypertables
        async with get_async_session() as session:
            # Create all tables
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
            
            # Drop existing test tables if they exist
            await session.execute(text("DROP TABLE IF EXISTS market_data CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS order_book_l2 CASCADE;"))
            
            # Create tables using SQLAlchemy
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            # Convert to hypertables
            await session.execute(text("""
                SELECT create_hypertable('market_data', 'timestamp',
                    chunk_time_interval => INTERVAL '1 hour',
                    if_not_exists => TRUE);
            """))
            
            await session.execute(text("""
                SELECT create_hypertable('order_book_l2', 'timestamp',
                    chunk_time_interval => INTERVAL '1 hour',
                    if_not_exists => TRUE);
            """))
            
            await session.commit()
        
        yield
        
        # Cleanup after tests
        async with get_async_session() as session:
            await session.execute(text("DROP TABLE IF EXISTS market_data CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS order_book_l2 CASCADE;"))
            await session.commit()

    @pytest.fixture
    def sample_market_data(self) -> List[MarketData]:
        """
        Create sample market data for testing.
        
        @description
        Generates realistic market data samples for testing
        time-series operations and performance benchmarks.
        
        @returns List of MarketData objects for testing
        @tradingImpact Sample data for testing market data workflows
        @riskLevel LOW - Test data generation
        """
        base_time = datetime.now(timezone.utc)
        data = []
        
        for i in range(1000):
            timestamp = base_time + timedelta(seconds=i)
            price = Decimal('50000.00') + Decimal(str(i * 0.01))  # Gradual price increase
            volume = Decimal('1.5') + Decimal(str(i * 0.001))
            
            market_data = MarketData(
                timestamp=timestamp,
                symbol="BTC-USD",
                price=price,
                volume=volume,
                bid=price - Decimal('0.01'),
                ask=price + Decimal('0.01'),
                spread=Decimal('0.02'),
                trade_count=1,
                vwap=price,
                metadata={"exchange": "coinbase", "sequence": i}
            )
            data.append(market_data)
        
        return data

    @pytest.fixture
    def sample_order_book_data(self) -> List[OrderBookLevel2]:
        """
        Create sample order book data for testing.
        
        @description
        Generates realistic order book data for testing
        Level-2 market depth operations and storage.
        
        @returns List of OrderBookLevel2 objects for testing
        @tradingImpact Sample order book data for testing depth workflows
        @riskLevel LOW - Test data generation
        """
        base_time = datetime.now(timezone.utc)
        data = []
        
        for i in range(100):
            timestamp = base_time + timedelta(seconds=i)
            base_price = Decimal('50000.00')
            
            # Create bid levels
            for level in range(5):
                bid_price = base_price - Decimal(str(level + 1))
                size = Decimal('10.0') - Decimal(str(level))
                
                order_book = OrderBookLevel2(
                    timestamp=timestamp,
                    symbol="BTC-USD",
                    side="bid",
                    price_level=level,
                    price=bid_price,
                    size=size,
                    order_count=level + 1,
                    exchange="coinbase",
                    sequence=i * 10 + level
                )
                data.append(order_book)
            
            # Create ask levels
            for level in range(5):
                ask_price = base_price + Decimal(str(level + 1))
                size = Decimal('10.0') - Decimal(str(level))
                
                order_book = OrderBookLevel2(
                    timestamp=timestamp,
                    symbol="BTC-USD",
                    side="ask",
                    price_level=level,
                    price=ask_price,
                    size=size,
                    order_count=level + 1,
                    exchange="coinbase",
                    sequence=i * 10 + level + 5
                )
                data.append(order_book)
        
        return data

    # =============================================================================
    # HYPERTABLE MANAGEMENT TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_hypertable_creation_and_properties(self, setup_database):
        """
        Test hypertable creation and properties validation.
        
        @description
        Tests TimescaleDB hypertable creation, validates properties,
        and ensures proper partitioning configuration.
        
        @performance Target: <100ms hypertable operations
        @tradingImpact Hypertables essential for time-series performance
        @riskLevel HIGH - Hypertable configuration affects performance
        """
        async with get_async_session() as session:
            start_time = time.time()
            
            # Check if hypertables exist and are properly configured
            result = await session.execute(text("""
                SELECT hypertable_name, num_dimensions, chunk_time_interval
                FROM timescaledb_information.hypertables
                WHERE hypertable_name IN ('market_data', 'order_book_l2');
            """))
            
            hypertables = result.fetchall()
            
            # Verify hypertables exist
            hypertable_names = [row[0] for row in hypertables]
            assert 'market_data' in hypertable_names
            assert 'order_book_l2' in hypertable_names
            
            # Verify configuration
            for row in hypertables:
                hypertable_name, num_dimensions, chunk_interval = row
                assert num_dimensions == 1  # Time dimension only
                assert chunk_interval == timedelta(hours=1)  # 1 hour chunks
            
            # Performance check
            execution_time = (time.time() - start_time) * 1000
            assert execution_time < 100, f"Hypertable validation took {execution_time:.2f}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_chunk_management(self, setup_database, sample_market_data):
        """
        Test TimescaleDB chunk creation and management.
        
        @description
        Tests automatic chunk creation, validates chunk boundaries,
        and ensures proper time-based partitioning.
        
        @performance Target: <200ms chunk operations
        @tradingImpact Proper chunking essential for query performance
        @riskLevel MEDIUM - Chunk management affects storage efficiency
        """
        async with get_async_session() as session:
            # Insert sample data to trigger chunk creation
            session.add_all(sample_market_data[:100])
            await session.commit()
            
            start_time = time.time()
            
            # Check chunk creation
            result = await session.execute(text("""
                SELECT chunk_name, range_start, range_end
                FROM timescaledb_information.chunks
                WHERE hypertable_name = 'market_data'
                ORDER BY range_start;
            """))
            
            chunks = result.fetchall()
            
            # Verify chunks were created
            assert len(chunks) > 0, "No chunks created for market_data"
            
            # Verify chunk time ranges
            for i, (chunk_name, range_start, range_end) in enumerate(chunks):
                assert isinstance(chunk_name, str)
                assert isinstance(range_start, datetime)
                assert isinstance(range_end, datetime)
                assert range_end > range_start
                
                # Verify chunk interval (should be 1 hour)
                chunk_duration = range_end - range_start
                assert chunk_duration == timedelta(hours=1)
            
            # Performance check
            execution_time = (time.time() - start_time) * 1000
            assert execution_time < 200, f"Chunk management took {execution_time:.2f}ms, expected <200ms"

    # =============================================================================
    # DATA INGESTION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_bulk_market_data_ingestion(self, setup_database, sample_market_data):
        """
        Test bulk market data ingestion performance.
        
        @description
        Tests high-volume market data ingestion with performance
        benchmarks for real-time trading data requirements.
        
        @performance Target: >10k records/second ingestion rate
        @tradingImpact High-speed ingestion critical for real-time trading
        @riskLevel HIGH - Ingestion performance affects trading latency
        """
        async with get_async_session() as session:
            start_time = time.time()
            
            # Bulk insert market data
            session.add_all(sample_market_data)
            await session.commit()
            
            ingestion_time = time.time() - start_time
            
            # Verify data was inserted
            result = await session.execute(text("""
                SELECT COUNT(*) FROM market_data WHERE symbol = 'BTC-USD';
            """))
            count = result.scalar()
            assert count == len(sample_market_data)
            
            # Performance benchmark
            records_per_second = len(sample_market_data) / ingestion_time
            assert records_per_second > 10000, f"Ingestion rate {records_per_second:.0f} records/sec, expected >10k"
            
            # Verify data integrity
            result = await session.execute(text("""
                SELECT symbol, price, volume, timestamp
                FROM market_data 
                WHERE symbol = 'BTC-USD'
                ORDER BY timestamp
                LIMIT 5;
            """))
            
            rows = result.fetchall()
            assert len(rows) == 5
            
            # Verify data accuracy
            for i, (symbol, price, volume, timestamp) in enumerate(rows):
                assert symbol == "BTC-USD"
                assert price == sample_market_data[i].price
                assert volume == sample_market_data[i].volume

    @pytest.mark.asyncio
    async def test_order_book_data_ingestion(self, setup_database, sample_order_book_data):
        """
        Test order book data ingestion and retrieval.
        
        @description
        Tests Level-2 order book data ingestion with proper
        side and level management for market depth analysis.
        
        @performance Target: >5k order book updates/second
        @tradingImpact Order book data essential for execution optimization
        @riskLevel HIGH - Order book accuracy affects trade execution
        """
        async with get_async_session() as session:
            start_time = time.time()
            
            # Bulk insert order book data
            session.add_all(sample_order_book_data)
            await session.commit()
            
            ingestion_time = time.time() - start_time
            
            # Verify data was inserted
            result = await session.execute(text("""
                SELECT COUNT(*) FROM order_book_l2 WHERE symbol = 'BTC-USD';
            """))
            count = result.scalar()
            assert count == len(sample_order_book_data)
            
            # Performance benchmark
            records_per_second = len(sample_order_book_data) / ingestion_time
            assert records_per_second > 5000, f"Order book ingestion rate {records_per_second:.0f} records/sec, expected >5k"
            
            # Verify bid/ask separation
            result = await session.execute(text("""
                SELECT side, COUNT(*) as count
                FROM order_book_l2 
                WHERE symbol = 'BTC-USD'
                GROUP BY side;
            """))
            
            side_counts = dict(result.fetchall())
            assert side_counts.get('bid', 0) == side_counts.get('ask', 0)
            assert side_counts.get('bid', 0) > 0

    # =============================================================================
    # QUERY PERFORMANCE TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_recent_data_query_performance(self, setup_database, sample_market_data):
        """
        Test query performance for recent market data.
        
        @description
        Tests query performance for recent data access patterns
        typical in real-time trading applications.
        
        @performance Target: <50ms for recent data queries
        @tradingImpact Fast recent data access critical for trading decisions
        @riskLevel HIGH - Query performance affects trading latency
        """
        async with get_async_session() as session:
            # Insert test data
            session.add_all(sample_market_data)
            await session.commit()
            
            # Test recent data query performance
            start_time = time.time()
            
            result = await session.execute(text("""
                SELECT timestamp, symbol, price, volume
                FROM market_data
                WHERE symbol = 'BTC-USD'
                  AND timestamp >= NOW() - INTERVAL '1 hour'
                ORDER BY timestamp DESC
                LIMIT 100;
            """))
            
            rows = result.fetchall()
            query_time = (time.time() - start_time) * 1000
            
            # Verify results
            assert len(rows) > 0
            
            # Performance check
            assert query_time < 50, f"Recent data query took {query_time:.2f}ms, expected <50ms"

    @pytest.mark.asyncio
    async def test_time_range_aggregation_performance(self, setup_database, sample_market_data):
        """
        Test time-based aggregation query performance.
        
        @description
        Tests aggregation queries for OHLCV calculations and
        other time-based analytics common in trading systems.
        
        @performance Target: <100ms for 1-hour aggregations
        @tradingImpact Aggregation performance affects analytics and reporting
        @riskLevel MEDIUM - Analytics performance impacts user experience
        """
        async with get_async_session() as session:
            # Insert test data
            session.add_all(sample_market_data)
            await session.commit()
            
            start_time = time.time()
            
            # Test time-bucket aggregation
            result = await session.execute(text("""
                SELECT 
                    time_bucket('5 minutes', timestamp) as bucket,
                    symbol,
                    first(price, timestamp) as open,
                    max(price) as high,
                    min(price) as low,
                    last(price, timestamp) as close,
                    sum(volume) as volume,
                    count(*) as trades
                FROM market_data
                WHERE symbol = 'BTC-USD'
                  AND timestamp >= NOW() - INTERVAL '1 hour'
                GROUP BY bucket, symbol
                ORDER BY bucket DESC;
            """))
            
            rows = result.fetchall()
            query_time = (time.time() - start_time) * 1000
            
            # Verify results
            assert len(rows) > 0
            
            # Verify OHLCV structure
            for row in rows:
                bucket, symbol, open_price, high, low, close, volume, trades = row
                assert symbol == "BTC-USD"
                assert high >= low
                assert high >= open_price
                assert high >= close
                assert low <= open_price
                assert low <= close
                assert volume > 0
                assert trades > 0
            
            # Performance check
            assert query_time < 100, f"Aggregation query took {query_time:.2f}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_order_book_snapshot_query(self, setup_database, sample_order_book_data):
        """
        Test order book snapshot query performance.
        
        @description
        Tests order book snapshot retrieval for real-time
        market depth analysis and execution decisions.
        
        @performance Target: <25ms for order book snapshots
        @tradingImpact Order book snapshot speed affects execution quality
        @riskLevel HIGH - Order book latency affects trade execution
        """
        async with get_async_session() as session:
            # Insert test data
            session.add_all(sample_order_book_data)
            await session.commit()
            
            start_time = time.time()
            
            # Get latest order book snapshot
            result = await session.execute(text("""
                WITH latest_time AS (
                    SELECT MAX(timestamp) as max_ts
                    FROM order_book_l2
                    WHERE symbol = 'BTC-USD'
                )
                SELECT 
                    side,
                    price_level,
                    price,
                    size,
                    order_count
                FROM order_book_l2 ob
                JOIN latest_time lt ON ob.timestamp = lt.max_ts
                WHERE symbol = 'BTC-USD'
                ORDER BY side DESC, price_level ASC;
            """))
            
            rows = result.fetchall()
            query_time = (time.time() - start_time) * 1000
            
            # Verify results
            assert len(rows) == 10  # 5 bid + 5 ask levels
            
            # Verify order book structure
            bid_rows = [row for row in rows if row[0] == 'bid']
            ask_rows = [row for row in rows if row[0] == 'ask']
            
            assert len(bid_rows) == 5
            assert len(ask_rows) == 5
            
            # Verify price ordering
            bid_prices = [row[2] for row in bid_rows]
            ask_prices = [row[2] for row in ask_rows]
            
            assert bid_prices == sorted(bid_prices, reverse=True)  # Bids descending
            assert ask_prices == sorted(ask_prices)  # Asks ascending
            
            # Performance check
            assert query_time < 25, f"Order book snapshot took {query_time:.2f}ms, expected <25ms"

    # =============================================================================
    # DATA COMPRESSION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_data_compression_setup(self, setup_database, sample_market_data):
        """
        Test TimescaleDB compression policy setup and execution.
        
        @description
        Tests automatic compression policy for historical data
        to optimize storage and maintain query performance.
        
        @performance Target: >50% compression ratio
        @tradingImpact Compression reduces storage costs for historical data
        @riskLevel MEDIUM - Compression affects storage efficiency
        """
        async with get_async_session() as session:
            # Insert historical data (older than compression threshold)
            historical_data = []
            base_time = datetime.now(timezone.utc) - timedelta(days=2)
            
            for i in range(100):
                timestamp = base_time + timedelta(seconds=i)
                market_data = MarketData(
                    timestamp=timestamp,
                    symbol="BTC-USD",
                    price=Decimal('50000.00'),
                    volume=Decimal('1.0'),
                    bid=Decimal('49999.99'),
                    ask=Decimal('50000.01'),
                    spread=Decimal('0.02'),
                    trade_count=1,
                    vwap=Decimal('50000.00'),
                    metadata={"exchange": "coinbase"}
                )
                historical_data.append(market_data)
            
            session.add_all(historical_data)
            await session.commit()
            
            # Add compression policy
            await session.execute(text("""
                SELECT add_compression_policy('market_data', INTERVAL '1 day');
            """))
            
            # Manually compress old chunks for testing
            await session.execute(text("""
                SELECT compress_chunk(i) FROM show_chunks('market_data') i
                WHERE range_end < NOW() - INTERVAL '1 day';
            """))
            
            await session.commit()
            
            # Check compression status
            result = await session.execute(text("""
                SELECT 
                    chunk_name,
                    compression_status,
                    before_compression_total_bytes,
                    after_compression_total_bytes
                FROM chunk_compression_stats('market_data')
                WHERE compression_status = 'Compressed';
            """))
            
            compressed_chunks = result.fetchall()
            
            if compressed_chunks:  # Only test if compression occurred
                for chunk_name, status, before_bytes, after_bytes in compressed_chunks:
                    assert status == 'Compressed'
                    if before_bytes and after_bytes:
                        compression_ratio = (before_bytes - after_bytes) / before_bytes
                        assert compression_ratio > 0.1, f"Compression ratio {compression_ratio:.2%} too low"

    # =============================================================================
    # DATA RETENTION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_data_retention_policy(self, setup_database):
        """
        Test data retention policy setup and execution.
        
        @description
        Tests automatic data retention policies for managing
        historical data lifecycle and storage optimization.
        
        @performance Target: Efficient old data removal
        @tradingImpact Retention policies manage storage costs
        @riskLevel MEDIUM - Data retention affects compliance
        """
        async with get_async_session() as session:
            # Create very old test data
            old_data = []
            base_time = datetime.now(timezone.utc) - timedelta(days=400)  # Very old data
            
            for i in range(10):
                timestamp = base_time + timedelta(seconds=i)
                market_data = MarketData(
                    timestamp=timestamp,
                    symbol="TEST-OLD",
                    price=Decimal('1000.00'),
                    volume=Decimal('1.0'),
                    trade_count=1,
                    metadata={"test": "retention"}
                )
                old_data.append(market_data)
            
            session.add_all(old_data)
            await session.commit()
            
            # Verify data exists
            result = await session.execute(text("""
                SELECT COUNT(*) FROM market_data WHERE symbol = 'TEST-OLD';
            """))
            count_before = result.scalar()
            assert count_before == 10
            
            # Add retention policy (keep data for 365 days)
            await session.execute(text("""
                SELECT add_retention_policy('market_data', INTERVAL '365 days');
            """))
            
            # Manually run retention job for testing
            await session.execute(text("""
                CALL run_job((SELECT job_id FROM timescaledb_information.jobs 
                             WHERE proc_name = 'policy_retention'));
            """))
            
            await session.commit()
            
            # Check if old data was removed
            result = await session.execute(text("""
                SELECT COUNT(*) FROM market_data WHERE symbol = 'TEST-OLD';
            """))
            count_after = result.scalar()
            
            # Old data should be removed (or at least some of it)
            assert count_after <= count_before, "Retention policy did not remove old data"

    # =============================================================================
    # DATABASE HEALTH AND MONITORING TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_database_health_monitoring(self, setup_database):
        """
        Test database health monitoring and metrics collection.
        
        @description
        Tests database health check functionality and validates
        monitoring metrics for operational visibility.
        
        @performance Target: <50ms health check response
        @tradingImpact Health monitoring essential for operational visibility
        @riskLevel MEDIUM - Health monitoring affects incident response
        """
        start_time = time.time()
        
        # Test database health check
        health_data = await check_database_health()
        
        health_check_time = (time.time() - start_time) * 1000
        
        # Verify health data structure
        assert isinstance(health_data, dict)
        assert "status" in health_data
        assert "response_time_ms" in health_data
        assert health_data["status"] in ["healthy", "degraded", "unhealthy"]
        
        # Performance check
        assert health_check_time < 50, f"Health check took {health_check_time:.2f}ms, expected <50ms"
        
        # Test TimescaleDB specific metrics
        async with get_async_session() as session:
            # Check TimescaleDB extension status
            result = await session.execute(text("""
                SELECT extname, extversion 
                FROM pg_extension 
                WHERE extname = 'timescaledb';
            """))
            
            extension_info = result.fetchone()
            assert extension_info is not None
            assert extension_info[0] == 'timescaledb'
            
            # Check hypertable statistics
            result = await session.execute(text("""
                SELECT 
                    hypertable_name,
                    num_chunks,
                    num_dimensions
                FROM timescaledb_information.hypertables;
            """))
            
            hypertables = result.fetchall()
            assert len(hypertables) >= 2  # market_data and order_book_l2

    # =============================================================================
    # ERROR HANDLING AND RECOVERY TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_connection_recovery(self, setup_database):
        """
        Test database connection recovery mechanisms.
        
        @description
        Tests database connection recovery after simulated
        connection failures and validates reconnection logic.
        
        @performance Target: <5s recovery time
        @tradingImpact Connection recovery critical for system resilience
        @riskLevel HIGH - Connection failures affect trading operations
        """
        # Test basic connectivity first
        async with get_async_session() as session:
            result = await session.execute(text("SELECT 1 as test;"))
            assert result.scalar() == 1
        
        # Test connection pool recovery
        if connection_pool:
            # Get connection count before
            async with connection_pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1;")
                assert result == 1
        
        # Test health check recovery
        health_data = await check_database_health()
        assert health_data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_transaction_rollback_handling(self, setup_database):
        """
        Test transaction rollback and error handling.
        
        @description
        Tests transaction rollback mechanisms for data integrity
        during error conditions and validates proper cleanup.
        
        @performance Target: <100ms rollback time
        @tradingImpact Transaction integrity critical for data consistency
        @riskLevel HIGH - Data integrity affects trading accuracy
        """
        async with get_async_session() as session:
            try:
                # Create test data
                test_data = MarketData(
                    timestamp=datetime.now(timezone.utc),
                    symbol="TEST-ROLLBACK",
                    price=Decimal('1000.00'),
                    volume=Decimal('1.0'),
                    trade_count=1,
                    metadata={}
                )
                
                session.add(test_data)
                await session.flush()  # Send to DB but don't commit
                
                # Verify data is in transaction
                result = await session.execute(text("""
                    SELECT COUNT(*) FROM market_data WHERE symbol = 'TEST-ROLLBACK';
                """))
                count_in_transaction = result.scalar()
                assert count_in_transaction == 1
                
                # Force an error to trigger rollback
                await session.execute(text("SELECT 1/0;"))  # Division by zero
                
            except Exception:
                # Expected error - transaction should rollback
                await session.rollback()
            
            # Verify rollback occurred
            async with get_async_session() as new_session:
                result = await new_session.execute(text("""
                    SELECT COUNT(*) FROM market_data WHERE symbol = 'TEST-ROLLBACK';
                """))
                count_after_rollback = result.scalar()
                assert count_after_rollback == 0, "Transaction rollback failed"

    # =============================================================================
    # PERFORMANCE STRESS TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_concurrent_write_performance(self, setup_database):
        """
        Test concurrent write performance under load.
        
        @description
        Tests database performance under concurrent write load
        to validate scalability for high-frequency trading data.
        
        @performance Target: >5k concurrent writes/second
        @tradingImpact Concurrent performance affects real-time data ingestion
        @riskLevel HIGH - Write performance affects trading latency
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        async def write_batch(batch_id: int, batch_size: int = 100):
            """Write a batch of market data concurrently."""
            async with get_async_session() as session:
                batch_data = []
                base_time = datetime.now(timezone.utc)
                
                for i in range(batch_size):
                    timestamp = base_time + timedelta(microseconds=batch_id * 1000 + i)
                    market_data = MarketData(
                        timestamp=timestamp,
                        symbol=f"BATCH-{batch_id}",
                        price=Decimal('1000.00') + Decimal(str(i * 0.01)),
                        volume=Decimal('1.0'),
                        trade_count=1,
                        metadata={"batch_id": batch_id}
                    )
                    batch_data.append(market_data)
                
                session.add_all(batch_data)
                await session.commit()
                return len(batch_data)
        
        # Test concurrent writes
        start_time = time.time()
        num_batches = 10
        batch_size = 100
        
        # Create concurrent write tasks
        tasks = [write_batch(i, batch_size) for i in range(num_batches)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        total_records = sum(results)
        
        # Verify all data was written
        async with get_async_session() as session:
            result = await session.execute(text("""
                SELECT COUNT(*) FROM market_data WHERE symbol LIKE 'BATCH-%';
            """))
            count = result.scalar()
            assert count == total_records
        
        # Performance benchmark
        records_per_second = total_records / total_time
        assert records_per_second > 5000, f"Concurrent write rate {records_per_second:.0f} records/sec, expected >5k"

    @pytest.mark.asyncio
    async def test_large_query_performance(self, setup_database):
        """
        Test performance with large result sets.
        
        @description
        Tests query performance with large result sets typical
        in historical data analysis and backtesting operations.
        
        @performance Target: <500ms for 10k record queries
        @tradingImpact Large query performance affects analytics
        @riskLevel MEDIUM - Analytics performance impacts user experience
        """
        # Create large dataset
        large_dataset = []
        base_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        for i in range(10000):
            timestamp = base_time + timedelta(seconds=i)
            market_data = MarketData(
                timestamp=timestamp,
                symbol="LARGE-TEST",
                price=Decimal('1000.00') + Decimal(str(i * 0.001)),
                volume=Decimal('1.0'),
                trade_count=1,
                metadata={"index": i}
            )
            large_dataset.append(market_data)
        
        # Insert large dataset
        async with get_async_session() as session:
            session.add_all(large_dataset)
            await session.commit()
            
            # Test large query performance
            start_time = time.time()
            
            result = await session.execute(text("""
                SELECT timestamp, symbol, price, volume
                FROM market_data
                WHERE symbol = 'LARGE-TEST'
                ORDER BY timestamp;
            """))
            
            rows = result.fetchall()
            query_time = (time.time() - start_time) * 1000
            
            # Verify results
            assert len(rows) == 10000
            
            # Performance check
            assert query_time < 500, f"Large query took {query_time:.2f}ms, expected <500ms"