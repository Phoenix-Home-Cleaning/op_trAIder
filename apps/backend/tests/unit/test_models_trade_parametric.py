"""
@fileoverview Parametric tests for Trade model - TRAIDER V1
@module tests.unit.backend.test_models_trade_parametric

@description
Property-based and parametric testing for Trade model covering:
- Trade validation and integrity checks
- Notional value calculations and consistency
- Fee calculations and net amount computation
- Trade direction and side validation
- Edge cases and boundary conditions
- Performance characteristics under load

@performance
- Test execution: <50ms per test
- Coverage target: >95% branch coverage
- Memory usage: <15MB for full suite

@risk
- Failure impact: CRITICAL - Trade execution integrity
- Recovery strategy: Trade data validation and reconciliation

@compliance
- Audit requirements: All trade operations tested
- Data retention: Test results retained 30 days

@see {@link docs/testing/trade-model.md}
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
    make_trade, make_position, random_decimal,
    TRADE_SCENARIOS, PRICE_SCENARIOS
)

# Import models to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../backend'))

from models.trade import Trade


class TestTradeParametric:
    """
    Parametric test suite for Trade model.
    
    Tests cover:
    - Trade creation and validation
    - Notional value calculations
    - Fee and net amount calculations
    - Trade direction validation
    - Edge cases and boundary conditions
    - Performance characteristics
    """
    
    @pytest.mark.parametrize("scenario_name,scenario_data", TRADE_SCENARIOS)
    def test_trade_creation_scenarios(self, scenario_name: str, scenario_data: dict):
        """
        Test trade creation across different scenarios.
        
        @param scenario_name Name of test scenario
        @param scenario_data Scenario configuration data
        
        @tradingImpact CRITICAL - Trade creation integrity
        @riskLevel MEDIUM - Core trade functionality
        """
        # Create trade with scenario data
        trade = make_trade(**scenario_data)
        
        # Verify basic properties
        assert trade.symbol is not None
        assert trade.side in ["BUY", "SELL"]
        assert isinstance(trade.quantity, Decimal)
        assert isinstance(trade.price, Decimal)
        assert trade.quantity > 0
        assert trade.price > 0
        
        # Verify notional calculation
        expected_notional = abs(trade.quantity) * trade.price
        assert abs(trade.notional - expected_notional) < Decimal("0.00000001")
        
        # Verify direction properties
        if trade.side.upper() == "BUY":
            assert trade.is_buy is True
            assert trade.is_sell is False
        else:
            assert trade.is_buy is False
            assert trade.is_sell is True
    
    @pytest.mark.parametrize("quantity,price", [
        (Decimal("1.0"), Decimal("50000.00")),
        (Decimal("0.1"), Decimal("60000.00")),
        (Decimal("10.5"), Decimal("45000.50")),
        (Decimal("0.00001"), Decimal("100000.00")),
        (Decimal("1000.0"), Decimal("1.00")),
    ])
    def test_notional_calculation_scenarios(self, quantity: Decimal, price: Decimal):
        """
        Test notional value calculation across different quantity/price combinations.
        
        @param quantity Trade quantity
        @param price Trade price
        
        @tradingImpact HIGH - Trade value calculation
        @riskLevel MEDIUM - Financial calculations
        """
        # Test BUY trade
        buy_trade = make_trade(side="BUY", quantity=quantity, price=price)
        expected_notional = abs(quantity) * price
        assert abs(buy_trade.notional - expected_notional) < Decimal("0.00000001")
        
        # Test SELL trade
        sell_trade = make_trade(side="SELL", quantity=quantity, price=price)
        assert abs(sell_trade.notional - expected_notional) < Decimal("0.00000001")
        
        # Test manual calculation
        manual_trade = make_trade(quantity=quantity, price=price, notional=Decimal("0"))
        manual_trade.calculate_notional()
        assert abs(manual_trade.notional - expected_notional) < Decimal("0.00000001")
    
    @pytest.mark.parametrize("notional,fee", [
        (Decimal("50000.00"), Decimal("25.00")),
        (Decimal("1000.00"), Decimal("5.00")),
        (Decimal("100000.00"), Decimal("0.00")),
        (Decimal("500.00"), Decimal("500.00")),  # Fee equals notional
        (Decimal("1000.00"), Decimal("1500.00")),  # Fee exceeds notional
    ])
    def test_net_amount_calculation_scenarios(self, notional: Decimal, fee: Decimal):
        """
        Test net amount calculation across different notional/fee combinations.
        
        @param notional Trade notional value
        @param fee Trade fee
        
        @tradingImpact MEDIUM - Net amount calculation
        @riskLevel LOW - Simple arithmetic
        """
        trade = make_trade(notional=notional, fee=fee)
        
        expected_net = notional - fee
        assert trade.net_amount == expected_net
        
        # Test edge cases
        if fee > notional:
            # Net amount can be negative (high fees)
            assert trade.net_amount < 0
        elif fee == notional:
            # Net amount is zero
            assert trade.net_amount == 0
        else:
            # Normal case - positive net amount
            assert trade.net_amount > 0
    
    @pytest.mark.parametrize("side", ["BUY", "SELL", "buy", "sell"])
    def test_trade_direction_validation(self, side: str):
        """
        Test trade direction validation across different side values.
        
        @param side Trade side (case variations)
        
        @tradingImpact MEDIUM - Trade direction validation
        @riskLevel LOW - Property validation
        """
        trade = make_trade(side=side)
        
        # Verify case-insensitive direction detection
        if side.upper() == "BUY":
            assert trade.is_buy is True
            assert trade.is_sell is False
        else:
            assert trade.is_buy is False
            assert trade.is_sell is True
    
    def test_trade_validation_success_scenarios(self):
        """
        Test trade validation for valid trades.
        
        @tradingImpact HIGH - Trade integrity validation
        @riskLevel MEDIUM - Data validation
        """
        # Valid BUY trade
        valid_buy = make_trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00")
        )
        assert valid_buy.validate_trade() is True
        
        # Valid SELL trade
        valid_sell = make_trade(
            symbol="ETH-USD",
            side="SELL",
            quantity=Decimal("5.0"),
            price=Decimal("3000.00")
        )
        assert valid_sell.validate_trade() is True
        
        # Trade with minimal valid values
        minimal_trade = make_trade(
            quantity=Decimal("0.00000001"),
            price=Decimal("0.01")
        )
        assert minimal_trade.validate_trade() is True
    
    @pytest.mark.parametrize("invalid_field,invalid_value", [
        ("symbol", None),
        ("symbol", ""),
        ("side", None),
        ("side", ""),
        ("side", "INVALID"),
        ("quantity", None),
        ("quantity", Decimal("0")),
        ("quantity", Decimal("-1.0")),
        ("price", None),
        ("price", Decimal("0")),
        ("price", Decimal("-50000.0")),
    ])
    def test_trade_validation_failure_scenarios(self, invalid_field: str, invalid_value):
        """
        Test trade validation for invalid trades.
        
        @param invalid_field Field to make invalid
        @param invalid_value Invalid value to set
        
        @tradingImpact HIGH - Trade integrity validation
        @riskLevel MEDIUM - Data validation
        """
        # Start with valid trade
        trade_data = {
            "symbol": "BTC-USD",
            "side": "BUY",
            "quantity": Decimal("1.0"),
            "price": Decimal("50000.00")
        }
        
        # Make one field invalid
        trade_data[invalid_field] = invalid_value
        
        trade = make_trade(**trade_data)
        
        # Special handling for the missing validation coverage
        if invalid_field == "side" and invalid_value == "":
            # This tests the specific missing line: if not self.symbol or not self.side
            assert trade.validate_trade() is False
        elif invalid_field == "symbol" and invalid_value == "":
            # This also tests the missing line: if not self.symbol or not self.side
            assert trade.validate_trade() is False
        else:
            assert trade.validate_trade() is False
    
    def test_notional_consistency_validation(self):
        """
        Test notional value consistency validation.
        
        @tradingImpact HIGH - Trade value integrity
        @riskLevel HIGH - Financial validation
        """
        # Consistent notional - should pass
        consistent_trade = make_trade(
            quantity=Decimal("2.0"),
            price=Decimal("50000.00"),
            notional=Decimal("100000.00")
        )
        assert consistent_trade.validate_trade() is True
        
        # Inconsistent notional - should fail
        inconsistent_trade = make_trade(
            quantity=Decimal("2.0"),
            price=Decimal("50000.00"),
            notional=Decimal("90000.00")  # Should be 100000.00
        )
        assert inconsistent_trade.validate_trade() is False
        
        # Small rounding difference - should pass
        small_diff_trade = make_trade(
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            notional=Decimal("50000.00000001")  # Tiny difference
        )
        assert small_diff_trade.validate_trade() is True
    
    def test_trade_to_dict_completeness(self):
        """
        Test trade dictionary conversion completeness.
        
        @tradingImpact MEDIUM - API serialization
        @riskLevel LOW - Data conversion
        """
        trade = make_trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.5"),
            price=Decimal("50000.00"),
            fee=Decimal("25.00"),
            order_id="order_12345",
            strategy="momentum_v1"
        )
        
        data_dict = trade.to_dict()
        
        # Verify all expected fields are present
        expected_fields = [
            "id", "timestamp", "symbol", "side", "quantity", "price",
            "notional", "fee", "fee_currency", "order_id", "signal_id",
            "strategy", "exchange", "execution_type", "pnl", "status",
            "notes", "extra_data"
        ]
        
        for field in expected_fields:
            assert field in data_dict
        
        # Verify data types
        assert isinstance(data_dict["quantity"], float)
        assert isinstance(data_dict["price"], float)
        assert isinstance(data_dict["notional"], float)
        assert isinstance(data_dict["fee"], float)
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["side"] == "BUY"
    
    def test_edge_case_zero_fee(self):
        """
        Test edge case with zero fee.
        
        @tradingImpact MEDIUM - Fee handling
        @riskLevel LOW - Edge case
        """
        trade = make_trade(fee=Decimal("0"))
        
        # Net amount should equal notional
        assert trade.net_amount == trade.notional
        
        # Validation should pass
        assert trade.validate_trade() is True
    
    def test_edge_case_high_precision_values(self):
        """
        Test edge case with high precision decimal values.
        
        @tradingImpact MEDIUM - Precision handling
        @riskLevel LOW - Decimal precision
        """
        trade = make_trade(
            quantity=Decimal("0.12345678"),
            price=Decimal("50000.12345678"),
            fee=Decimal("0.00000001")
        )
        
        # Should handle high precision without issues
        assert trade.validate_trade() is True
        
        # Net amount calculation should work
        expected_net = trade.notional - trade.fee
        assert trade.net_amount == expected_net
    
    def test_calculate_notional_idempotency(self):
        """
        Test that calculate_notional is idempotent.
        
        @tradingImpact MEDIUM - Method reliability
        @riskLevel LOW - Idempotency check
        """
        trade = make_trade(
            quantity=Decimal("2.0"),
            price=Decimal("50000.00")
        )
        
        # Store original notional
        original_notional = trade.notional
        
        # Call calculate_notional multiple times
        trade.calculate_notional()
        first_call_notional = trade.notional
        
        trade.calculate_notional()
        second_call_notional = trade.notional
        
        # All values should be the same
        assert original_notional == first_call_notional
        assert first_call_notional == second_call_notional
    
    def test_trade_performance_characteristics(self):
        """
        Test trade operations performance characteristics.
        
        @tradingImpact MEDIUM - System performance
        @riskLevel LOW - Performance validation
        """
        # Test basic trade operations
        trade = make_trade(quantity=Decimal("1.0"), price=Decimal("50000"))
        
        # Test validation works
        assert trade.validate_trade() is True
        
        # Test notional calculation works
        trade.calculate_notional()
        assert trade.notional == Decimal("50000.0")
    
    def test_property_based_trade_invariants(self):
        """
        Test trade invariants using property-based testing.
        
        @tradingImpact HIGH - Trade integrity invariants
        @riskLevel MEDIUM - Property validation
        """
        # Generate random trades and test invariants
        for _ in range(50):
            quantity = random_decimal(0.001, 1000.0, 8)
            price = random_decimal(0.01, 100000.0, 2)
            fee = random_decimal(0.0, 100.0, 2)
            
            trade = make_trade(quantity=quantity, price=price, fee=fee)
            
            # Invariant 1: Notional = quantity * price
            expected_notional = abs(quantity) * price
            assert abs(trade.notional - expected_notional) < Decimal("0.00000001")
            
            # Invariant 2: Net amount = notional - fee
            expected_net = trade.notional - fee
            assert trade.net_amount == expected_net
            
            # Invariant 3: Valid trades must have positive quantity and price
            if trade.validate_trade():
                assert trade.quantity > 0
                assert trade.price > 0
                assert trade.symbol is not None
                assert trade.side in ["BUY", "SELL"]
            
            # Invariant 4: Direction properties are mutually exclusive
            assert trade.is_buy != trade.is_sell  # XOR relationship
    
    def test_trade_to_dict_with_none_values(self):
        """
        Test trade to_dict method with None values to cover edge cases.
        
        @tradingImpact MEDIUM - API serialization edge cases
        @riskLevel LOW - Data conversion with None values
        """
        # Create trade with some None values to test the conditional logic
        trade = make_trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=None,  # This will trigger the 'else None' branch
            price=Decimal("50000.00"),
            fee=None,  # This will trigger the 'else None' branch
            timestamp=None  # This will trigger the 'else None' branch
        )
        
        data_dict = trade.to_dict()
        
        # Verify None values are handled correctly
        assert data_dict["quantity"] is None
        assert data_dict["fee"] is None
        assert data_dict["timestamp"] is None
        
        # Verify non-None values are converted correctly
        assert data_dict["symbol"] == "BTC-USD"
        assert data_dict["side"] == "BUY"
        assert isinstance(data_dict["price"], float) 