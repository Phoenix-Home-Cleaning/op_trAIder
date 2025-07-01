"""
@fileoverview Comprehensive backend model tests for TRAIDER V1
@module tests.unit.backend.test_models_basic

@description
Institutional-grade test coverage for critical trading models:
- MarketData model with TimescaleDB integration
- Signal model with trading logic validation
- Position and Trade models for portfolio management
- Performance and edge case testing

@performance
- Test execution: <100ms total
- Coverage target: >90%
- Memory usage: <50MB

@risk
- Failure impact: CRITICAL - Trading model integrity
- Recovery strategy: Comprehensive validation

@compliance
- Audit requirements: All model operations tested
- Data retention: Test results retained 30 days

@see {@link docs/testing/backend-models.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
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


class TestMarketDataModel:
    """
    Comprehensive MarketData model tests.
    
    @tradingImpact CRITICAL - Market data integrity
    @riskLevel HIGH - Data quality affects all trading decisions
    """
    
    def test_market_data_creation_success(self):
        """
        Test successful market data creation with all fields.
        
        @tradingImpact HIGH - Market data validation
        @riskLevel LOW - Basic model validation
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.12345678"),
            volume=Decimal("1.23456789"),
            bid=Decimal("49999.99"),
            ask=Decimal("50000.25"),
            spread=Decimal("0.26"),
            trade_count=5,
            vwap=Decimal("50000.00"),
            metadata={"exchange": "coinbase", "sequence": 12345}
        )
        
        assert market_data.symbol == "BTC-USD"
        assert market_data.price == Decimal("50000.12345678")
        assert market_data.volume == Decimal("1.23456789")
        assert market_data.bid == Decimal("49999.99")
        assert market_data.ask == Decimal("50000.25")
        assert market_data.trade_count == 5
        assert market_data.metadata["exchange"] == "coinbase"
    
    def test_market_data_minimal_creation(self):
        """
        Test market data creation with minimal required fields.
        
        @tradingImpact MEDIUM - Minimal data validation
        @riskLevel LOW - Basic model validation
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="ETH-USD",
            price=Decimal("3000.00"),
            volume=Decimal("0.00")
        )
        
        assert market_data.symbol == "ETH-USD"
        assert market_data.price == Decimal("3000.00")
        assert market_data.volume == Decimal("0.00")
        assert market_data.bid is None
        assert market_data.ask is None
        assert market_data.trade_count == 1  # Default value
        assert market_data.metadata == {}  # Default empty dict
    
    def test_market_data_mid_price_calculation(self):
        """
        Test mid price calculation for fair value determination.
        
        @tradingImpact HIGH - Fair value calculation for trading
        @riskLevel LOW - Simple arithmetic
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
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
    
    def test_market_data_to_dict_conversion(self):
        """
        Test market data serialization for API responses.
        
        @tradingImpact MEDIUM - API data serialization
        @riskLevel LOW - Data conversion
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.00"),
            metadata={"test": "value"}
        )
        
        data_dict = market_data.to_dict()
        
        assert "timestamp" in data_dict
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["price"] == 50000.00
        assert data_dict["volume"] == 1.00
        assert data_dict["metadata"]["test"] == "value"
    
    def test_market_data_precision_handling(self):
        """
        Test high precision decimal handling for institutional trading.
        
        @tradingImpact CRITICAL - Price precision for trading
        @riskLevel HIGH - Financial precision requirements
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.12345678"),
            volume=Decimal("1.23456789")
        )
        
        # Verify precision is maintained
        assert str(market_data.price) == "50000.12345678"
        assert str(market_data.volume) == "1.23456789"


class TestOrderBookLevel2Model:
    """
    Comprehensive OrderBookLevel2 model tests.
    
    @tradingImpact HIGH - Order book integrity
    @riskLevel MEDIUM - Market depth accuracy
    """
    
    def test_order_book_level_creation(self):
        """
        Test order book level creation and validation.
        
        @tradingImpact HIGH - Order book data integrity
        @riskLevel LOW - Basic model validation
        """
        level = OrderBookLevel2(
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
        
        assert level.symbol == "BTC-USD"
        assert level.side == "bid"
        assert level.price_level == 0
        assert level.price == Decimal("49999.99")
        assert level.size == Decimal("1.5")
        assert level.order_count == 3
        assert level.exchange == "coinbase"
        assert level.sequence == 12345
    
    def test_order_book_level_to_dict(self):
        """
        Test order book level serialization.
        
        @tradingImpact MEDIUM - API data serialization
        @riskLevel LOW - Data conversion
        """
        level = OrderBookLevel2(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            side="ask",
            price_level=0,
            price=Decimal("50000.01"),
            size=Decimal("2.0"),
            order_count=5
        )
        
        data_dict = level.to_dict()
        
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["side"] == "ask"
        assert data_dict["price_level"] == 0
        assert data_dict["price"] == 50000.01
        assert data_dict["size"] == 2.0
        assert data_dict["order_count"] == 5


class TestSignalModel:
    """
    Comprehensive Signal model tests.
    
    @tradingImpact CRITICAL - Trading signal integrity
    @riskLevel HIGH - Signal accuracy affects trading performance
    """
    
    def test_signal_creation_success(self):
        """
        Test successful signal creation with validation.
        
        @tradingImpact CRITICAL - Signal integrity validation
        @riskLevel LOW - Basic model validation
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="momentum_v1",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG",
            target_price=Decimal("52000.00"),
            stop_loss=Decimal("48000.00"),
            take_profit=Decimal("55000.00"),
            features={"rsi": 65.5, "macd": 0.025, "volume_ratio": 1.25},
            model_version="v1.2.3"
        )
        
        assert signal.symbol == "BTC-USD"
        assert signal.strategy == "momentum_v1"
        assert signal.signal_strength == Decimal("0.75")
        assert signal.confidence == Decimal("0.85")
        assert signal.direction == "LONG"
        assert signal.target_price == Decimal("52000.00")
        assert signal.stop_loss == Decimal("48000.00")
        assert signal.take_profit == Decimal("55000.00")
        assert signal.model_version == "v1.2.3"
        assert signal.executed is False
        assert signal.status == "GENERATED"
    
    def test_signal_direction_properties(self):
        """
        Test signal direction property methods.
        
        @tradingImpact HIGH - Trading direction validation
        @riskLevel LOW - Property validation
        """
        # Test long signal
        long_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.8"),
            confidence=Decimal("0.9"),
            direction="LONG"
        )
        
        assert long_signal.is_long is True
        assert long_signal.is_short is False
        
        # Test short signal
        short_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("-0.7"),
            confidence=Decimal("0.8"),
            direction="SHORT"
        )
        
        assert short_signal.is_long is False
        assert short_signal.is_short is True
    
    def test_signal_strength_and_confidence_properties(self):
        """
        Test signal strength and confidence property methods.
        
        @tradingImpact HIGH - Signal quality validation
        @riskLevel LOW - Property validation
        """
        # Test strong, high confidence signal
        signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG"
        )
        
        assert signal.is_strong is True  # 0.75 > 0.5
        assert signal.is_high_confidence is True  # 0.85 > 0.7
        
        # Test weak, low confidence signal
        weak_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.3"),
            confidence=Decimal("0.6"),
            direction="LONG"
        )
        
        assert weak_signal.is_strong is False  # 0.3 < 0.5
        assert weak_signal.is_high_confidence is False  # 0.6 < 0.7
    
    def test_signal_execution_tracking(self):
        """
        Test signal execution tracking functionality.
        
        @tradingImpact CRITICAL - Signal execution validation
        @riskLevel MEDIUM - Execution state management
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="test_strategy",
            signal_strength=Decimal("0.8"),
            confidence=Decimal("0.9"),
            direction="LONG"
        )
        
        # Initial state
        assert signal.executed is False
        assert signal.execution_price is None
        assert signal.execution_timestamp is None
        assert signal.status == "GENERATED"
        
        # Mark as executed
        execution_price = Decimal("51500.00")
        execution_time = datetime.now(timezone.utc)
        
        signal.mark_executed(execution_price, execution_time)
        
        # Verify execution state
        assert signal.executed is True
        assert signal.execution_price == execution_price
        assert signal.execution_timestamp == execution_time
        assert signal.status == "EXECUTED"
    
    def test_signal_validation(self):
        """
        Test signal validation with edge cases.
        
        @tradingImpact CRITICAL - Invalid signal prevention
        @riskLevel HIGH - Data validation
        """
        # Test valid signal
        valid_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG"
        )
        
        is_valid = valid_signal.validate_signal()
        assert is_valid is True
        
        # Test invalid signal strength
        invalid_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("1.5"),  # > 1.0, invalid
            confidence=Decimal("0.85"),
            direction="LONG"
        )
        
        is_valid = invalid_signal.validate_signal()
        assert is_valid is False
    
    def test_signal_to_dict_conversion(self):
        """
        Test signal serialization for API responses.
        
        @tradingImpact MEDIUM - API data serialization
        @riskLevel LOW - Data conversion
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="test_strategy",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG",
            features={"rsi": 65.5, "macd": 0.025}
        )
        
        data_dict = signal.to_dict()
        
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["strategy"] == "test_strategy"
        assert data_dict["signal_strength"] == 0.75
        assert data_dict["confidence"] == 0.85
        assert data_dict["direction"] == "LONG"
        assert data_dict["features"]["rsi"] == 65.5
        assert data_dict["features"]["macd"] == 0.025


class TestPositionModel:
    """
    Comprehensive Position model tests.
    
    @tradingImpact HIGH - Portfolio management
    @riskLevel MEDIUM - Position tracking accuracy
    """
    
    def test_position_creation_success(self):
        """
        Test successful position creation with validation.
        
        @tradingImpact HIGH - Position tracking
        @riskLevel LOW - Basic model validation
        """
        position = Position(
            user_id=1,
            symbol="BTC-USD",
            side="LONG",
            size=Decimal("1.5"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00"),
            stop_loss=Decimal("48000.00"),
            take_profit=Decimal("55000.00"),
            unrealized_pnl=Decimal("1500.00"),
            status="OPEN"
        )
        
        assert position.user_id == 1
        assert position.symbol == "BTC-USD"
        assert position.side == "LONG"
        assert position.size == Decimal("1.5")
        assert position.entry_price == Decimal("50000.00")
        assert position.current_price == Decimal("51000.00")
        assert position.unrealized_pnl == Decimal("1500.00")
        assert position.status == "OPEN"
    
    def test_position_to_dict_conversion(self):
        """
        Test position serialization for API responses.
        
        @tradingImpact MEDIUM - API data serialization
        @riskLevel LOW - Data conversion
        """
        position = Position(
            user_id=1,
            symbol="BTC-USD",
            side="LONG",
            size=Decimal("1.5"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00")
        )
        
        data_dict = position.to_dict()
        
        assert data_dict["user_id"] == 1
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["side"] == "LONG"
        assert data_dict["size"] == 1.5
        assert data_dict["entry_price"] == 50000.00
        assert data_dict["current_price"] == 51000.00


class TestTradeModel:
    """
    Comprehensive Trade model tests.
    
    @tradingImpact HIGH - Trade execution tracking
    @riskLevel MEDIUM - Trade data accuracy
    """
    
    def test_trade_creation_success(self):
        """
        Test successful trade creation with validation.
        
        @tradingImpact HIGH - Trade tracking
        @riskLevel LOW - Basic model validation
        """
        trade = Trade(
            user_id=1,
            symbol="BTC-USD",
            side="BUY",
            size=Decimal("1.0"),
            price=Decimal("50000.00"),
            fee=Decimal("25.00"),
            status="FILLED",
            order_type="MARKET",
            trade_type="SPOT"
        )
        
        assert trade.user_id == 1
        assert trade.symbol == "BTC-USD"
        assert trade.side == "BUY"
        assert trade.size == Decimal("1.0")
        assert trade.price == Decimal("50000.00")
        assert trade.fee == Decimal("25.00")
        assert trade.status == "FILLED"
    
    def test_trade_to_dict_conversion(self):
        """
        Test trade serialization for API responses.
        
        @tradingImpact MEDIUM - API data serialization
        @riskLevel LOW - Data conversion
        """
        trade = Trade(
            user_id=1,
            symbol="BTC-USD",
            side="BUY",
            size=Decimal("1.0"),
            price=Decimal("50000.00"),
            fee=Decimal("25.00")
        )
        
        data_dict = trade.to_dict()
        
        assert data_dict["user_id"] == 1
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["side"] == "BUY"
        assert data_dict["size"] == 1.0
        assert data_dict["price"] == 50000.00
        assert data_dict["fee"] == 25.00


class TestUserModel:
    """
    Comprehensive User model tests.
    
    @tradingImpact MEDIUM - User management
    @riskLevel LOW - User data handling
    """
    
    def test_user_creation_success(self):
        """
        Test successful user creation with validation.
        
        @tradingImpact MEDIUM - User management
        @riskLevel LOW - Basic model validation
        """
        user = User(
            email="test@traider.com",
            username="testuser",
            hashed_password="hashed_password_123",
            is_active=True,
            is_verified=True,
            role="TRADER"
        )
        
        assert user.email == "test@traider.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.role == "TRADER"
    
    def test_user_to_dict_conversion(self):
        """
        Test user serialization for API responses (excluding sensitive data).
        
        @tradingImpact MEDIUM - API data serialization
        @riskLevel MEDIUM - Sensitive data handling
        """
        user = User(
            email="test@traider.com",
            username="testuser",
            hashed_password="hashed_password_123",
            is_active=True
        )
        
        data_dict = user.to_dict()
        
        assert data_dict["email"] == "test@traider.com"
        assert data_dict["username"] == "testuser"
        assert data_dict["is_active"] is True
        # Ensure password is not included in serialization
        assert "hashed_password" not in data_dict or data_dict["hashed_password"] is None


class TestModelPerformance:
    """
    Performance tests for all models.
    
    @tradingImpact HIGH - System performance
    @riskLevel MEDIUM - Performance degradation
    """
    
    def test_market_data_creation_performance(self):
        """
        Test market data creation performance.
        
        @performance Target: <50ms for 100 objects
        @tradingImpact HIGH - Market data ingestion speed
        @riskLevel MEDIUM - Performance degradation
        """
        import time
        
        start_time = time.perf_counter()
        
        for i in range(100):
            market_data = MarketData(
                timestamp=datetime.now(timezone.utc),
                symbol=f"SYMBOL-{i}",
                price=Decimal("50000.00") + Decimal(str(i)),
                volume=Decimal("1.00")
            )
        
        end_time = time.perf_counter()
        creation_time = (end_time - start_time) * 1000  # Convert to ms
        
        assert creation_time < 50.0, f"Creation took {creation_time:.3f}ms, expected <50ms"
    
    def test_signal_serialization_performance(self):
        """
        Test signal serialization performance.
        
        @performance Target: <100ms for 100 serializations
        @tradingImpact HIGH - API response times
        @riskLevel MEDIUM - Performance degradation
        """
        import time
        
        # Create signals
        signals = []
        for i in range(100):
            signal = Signal(
                symbol=f"SYMBOL-{i}",
                strategy=f"strategy_{i % 5}",
                signal_strength=Decimal("0.75"),
                confidence=Decimal("0.85"),
                direction="LONG" if i % 2 == 0 else "SHORT"
            )
            signals.append(signal)
        
        # Test serialization performance
        start_time = time.perf_counter()
        
        for signal in signals:
            data_dict = signal.to_dict()
        
        end_time = time.perf_counter()
        serialization_time = (end_time - start_time) * 1000  # Convert to ms
        
        assert serialization_time < 100.0, f"Serialization took {serialization_time:.3f}ms, expected <100ms"


class TestModelEdgeCases:
    """
    Edge case tests for all models.
    
    @tradingImpact HIGH - System robustness
    @riskLevel HIGH - Edge case handling
    """
    
    def test_market_data_null_handling(self):
        """
        Test market data with null/None values.
        
        @tradingImpact MEDIUM - Data completeness handling
        @riskLevel LOW - Null value handling
        """
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.00"),
            bid=None,
            ask=None,
            vwap=None
        )
        
        assert market_data.bid is None
        assert market_data.ask is None
        assert market_data.vwap is None
        assert market_data.mid_price is None
        
        # Test serialization with None values
        data_dict = market_data.to_dict()
        assert data_dict["bid"] is None
        assert data_dict["ask"] is None
        assert data_dict["vwap"] is None
    
    def test_signal_boundary_values(self):
        """
        Test signal with boundary values.
        
        @tradingImpact HIGH - Signal validation robustness
        @riskLevel MEDIUM - Boundary value handling
        """
        # Test minimum valid values
        signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("-1.0"),  # Minimum
            confidence=Decimal("0.0"),        # Minimum
            direction="SHORT"
        )
        
        assert signal.signal_strength == Decimal("-1.0")
        assert signal.confidence == Decimal("0.0")
        assert signal.is_strong is True  # |-1.0| > 0.5
        assert signal.is_high_confidence is False  # 0.0 < 0.7
        
        # Test maximum valid values
        signal_max = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("1.0"),   # Maximum
            confidence=Decimal("1.0"),        # Maximum
            direction="LONG"
        )
        
        assert signal_max.signal_strength == Decimal("1.0")
        assert signal_max.confidence == Decimal("1.0")
        assert signal_max.is_strong is True  # 1.0 > 0.5
        assert signal_max.is_high_confidence is True  # 1.0 > 0.7


class TestModelIntegration:
    """
    Integration tests between models.
    
    @tradingImpact HIGH - System integration
    @riskLevel MEDIUM - Cross-model consistency
    """
    
    def test_signal_to_trade_workflow(self):
        """
        Test workflow from signal generation to trade execution.
        
        @tradingImpact CRITICAL - Trading workflow integrity
        @riskLevel MEDIUM - Workflow consistency
        """
        # Create a signal
        signal = Signal(
            symbol="BTC-USD",
            strategy="momentum_v1",
            signal_strength=Decimal("0.8"),
            confidence=Decimal("0.9"),
            direction="LONG",
            target_price=Decimal("52000.00")
        )
        
        assert signal.status == "GENERATED"
        assert signal.executed is False
        
        # Mark signal as executed
        execution_price = Decimal("51500.00")
        signal.mark_executed(execution_price)
        
        assert signal.executed is True
        assert signal.execution_price == execution_price
        assert signal.status == "EXECUTED"
        
        # Create corresponding trade
        trade = Trade(
            user_id=1,
            symbol=signal.symbol,
            side="BUY",  # LONG signal -> BUY trade
            size=Decimal("1.0"),
            price=signal.execution_price,
            status="FILLED"
        )
        
        assert trade.symbol == signal.symbol
        assert trade.price == signal.execution_price
        assert trade.status == "FILLED"
    
    def test_market_data_to_signal_workflow(self):
        """
        Test workflow from market data to signal generation.
        
        @tradingImpact HIGH - Data-driven signal generation
        @riskLevel MEDIUM - Data consistency
        """
        # Create market data
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("10.0"),
            bid=Decimal("49999.50"),
            ask=Decimal("50000.50"),
            metadata={"exchange": "coinbase"}
        )
        
        # Simulate signal generation based on market data
        signal = Signal(
            symbol=market_data.symbol,
            strategy="market_data_strategy",
            signal_strength=Decimal("0.7"),
            confidence=Decimal("0.8"),
            direction="LONG",
            target_price=market_data.ask,  # Use ask price as target
            features={
                "current_price": float(market_data.price),
                "volume": float(market_data.volume),
                "spread": float(market_data.ask - market_data.bid)
            }
        )
        
        assert signal.symbol == market_data.symbol
        assert signal.target_price == market_data.ask
        assert signal.features["current_price"] == float(market_data.price)
        assert signal.features["volume"] == float(market_data.volume)
        assert signal.features["spread"] == float(market_data.ask - market_data.bid)
