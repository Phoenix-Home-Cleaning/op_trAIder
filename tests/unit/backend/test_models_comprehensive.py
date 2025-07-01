"""
@fileoverview Comprehensive tests for all backend models
@module tests.unit.backend.test_models_comprehensive

@description
Institutional-grade test coverage for all trading models including:
- MarketData and OrderBookLevel2 models
- Signal model with trading logic validation
- Position and Trade models
- User model with authentication
- Performance and edge case testing

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

@see {@link docs/testing/backend-models-comprehensive.md}
@since 1.0.0-alpha
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

from models.market_data import MarketData, OrderBookLevel2
from models.signal import Signal
from models.position import Position
from models.trade import Trade
from models.user import User


class TestMarketDataModel:
    """Comprehensive MarketData model tests."""
    
    def test_market_data_creation_and_validation(self):
        """Test market data creation with validation."""
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.12345678"),
            volume=Decimal("1.23456789"),
            bid=Decimal("49999.99"),
            ask=Decimal("50000.25"),
            trade_count=5,
            metadata={"exchange": "coinbase"}
        )
        
        assert market_data.symbol == "BTC-USD"
        assert market_data.price == Decimal("50000.12345678")
        assert market_data.volume == Decimal("1.23456789")
        assert market_data.trade_count == 5
        
    def test_market_data_mid_price_calculation(self):
        """Test mid price calculation for fair value."""
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.00"),
            bid=Decimal("49999.50"),
            ask=Decimal("50000.50")
        )
        
        assert market_data.mid_price == Decimal("50000.00")
        
    def test_market_data_to_dict_serialization(self):
        """Test market data serialization for API."""
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            price=Decimal("50000.00"),
            volume=Decimal("1.00")
        )
        
        data_dict = market_data.to_dict()
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["price"] == 50000.00
        assert "timestamp" in data_dict
        
    def test_market_data_precision_handling(self):
        """Test high precision decimal handling."""
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
    """Comprehensive OrderBookLevel2 model tests."""
    
    def test_order_book_level_creation(self):
        """Test order book level creation."""
        level = OrderBookLevel2(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC-USD",
            side="bid",
            price_level=0,
            price=Decimal("49999.99"),
            size=Decimal("1.5"),
            order_count=3,
            exchange="coinbase"
        )
        
        assert level.symbol == "BTC-USD"
        assert level.side == "bid"
        assert level.price_level == 0
        assert level.price == Decimal("49999.99")
        assert level.size == Decimal("1.5")
        assert level.order_count == 3
        
    def test_order_book_level_to_dict(self):
        """Test order book level serialization."""
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
        assert data_dict["price"] == 50000.01
        assert data_dict["size"] == 2.0


class TestSignalModel:
    """Comprehensive Signal model tests."""
    
    def test_signal_creation_and_validation(self):
        """Test signal creation with validation."""
        signal = Signal(
            symbol="BTC-USD",
            strategy="momentum_v1",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG",
            target_price=Decimal("52000.00"),
            stop_loss=Decimal("48000.00"),
            take_profit=Decimal("55000.00"),
            features={"rsi": 65.5, "macd": 0.025}
        )
        
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
        """Test signal execution tracking."""
        signal = Signal(
            symbol="BTC-USD",
            strategy="test_strategy",
            signal_strength=Decimal("0.8"),
            confidence=Decimal("0.9"),
            direction="LONG"
        )
        
        # Initial state
        assert signal.executed is False
        assert signal.status == "GENERATED"
        
        # Mark as executed
        execution_price = Decimal("51500.00")
        signal.mark_executed(execution_price)
        
        assert signal.executed is True
        assert signal.execution_price == execution_price
        assert signal.status == "EXECUTED"
        
    def test_signal_to_dict_serialization(self):
        """Test signal serialization for API."""
        signal = Signal(
            symbol="BTC-USD",
            strategy="test_strategy",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG",
            features={"rsi": 65.5}
        )
        
        data_dict = signal.to_dict()
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["strategy"] == "test_strategy"
        assert data_dict["signal_strength"] == 0.75
        assert data_dict["confidence"] == 0.85
        assert data_dict["direction"] == "LONG"
        assert data_dict["features"]["rsi"] == 65.5
        
    def test_signal_validation_edge_cases(self):
        """Test signal validation with edge cases."""
        # Test invalid signal strength
        signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("1.5"),  # Invalid: > 1.0
            confidence=Decimal("0.85"),
            direction="LONG"
        )
        
        is_valid = signal.validate_signal()
        assert is_valid is False
        
        # Test invalid confidence
        signal.signal_strength = Decimal("0.75")
        signal.confidence = Decimal("1.2")  # Invalid: > 1.0
        
        is_valid = signal.validate_signal()
        assert is_valid is False


class TestPositionModel:
    """Comprehensive Position model tests."""
    
    def test_position_creation_and_validation(self):
        """Test position creation with validation."""
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
        
    def test_position_pnl_calculation(self):
        """Test position P&L calculation."""
        position = Position(
            user_id=1,
            symbol="BTC-USD",
            side="LONG",
            size=Decimal("1.0"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00")
        )
        
        # Test P&L calculation method if it exists
        if hasattr(position, 'calculate_pnl'):
            pnl = position.calculate_pnl()
            assert pnl == Decimal("1000.00")  # (51000 - 50000) * 1.0
            
    def test_position_to_dict_serialization(self):
        """Test position serialization for API."""
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


class TestTradeModel:
    """Comprehensive Trade model tests."""
    
    def test_trade_creation_and_validation(self):
        """Test trade creation with validation."""
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
        
    def test_trade_to_dict_serialization(self):
        """Test trade serialization for API."""
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
    """Comprehensive User model tests."""
    
    def test_user_creation_and_validation(self):
        """Test user creation with validation."""
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
        
    def test_user_to_dict_serialization(self):
        """Test user serialization for API (excluding sensitive data)."""
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
    """Performance tests for all models."""
    
    def test_market_data_creation_performance(self):
        """Test market data creation performance."""
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
        
        # Should create 100 market data objects in <50ms
        assert creation_time < 50.0, f"Creation took {creation_time:.3f}ms, expected <50ms"
        
    def test_signal_creation_performance(self):
        """Test signal creation performance."""
        import time
        
        start_time = time.perf_counter()
        
        for i in range(100):
            signal = Signal(
                symbol=f"SYMBOL-{i}",
                strategy=f"strategy_{i % 5}",
                signal_strength=Decimal("0.75"),
                confidence=Decimal("0.85"),
                direction="LONG" if i % 2 == 0 else "SHORT"
            )
        
        end_time = time.perf_counter()
        creation_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Should create 100 signals in <100ms
        assert creation_time < 100.0, f"Creation took {creation_time:.3f}ms, expected <100ms"
        
    def test_bulk_serialization_performance(self):
        """Test bulk model serialization performance."""
        import time
        
        # Create test data
        market_data_list = []
        signal_list = []
        
        for i in range(50):
            market_data = MarketData(
                timestamp=datetime.now(timezone.utc),
                symbol=f"SYMBOL-{i}",
                price=Decimal("50000.00"),
                volume=Decimal("1.00")
            )
            market_data_list.append(market_data)
            
            signal = Signal(
                symbol=f"SYMBOL-{i}",
                strategy="test_strategy",
                signal_strength=Decimal("0.75"),
                confidence=Decimal("0.85"),
                direction="LONG"
            )
            signal_list.append(signal)
        
        # Test serialization performance
        start_time = time.perf_counter()
        
        for market_data in market_data_list:
            data_dict = market_data.to_dict()
            
        for signal in signal_list:
            data_dict = signal.to_dict()
        
        end_time = time.perf_counter()
        serialization_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Should serialize 100 objects in <50ms
        assert serialization_time < 50.0, f"Serialization took {serialization_time:.3f}ms, expected <50ms"


class TestModelEdgeCases:
    """Edge case tests for all models."""
    
    def test_market_data_null_handling(self):
        """Test market data with null/None values."""
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
        """Test signal with boundary values."""
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
        signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("1.0"),   # Maximum
            confidence=Decimal("1.0"),        # Maximum
            direction="LONG"
        )
        
        assert signal.signal_strength == Decimal("1.0")
        assert signal.confidence == Decimal("1.0")
        assert signal.is_strong is True  # 1.0 > 0.5
        assert signal.is_high_confidence is True  # 1.0 > 0.7
        
    def test_position_zero_size_handling(self):
        """Test position with zero size."""
        position = Position(
            user_id=1,
            symbol="BTC-USD",
            side="LONG",
            size=Decimal("0.0"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00")
        )
        
        assert position.size == Decimal("0.0")
        
        # Test P&L calculation with zero size
        if hasattr(position, 'calculate_pnl'):
            pnl = position.calculate_pnl()
            assert pnl == Decimal("0.0")
            
    def test_trade_partial_fill_handling(self):
        """Test trade with partial fill."""
        trade = Trade(
            user_id=1,
            symbol="BTC-USD",
            side="BUY",
            size=Decimal("1.0"),
            filled_size=Decimal("0.5"),  # Partial fill
            price=Decimal("50000.00"),
            status="PARTIALLY_FILLED"
        )
        
        assert trade.size == Decimal("1.0")
        assert trade.filled_size == Decimal("0.5")
        assert trade.status == "PARTIALLY_FILLED"
        
        # Test remaining size calculation if method exists
        if hasattr(trade, 'remaining_size'):
            remaining = trade.remaining_size()
            assert remaining == Decimal("0.5")


class TestModelIntegration:
    """Integration tests between models."""
    
    def test_signal_to_trade_workflow(self):
        """Test workflow from signal generation to trade execution."""
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
        
    def test_trade_to_position_workflow(self):
        """Test workflow from trade execution to position creation."""
        # Create a trade
        trade = Trade(
            user_id=1,
            symbol="BTC-USD",
            side="BUY",
            size=Decimal("1.0"),
            price=Decimal("50000.00"),
            status="FILLED"
        )
        
        # Create corresponding position
        position = Position(
            user_id=trade.user_id,
            symbol=trade.symbol,
            side="LONG",  # BUY trade -> LONG position
            size=trade.size,
            entry_price=trade.price,
            current_price=Decimal("51000.00"),
            status="OPEN"
        )
        
        assert position.user_id == trade.user_id
        assert position.symbol == trade.symbol
        assert position.size == trade.size
        assert position.entry_price == trade.price
        assert position.status == "OPEN"
        
    def test_market_data_to_signal_workflow(self):
        """Test workflow from market data to signal generation."""
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