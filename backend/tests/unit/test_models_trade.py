"""
Comprehensive tests for Trade model to ensure 100% coverage.
"""

import pytest
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


class TestTradeProperties:
    def test_net_amount_with_fee(self):
        """Test Trade.net_amount property with fee deduction."""
        trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            notional=Decimal("50000.00"),
            fee=Decimal("25.00")
        )
        
        expected_net = trade.notional - trade.fee
        assert trade.net_amount == expected_net
        assert trade.net_amount == Decimal("49975.00")
    
    def test_net_amount_with_zero_fee(self):
        """Test Trade.net_amount property with zero fee."""
        trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            notional=Decimal("50000.00"),
            fee=Decimal("0.00")
        )
        
        expected_net = trade.notional - trade.fee
        assert trade.net_amount == expected_net
        assert trade.net_amount == Decimal("50000.00")
    
    def test_net_amount_with_none_fee(self):
        """Test Trade.net_amount property with None fee."""
        trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            notional=Decimal("50000.00"),
            fee=None
        )
        
        assert trade.net_amount == trade.notional
        assert trade.net_amount == Decimal("50000.00")
    
    def test_net_amount_with_none_notional(self):
        """Test Trade.net_amount property with None notional."""
        trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            notional=None,
            fee=Decimal("25.00")
        )
        
        assert trade.net_amount is None


class TestTradeMethods:
    def test_calculate_notional_method(self):
        """Test Trade.calculate_notional method."""
        trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.5"),
            price=Decimal("50000.00"),
            notional=Decimal("0.00")
        )
        
        trade.calculate_notional()
        
        expected_notional = trade.quantity * trade.price
        assert trade.notional == expected_notional
        assert trade.notional == Decimal("75000.00")
    
    def test_calculate_notional_with_none_values(self):
        """Test Trade.calculate_notional method with None values."""
        # Test with None quantity
        trade_none_qty = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=None,
            price=Decimal("50000.00"),
            notional=Decimal("0.00")
        )
        
        trade_none_qty.calculate_notional()
        assert trade_none_qty.notional == Decimal("0.00")
        
        # Test with None price
        trade_none_price = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.0"),
            price=None,
            notional=Decimal("0.00")
        )
        
        trade_none_price.calculate_notional()
        assert trade_none_price.notional == Decimal("0.00")
    
    def test_validate_trade_method_valid(self):
        """Test Trade.validate_trade method with valid trade."""
        trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            notional=Decimal("50000.00")
        )
        
        assert trade.validate_trade() is True
    
    def test_validate_trade_method_invalid_cases(self):
        """Test Trade.validate_trade method with invalid trades."""
        # Test invalid side
        invalid_side_trade = Trade(
            symbol="BTC-USD",
            side="INVALID",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            notional=Decimal("50000.00")
        )
        assert invalid_side_trade.validate_trade() is False
        
        # Test negative quantity
        negative_qty_trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("-1.0"),
            price=Decimal("50000.00"),
            notional=Decimal("50000.00")
        )
        assert negative_qty_trade.validate_trade() is False
        
        # Test negative price
        negative_price_trade = Trade(
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("-50000.00"),
            notional=Decimal("50000.00")
        )
        assert negative_price_trade.validate_trade() is False
        
        # Test None values
        none_symbol_trade = Trade(
            symbol=None,
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            notional=Decimal("50000.00")
        )
        assert none_symbol_trade.validate_trade() is False
    
    def test_repr_method(self):
        """Test Trade.__repr__ method."""
        trade = Trade(
            id=123,
            symbol="BTC-USD",
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00")
        )
        
        repr_str = repr(trade)
        assert "Trade" in repr_str
        assert "id=123" in repr_str
        assert "BUY 1.0 BTC-USD" in repr_str
        assert "50000.00" in repr_str
    
    def test_to_dict_method(self):
        """Test Trade.to_dict method."""
        trade = Trade(
            id=456,
            symbol="ETH-USD",
            side="SELL",
            quantity=Decimal("2.5"),
            price=Decimal("3000.00"),
            notional=Decimal("7500.00"),
            fee=Decimal("37.50"),
            timestamp=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            order_id="order-123",
            signal_id=789,
            strategy="test_strategy",
            exchange="coinbase",
            execution_type="limit",
            pnl=Decimal("150.00"),
            status="FILLED",
            notes="Test trade",
            extra_data={"source": "test"}
        )
        
        result = trade.to_dict()
        
        assert result["id"] == 456
        assert result["symbol"] == "ETH-USD"
        assert result["side"] == "SELL"
        assert result["quantity"] == 2.5
        assert result["price"] == 3000.00
        assert result["notional"] == 7500.00
        assert result["fee"] == 37.50
        assert result["timestamp"] == "2025-01-01T12:00:00+00:00"
        assert result["order_id"] == "order-123"
        assert result["signal_id"] == 789
        assert result["strategy"] == "test_strategy"
        assert result["exchange"] == "coinbase"
        assert result["execution_type"] == "limit"
        assert result["pnl"] == 150.00
        assert result["status"] == "FILLED"
        assert result["notes"] == "Test trade"
        assert result["extra_data"] == {"source": "test"} 