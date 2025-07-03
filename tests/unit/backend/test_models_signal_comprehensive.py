"""
@fileoverview Comprehensive Signal model tests for 95%+ coverage achievement
@module tests.unit.backend.test_models_signal_comprehensive

@description
World-class institutional-grade test coverage for all Signal model methods:
- Complete method coverage (repr, to_dict, properties, lifecycle)
- Edge case validation and error handling
- Performance tracking and execution logic
- Signal validation and data integrity
- Trading logic validation with real-world scenarios

@performance
- Test execution: <100ms per test suite
- Coverage target: 95%+ for Signal model
- Memory usage: <50MB

@risk
- Failure impact: CRITICAL - Trading signal integrity
- Recovery strategy: Signal validation and regeneration

@compliance
- Audit requirements: All signal operations tested
- Data retention: Test results retained 30 days

@see {@link docs/testing/signal-comprehensive.md}
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

from models.signal import Signal


class TestSignalComprehensive:
    """
    Comprehensive test suite for Signal model methods.
    
    Achieves 95%+ coverage by testing all methods and edge cases.
    """
    
    @pytest.fixture
    def basic_signal(self):
        """Create basic signal for testing."""
        return Signal(
            symbol="BTC-USD",
            strategy="test_strategy",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG"
        )
    
    @pytest.fixture
    def executed_signal(self):
        """Create executed signal for testing."""
        signal = Signal(
            symbol="ETH-USD",
            strategy="momentum",
            signal_strength=Decimal("-0.60"),
            confidence=Decimal("0.80"),
            direction="SHORT",
            target_price=Decimal("3000.00"),
            stop_loss=Decimal("3200.00"),
            take_profit=Decimal("2800.00")
        )
        signal.executed = True
        signal.execution_price = Decimal("3000.00")
        signal.execution_timestamp = datetime.now(timezone.utc)
        # Initialize performance tracking fields
        signal.max_favorable = Decimal("0")
        signal.max_adverse = Decimal("0")
        return signal
    
    def test_signal_repr_method(self, basic_signal):
        """
        Test Signal.__repr__ method.
        
        @tradingImpact LOW - Logging and debugging
        @riskLevel LOW - String formatting
        """
        # Test with ID set
        basic_signal.id = 123
        repr_str = repr(basic_signal)
        
        assert "Signal" in repr_str
        assert "id=123" in repr_str
        assert "LONG BTC-USD" in repr_str
        assert "0.750" in repr_str
        
        # Test without ID
        basic_signal.id = None
        repr_str = repr(basic_signal)
        assert "Signal" in repr_str
        assert "LONG BTC-USD" in repr_str
    
    def test_signal_to_dict_method(self, basic_signal):
        """
        Test Signal.to_dict method with all field types.
        
        @tradingImpact MEDIUM - Data serialization for API
        @riskLevel LOW - Read-only data conversion
        """
        # Set all fields for comprehensive testing
        basic_signal.id = 456
        basic_signal.timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        basic_signal.target_price = Decimal("52000.00")
        basic_signal.stop_loss = Decimal("48000.00")
        basic_signal.take_profit = Decimal("55000.00")
        basic_signal.features = {"rsi": 65.5, "macd": 0.025}
        basic_signal.model_version = "v1.2.3"
        basic_signal.executed = True
        basic_signal.execution_price = Decimal("51500.00")
        basic_signal.execution_timestamp = datetime(2024, 1, 15, 11, 0, 0, tzinfo=timezone.utc)
        basic_signal.pnl = Decimal("1500.00")
        basic_signal.max_favorable = Decimal("2000.00")
        basic_signal.max_adverse = Decimal("-500.00")
        basic_signal.status = "EXECUTED"
        basic_signal.notes = "Test signal"
        basic_signal.extra_data = {"source": "test"}
        
        result = basic_signal.to_dict()
        
        # Verify all fields are properly converted
        assert result["id"] == 456
        assert result["timestamp"] == "2024-01-15T10:30:00+00:00"
        assert result["symbol"] == "BTC-USD"
        assert result["strategy"] == "test_strategy"
        assert result["signal_strength"] == 0.75
        assert result["confidence"] == 0.85
        assert result["direction"] == "LONG"
        assert result["target_price"] == 52000.00
        assert result["stop_loss"] == 48000.00
        assert result["take_profit"] == 55000.00
        assert result["features"] == {"rsi": 65.5, "macd": 0.025}
        assert result["model_version"] == "v1.2.3"
        assert result["executed"] is True
        assert result["execution_price"] == 51500.00
        assert result["execution_timestamp"] == "2024-01-15T11:00:00+00:00"
        assert result["pnl"] == 1500.00
        assert result["max_favorable"] == 2000.00
        assert result["max_adverse"] == -500.00
        assert result["status"] == "EXECUTED"
        assert result["notes"] == "Test signal"
        assert result["extra_data"] == {"source": "test"}
    
    def test_signal_to_dict_with_none_values(self):
        """
        Test Signal.to_dict method with None values.
        
        @tradingImpact MEDIUM - Handle missing data gracefully
        @riskLevel LOW - Null value handling
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        
        result = signal.to_dict()
        
        # Verify None values are handled correctly
        assert result["timestamp"] is None
        assert result["target_price"] is None
        assert result["stop_loss"] is None
        assert result["take_profit"] is None
        assert result["execution_price"] is None
        assert result["execution_timestamp"] is None
        assert result["pnl"] is None
        assert result["max_favorable"] is None
        assert result["max_adverse"] is None
    
    def test_signal_is_long_property(self):
        """
        Test Signal.is_long property.
        
        @tradingImpact LOW - Signal direction check
        @riskLevel LOW - Simple property
        """
        # Test LONG direction
        long_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        assert long_signal.is_long is True
        
        # Test lowercase long
        long_signal.direction = "long"
        assert long_signal.is_long is True
        
        # Test SHORT direction
        short_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("-0.5"),
            confidence=Decimal("0.7"),
            direction="SHORT"
        )
        assert short_signal.is_long is False
        
        # Test FLAT direction
        flat_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.0"),
            confidence=Decimal("0.7"),
            direction="FLAT"
        )
        assert flat_signal.is_long is False
    
    def test_signal_is_short_property(self):
        """
        Test Signal.is_short property.
        
        @tradingImpact LOW - Signal direction check
        @riskLevel LOW - Simple property
        """
        # Test SHORT direction
        short_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("-0.5"),
            confidence=Decimal("0.7"),
            direction="SHORT"
        )
        assert short_signal.is_short is True
        
        # Test lowercase short
        short_signal.direction = "short"
        assert short_signal.is_short is True
        
        # Test LONG direction
        long_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        assert long_signal.is_short is False
        
        # Test FLAT direction
        flat_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.0"),
            confidence=Decimal("0.7"),
            direction="FLAT"
        )
        assert flat_signal.is_short is False
    
    def test_signal_is_strong_property(self):
        """
        Test Signal.is_strong property.
        
        @tradingImpact MEDIUM - Signal strength assessment
        @riskLevel LOW - Simple calculation
        """
        # Test strong positive signal
        strong_long = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        assert strong_long.is_strong is True
        
        # Test strong negative signal
        strong_short = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("-0.65"),
            confidence=Decimal("0.7"),
            direction="SHORT"
        )
        assert strong_short.is_strong is True
        
        # Test weak positive signal
        weak_long = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.3"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        assert weak_long.is_strong is False
        
        # Test boundary case (exactly 0.5)
        boundary_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        assert boundary_signal.is_strong is False
        
        # Test None signal strength
        none_signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=None,
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        assert none_signal.is_strong is False
    
    def test_signal_is_high_confidence_property(self):
        """
        Test Signal.is_high_confidence property.
        
        @tradingImpact MEDIUM - Signal confidence assessment
        @riskLevel LOW - Simple calculation
        """
        # Test high confidence signal
        high_conf = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.85"),
            direction="LONG"
        )
        assert high_conf.is_high_confidence is True
        
        # Test low confidence signal
        low_conf = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.6"),
            direction="LONG"
        )
        assert low_conf.is_high_confidence is False
        
        # Test boundary case (exactly 0.7)
        boundary_conf = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        assert boundary_conf.is_high_confidence is False
        
        # Test None confidence
        none_conf = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=None,
            direction="LONG"
        )
        assert none_conf.is_high_confidence is False
    
    def test_signal_mark_executed_method(self):
        """
        Test Signal.mark_executed method.
        
        @tradingImpact HIGH - Signal execution tracking
        @riskLevel MEDIUM - Status update
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        
        # Test marking executed with price and timestamp
        execution_price = Decimal("50000.00")
        execution_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        
        signal.mark_executed(execution_price, execution_time)
        
        assert signal.executed is True
        assert signal.execution_price == execution_price
        assert signal.execution_timestamp == execution_time
        assert signal.status == "EXECUTED"
    
    def test_signal_mark_executed_without_timestamp(self):
        """
        Test Signal.mark_executed method without timestamp (uses current time).
        
        @tradingImpact HIGH - Signal execution tracking
        @riskLevel MEDIUM - Default timestamp handling
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        
        execution_price = Decimal("50000.00")
        
        # Mock datetime.now to control timestamp
        with patch('models.signal.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            
            signal.mark_executed(execution_price)
            
            assert signal.executed is True
            assert signal.execution_price == execution_price
            assert signal.execution_timestamp == mock_now
            assert signal.status == "EXECUTED"
    
    def test_signal_update_performance_long_position(self, executed_signal):
        """
        Test Signal.update_performance method for long position.
        
        @tradingImpact HIGH - Signal performance tracking
        @riskLevel MEDIUM - Performance calculations
        """
        # Set up long signal
        executed_signal.direction = "LONG"
        executed_signal.execution_price = Decimal("3000.00")
        
        # Test profitable scenario
        current_price = Decimal("3200.00")
        executed_signal.update_performance(current_price)
        
        expected_pnl = current_price - executed_signal.execution_price  # 200.00
        assert executed_signal.pnl == expected_pnl
        assert executed_signal.max_favorable == expected_pnl
        assert executed_signal.max_adverse == 0  # No adverse movement yet
        
        # Test losing scenario
        losing_price = Decimal("2800.00")
        executed_signal.update_performance(losing_price)
        
        expected_loss = losing_price - executed_signal.execution_price  # -200.00
        assert executed_signal.pnl == expected_loss
        assert executed_signal.max_favorable == expected_pnl  # Keeps previous max
        assert executed_signal.max_adverse == expected_loss
    
    def test_signal_update_performance_short_position(self, executed_signal):
        """
        Test Signal.update_performance method for short position.
        
        @tradingImpact HIGH - Signal performance tracking
        @riskLevel MEDIUM - Performance calculations
        """
        # Set up short signal
        executed_signal.direction = "SHORT"
        executed_signal.execution_price = Decimal("3000.00")
        
        # Test profitable scenario (price goes down)
        current_price = Decimal("2800.00")
        executed_signal.update_performance(current_price)
        
        expected_pnl = -(current_price - executed_signal.execution_price)  # 200.00
        assert executed_signal.pnl == expected_pnl
        assert executed_signal.max_favorable == expected_pnl
        assert executed_signal.max_adverse == 0
        
        # Test losing scenario (price goes up)
        losing_price = Decimal("3200.00")
        executed_signal.update_performance(losing_price)
        
        expected_loss = -(losing_price - executed_signal.execution_price)  # -200.00
        assert executed_signal.pnl == expected_loss
        assert executed_signal.max_favorable == expected_pnl  # Keeps previous max
        assert executed_signal.max_adverse == expected_loss
    
    def test_signal_update_performance_flat_position(self):
        """
        Test Signal.update_performance method for flat position.
        
        @tradingImpact HIGH - Signal performance tracking
        @riskLevel LOW - Flat position handling
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.0"),
            confidence=Decimal("0.7"),
            direction="FLAT"
        )
        signal.executed = True
        signal.execution_price = Decimal("3000.00")
        # Initialize performance tracking fields
        signal.max_favorable = Decimal("0")
        signal.max_adverse = Decimal("0")
        
        # Test flat position (no P&L change)
        current_price = Decimal("3200.00")
        signal.update_performance(current_price)
        
        assert signal.pnl == Decimal(0)
        assert signal.max_favorable == Decimal(0)
        assert signal.max_adverse == Decimal(0)
    
    def test_signal_update_performance_not_executed(self):
        """
        Test Signal.update_performance method for non-executed signal.
        
        @tradingImpact MEDIUM - Handle non-executed signals
        @riskLevel LOW - Early return logic
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        # Signal is not executed
        signal.executed = False
        
        current_price = Decimal("3200.00")
        signal.update_performance(current_price)
        
        # Should not update performance for non-executed signals
        assert signal.pnl == 0 or signal.pnl is None
    
    def test_signal_update_performance_no_execution_price(self):
        """
        Test Signal.update_performance method without execution price.
        
        @tradingImpact MEDIUM - Handle missing execution data
        @riskLevel LOW - Early return logic
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG"
        )
        signal.executed = True
        signal.execution_price = None  # No execution price
        
        current_price = Decimal("3200.00")
        signal.update_performance(current_price)
        
        # Should not update performance without execution price
        assert signal.pnl == 0 or signal.pnl is None
    
    def test_signal_validate_signal_success(self):
        """
        Test Signal.validate_signal method with valid data.
        
        @tradingImpact HIGH - Data integrity check
        @riskLevel MEDIUM - Validation logic
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="momentum_v1",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG",
            signal_type="entry"
        )
        
        assert signal.validate_signal() is True
    
    def test_signal_validate_signal_missing_symbol(self):
        """
        Test Signal.validate_signal method with missing symbol.
        
        @tradingImpact HIGH - Data integrity check
        @riskLevel MEDIUM - Validation logic
        """
        signal = Signal(
            symbol="",  # Empty symbol
            strategy="momentum_v1",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG"
        )
        
        assert signal.validate_signal() is False
        
        # Test None symbol
        signal.symbol = None
        assert signal.validate_signal() is False
    
    def test_signal_validate_signal_missing_strategy(self):
        """
        Test Signal.validate_signal method with missing strategy.
        
        @tradingImpact HIGH - Data integrity check
        @riskLevel MEDIUM - Validation logic
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="",  # Empty strategy
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG"
        )
        
        assert signal.validate_signal() is False
        
        # Test None strategy
        signal.strategy = None
        assert signal.validate_signal() is False
    
    def test_signal_validate_signal_invalid_strength(self):
        """
        Test Signal.validate_signal method with invalid signal strength.
        
        @tradingImpact HIGH - Data integrity check
        @riskLevel MEDIUM - Validation logic
        """
        # Test None signal strength
        signal = Signal(
            symbol="BTC-USD",
            strategy="momentum_v1",
            signal_strength=None,
            confidence=Decimal("0.85"),
            direction="LONG"
        )
        assert signal.validate_signal() is False
        
        # Test signal strength > 1
        signal.signal_strength = Decimal("1.5")
        assert signal.validate_signal() is False
        
        # Test signal strength < -1
        signal.signal_strength = Decimal("-1.5")
        assert signal.validate_signal() is False
        
        # Test boundary values (should be valid)
        signal.signal_strength = Decimal("1.0")
        assert signal.validate_signal() is True
        
        signal.signal_strength = Decimal("-1.0")
        assert signal.validate_signal() is True
    
    def test_signal_validate_signal_invalid_confidence(self):
        """
        Test Signal.validate_signal method with invalid confidence.
        
        @tradingImpact HIGH - Data integrity check
        @riskLevel MEDIUM - Validation logic
        """
        # Test None confidence
        signal = Signal(
            symbol="BTC-USD",
            strategy="momentum_v1",
            signal_strength=Decimal("0.75"),
            confidence=None,
            direction="LONG"
        )
        assert signal.validate_signal() is False
        
        # Test confidence > 1
        signal.confidence = Decimal("1.5")
        assert signal.validate_signal() is False
        
        # Test confidence < 0
        signal.confidence = Decimal("-0.1")
        assert signal.validate_signal() is False
        
        # Test boundary values (should be valid)
        signal.confidence = Decimal("1.0")
        assert signal.validate_signal() is True
        
        signal.confidence = Decimal("0.0")
        assert signal.validate_signal() is True
    
    def test_signal_validate_signal_invalid_direction(self):
        """
        Test Signal.validate_signal method with invalid direction.
        
        @tradingImpact HIGH - Data integrity check
        @riskLevel MEDIUM - Validation logic
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="momentum_v1",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="INVALID"
        )
        
        assert signal.validate_signal() is False
        
        # Test case insensitive validation
        signal.direction = "long"
        assert signal.validate_signal() is True
        
        signal.direction = "short"
        assert signal.validate_signal() is True
        
        signal.direction = "flat"
        assert signal.validate_signal() is True
    
    def test_signal_validate_signal_invalid_signal_type(self):
        """
        Test Signal.validate_signal method with invalid signal type.
        
        @tradingImpact HIGH - Data integrity check
        @riskLevel MEDIUM - Validation logic
        """
        signal = Signal(
            symbol="BTC-USD",
            strategy="momentum_v1",
            signal_strength=Decimal("0.75"),
            confidence=Decimal("0.85"),
            direction="LONG",
            signal_type="invalid_type"
        )
        
        assert signal.validate_signal() is False
        
        # Test valid signal types
        for valid_type in ["entry", "exit", "rebalance"]:
            signal.signal_type = valid_type
            assert signal.validate_signal() is True
    
    def test_signal_validate_signal_none_signal_type(self):
        """
        Test Signal.validate_signal with None signal_type.
        
        @tradingImpact HIGH - Signal validation with default type
        @riskLevel MEDIUM - Default value handling
        """
        # Create signal with None signal_type
        signal = Signal(
            symbol="BTC-USD",
            strategy="test_strategy",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG",
            signal_type=None  # This should use default "entry"
        )
        
        # Validation should pass with default signal_type
        assert signal.validate_signal() is True
        
        # Verify the original value is unchanged
        assert signal.signal_type is None
    
    def test_signal_validate_signal_with_empty_signal_type(self):
        """
        Test Signal.validate_signal with empty string signal_type.
        
        @tradingImpact HIGH - Signal validation edge case
        @riskLevel MEDIUM - Empty value handling
        """
        # Create signal with empty signal_type
        signal = Signal(
            symbol="BTC-USD",
            strategy="test_strategy",
            signal_strength=Decimal("0.5"),
            confidence=Decimal("0.7"),
            direction="LONG",
            signal_type=""  # Empty string
        )
        
        # Validation should pass for empty string (treated as valid)
        assert signal.validate_signal() is True
    
    def test_signal_validate_signal_comprehensive_edge_cases(self):
        """
        Test Signal.validate_signal with comprehensive edge cases.
        
        @tradingImpact HIGH - Complete validation testing
        @riskLevel MEDIUM - Edge case handling
        """
        # Test all None values
        signal_all_none = Signal(
            symbol=None,
            strategy=None,
            signal_strength=None,
            confidence=None,
            direction=None,
            signal_type=None
        )
        assert signal_all_none.validate_signal() is False
        
        # Test boundary values that should be valid
        signal_boundary = Signal(
            symbol="BTC-USD",
            strategy="test",
            signal_strength=Decimal("1.0"),  # Max valid
            confidence=Decimal("1.0"),       # Max valid
            direction="LONG",
            signal_type="entry"
        )
        assert signal_boundary.validate_signal() is True
        
        # Test invalid signal types
        invalid_types = ["invalid", "unknown", "bad_type", "ENTRY"]
        for invalid_type in invalid_types:
            signal_invalid = Signal(
                symbol="BTC-USD",
                strategy="test",
                signal_strength=Decimal("0.5"),
                confidence=Decimal("0.7"),
                direction="LONG",
                signal_type=invalid_type
            )
            assert signal_invalid.validate_signal() is False, f"Signal type '{invalid_type}' should be invalid" 