"""
Comprehensive tests for Trade model to improve coverage above threshold.
"""

from decimal import Decimal
from datetime import datetime, timezone

from models.trade import Trade


class TestTradeModel:
    def _sample_trade(self) -> Trade:
        return Trade(
            id=1,
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("0.5"),
            price=Decimal("60000.00"),
            notional=Decimal("30000.00"),
            fee=Decimal("10.00"),
            fee_currency="USD",
            strategy="scalping",
        )

    def test_to_dict_serialization(self):
        trade = self._sample_trade()
        data = trade.to_dict()
        assert data["symbol"] == "BTC-USD"
        assert data["side"] == "BUY"
        assert data["quantity"] == 0.5
        assert data["price"] == 60000.0
        assert data["notional"] == 30000.0
        assert data["fee"] == 10.0

    def test_direction_properties(self):
        trade = self._sample_trade()
        assert trade.is_buy is True
        assert trade.is_sell is False
        # Flip direction
        trade.side = "SELL"
        assert trade.is_sell is True
        assert trade.is_buy is False

    def test_net_amount_calculation(self):
        trade = self._sample_trade()
        assert trade.net_amount == Decimal("29990.00")  # 30000 - 10

    def test_calculate_notional(self):
        trade = Trade(
            symbol="ETH-USD",
            side="BUY",
            quantity=Decimal("2.0"),
            price=Decimal("2500.00"),
            notional=Decimal("0.00"),
            fee=Decimal("0.00"),
            timestamp=datetime.now(timezone.utc),
        )
        trade.calculate_notional()
        assert trade.notional == Decimal("5000.00")

    def test_validation_success(self):
        trade = self._sample_trade()
        assert trade.validate_trade() is True

    def test_validation_failure(self):
        trade = self._sample_trade()
        trade.price = Decimal("0")
        assert trade.validate_trade() is False 