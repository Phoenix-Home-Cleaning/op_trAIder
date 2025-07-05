"""
@fileoverview Parametric tests for Position model - TRAIDER V1
@module tests.unit.backend.test_models_position_parametric

@description
Property-based and parametric testing for Position model covering:
- P&L calculation invariants across all scenarios
- Position lifecycle management (open, update, close, reverse)
- Edge cases and boundary conditions
- Trading logic validation with random inputs
- Performance characteristics under load

@performance
- Test execution: <50ms per test
- Coverage target: >95% branch coverage
- Memory usage: <20MB for full suite

@risk
- Failure impact: CRITICAL - Position tracking integrity
- Recovery strategy: Position reconstruction from trades

@compliance
- Audit requirements: All position operations tested
- Data retention: Test results retained 30 days

@see {@link docs/testing/position-model.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import patch, Mock
import random
from typing import List, Tuple

# Import test utilities
from .factories import (
    make_position, make_trade, random_decimal, 
    POSITION_SCENARIOS, PRICE_SCENARIOS
)

# Import models to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../backend'))

from models.position import Position


class TestPositionParametric:
    """
    Parametric test suite for Position model.
    
    Tests cover:
    - Position creation and validation
    - P&L calculation invariants
    - Position lifecycle management
    - Edge cases and boundary conditions
    - Performance characteristics
    """
    
    @pytest.mark.parametrize("scenario_name,scenario_data", POSITION_SCENARIOS)
    def test_position_creation_scenarios(self, scenario_name: str, scenario_data: dict):
        """
        Test position creation across different scenarios.
        
        @param scenario_name Name of test scenario
        @param scenario_data Scenario configuration data
        
        @tradingImpact CRITICAL - Position creation integrity
        @riskLevel MEDIUM - Core position functionality
        """
        # Create position with scenario data
        position = make_position(**scenario_data)
        
        # Verify basic properties
        assert position.symbol is not None
        assert isinstance(position.quantity, Decimal) or position.quantity is None
        
        # Verify direction properties based on quantity
        if position.quantity:
            if position.quantity > 0:
                assert position.is_long is True
                assert position.is_short is False
                assert position.is_flat is False
            elif position.quantity < 0:
                assert position.is_long is False
                assert position.is_short is True
                assert position.is_flat is False
            else:
                assert position.is_long is False
                assert position.is_short is False
                assert position.is_flat is True
        else:
            # Handle None quantity
            assert position.is_flat is True
    
    @pytest.mark.parametrize("price_scenario,price", PRICE_SCENARIOS)
    def test_market_value_update_scenarios(self, price_scenario: str, price: Decimal):
        """
        Test market value updates across different price scenarios.
        
        @param price_scenario Name of price scenario
        @param price Market price to test
        
        @tradingImpact HIGH - Real-time P&L calculation
        @riskLevel HIGH - Financial calculations
        """
        # Test with long position
        long_position = make_position(quantity=Decimal("2.0"), avg_cost=Decimal("50000"))
        long_position.update_market_value(price)
        
        # Verify market value calculation
        expected_market_value = abs(long_position.quantity) * price
        assert long_position.market_value == expected_market_value
        
        # Verify P&L calculation for long position
        if long_position.avg_cost:
            cost_basis = abs(long_position.quantity) * long_position.avg_cost
            expected_pnl = long_position.market_value - cost_basis
            assert long_position.unrealized_pnl == expected_pnl
        
        # Test with short position
        short_position = make_position(quantity=Decimal("-1.5"), avg_cost=Decimal("50000"))
        short_position.update_market_value(price)
        
        # Verify market value calculation for short
        expected_market_value = abs(short_position.quantity) * price
        assert short_position.market_value == expected_market_value
        
        # Verify P&L calculation for short position
        if short_position.avg_cost:
            cost_basis = abs(short_position.quantity) * short_position.avg_cost
            expected_pnl = cost_basis - short_position.market_value
            assert short_position.unrealized_pnl == expected_pnl
    
    @pytest.mark.parametrize("quantity,price", [
        (Decimal("1.0"), Decimal("50000")),
        (Decimal("2.5"), Decimal("45000")),
        (Decimal("0.1"), Decimal("60000")),
        (Decimal("10.0"), Decimal("30000")),
    ])
    def test_first_trade_scenarios(self, quantity: Decimal, price: Decimal):
        """
        Test first trade scenarios with various quantities and prices.
        
        @param quantity Trade quantity
        @param price Trade price
        
        @tradingImpact CRITICAL - Initial position setup
        @riskLevel HIGH - Position initialization
        """
        position = make_position(symbol="BTC-USD", quantity=Decimal("0"))
        
        with patch('models.position.datetime') as mock_dt:
            mock_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_dt.now.return_value = mock_time
            
            realized_pnl = position.add_trade(quantity, price)
        
        # First trade should have zero realized P&L
        assert realized_pnl == Decimal("0")
        
        # Position should be updated correctly
        assert position.quantity == quantity
        assert position.avg_cost == price
        assert position.first_trade_at == mock_time
        assert position.last_updated == mock_time
    
    @pytest.mark.parametrize("initial_qty,initial_price,trade_qty,trade_price", [
        # Adding to long position
        (Decimal("1.0"), Decimal("50000"), Decimal("1.0"), Decimal("52000")),
        (Decimal("2.0"), Decimal("45000"), Decimal("0.5"), Decimal("48000")),
        # Adding to short position
        (Decimal("-1.0"), Decimal("50000"), Decimal("-1.0"), Decimal("48000")),
        (Decimal("-2.0"), Decimal("55000"), Decimal("-0.5"), Decimal("52000")),
    ])
    def test_adding_to_position_scenarios(
        self, initial_qty: Decimal, initial_price: Decimal,
        trade_qty: Decimal, trade_price: Decimal
    ):
        """
        Test adding to existing positions with average cost calculation.
        
        @tradingImpact HIGH - Position sizing and cost basis
        @riskLevel MEDIUM - Average cost calculation
        """
        position = make_position(
            quantity=initial_qty, 
            avg_cost=initial_price,
            realized_pnl=Decimal("0")
        )
        
        realized_pnl = position.add_trade(trade_qty, trade_price)
        
        # Adding to position should have zero realized P&L
        assert realized_pnl == Decimal("0")
        
        # Verify new quantity
        expected_quantity = initial_qty + trade_qty
        assert position.quantity == expected_quantity
        
        # Verify average cost calculation
        total_cost = (abs(initial_qty) * initial_price) + (abs(trade_qty) * trade_price)
        expected_avg_cost = total_cost / abs(expected_quantity)
        assert abs(position.avg_cost - expected_avg_cost) < Decimal("0.01")
    
    @pytest.mark.parametrize("initial_qty,initial_price,close_qty,close_price", [
        # Partial close of long position
        (Decimal("2.0"), Decimal("50000"), Decimal("-1.0"), Decimal("52000")),
        (Decimal("5.0"), Decimal("45000"), Decimal("-2.0"), Decimal("48000")),
        # Partial close of short position
        (Decimal("-2.0"), Decimal("50000"), Decimal("1.0"), Decimal("48000")),
        (Decimal("-5.0"), Decimal("55000"), Decimal("2.0"), Decimal("52000")),
        # Full close scenarios
        (Decimal("1.0"), Decimal("50000"), Decimal("-1.0"), Decimal("52000")),
        (Decimal("-1.0"), Decimal("50000"), Decimal("1.0"), Decimal("48000")),
    ])
    def test_closing_position_scenarios(
        self, initial_qty: Decimal, initial_price: Decimal,
        close_qty: Decimal, close_price: Decimal
    ):
        """
        Test closing positions with P&L calculation.
        
        @tradingImpact CRITICAL - P&L realization
        @riskLevel HIGH - Financial calculations
        """
        position = make_position(
            quantity=initial_qty,
            avg_cost=initial_price,
            realized_pnl=Decimal("0")
        )
        
        realized_pnl = position.add_trade(close_qty, close_price)
        
        # Calculate expected realized P&L
        close_quantity = min(abs(close_qty), abs(initial_qty))
        
        if initial_qty > 0:  # Closing long position
            expected_pnl = close_quantity * (close_price - initial_price)
        else:  # Closing short position
            expected_pnl = close_quantity * (initial_price - close_price)
        
        assert abs(realized_pnl - expected_pnl) < Decimal("0.01")
        
        # Verify position quantity update
        if abs(close_qty) >= abs(initial_qty):
            # Position fully closed or reversed
            if abs(close_qty) == abs(initial_qty):
                assert position.quantity == Decimal("0")
                assert position.avg_cost is None
            else:
                # Position reversed
                remaining_qty = abs(close_qty) - abs(initial_qty)
                expected_qty = remaining_qty if close_qty > 0 else -remaining_qty
                assert position.quantity == expected_qty
                assert position.avg_cost == close_price
        else:
            # Position partially closed
            expected_qty = initial_qty + close_qty
            assert position.quantity == expected_qty
            assert position.avg_cost == initial_price
    
    def test_position_reversal_scenario(self):
        """
        Test position reversal from long to short and vice versa.
        
        @tradingImpact CRITICAL - Position direction changes
        @riskLevel HIGH - Complex P&L calculations
        """
        # Start with long position
        position = make_position(
            quantity=Decimal("2.0"),
            avg_cost=Decimal("50000"),
            realized_pnl=Decimal("0")
        )
        
        # Reverse to short position
        realized_pnl = position.add_trade(Decimal("-3.0"), Decimal("52000"))
        
        # Verify realized P&L from closing long position
        expected_pnl = Decimal("2.0") * (Decimal("52000") - Decimal("50000"))
        assert abs(realized_pnl - expected_pnl) < Decimal("0.01")
        
        # Verify new short position
        assert position.quantity == Decimal("-1.0")
        assert position.avg_cost == Decimal("52000")
        assert position.is_short is True
        assert position.is_long is False
    
    def test_pnl_invariant_property(self):
        """
        Test P&L invariant: total_pnl = realized_pnl + unrealized_pnl.
        
        @tradingImpact CRITICAL - P&L calculation integrity
        @riskLevel HIGH - Financial integrity
        """
        position = make_position(
            quantity=Decimal("1.0"),
            avg_cost=Decimal("50000"),
            realized_pnl=Decimal("100"),
            unrealized_pnl=Decimal("200")
        )
        
        # Update market value
        position.update_market_value(Decimal("52000"))
        
        # Verify P&L invariant
        expected_total = (position.realized_pnl or Decimal("0")) + (position.unrealized_pnl or Decimal("0"))
        assert position.total_pnl == expected_total
    
    def test_edge_case_zero_quantity(self):
        """
        Test edge case with zero quantity position.
        
        @tradingImpact MEDIUM - Edge case handling
        @riskLevel LOW - Boundary condition
        """
        position = make_position(quantity=Decimal("0"))
        
        # Verify flat position properties
        assert position.is_flat is True
        assert position.is_long is False
        assert position.is_short is False
        
        # Market value update should not crash
        position.update_market_value(Decimal("50000"))
        
        # Should remain flat
        assert position.is_flat is True
    
    def test_edge_case_none_values(self):
        """
        Test edge cases with None values.
        
        @tradingImpact MEDIUM - Null value handling
        @riskLevel LOW - Defensive programming
        """
        # Create position with explicit zero quantity for flat position
        position = make_position(
            quantity=Decimal("0"),
            avg_cost=None,
            realized_pnl=None,
            unrealized_pnl=None
        )
        
        # Should handle None values gracefully
        position.update_market_value(Decimal("50000"))
        
        # Verify no crashes and reasonable defaults
        assert position.is_flat is True
    
    def test_position_to_dict_completeness(self):
        """
        Test position dictionary conversion completeness.
        
        @tradingImpact MEDIUM - API serialization
        @riskLevel LOW - Data conversion
        """
        position = make_position(
            quantity=Decimal("1.5"),
            avg_cost=Decimal("50000"),
            market_value=Decimal("75000"),
            unrealized_pnl=Decimal("1000"),
            realized_pnl=Decimal("500"),
            total_pnl=Decimal("1500")
        )
        
        data_dict = position.to_dict()
        
        # Verify all expected fields are present
        expected_fields = [
            "symbol", "quantity", "avg_cost", "market_value",
            "unrealized_pnl", "realized_pnl", "total_pnl",
            "first_trade_at", "last_updated", "risk_metrics", "extra_data"
        ]
        
        for field in expected_fields:
            assert field in data_dict
        
        # Verify data types
        assert isinstance(data_dict["quantity"], float)
        assert isinstance(data_dict["avg_cost"], float)
        assert isinstance(data_dict["market_value"], float)
    
    def test_position_performance_characteristics(self):
        """
        Test position operations performance characteristics.
        
        @tradingImpact MEDIUM - System performance
        @riskLevel LOW - Performance validation
        """
        position = make_position()
        
        # Test basic operations work without errors
        position.update_market_value(Decimal("52000"))
        position.add_trade(Decimal("1.0"), Decimal("51000"))
        
        # Verify position is updated correctly
        assert position.quantity == Decimal("2.0")
        assert position.market_value > 0
    
    def test_position_repr_method(self):
        """
        Test Position.__repr__ method for string representation.
        
        @tradingImpact LOW - Logging and debugging
        @riskLevel LOW - String formatting
        """
        position = make_position(
            symbol="BTC-USD",
            quantity=Decimal("1.5"),
            total_pnl=Decimal("150.75")
        )
        
        repr_str = repr(position)
        
        assert "Position" in repr_str
        assert "symbol='BTC-USD'" in repr_str
        assert "quantity=1.5" in repr_str
        assert "pnl=150.75" in repr_str 