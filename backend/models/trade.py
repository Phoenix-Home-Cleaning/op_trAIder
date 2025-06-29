"""
@fileoverview Trade model for TRAIDER V1 transaction tracking
@module backend.models.trade

@description
SQLAlchemy model for trade execution tracking and audit trail.
Records all trading transactions with comprehensive metadata
for regulatory compliance and performance analysis.

@performance
- Indexed symbol and timestamp for fast queries
- Efficient trade aggregation queries
- Optimized P&L calculation lookups

@risk
- Failure impact: CRITICAL - No trade audit trail
- Recovery strategy: Exchange trade data reconciliation

@compliance
- Audit requirements: All trades permanently logged
- Data retention: Trade records retained indefinitely

@see {@link docs/architecture/trade-tracking.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, String, DateTime, Numeric, Integer, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import JSONB

from ..database import Base


class Trade(Base):
    """
    Trade model for transaction tracking and audit trail.
    
    @description
    Records all trade executions with comprehensive metadata including
    order details, execution prices, fees, and P&L calculations.
    
    @attributes
    - id: Primary key (auto-increment)
    - timestamp: Trade execution timestamp
    - symbol: Trading symbol
    - side: Trade side (BUY/SELL)
    - quantity: Trade quantity
    - price: Execution price
    - notional: Trade notional value (quantity * price)
    - fee: Trading fee paid
    - fee_currency: Currency of trading fee
    - order_id: Associated order identifier
    - signal_id: Associated signal identifier
    - strategy: Trading strategy name
    - exchange: Execution exchange
    - execution_type: Execution type (market, limit, etc.)
    - pnl: Realized P&L from this trade
    - status: Trade status
    - metadata: Additional trade information
    
    @tradingImpact CRITICAL - Complete trade audit trail
    @riskLevel HIGH - Financial transaction records
    """
    
    __tablename__ = "trades"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Trade identification
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, default=lambda: datetime.now(timezone.utc))
    symbol = Column(String(20), nullable=False, index=True)
    
    # Trade details
    side = Column(String(4), nullable=False)  # 'BUY' or 'SELL'
    quantity = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    notional = Column(Numeric(20, 8), nullable=False)
    
    # Fee information
    fee = Column(Numeric(20, 8), nullable=False, default=0)
    fee_currency = Column(String(10), nullable=False, default="USD")
    
    # Order and signal tracking
    order_id = Column(String(100), nullable=True, index=True)
    signal_id = Column(Integer, nullable=True, index=True)
    strategy = Column(String(50), nullable=True, index=True)
    
    # Execution details
    exchange = Column(String(20), nullable=False, default="coinbase")
    execution_type = Column(String(20), nullable=False, default="market")
    
    # P&L tracking
    pnl = Column(Numeric(20, 8), nullable=False, default=0)
    
    # Status and metadata
    status = Column(String(20), nullable=False, default="FILLED")
    notes = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=False, default=dict)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_trades_timestamp_symbol', 'timestamp', 'symbol'),
        Index('ix_trades_symbol_timestamp', 'symbol', 'timestamp'),
        Index('ix_trades_strategy_timestamp', 'strategy', 'timestamp'),
        Index('ix_trades_pnl', 'pnl'),
    )
    
    def __repr__(self) -> str:
        """String representation of trade."""
        return f"<Trade(id={self.id}, {self.side} {self.quantity} {self.symbol} @ {self.price})>"
    
    def to_dict(self) -> dict:
        """
        Convert trade to dictionary representation.
        
        @returns Dictionary representation of trade
        
        @performance <1ms serialization
        @sideEffects None
        
        @tradingImpact MEDIUM - Data serialization for API
        @riskLevel LOW - Read-only data conversion
        """
        
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": float(self.quantity) if self.quantity else None,
            "price": float(self.price) if self.price else None,
            "notional": float(self.notional) if self.notional else None,
            "fee": float(self.fee) if self.fee else None,
            "fee_currency": self.fee_currency,
            "order_id": self.order_id,
            "signal_id": self.signal_id,
            "strategy": self.strategy,
            "exchange": self.exchange,
            "execution_type": self.execution_type,
            "pnl": float(self.pnl) if self.pnl else None,
            "status": self.status,
            "notes": self.notes,
            "metadata": self.metadata,
        }
    
    @property
    def is_buy(self) -> bool:
        """
        Check if trade is a buy.
        
        @returns True if trade is a buy
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact LOW - Trade direction check
        @riskLevel LOW - Simple property
        """
        
        return self.side.upper() == "BUY"
    
    @property
    def is_sell(self) -> bool:
        """
        Check if trade is a sell.
        
        @returns True if trade is a sell
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact LOW - Trade direction check
        @riskLevel LOW - Simple property
        """
        
        return self.side.upper() == "SELL"
    
    @property
    def net_amount(self) -> Decimal:
        """
        Calculate net amount after fees.
        
        @returns Net amount (notional - fees)
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact MEDIUM - Net amount calculation
        @riskLevel LOW - Simple calculation
        """
        
        return self.notional - self.fee if self.notional and self.fee else self.notional
    
    def calculate_notional(self) -> None:
        """
        Calculate and update notional value.
        
        @performance <0.1ms calculation
        @sideEffects Updates notional field
        
        @tradingImpact MEDIUM - Trade value calculation
        @riskLevel LOW - Simple calculation
        """
        
        if self.quantity and self.price:
            self.notional = abs(self.quantity) * self.price
    
    def validate_trade(self) -> bool:
        """
        Validate trade data consistency.
        
        @returns True if trade data is valid
        
        @performance <1ms validation
        @sideEffects None
        
        @tradingImpact HIGH - Data integrity check
        @riskLevel MEDIUM - Validation logic
        """
        
        # Basic validation checks
        if not self.symbol or not self.side:
            return False
        
        if not self.quantity or self.quantity <= 0:
            return False
        
        if not self.price or self.price <= 0:
            return False
        
        if self.side.upper() not in ["BUY", "SELL"]:
            return False
        
        # Notional value consistency
        expected_notional = abs(self.quantity) * self.price
        if abs(self.notional - expected_notional) > Decimal("0.00000001"):
            return False
        
        return True 