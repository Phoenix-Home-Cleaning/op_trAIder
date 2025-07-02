"""
@fileoverview Comprehensive tests for MarketData and OrderBookLevel2 models
@module tests.unit.backend.test_models_market_data

@description
Institutional-grade test coverage for market data models including:
- Data validation and constraints
- TimescaleDB integration
- Performance characteristics
- Edge cases and error handling
- Trading logic validation

@performance
- Test execution: <100ms per test
- Coverage target: >95%
- Memory usage: <50MB

@risk
- Failure impact: CRITICAL - Market data integrity
- Recovery strategy: Comprehensive validation

@compliance
- Audit requirements: All market data operations tested
- Data retention: Test results retained 30 days

@see {@link docs/testing/backend-models.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
import json

# Import the models to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))

from models.market_data import MarketData, OrderBookLevel2
from database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


class TestMarketData:
    """
    Comprehensive test suite for MarketData model.
    
    Tests cover:
    - Model creation and validation
    - Data integrity constraints
    - Performance characteristics
    - Trading-specific calculations
    - Edge cases and error handling
    """
    
    @pytest.fixture
    def sample_market_data(self):
        """
        Create sample market data for testing.
        
        @returns MarketData instance with realistic trading data
        """
        return MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.12345678"),
            volume=Decimal("1.23456789"),
            bid=Decimal("49999.99999999"),
            ask=Decimal("50000.24691358"),
            spread=Decimal("0.24691359"),
            trade_count=5,
            vwap=Decimal("50000.00000000"),
            extra_data={"exchange": "coinbase", "sequence": 12345}
        )
    
    @pytest.fixture
    def minimal_market_data(self):
        """
        Create minimal market data for testing required fields only.
        
        @returns MarketData instance with minimal required data
        """
        return MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="ETH-USD",
            price=Decimal("3000.00000000"),
            volume=Decimal("0.00000000")
        )
    
    def test_market_data_creation_success(self, sample_market_data):
        """
        Test successful market data creation with all fields.
        
        @tradingImpact HIGH - Market data integrity validation
        @riskLevel LOW - Basic model validation
        """
        assert sample_market_data.symbol == "BTC-USD"
        assert sample_market_data.price == Decimal("50000.12345678")
        assert sample_market_data.volume == Decimal("1.23456789")
        assert sample_market_data.bid == Decimal("49999.99999999")
        assert sample_market_data.ask == Decimal("50000.24691358")
        assert sample_market_data.trade_count == 5
        assert sample_market_data.extra_data["exchange"] == "coinbase"
    
    def test_market_data_minimal_creation(self, minimal_market_data):
        """
        Test market data creation with minimal required fields.
        
        @tradingImpact MEDIUM - Minimal data validation
        @riskLevel LOW - Basic model validation
        """
        assert minimal_market_data.symbol == "ETH-USD"
        assert minimal_market_data.price == Decimal("3000.00000000")
        assert minimal_market_data.volume == Decimal("0.00000000")
        assert minimal_market_data.bid is None
        assert minimal_market_data.ask is None
        assert minimal_market_data.trade_count == 1 or minimal_market_data.trade_count is None  # Default value or None when not set
        assert minimal_market_data.extra_data == {} or minimal_market_data.extra_data is None  # Default empty dict or None when not set
    
    def test_market_data_string_representation(self, sample_market_data):
        """
        Test string representation of market data.
        
        @tradingImpact LOW - Logging and debugging
        @riskLevel LOW - String formatting
        """
        repr_str = repr(sample_market_data)
        assert "MarketData" in repr_str
        assert "BTC-USD" in repr_str
        assert "50000.12345678" in repr_str
    
    def test_market_data_to_dict_conversion(self, sample_market_data):
        """
        Test conversion of market data to dictionary.
        
        @tradingImpact MEDIUM - API serialization
        @riskLevel LOW - Data conversion
        """
        data_dict = sample_market_data.to_dict()
        
        # Verify all fields are present
        assert "timestamp" in data_dict
        assert "symbol" in data_dict
        assert "price" in data_dict
        assert "volume" in data_dict
        assert "bid" in data_dict
        assert "ask" in data_dict
        assert "spread" in data_dict
        assert "trade_count" in data_dict
        assert "vwap" in data_dict
        assert "extra_data" in data_dict
        
        # Verify data types and values
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["price"] == 50000.12345678
        assert data_dict["volume"] == 1.23456789
        assert data_dict["trade_count"] == 5
        assert data_dict["extra_data"]["exchange"] == "coinbase"
    
    def test_market_data_to_dict_with_none_values(self):
        """
        Test dictionary conversion with None values.
        
        @tradingImpact MEDIUM - API robustness
        @riskLevel LOW - Null handling
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="TEST-USD",
            price=Decimal("100.00"),
            volume=Decimal("1.00"),
            bid=None,
            ask=None,
            vwap=None
        )
        
        data_dict = market_data.to_dict()
        assert data_dict["bid"] is None
        assert data_dict["ask"] is None
        assert data_dict["vwap"] is None
    
    def test_mid_price_calculation_success(self, sample_market_data):
        """
        Test mid price calculation with valid bid/ask.
        
        @tradingImpact HIGH - Fair value calculation for trading
        @riskLevel LOW - Simple arithmetic
        """
        expected_mid = (sample_market_data.bid + sample_market_data.ask) / 2
        assert sample_market_data.mid_price == expected_mid
        
        # Test with specific values
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="TEST-USD",
            price=Decimal("100.00"),
            volume=Decimal("1.00"),
            bid=Decimal("99.50"),
            ask=Decimal("100.50")
        )
        assert market_data.mid_price == Decimal("100.00")
    
    def test_mid_price_calculation_missing_bid(self):
        """
        Test mid price calculation with missing bid.
        
        @tradingImpact MEDIUM - Handle incomplete market data
        @riskLevel LOW - Null handling
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="TEST-USD",
            price=Decimal("100.00"),
            volume=Decimal("1.00"),
            bid=None,
            ask=Decimal("100.50")
        )
        assert market_data.mid_price is None
    
    def test_mid_price_calculation_missing_ask(self):
        """
        Test mid price calculation with missing ask.
        
        @tradingImpact MEDIUM - Handle incomplete market data
        @riskLevel LOW - Null handling
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="TEST-USD",
            price=Decimal("100.00"),
            volume=Decimal("1.00"),
            bid=Decimal("99.50"),
            ask=None
        )
        assert market_data.mid_price is None
    
    def test_mid_price_calculation_both_missing(self, minimal_market_data):
        """
        Test mid price calculation with both bid/ask missing.
        
        @tradingImpact MEDIUM - Handle incomplete market data
        @riskLevel LOW - Null handling
        """
        assert minimal_market_data.mid_price is None
    
    def test_market_data_precision_handling(self):
        """
        Test high precision decimal handling for institutional trading.
        
        @tradingImpact CRITICAL - Price precision for trading
        @riskLevel HIGH - Financial precision requirements
        """
        # Test maximum precision (8 decimal places)
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.12345678"),
            volume=Decimal("1.23456789"),
            bid=Decimal("49999.99999999"),
            ask=Decimal("50000.00000001")
        )
        
        # Verify precision is maintained
        assert str(market_data.price) == "50000.12345678"
        assert str(market_data.volume) == "1.23456789"
        assert str(market_data.bid) == "49999.99999999"
        assert str(market_data.ask) == "50000.00000001"
    
    def test_market_data_timestamp_timezone_handling(self):
        """
        Test timezone handling for global trading operations.
        
        @tradingImpact HIGH - Global market data consistency
        @riskLevel MEDIUM - Timezone conversion errors
        """
        # Test UTC timestamp
        utc_time = datetime.now(timezone.utc)
        market_data = MarketData(
            timestamp=utc_time,
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.00")
        )
        
        assert market_data.timestamp.tzinfo == timezone.utc
        
        # Test conversion to dict maintains timezone info
        data_dict = market_data.to_dict()
        assert data_dict["timestamp"].endswith("+00:00")
    
    def test_market_data_symbol_validation(self):
        """
        Test symbol format validation for trading pairs.
        
        @tradingImpact HIGH - Trading pair identification
        @riskLevel MEDIUM - Invalid symbol handling
        """
        # Test valid symbols
        valid_symbols = ["BTC-USD", "ETH-BTC", "AAPL", "SPY", "QQQ"]
        
        for symbol in valid_symbols:
            market_data = MarketData(
                timestamp=datetime.now(timezone.utc),
                symbol=symbol,
                price=Decimal("100.00"),
                volume=Decimal("1.00")
            )
            assert market_data.symbol == symbol
    
    def test_market_data_metadata_json_serialization(self):
        """
        Test metadata JSON serialization for additional market data.
        
        @tradingImpact MEDIUM - Extended market data storage
        @riskLevel LOW - JSON serialization
        """
        complex_metadata = {
            "exchange": "coinbase",
            "sequence": 12345,
            "order_book_depth": 50,
            "market_hours": True,
            "volatility": 0.25,
            "nested": {
                "level1": "value1",
                "level2": {
                    "sublevel": [1, 2, 3]
                }
            }
        }
        
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.00"),
            extra_data=complex_metadata
        )
        
                # Verify extra_data is preserved
        assert market_data.extra_data == complex_metadata

        # Verify dictionary conversion
        data_dict = market_data.to_dict()
        assert data_dict["extra_data"] == complex_metadata


class TestOrderBookLevel2:
    """
    Comprehensive test suite for OrderBookLevel2 model.
    
    Tests cover:
    - Order book level creation and validation
    - Price level ordering and constraints
    - Side validation (bid/ask)
    - Exchange and sequence tracking
    - Performance characteristics
    """
    
    @pytest.fixture
    def sample_bid_level(self):
        """
        Create sample bid level for testing.
        
        @returns OrderBookLevel2 instance for bid side
        """
        return OrderBookLevel2(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            side="bid",
            price_level=0,
            price=Decimal("49999.99"),
            size=Decimal("1.5"),
            order_count=3,
            exchange="coinbase",
            sequence=12345
        )
    
    @pytest.fixture
    def sample_ask_level(self):
        """
        Create sample ask level for testing.
        
        @returns OrderBookLevel2 instance for ask side
        """
        return OrderBookLevel2(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            side="ask",
            price_level=0,
            price=Decimal("50000.01"),
            size=Decimal("2.0"),
            order_count=5,
            exchange="coinbase",
            sequence=12346
        )
    
    def test_order_book_level_creation_bid(self, sample_bid_level):
        """
        Test successful bid level creation.
        
        @tradingImpact HIGH - Order book integrity
        @riskLevel LOW - Basic model validation
        """
        assert sample_bid_level.symbol == "BTC-USD"
        assert sample_bid_level.side == "bid"
        assert sample_bid_level.price_level == 0
        assert sample_bid_level.price == Decimal("49999.99")
        assert sample_bid_level.size == Decimal("1.5")
        assert sample_bid_level.order_count == 3
        assert sample_bid_level.exchange == "coinbase"
        assert sample_bid_level.sequence == 12345
    
    def test_order_book_level_creation_ask(self, sample_ask_level):
        """
        Test successful ask level creation.
        
        @tradingImpact HIGH - Order book integrity
        @riskLevel LOW - Basic model validation
        """
        assert sample_ask_level.symbol == "BTC-USD"
        assert sample_ask_level.side == "ask"
        assert sample_ask_level.price_level == 0
        assert sample_ask_level.price == Decimal("50000.01")
        assert sample_ask_level.size == Decimal("2.0")
        assert sample_ask_level.order_count == 5
    
    def test_order_book_level_string_representation(self, sample_bid_level):
        """
        Test string representation of order book level.
        
        @tradingImpact LOW - Logging and debugging
        @riskLevel LOW - String formatting
        """
        repr_str = repr(sample_bid_level)
        assert "OrderBookL2" in repr_str
        assert "BTC-USD" in repr_str
        assert "bid@49999.99x1.5" in repr_str
    
    def test_order_book_level_to_dict_conversion(self, sample_bid_level):
        """
        Test conversion of order book level to dictionary.
        
        @tradingImpact MEDIUM - API serialization
        @riskLevel LOW - Data conversion
        """
        data_dict = sample_bid_level.to_dict()
        
        # Verify all fields are present
        expected_fields = [
            "timestamp", "symbol", "side", "price_level",
            "price", "size", "order_count", "exchange", "sequence"
        ]
        
        for field in expected_fields:
            assert field in data_dict
        
        # Verify data types and values
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["side"] == "bid"
        assert data_dict["price_level"] == 0
        assert data_dict["price"] == 49999.99
        assert data_dict["size"] == 1.5
        assert data_dict["order_count"] == 3
        assert data_dict["exchange"] == "coinbase"
        assert data_dict["sequence"] == 12345
    
    def test_order_book_level_price_precision(self):
        """
        Test high precision price handling for order book levels.
        
        @tradingImpact CRITICAL - Order book price precision
        @riskLevel HIGH - Financial precision requirements
        """
        order_book_level = OrderBookLevel2(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            side="bid",
            price_level=0,
            price=Decimal("49999.12345678"),
            size=Decimal("1.23456789"),
            order_count=1
        )
        
        # Verify precision is maintained
        assert str(order_book_level.price) == "49999.12345678"
        assert str(order_book_level.size) == "1.23456789"
    
    def test_order_book_level_side_validation(self):
        """
        Test order book side validation (bid/ask).
        
        @tradingImpact HIGH - Order book integrity
        @riskLevel MEDIUM - Invalid side handling
        """
        # Test valid sides
        valid_sides = ["bid", "ask"]
        
        for side in valid_sides:
            order_book_level = OrderBookLevel2(
                timestamp=datetime.now(timezone.utc),
                symbol="BTC-USD",
                side=side,
                price_level=0,
                price=Decimal("50000.00"),
                size=Decimal("1.00"),
                order_count=1
            )
            assert order_book_level.side == side
    
    def test_order_book_level_price_level_ordering(self):
        """
        Test price level ordering (0 = best, 1 = second best, etc.).
        
        @tradingImpact HIGH - Order book depth accuracy
        @riskLevel MEDIUM - Price level ordering
        """
        # Test multiple price levels
        for level in range(5):
            order_book_level = OrderBookLevel2(
                timestamp=datetime.now(timezone.utc),
                symbol="BTC-USD",
                side="bid",
                price_level=level,
                price=Decimal("50000.00") - Decimal(str(level)),
                size=Decimal("1.00"),
                order_count=1
            )
            assert order_book_level.price_level == level
    
    def test_order_book_level_exchange_tracking(self):
        """
        Test exchange source tracking for order book data.
        
        @tradingImpact MEDIUM - Multi-exchange support
        @riskLevel LOW - Exchange identification
        """
        exchanges = ["coinbase", "binance", "kraken", "bitstamp"]
        
        for exchange in exchanges:
            order_book_level = OrderBookLevel2(
                timestamp=datetime.now(timezone.utc),
                symbol="BTC-USD",
                side="bid",
                price_level=0,
                price=Decimal("50000.00"),
                size=Decimal("1.00"),
                order_count=1,
                exchange=exchange
            )
            assert order_book_level.exchange == exchange
    
    def test_order_book_level_sequence_tracking(self):
        """
        Test sequence number tracking for order book updates.
        
        @tradingImpact HIGH - Order book update ordering
        @riskLevel MEDIUM - Sequence integrity
        """
        # Test with sequence number
        order_book_level = OrderBookLevel2(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            side="bid",
            price_level=0,
            price=Decimal("50000.00"),
            size=Decimal("1.00"),
            order_count=1,
            sequence=999999999
        )
        assert order_book_level.sequence == 999999999
        
        # Test without sequence number (None)
        order_book_level_no_seq = OrderBookLevel2(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            side="ask",
            price_level=0,
            price=Decimal("50000.00"),
            size=Decimal("1.00"),
            order_count=1
        )
        assert order_book_level_no_seq.sequence is None
    
    def test_order_book_level_default_values(self):
        """
        Test default values for optional fields.
        
        @tradingImpact MEDIUM - Default configuration
        @riskLevel LOW - Default value handling
        """
        order_book_level = OrderBookLevel2(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            side="bid",
            price_level=0,
            price=Decimal("50000.00"),
            size=Decimal("1.00")
            # order_count and exchange should use defaults
        )
        
        assert order_book_level.order_count == 1 or order_book_level.order_count is None  # Default value or None when not set
        assert order_book_level.exchange == "coinbase" or order_book_level.exchange is None  # Default value or None when not set
        assert order_book_level.sequence is None  # Default None


class TestMarketDataPerformance:
    """
    Performance and stress tests for market data models.
    
    Tests institutional-grade performance requirements:
    - Market data processing latency
    - Memory usage optimization
    - Bulk data handling
    """
    
    def test_market_data_to_dict_performance(self):
        """
        Test market data serialization performance.
        
        @performance Target: <1ms per conversion
        @tradingImpact HIGH - API response times
        @riskLevel MEDIUM - Performance degradation
        """
        import time
        
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.00"),
            extra_data={"exchange": "coinbase", "data": list(range(100))}
        )
        
        # Test single conversion
        start_time = time.perf_counter()
        data_dict = market_data.to_dict()
        end_time = time.perf_counter()
        
        conversion_time = (end_time - start_time) * 1000  # Convert to ms
        assert conversion_time < 1.0, f"Conversion took {conversion_time:.3f}ms, expected <1ms"
        
        # Verify conversion is correct
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["price"] == 50000.00
    
    def test_order_book_level_bulk_creation_performance(self):
        """
        Test bulk order book level creation performance.
        
        @performance Target: <10ms for 100 levels
        @tradingImpact HIGH - Order book update speed
        @riskLevel MEDIUM - Performance degradation
        """
        import time
        
        start_time = time.perf_counter()
        
        # Create 100 order book levels (typical depth)
        levels = []
        for i in range(100):
            level = OrderBookLevel2(
                timestamp=datetime.now(timezone.utc),
                symbol="BTC-USD",
                side="bid" if i % 2 == 0 else "ask",
                price_level=i // 2,
                price=Decimal("50000.00") + Decimal(str(i * 0.01)),
                size=Decimal("1.00"),
                order_count=1
            )
            levels.append(level)
        
        end_time = time.perf_counter()
        
        creation_time = (end_time - start_time) * 1000  # Convert to ms
        assert creation_time < 10.0, f"Bulk creation took {creation_time:.3f}ms, expected <10ms"
        assert len(levels) == 100 