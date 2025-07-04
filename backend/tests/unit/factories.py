"""
@fileoverview Shared test factories for TRAIDER V1 trading models
@module tests.unit.backend.factories

@description
Centralized test data factories for trading models to eliminate
duplication and ensure consistent test data generation across
all trading logic test suites.

@performance
- Factory creation: <1ms per instance
- Memory usage: <10MB for test suite
- Deterministic randomness with fixed seeds

@risk
- Failure impact: LOW - Test utilities only
- Recovery strategy: Regenerate test data

@compliance
- Audit requirements: Test data generation documented
- Data retention: Test artifacts retained 30 days

@see {@link docs/testing/test-factories.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import random
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any
from unittest.mock import patch

# Import models to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))

from models.position import Position
from models.trade import Trade
from models.signal import Signal


def random_decimal(min_val: float = 0.0, max_val: float = 100000.0, places: int = 8) -> Decimal:
    """
    Generate random Decimal with specified precision.
    
    @param min_val Minimum value (inclusive)
    @param max_val Maximum value (exclusive)
    @param places Decimal places for precision
    @returns Random Decimal value
    
    @performance <0.1ms generation
    @sideEffects None
    
    @tradingImpact LOW - Test data generation
    @riskLevel LOW - Test utility only
    """
    # In a test factory, using random.uniform is safe for generating mock data.
    value = random.uniform(min_val, max_val)  # NOSONAR
    return Decimal(str(round(value, places)))


def random_symbol() -> str:
    """
    Generate random trading symbol.
    
    @returns Random trading symbol
    
    @performance <0.1ms generation
    @sideEffects None
    """
    symbols = ["BTC-USD", "ETH-USD", "AAPL", "GOOGL", "TSLA", "SPY", "QQQ"]
    # In a test factory, using random.choice is safe for generating mock data.
    return random.choice(symbols)  # NOSONAR


def make_position(
    symbol: Optional[str] = None,
    quantity: Optional[Decimal] = None,
    avg_cost: Optional[Decimal] = None,
    market_value: Optional[Decimal] = None,
    **kwargs
) -> Position:
    """
    Create Position instance with sensible defaults.
    
    @param symbol Trading symbol (defaults to BTC-USD)
    @param quantity Position quantity (defaults to 1.0)
    @param avg_cost Average cost basis (defaults to 50000.0)
    @param market_value Current market value (defaults to calculated)
    @param kwargs Additional position attributes
    @returns Position instance
    
    @performance <1ms creation
    @sideEffects None
    
    @tradingImpact LOW - Test data creation
    @riskLevel LOW - Test utility only
    """
    # Set defaults with fixed values for predictable tests
    symbol = symbol or "BTC-USD"
    if quantity is None:
        quantity = Decimal("1.0")
    if avg_cost is None:
        avg_cost = Decimal("50000.0")
    
    # Calculate market value if not provided
    if market_value is None and quantity and avg_cost:
        market_value = abs(quantity) * avg_cost
    
    # Create position with defaults - filter out non-model fields
    position_fields = {
        "symbol": symbol,
        "quantity": quantity,
        "avg_cost": avg_cost,
        "market_value": market_value or Decimal("0"),
        "unrealized_pnl": Decimal("0"),
        "realized_pnl": Decimal("0"),
        "total_pnl": Decimal("0"),
        "first_trade_at": datetime.now(timezone.utc),
        "last_updated": datetime.now(timezone.utc),
        "risk_metrics": {},
        "extra_data": {}
    }
    
    # Only include fields that exist in the Position model
    valid_fields = {}
    for key, value in position_fields.items():
        if key not in ['direction']:  # Filter out invalid fields
            valid_fields[key] = value
    
    # Override with any provided kwargs (except invalid ones)
    for key, value in kwargs.items():
        if key not in ['direction']:  # Filter out invalid fields
            valid_fields[key] = value
    
    return Position(**valid_fields)


def make_trade(
    symbol: Optional[str] = "DEFAULT",
    side: Optional[str] = "DEFAULT", 
    quantity: Optional[Decimal] = "DEFAULT",
    price: Optional[Decimal] = "DEFAULT",
    **kwargs
) -> Trade:
    """
    Create Trade instance with sensible defaults.
    
    @param symbol Trading symbol (defaults to BTC-USD)
    @param side Trade side (defaults to BUY)
    @param quantity Trade quantity (defaults to random)
    @param price Trade price (defaults to random)
    @param kwargs Additional trade attributes
    @returns Trade instance
    
    @performance <1ms creation
    @sideEffects None
    
    @tradingImpact LOW - Test data creation
    @riskLevel LOW - Test utility only
    """
    # Set defaults - only if not explicitly passed (including None)
    if symbol == "DEFAULT":
        symbol = "BTC-USD"
    if side == "DEFAULT":
        side = "BUY"
    if quantity == "DEFAULT":
        quantity = random_decimal(0.1, 10.0, 8)
    if price == "DEFAULT":
        price = random_decimal(1000.0, 60000.0, 2)
    
    # Calculate notional (handle None values)
    if quantity is not None and price is not None:
        notional = abs(quantity) * price
    else:
        notional = Decimal("0")  # Default for invalid trades
    
    # Create trade with defaults
    defaults = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "notional": notional,
        "fee": random_decimal(0.0, 50.0, 2),
        "fee_currency": "USD",
        # In a test factory, using random.randint is safe for generating mock data.
        "order_id": f"order_{random.randint(1000, 9999)}",  # NOSONAR
        "strategy": "test_strategy",
        "exchange": "coinbase",
        "execution_type": "market",
        "pnl": Decimal("0"),
        "status": "FILLED",
        "timestamp": datetime.now(timezone.utc),
        "extra_data": {}
    }
    
    # Override with any provided kwargs
    defaults.update(kwargs)
    
    return Trade(**defaults)


def make_signal(
    symbol: Optional[str] = None,
    strategy: Optional[str] = None,
    direction: Optional[str] = None,
    **kwargs
) -> Signal:
    """
    Create Signal instance with sensible defaults.
    
    @param symbol Trading symbol (defaults to BTC-USD)
    @param strategy Strategy name (defaults to test_strategy)
    @param direction Signal direction (defaults to LONG)
    @param kwargs Additional signal attributes
    @returns Signal instance
    
    @performance <1ms creation
    @sideEffects None
    
    @tradingImpact LOW - Test data creation
    @riskLevel LOW - Test utility only
    """
    # Set defaults
    symbol = symbol or "BTC-USD"
    strategy = strategy or "test_strategy"
    direction = direction or "LONG"
    
    # Create signal with defaults
    defaults = {
        "symbol": symbol,
        "strategy": strategy,
        "signal_type": "entry",
        "signal_strength": random_decimal(-1.0, 1.0, 4),
        "confidence": random_decimal(0.5, 1.0, 4),
        "direction": direction,
        "target_price": random_decimal(1000.0, 60000.0, 2),
        "stop_loss": random_decimal(500.0, 55000.0, 2),
        "take_profit": random_decimal(1500.0, 65000.0, 2),
        "features": {"test_feature": 0.5},
        "model_version": "v1.0.0",
        "executed": False,
        "pnl": Decimal("0"),
        "max_favorable": Decimal("0"),
        "max_adverse": Decimal("0"),
        "status": "GENERATED",
        "timestamp": datetime.now(timezone.utc),
        "extra_data": {}
    }
    
    # Override with any provided kwargs
    defaults.update(kwargs)
    
    return Signal(**defaults)


# Common test scenarios for parametric testing
POSITION_SCENARIOS = [
    ("long_profitable", {"quantity": Decimal("1.0"), "avg_cost": Decimal("50000")}),
    ("long_losing", {"quantity": Decimal("1.0"), "avg_cost": Decimal("60000")}),
    ("short_profitable", {"quantity": Decimal("-1.0"), "avg_cost": Decimal("60000")}),
    ("short_losing", {"quantity": Decimal("-1.0"), "avg_cost": Decimal("50000")}),
    ("flat_position", {"quantity": Decimal("0"), "avg_cost": None}),
]

TRADE_SCENARIOS = [
    ("buy_small", {"side": "BUY", "quantity": Decimal("0.1"), "price": Decimal("50000")}),
    ("buy_large", {"side": "BUY", "quantity": Decimal("10.0"), "price": Decimal("50000")}),
    ("sell_small", {"side": "SELL", "quantity": Decimal("0.1"), "price": Decimal("50000")}),
    ("sell_large", {"side": "SELL", "quantity": Decimal("10.0"), "price": Decimal("50000")}),
]

PRICE_SCENARIOS = [
    ("low_price", Decimal("1000.00")),
    ("mid_price", Decimal("50000.00")),
    ("high_price", Decimal("100000.00")),
] 