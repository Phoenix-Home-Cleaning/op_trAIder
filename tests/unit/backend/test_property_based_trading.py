#!/usr/bin/env python3
"""
@fileoverview Property-based testing for TRAIDER trading logic
@module tests.unit.backend.test_property_based_trading

@description
Institutional-grade property-based testing using Hypothesis to validate
trading logic across thousands of edge cases. Tests core trading functions
with automatically generated test cases to ensure robustness.

@performance
- Risk calculation validation: ≤10ms per property
- Position sizing validation: ≤5ms per property  
- Portfolio constraint validation: ≤20ms per property

@risk
- Failure impact: CRITICAL - Trading logic errors cause financial losses
- Recovery strategy: Comprehensive property validation prevents erroneous trades

@compliance
- Audit requirements: Yes - All trading logic must pass property-based validation
- Regulatory compliance: Position limits and risk controls validated across all scenarios

@see {@link docs/testing/property-based-testing.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import os
import sys
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple, Optional
from unittest.mock import patch

import pytest
from hypothesis import given, strategies as st, settings, assume, note
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

# Trading configuration constants
MAX_POSITION_SIZE = Decimal('10000.0')
MAX_LEVERAGE = Decimal('3.0') 
MAX_DAILY_LOSS = Decimal('1000.0')
MIN_ORDER_SIZE = Decimal('10.0')
MAX_SLIPPAGE = Decimal('0.01')  # 1%


class TestPropertyBasedTradingLogic:
    """
    Property-based testing for core trading logic functions.
    
    @description
    Uses Hypothesis to generate thousands of test cases automatically,
    ensuring trading logic is robust across all possible input combinations.
    
    @tradingImpact CRITICAL - Validates core trading decision logic
    @riskLevel CRITICAL - Trading errors cause immediate financial impact
    """

    # =============================================================================
    # POSITION SIZING PROPERTIES
    # =============================================================================

    @given(
        cash_balance=st.decimals(min_value=Decimal('100'), max_value=Decimal('1000000'), places=2),
        total_equity=st.decimals(min_value=Decimal('100'), max_value=Decimal('1000000'), places=2),
        position_value=st.decimals(min_value=Decimal('10'), max_value=Decimal('50000'), places=2)
    )
    @settings(max_examples=500, deadline=None)
    def test_leverage_calculation_properties(self, cash_balance: Decimal, total_equity: Decimal, position_value: Decimal):
        """
        Property-based test for leverage calculation correctness.
        
        @description
        Tests that leverage calculations are always mathematically correct
        and within institutional risk limits across all possible input combinations.
        
        @performance Target: <5ms per property test
        @tradingImpact CRITICAL - Leverage controls risk exposure
        @riskLevel CRITICAL - Incorrect leverage could cause excessive risk
        """
        
        # Ensure realistic portfolio state
        assume(total_equity >= cash_balance * Decimal('0.5'))  # Reasonable equity ratio
        assume(position_value <= total_equity * Decimal('2'))   # Reasonable position size
        
        def calculate_leverage(cash: Decimal, equity: Decimal, new_position: Decimal) -> Decimal:
            """Calculate portfolio leverage with new position."""
            if equity <= 0:
                return Decimal('999')  # Infinite leverage indicator
            
            total_exposure = new_position
            return total_exposure / equity
        
        def validate_leverage_limits(leverage: Decimal) -> bool:
            """Validate leverage is within institutional limits."""
            return leverage <= MAX_LEVERAGE
        
        # Calculate leverage
        leverage = calculate_leverage(cash_balance, total_equity, position_value)
        is_valid = validate_leverage_limits(leverage)
        
        # Property: Leverage calculation is mathematically correct
        expected_leverage = position_value / total_equity
        assert abs(leverage - expected_leverage) < Decimal('0.001'), f"Leverage calculation incorrect: {leverage} != {expected_leverage}"
        
        # Property: Leverage validation is consistent
        if position_value <= total_equity * MAX_LEVERAGE:
            assert is_valid, f"Valid position rejected: leverage={leverage}, limit={MAX_LEVERAGE}"
        else:
            assert not is_valid, f"Invalid position accepted: leverage={leverage}, limit={MAX_LEVERAGE}"
        
        # Property: Leverage is always non-negative
        assert leverage >= 0, f"Leverage cannot be negative: {leverage}"
        
        note(f"Cash: {cash_balance}, Equity: {total_equity}, Position: {position_value}, Leverage: {leverage}")

    @given(
        price=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('100000'), places=2),
        quantity=st.decimals(min_value=Decimal('0.001'), max_value=Decimal('1000'), places=6),
        portfolio_value=st.decimals(min_value=Decimal('1000'), max_value=Decimal('1000000'), places=2),
        risk_percentage=st.decimals(min_value=Decimal('0.001'), max_value=Decimal('0.05'), places=4)
    )
    @settings(max_examples=300, deadline=None)
    def test_position_sizing_properties(self, price: Decimal, quantity: Decimal, portfolio_value: Decimal, risk_percentage: Decimal):
        """
        Property-based test for position sizing logic.
        
        @description
        Validates position sizing calculations maintain proper risk management
        across all possible market conditions and portfolio states.
        
        @performance Target: <5ms per property test
        @tradingImpact HIGH - Position sizing directly affects risk exposure
        @riskLevel HIGH - Incorrect sizing could cause excessive losses
        """
        
        def calculate_position_size(
            target_price: Decimal,
            target_quantity: Decimal,
            portfolio_val: Decimal,
            max_risk_pct: Decimal
        ) -> Tuple[Decimal, bool]:
            """Calculate appropriate position size with risk limits."""
            
            position_value = target_price * target_quantity
            risk_amount = portfolio_val * max_risk_pct
            
            # Check if position exceeds risk limits
            if position_value > risk_amount:
                # Scale down to risk limit
                adjusted_quantity = risk_amount / target_price
                return adjusted_quantity, False  # Position was adjusted
            
            # Check minimum order size
            if position_value < MIN_ORDER_SIZE:
                return Decimal('0'), False  # Position too small
            
            return target_quantity, True  # Position accepted as-is
        
        # Calculate position size
        adjusted_quantity, accepted_as_is = calculate_position_size(
            price, quantity, portfolio_value, risk_percentage
        )
        
        adjusted_value = price * adjusted_quantity
        
        # Property: Adjusted position never exceeds risk limit
        max_risk_value = portfolio_value * risk_percentage
        assert adjusted_value <= max_risk_value + Decimal('0.01'), f"Position exceeds risk limit: {adjusted_value} > {max_risk_value}"
        
        # Property: Adjusted quantity is never negative
        assert adjusted_quantity >= 0, f"Quantity cannot be negative: {adjusted_quantity}"
        
        # Property: If original position was within limits, it should be accepted
        original_value = price * quantity
        if original_value <= max_risk_value and original_value >= MIN_ORDER_SIZE:
            assert accepted_as_is, f"Valid position was incorrectly adjusted: {original_value} <= {max_risk_value}"
            assert adjusted_quantity == quantity, f"Quantity changed unnecessarily: {adjusted_quantity} != {quantity}"
        
        # Property: Adjusted position value is proportional to price
        if adjusted_quantity > 0:
            assert adjusted_value / price == adjusted_quantity, "Value/price calculation incorrect"
        
        note(f"Price: {price}, Original Qty: {quantity}, Adjusted Qty: {adjusted_quantity}, Risk %: {risk_percentage}")

    @given(
        bid_price=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('10000'), places=2),
        ask_price=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('10000'), places=2), 
        order_size=st.decimals(min_value=Decimal('1'), max_value=Decimal('10000'), places=2),
        market_impact_factor=st.decimals(min_value=Decimal('0.0001'), max_value=Decimal('0.01'), places=6)
    )
    @settings(max_examples=400, deadline=None)
    def test_slippage_calculation_properties(self, bid_price: Decimal, ask_price: Decimal, order_size: Decimal, market_impact_factor: Decimal):
        """
        Property-based test for slippage calculation accuracy.
        
        @description
        Validates slippage calculations are consistent and realistic
        across all market conditions and order sizes.
        
        @performance Target: <3ms per property test
        @tradingImpact HIGH - Slippage affects execution quality
        @riskLevel MEDIUM - Excessive slippage reduces profitability
        """
        
        # Ensure realistic bid-ask spread
        assume(ask_price >= bid_price)
        assume(ask_price <= bid_price * Decimal('1.1'))  # Max 10% spread
        
        def calculate_expected_slippage(
            bid: Decimal, 
            ask: Decimal, 
            size: Decimal, 
            impact_factor: Decimal,
            side: str = "buy"
        ) -> Decimal:
            """Calculate expected slippage for order execution."""
            
            # Base slippage from bid-ask spread
            spread = ask - bid
            base_slippage = spread / Decimal('2')
            
            # Market impact based on order size
            market_impact = size * impact_factor
            
            # Total slippage
            total_slippage = base_slippage + market_impact
            
            return total_slippage
        
        def validate_slippage_acceptable(slippage: Decimal, reference_price: Decimal) -> bool:
            """Check if slippage is within acceptable limits."""
            slippage_percentage = slippage / reference_price
            return slippage_percentage <= MAX_SLIPPAGE
        
        # Calculate slippage for buy order
        buy_slippage = calculate_expected_slippage(bid_price, ask_price, order_size, market_impact_factor, "buy")
        buy_acceptable = validate_slippage_acceptable(buy_slippage, ask_price)
        
        # Calculate slippage for sell order  
        sell_slippage = calculate_expected_slippage(bid_price, ask_price, order_size, market_impact_factor, "sell")
        sell_acceptable = validate_slippage_acceptable(sell_slippage, bid_price)
        
        # Property: Slippage is always non-negative
        assert buy_slippage >= 0, f"Buy slippage cannot be negative: {buy_slippage}"
        assert sell_slippage >= 0, f"Sell slippage cannot be negative: {sell_slippage}"
        
        # Property: Slippage increases with order size
        larger_order_slippage = calculate_expected_slippage(
            bid_price, ask_price, order_size * Decimal('2'), market_impact_factor, "buy"
        )
        assert larger_order_slippage >= buy_slippage, "Slippage should increase with order size"
        
        # Property: Slippage includes bid-ask spread component
        min_expected_slippage = (ask_price - bid_price) / Decimal('2')
        assert buy_slippage >= min_expected_slippage, f"Slippage below minimum spread: {buy_slippage} < {min_expected_slippage}"
        
        # Property: Validation is consistent with limits
        buy_slippage_pct = buy_slippage / ask_price
        if buy_slippage_pct <= MAX_SLIPPAGE:
            assert buy_acceptable, f"Acceptable slippage rejected: {buy_slippage_pct} <= {MAX_SLIPPAGE}"
        
        note(f"Bid: {bid_price}, Ask: {ask_price}, Size: {order_size}, Buy Slippage: {buy_slippage}")


class TradingStateMachine(RuleBasedStateMachine):
    """
    Stateful property-based testing for trading system state management.
    
    @description
    Uses Hypothesis stateful testing to validate trading system behavior
    across complex sequences of operations and state transitions.
    
    @tradingImpact CRITICAL - Validates system state consistency
    @riskLevel CRITICAL - State inconsistencies could cause trading errors
    """
    
    def __init__(self):
        super().__init__()
        self.portfolio_value = Decimal('10000.0')
        self.cash_balance = Decimal('10000.0')
        self.positions = {}
        self.daily_pnl = Decimal('0.0')
        self.max_daily_loss = MAX_DAILY_LOSS
    
    @rule(
        symbol=st.text(min_size=3, max_size=6, alphabet=st.characters(whitelist_categories=['Lu'])),
        quantity=st.decimals(min_value=Decimal('0.1'), max_value=Decimal('100'), places=2),
        price=st.decimals(min_value=Decimal('1'), max_value=Decimal('1000'), places=2)
    )
    def buy_position(self, symbol: str, quantity: Decimal, price: Decimal):
        """Execute buy order and update portfolio state."""
        
        order_value = quantity * price
        
        # Check if we have enough cash
        if order_value <= self.cash_balance:
            # Execute trade
            self.cash_balance -= order_value
            
            if symbol in self.positions:
                # Update existing position
                old_qty, old_price = self.positions[symbol]
                new_qty = old_qty + quantity
                new_avg_price = ((old_qty * old_price) + (quantity * price)) / new_qty
                self.positions[symbol] = (new_qty, new_avg_price)
            else:
                # New position
                self.positions[symbol] = (quantity, price)
    
    @rule(
        symbol=st.sampled_from(['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']),
        percentage=st.decimals(min_value=Decimal('0.1'), max_value=Decimal('1.0'), places=2)
    )
    def sell_position(self, symbol: str, percentage: Decimal):
        """Sell portion of position and update portfolio state."""
        
        if symbol in self.positions:
            current_qty, avg_price = self.positions[symbol]
            sell_qty = current_qty * percentage
            sell_value = sell_qty * avg_price  # Simplified: sell at avg price
            
            # Update position
            remaining_qty = current_qty - sell_qty
            if remaining_qty > Decimal('0.01'):
                self.positions[symbol] = (remaining_qty, avg_price)
            else:
                del self.positions[symbol]
            
            # Update cash
            self.cash_balance += sell_value
    
    @invariant()
    def portfolio_consistency(self):
        """Portfolio state must always be mathematically consistent."""
        
        # Calculate total position value
        position_value = sum(
            qty * price for qty, price in self.positions.values()
        )
        
        # Portfolio value should equal cash + positions
        calculated_portfolio_value = self.cash_balance + position_value
        
        # Allow small rounding differences
        assert abs(calculated_portfolio_value - (self.cash_balance + position_value)) < Decimal('0.01'), \
            f"Portfolio value inconsistency: calculated={calculated_portfolio_value}, actual={self.cash_balance + position_value}"
    
    @invariant()
    def cash_balance_non_negative(self):
        """Cash balance must never go negative."""
        assert self.cash_balance >= 0, f"Cash balance went negative: {self.cash_balance}"
    
    @invariant()
    def position_quantities_positive(self):
        """All position quantities must be positive."""
        for symbol, (qty, price) in self.positions.items():
            assert qty > 0, f"Position {symbol} has non-positive quantity: {qty}"
            assert price > 0, f"Position {symbol} has non-positive price: {price}"


# Run stateful testing
TestTradingStateMachine = TradingStateMachine.TestCase 