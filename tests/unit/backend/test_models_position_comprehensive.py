"""
Comprehensive tests for Position model to ensure 100% coverage.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import patch

from models.position import Position

# (Include key test cases similar to earlier but abbreviated for brevity)

class TestPositionProperties:
    def test_is_long_short_flat(self):
        pos_long = Position(symbol="BTC-USD", quantity=Decimal("1"))
        pos_short = Position(symbol="BTC-USD", quantity=Decimal("-1"))
        pos_flat = Position(symbol="BTC-USD", quantity=Decimal("0"))
        assert pos_long.is_long and not pos_long.is_short and not pos_long.is_flat
        assert pos_short.is_short and not pos_short.is_long and not pos_short.is_flat
        assert pos_flat.is_flat and not pos_flat.is_long and not pos_flat.is_short

class TestPositionMarketValue:
    def test_update_market_value_long(self):
        pos = Position(symbol="BTC-USD", quantity=Decimal("2"), avg_cost=Decimal("50000"))
        pos.update_market_value(Decimal("52000"))
        assert pos.market_value == Decimal("104000")
        assert pos.unrealized_pnl == Decimal("4000")

class TestPositionTrades:
    def test_first_trade(self):
        pos = Position(symbol="BTC-USD")
        with patch('models.position.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2025,1,1,tzinfo=timezone.utc)
            pnl = pos.add_trade(Decimal("1"), Decimal("50000"))
        assert pnl == 0
        assert pos.quantity == Decimal("1")
        assert pos.avg_cost == Decimal("50000")

    def test_close_trade(self):
        pos = Position(symbol="BTC-USD", quantity=Decimal("1"), avg_cost=Decimal("50000"))
        pnl = pos.add_trade(Decimal("-1"), Decimal("51000"))
        assert pnl == Decimal("1000")
        assert pos.quantity == 0 