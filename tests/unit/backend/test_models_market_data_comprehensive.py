"""
@fileoverview Comprehensive MarketData model tests for 95%+ coverage achievement
@module tests.unit.backend.test_models_market_data_comprehensive

@description
World-class institutional-grade test coverage for all MarketData model methods:
- MarketData __repr__, to_dict, and mid_price methods
- OrderBookLevel2 __repr__ and to_dict methods
- Edge case validation and error handling
- Real-world market data scenarios
- Data serialization and conversion logic

@performance
- Test execution: <50ms per test suite
- Coverage target: 95%+ for MarketData models
- Memory usage: <30MB

@risk
- Failure impact: CRITICAL - Market data integrity
- Recovery strategy: Data validation and regeneration

@compliance
- Audit requirements: All market data operations tested
- Data retention: Test results retained 30 days

@see {@link docs/testing/market-data-comprehensive.md}
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


class TestMarketDataComprehensive:
    """
    Comprehensive test suite for MarketData model methods.
    
    Achieves 95%+ coverage by testing all methods and edge cases.
    """
    
    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data for testing."""
        return MarketData(
            timestamp=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
            symbol="BTC-USD",
            price=Decimal("52000.00"),
            volume=Decimal("1.5"),
            bid=Decimal("51999.50"),
            ask=Decimal("52000.50"),
            spread=Decimal("1.00"),
            trade_count=5,
            vwap=Decimal("51999.75"),
            extra_data={"source": "coinbase", "quality": "good"}
        )
    
    @pytest.fixture
    def sample_order_book(self):
        """Create sample order book level for testing."""
        return OrderBookLevel2(
            timestamp=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
            symbol="ETH-USD",
            side="bid",
            price_level=0,
            price=Decimal("2999.50"),
            size=Decimal("10.5"),
            order_count=3,
            exchange="coinbase",
            sequence=12345678
        )
    
    def test_market_data_repr_method(self, sample_market_data):
        """
        Test MarketData.__repr__ method.
        
        @tradingImpact LOW - Logging and debugging
        @riskLevel LOW - String formatting
        """
        repr_str = repr(sample_market_data)
        
        assert "MarketData" in repr_str
        assert "symbol='BTC-USD'" in repr_str
        assert "timestamp='2024-01-15 10:30:00+00:00'" in repr_str
        assert "price=52000.00" in repr_str
    
    def test_market_data_to_dict_method(self, sample_market_data):
        """
        Test MarketData.to_dict method with all fields.
        
        @tradingImpact MEDIUM - Data serialization for API
        @riskLevel LOW - Read-only data conversion
        """
        result = sample_market_data.to_dict()
        
        # Verify all fields are properly converted
        assert result["timestamp"] == "2024-01-15T10:30:00+00:00"
        assert result["symbol"] == "BTC-USD"
        assert result["price"] == 52000.00
        assert result["volume"] == 1.5
        assert result["bid"] == 51999.50
        assert result["ask"] == 52000.50
        assert result["spread"] == 1.00
        assert result["trade_count"] == 5
        assert result["vwap"] == 51999.75
        assert result["extra_data"] == {"source": "coinbase", "quality": "good"}
    
    def test_market_data_to_dict_with_none_values(self):
        """
        Test MarketData.to_dict method with None values.
        
        @tradingImpact MEDIUM - Handle missing data gracefully
        @riskLevel LOW - Null value handling
        """
        market_data = MarketData(
            timestamp=None,
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.0")
        )
        
        result = market_data.to_dict()
        
        # Verify None values are handled correctly
        assert result["timestamp"] is None
        assert result["symbol"] == "BTC-USD"
        assert result["price"] == 50000.00
        assert result["volume"] == 1.0
        assert result["bid"] is None
        assert result["ask"] is None
        assert result["spread"] is None
        assert result["vwap"] is None
    
    def test_market_data_mid_price_calculation(self):
        """
        Test MarketData.mid_price property calculation.
        
        @tradingImpact HIGH - Used for fair value calculations
        @riskLevel LOW - Simple calculation
        """
        # Test with both bid and ask available
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.0"),
            bid=Decimal("49999.00"),
            ask=Decimal("50001.00")
        )
        
        mid_price = market_data.mid_price
        expected_mid = (Decimal("49999.00") + Decimal("50001.00")) / 2
        
        assert mid_price == expected_mid
        assert mid_price == Decimal("50000.00")
    
    def test_market_data_mid_price_no_bid(self):
        """
        Test MarketData.mid_price property with missing bid.
        
        @tradingImpact HIGH - Handle incomplete order book data
        @riskLevel LOW - Null value handling
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.0"),
            bid=None,
            ask=Decimal("50001.00")
        )
        
        assert market_data.mid_price is None
    
    def test_market_data_mid_price_no_ask(self):
        """
        Test MarketData.mid_price property with missing ask.
        
        @tradingImpact HIGH - Handle incomplete order book data
        @riskLevel LOW - Null value handling
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.0"),
            bid=Decimal("49999.00"),
            ask=None
        )
        
        assert market_data.mid_price is None
    
    def test_market_data_mid_price_no_bid_ask(self):
        """
        Test MarketData.mid_price property with both bid and ask missing.
        
        @tradingImpact HIGH - Handle incomplete order book data
        @riskLevel LOW - Null value handling
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.0"),
            bid=None,
            ask=None
        )
        
        assert market_data.mid_price is None
    
    def test_order_book_level2_repr_method(self, sample_order_book):
        """
        Test OrderBookLevel2.__repr__ method.
        
        @tradingImpact LOW - Logging and debugging
        @riskLevel LOW - String formatting
        """
        repr_str = repr(sample_order_book)
        
        assert "OrderBookL2" in repr_str
        assert "symbol='ETH-USD'" in repr_str
        assert "bid@2999.50x10.5" in repr_str
    
    def test_order_book_level2_repr_ask_side(self):
        """
        Test OrderBookLevel2.__repr__ method for ask side.
        
        @tradingImpact LOW - Logging and debugging
        @riskLevel LOW - String formatting
        """
        order_book = OrderBookLevel2(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            side="ask",
            price_level=1,
            price=Decimal("50001.00"),
            size=Decimal("5.25"),
            order_count=2
        )
        
        repr_str = repr(order_book)
        
        assert "OrderBookL2" in repr_str
        assert "symbol='BTC-USD'" in repr_str
        assert "ask@50001.00x5.25" in repr_str
    
    def test_order_book_level2_to_dict_method(self, sample_order_book):
        """
        Test OrderBookLevel2.to_dict method with all fields.
        
        @tradingImpact MEDIUM - Data serialization for API
        @riskLevel LOW - Read-only data conversion
        """
        result = sample_order_book.to_dict()
        
        # Verify all fields are properly converted
        assert result["timestamp"] == "2024-01-15T10:30:00+00:00"
        assert result["symbol"] == "ETH-USD"
        assert result["side"] == "bid"
        assert result["price_level"] == 0
        assert result["price"] == 2999.50
        assert result["size"] == 10.5
        assert result["order_count"] == 3
        assert result["exchange"] == "coinbase"
        assert result["sequence"] == 12345678
    
    def test_order_book_level2_to_dict_with_none_values(self):
        """
        Test OrderBookLevel2.to_dict method with None values.
        
        @tradingImpact MEDIUM - Handle missing data gracefully
        @riskLevel LOW - Null value handling
        """
        order_book = OrderBookLevel2(
            timestamp=None,
            symbol="BTC-USD",
            side="ask",
            price_level=2,
            price=Decimal("50002.00"),
            size=Decimal("3.0"),
            order_count=1,
            sequence=None
        )
        
        result = order_book.to_dict()
        
        # Verify None values are handled correctly
        assert result["timestamp"] is None
        assert result["symbol"] == "BTC-USD"
        assert result["side"] == "ask"
        assert result["price_level"] == 2
        assert result["price"] == 50002.00
        assert result["size"] == 3.0
        assert result["order_count"] == 1
        assert result["sequence"] is None
    
    def test_market_data_precision_handling(self):
        """
        Test MarketData with high precision decimal values.
        
        @tradingImpact HIGH - Precision critical for trading
        @riskLevel MEDIUM - Decimal precision handling
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("52000.12345678"),
            volume=Decimal("1.23456789"),
            bid=Decimal("51999.87654321"),
            ask=Decimal("52000.98765432")
        )
        
        result = market_data.to_dict()
        
        # Verify precision is maintained in conversion
        assert result["price"] == 52000.12345678
        assert result["volume"] == 1.23456789
        assert result["bid"] == 51999.87654321
        assert result["ask"] == 52000.98765432
        
        # Test mid price calculation with high precision
        expected_mid = (Decimal("51999.87654321") + Decimal("52000.98765432")) / 2
        assert market_data.mid_price == expected_mid
    
    def test_order_book_level2_precision_handling(self):
        """
        Test OrderBookLevel2 with high precision decimal values.
        
        @tradingImpact HIGH - Precision critical for order book
        @riskLevel MEDIUM - Decimal precision handling
        """
        order_book = OrderBookLevel2(
            timestamp=datetime.now(timezone.utc),
            symbol="ETH-USD",
            side="bid",
            price_level=0,
            price=Decimal("2999.12345678"),
            size=Decimal("10.87654321"),
            order_count=5
        )
        
        result = order_book.to_dict()
        
        # Verify precision is maintained in conversion
        assert result["price"] == 2999.12345678
        assert result["size"] == 10.87654321 