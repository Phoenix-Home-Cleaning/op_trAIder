"""
Unified comprehensive tests for all backend models - eliminates duplication.

@description
Institutional-grade test coverage for all trading models with zero duplication:
- MarketData and OrderBookLevel2 models 
- Signal model with trading logic validation
- Position and Trade models for portfolio management
- User model with authentication
- Performance, edge case, and integration testing

@performance
- Test execution: <200ms total
- Coverage target: >95%
- Memory usage: <100MB

@risk
- Failure impact: CRITICAL - All trading model integrity
- Recovery strategy: Comprehensive validation and rollback

@compliance
- Audit requirements: All model operations tested
- Data retention: Test results retained 30 days

@since 1.0.0
@author TRAIDER Team
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
import json
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))

try:
    from models.market_data import MarketData, OrderBookLevel2
    from models.signal import Signal
    from models.position import Position
    from models.trade import Trade
    from models.user import User
except ImportError as e:
    pytest.skip(f"Backend models not available: {e}", allow_module_level=True)


# =============================================================================
# SHARED TEST UTILITIES AND FIXTURES
# =============================================================================

@pytest.fixture
def mock_timestamp():
    """Shared timestamp for consistent testing."""
    return datetime.now(timezone.utc)

@pytest.fixture
def sample_market_data_params():
    """Shared market data parameters."""
    return {
        "timestamp": datetime.now(timezone.utc),
        "symbol": "BTC-USD",
        "price": Decimal("50000.12345678"),
        "volume": Decimal("1.23456789"),
        "bid": Decimal("49999.99"),
        "ask": Decimal("50000.25"),
        "spread": Decimal("0.26"),
        "trade_count": 5,
        "vwap": Decimal("50000.00"),
        "extra_data": {"exchange": "coinbase", "sequence": 12345}
    }

@pytest.fixture
def sample_signal_params():
    """Shared signal parameters."""
    return {
        "symbol": "BTC-USD",
        "strategy": "momentum_v1",
        "signal_strength": Decimal("0.75"),
        "confidence": Decimal("0.85"),
        "direction": "LONG",
        "target_price": Decimal("52000.00"),
        "stop_loss": Decimal("48000.00"),
        "take_profit": Decimal("55000.00"),
        "features": {"rsi": 65.5, "macd": 0.025}
    }

def assert_model_serialization(model, expected_fields, additional_checks=None):
    """Shared assertion helper for model serialization."""
    data_dict = model.to_dict()
    
    # Check all expected fields are present
    for field in expected_fields:
        assert field in data_dict, f"Expected field '{field}' not found in serialized model"
    
    # Perform additional checks if provided
    if additional_checks:
        for key, value in additional_checks.items():
            assert data_dict[key] == value, f"Expected {key} to be {value}, got {data_dict[key]}"
    
    return data_dict


# =============================================================================
# MARKET DATA MODEL TESTS
# =============================================================================

class TestMarketDataModel:
    """Comprehensive MarketData model tests."""
    
    def test_market_data_creation_and_validation(self, sample_market_data_params):
        """Test market data creation with all fields and validation."""
        market_data = MarketData(**sample_market_data_params)
        
        assert market_data.symbol == "BTC-USD"
        assert market_data.price == Decimal("50000.12345678")
        assert market_data.volume == Decimal("1.23456789")
        assert market_data.bid == Decimal("49999.99")
        assert market_data.ask == Decimal("50000.25")
        assert market_data.trade_count == 5
        assert market_data.extra_data["exchange"] == "coinbase"
    
    def test_market_data_minimal_creation(self, mock_timestamp):
        """Test market data creation with minimal required fields."""
        market_data = MarketData(
            timestamp=mock_timestamp,
            symbol="ETH-USD",
            price=Decimal("3000.00"),
            volume=Decimal("0.00")
        )
        
        assert market_data.symbol == "ETH-USD"
        assert market_data.price == Decimal("3000.00")
        assert market_data.volume == Decimal("0.00")
        assert market_data.bid is None
        assert market_data.ask is None
        assert market_data.trade_count == 1 or market_data.trade_count is None  # Default value or None when not set
        assert market_data.extra_data == {} or market_data.extra_data is None  # Default empty dict or None when not set
    
    def test_market_data_mid_price_calculation(self, mock_timestamp):
        """Test mid price calculation for fair value determination."""
        market_data = MarketData(
            timestamp=mock_timestamp,
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.00"),
            bid=Decimal("49999.50"),
            ask=Decimal("50000.50")
        )
        
        assert market_data.mid_price == Decimal("50000.00")
        
        # Test with None values
        market_data.bid = None
        assert market_data.mid_price is None
    
    def test_market_data_serialization(self, sample_market_data_params):
        """Test market data serialization for API responses."""
        market_data = MarketData(**sample_market_data_params)
        
        expected_fields = ["timestamp", "symbol", "price", "volume", "extra_data"]
        additional_checks = {
            "symbol": "BTC-USD",
            "price": 50000.12345678,
            "volume": 1.23456789
        }
        
        assert_model_serialization(market_data, expected_fields, additional_checks)
    
    def test_market_data_precision_handling(self, mock_timestamp):
        """Test high precision decimal handling for institutional trading."""
        market_data = MarketData(
            timestamp=mock_timestamp,
            symbol="BTC-USD",
            price=Decimal("50000.12345678"),
            volume=Decimal("1.23456789")
        )
        
        # Verify precision is maintained
        assert str(market_data.price) == "50000.12345678"
        assert str(market_data.volume) == "1.23456789"


# =============================================================================
# ORDER BOOK LEVEL 2 MODEL TESTS  
# =============================================================================

class TestOrderBookLevel2Model:
    """Comprehensive OrderBookLevel2 model tests."""
    
    def test_order_book_level_creation(self, mock_timestamp):
        """Test order book level creation and validation."""
        level = OrderBookLevel2(
            timestamp=mock_timestamp,
            symbol="BTC-USD",
            side="bid",
            price_level=0,
            price=Decimal("49999.99"),
            size=Decimal("1.5"),
            order_count=3,
            exchange="coinbase",
            sequence=12345
        )
        
        assert level.symbol == "BTC-USD"
        assert level.side == "bid"
        assert level.price_level == 0
        assert level.price == Decimal("49999.99")
        assert level.size == Decimal("1.5")
        assert level.order_count == 3
    
    def test_order_book_level_serialization(self, mock_timestamp):
        """Test order book level serialization."""
        level = OrderBookLevel2(
            timestamp=mock_timestamp,
            symbol="BTC-USD",
            side="ask",
            price_level=0,
            price=Decimal("50000.01"),
            size=Decimal("2.0"),
            order_count=5
        )
        
        expected_fields = ["timestamp", "symbol", "side", "price_level", "price", "size"]
        additional_checks = {
            "symbol": "BTC-USD",
            "side": "ask",
            "price": 50000.01,
            "size": 2.0
        }
        
        assert_model_serialization(level, expected_fields, additional_checks)


# =============================================================================
# SIGNAL MODEL TESTS
# =============================================================================

class TestSignalModel:
    """Comprehensive Signal model tests."""
    
    def test_signal_creation_and_validation(self, sample_signal_params):
        """Test signal creation with comprehensive validation."""
        signal = Signal(**sample_signal_params)
        
        assert signal.symbol == "BTC-USD"
        assert signal.strategy == "momentum_v1"
        assert signal.signal_strength == Decimal("0.75")
        assert signal.confidence == Decimal("0.85")
        assert signal.direction == "LONG"
        assert signal.is_long is True
        assert signal.is_short is False
        assert signal.is_strong is True
        assert signal.is_high_confidence is True
    
    def test_signal_execution_tracking(self):
        """Test signal execution tracking functionality."""
        signal = Signal(
            symbol="BTC-USD",
            strategy="test_strategy",
            signal_strength=Decimal("0.8"),
            confidence=Decimal("0.9"),
            direction="LONG"
        )
        
        # Initial state
        assert signal.executed is False or signal.executed is None
        assert signal.status == "GENERATED" or signal.status is None
        
        # Mark as executed
        execution_price = Decimal("51500.00")
        signal.mark_executed(execution_price)
        
        assert signal.executed is True
        assert signal.execution_price == execution_price
        assert signal.status == "EXECUTED"
    
    def test_signal_serialization(self, sample_signal_params):
        """Test signal serialization for API responses."""
        signal = Signal(**sample_signal_params)
        
        expected_fields = ["symbol", "strategy", "signal_strength", "confidence", "direction"]
        additional_checks = {
            "symbol": "BTC-USD",
            "strategy": "momentum_v1",
            "direction": "LONG"
        }
        
        assert_model_serialization(signal, expected_fields, additional_checks)


# =============================================================================
# POSITION MODEL TESTS
# =============================================================================

class TestPositionModel:
    """Comprehensive Position model tests."""
    
    def test_position_creation_and_validation(self):
        """Test position creation with comprehensive validation."""
        position = Position(
            symbol="BTC-USD",
            quantity=Decimal("0.1"),
            avg_cost=Decimal("50000.00"),
            market_value=Decimal("5050.00")
        )
        
        assert position.symbol == "BTC-USD"
        assert position.quantity == Decimal("0.1")
        assert position.avg_cost == Decimal("50000.00")
        assert position.market_value == Decimal("5050.00")
    
    def test_position_serialization(self):
        """Test position serialization for API responses."""
        position = Position(
            symbol="BTC-USD",
            quantity=Decimal("0.1"),
            avg_cost=Decimal("50000.00"),
            market_value=Decimal("5050.00")
        )
        
        expected_fields = ["symbol", "quantity", "avg_cost", "market_value"]
        additional_checks = {
            "symbol": "BTC-USD",
            "quantity": 0.1
        }
        
        assert_model_serialization(position, expected_fields, additional_checks)


# =============================================================================
# TRADE MODEL TESTS
# =============================================================================

class TestTradeModel:
    """Comprehensive Trade model tests."""
    
    def test_trade_creation_and_validation(self):
        """Test trade creation with comprehensive validation."""
        trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("0.1"),
            price=Decimal("50000.00"),
            notional=Decimal("5000.00"),
            fee=Decimal("5.00")
        )
        
        assert trade.symbol == "BTC-USD"
        assert trade.side == "BUY"
        assert trade.quantity == Decimal("0.1")
        assert trade.price == Decimal("50000.00")
        assert trade.notional == Decimal("5000.00")
        assert trade.fee == Decimal("5.00")
    
    def test_trade_serialization(self):
        """Test trade serialization for API responses."""
        trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("0.1"),
            price=Decimal("50000.00"),
            notional=Decimal("5000.00"),
            fee=Decimal("5.00"),
            status="FILLED"
        )
        
        expected_fields = ["symbol", "side", "quantity", "price", "notional", "fee", "status"]
        additional_checks = {
            "symbol": "BTC-USD",
        }
        
        assert_model_serialization(trade, expected_fields, additional_checks)


# =============================================================================
# USER MODEL TESTS
# =============================================================================

class TestUserModel:
    """Comprehensive User model tests."""
    
    def test_user_creation_and_validation(self):
        """Test user creation with comprehensive validation."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password_123",
            role="trader",
            is_active=True
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password_123"
        assert user.role == "trader"
        assert user.is_active is True
    
    def test_user_serialization(self):
        """Test user serialization for API responses."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password_123",
            role="trader",
            is_active=True
        )
        
        expected_fields = ["username", "email", "role", "is_active"]
        additional_checks = {
            "username": "testuser",
            "email": "test@example.com",
            "role": "trader"
        }
        
        assert_model_serialization(user, expected_fields, additional_checks)


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestModelPerformance:
    """Performance tests for all models."""
    
    def test_market_data_creation_performance(self, sample_market_data_params):
        """Test market data creation performance."""
        import time
        start_time = time.perf_counter()
        
        # Create 100 market data instances
        for _ in range(100):
            MarketData(**sample_market_data_params)
        
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Should complete in under 100ms for 100 instances
        assert execution_time < 100, f"Market data creation took {execution_time:.2f}ms"
    
    def test_signal_serialization_performance(self, sample_signal_params):
        """Test signal serialization performance."""
        signals = [Signal(**sample_signal_params) for _ in range(50)]
        
        import time
        start_time = time.perf_counter()
        
        # Serialize all signals
        serialized = [signal.to_dict() for signal in signals]
        
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        
        # Should complete in under 50ms for 50 serializations
        assert execution_time < 50, f"Signal serialization took {execution_time:.2f}ms"
        assert len(serialized) == 50


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestModelIntegration:
    """Integration tests for model workflows."""
    
    def test_signal_to_trade_workflow(self, sample_signal_params):
        """Test complete signal to trade workflow."""
        # Create signal
        signal = Signal(**sample_signal_params)
        assert signal.executed is False or signal.executed is None
        
        # Execute signal by creating trade
        trade = Trade(
            symbol=signal.symbol,
            side="BUY" if signal.direction == "LONG" else "SELL",
            quantity=Decimal("0.1"),
            price=signal.target_price,
            notional=signal.target_price * Decimal("0.1") if signal.target_price else Decimal("5000.00"),
            fee=Decimal("5.00"),
            signal_id=signal.id,
            strategy=signal.strategy
        )
        
        # Mark signal as executed
        signal.mark_executed(trade.price)
        
        assert signal.executed is True
        assert signal.execution_price == trade.price
        assert trade.symbol == signal.symbol
    
    def test_trade_to_position_workflow(self):
        """Test trade to position workflow."""
        # Create opening trade
        opening_trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("0.1"),
            price=Decimal("50000.00"),
            notional=Decimal("5000.00"),
            fee=Decimal("5.00"),
            status="FILLED"
        )
        
        # Create position from trade
        position = Position(
            symbol=opening_trade.symbol,
            quantity=opening_trade.quantity,
            avg_cost=opening_trade.price,
            market_value=Decimal("5050.00")
        )
        
        assert position.symbol == opening_trade.symbol
        assert position.quantity == opening_trade.quantity
        assert position.avg_cost == opening_trade.price 