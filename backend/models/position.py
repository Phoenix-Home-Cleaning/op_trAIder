"""
@fileoverview Position model for TRAIDER V1 portfolio management
@module backend.models.position

@description
SQLAlchemy model for trading position tracking and P&L calculations.
Supports real-time position updates, risk metrics, and performance
analytics for institutional-grade portfolio management.

@performance
- Indexed symbol lookups for real-time updates
- Efficient P&L calculation queries
- Optimized position aggregation

@risk
- Failure impact: CRITICAL - Portfolio tracking unavailable
- Recovery strategy: Position reconstruction from trades

@compliance
- Audit requirements: All position changes logged
- Data retention: Position history retained indefinitely

@see {@link docs/architecture/position-management.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, String, DateTime, Numeric, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import JSONB

from backend.database import Base


class Position(Base):
    """
    Position model for portfolio tracking and risk management.
    
    @description
    Tracks current positions, P&L, and risk metrics for each trading symbol.
    Supports both long and short positions with real-time updates.
    
    @attributes
    - symbol: Trading symbol (primary key)
    - quantity: Current position size (positive = long, negative = short)
    - avg_cost: Average cost basis per unit
    - market_value: Current market value
    - unrealized_pnl: Unrealized profit/loss
    - realized_pnl: Realized profit/loss (closed portions)
    - total_pnl: Total P&L for this position
    - first_trade_at: Timestamp of first trade for this position
    - last_updated: Last position update timestamp
    - risk_metrics: JSON object with risk calculations
    - metadata: Additional position information
    
    @tradingImpact CRITICAL - Portfolio and risk management
    @riskLevel HIGH - Financial position tracking
    """
    
    __tablename__ = "positions"
    
    # Primary key
    symbol = Column(String(20), primary_key=True, nullable=False, index=True)
    
    # Position data
    quantity = Column(Numeric(20, 8), nullable=False, default=0)
    avg_cost = Column(Numeric(20, 8), nullable=True)
    market_value = Column(Numeric(20, 8), nullable=False, default=0)
    
    # P&L tracking
    unrealized_pnl = Column(Numeric(20, 8), nullable=False, default=0)
    realized_pnl = Column(Numeric(20, 8), nullable=False, default=0)
    total_pnl = Column(Numeric(20, 8), nullable=False, default=0)
    
    # Timestamps
    first_trade_at = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Risk and analytics
    risk_metrics = Column(JSONB, nullable=False, default=dict)
    metadata = Column(JSONB, nullable=False, default=dict)
    
    def __repr__(self) -> str:
        """String representation of position."""
        return f"<Position(symbol='{self.symbol}', quantity={self.quantity}, pnl={self.total_pnl})>"
    
    def to_dict(self) -> dict:
        """
        Convert position to dictionary representation.
        
        @returns Dictionary representation of position
        
        @performance <1ms serialization
        @sideEffects None
        
        @tradingImpact MEDIUM - Data serialization for API
        @riskLevel LOW - Read-only data conversion
        """
        
        return {
            "symbol": self.symbol,
            "quantity": float(self.quantity) if self.quantity else 0,
            "avg_cost": float(self.avg_cost) if self.avg_cost else None,
            "market_value": float(self.market_value) if self.market_value else 0,
            "unrealized_pnl": float(self.unrealized_pnl) if self.unrealized_pnl else 0,
            "realized_pnl": float(self.realized_pnl) if self.realized_pnl else 0,
            "total_pnl": float(self.total_pnl) if self.total_pnl else 0,
            "first_trade_at": self.first_trade_at.isoformat() if self.first_trade_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "risk_metrics": self.risk_metrics,
            "metadata": self.metadata,
        }
    
    @property
    def is_long(self) -> bool:
        """
        Check if position is long.
        
        @returns True if position is long (quantity > 0)
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact MEDIUM - Position direction check
        @riskLevel LOW - Simple calculation
        """
        
        return self.quantity and self.quantity > 0
    
    @property
    def is_short(self) -> bool:
        """
        Check if position is short.
        
        @returns True if position is short (quantity < 0)
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact MEDIUM - Position direction check
        @riskLevel LOW - Simple calculation
        """
        
        return self.quantity and self.quantity < 0
    
    @property
    def is_flat(self) -> bool:
        """
        Check if position is flat (no position).
        
        @returns True if position is flat (quantity = 0)
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact MEDIUM - Position status check
        @riskLevel LOW - Simple calculation
        """
        
        return not self.quantity or self.quantity == 0
    
    def update_market_value(self, current_price: Decimal) -> None:
        """
        Update market value and unrealized P&L based on current price.
        
        @param current_price Current market price
        
        @performance <1ms calculation
        @sideEffects Updates market_value and unrealized_pnl
        
        @tradingImpact HIGH - Real-time P&L calculation
        @riskLevel MEDIUM - Financial calculations
        """
        
        if self.quantity and current_price:
            # Calculate market value
            self.market_value = abs(self.quantity) * current_price
            
            # Calculate unrealized P&L
            if self.avg_cost:
                cost_basis = abs(self.quantity) * self.avg_cost
                if self.quantity > 0:  # Long position
                    self.unrealized_pnl = self.market_value - cost_basis
                else:  # Short position
                    self.unrealized_pnl = cost_basis - self.market_value
            
            # Update total P&L
            self.total_pnl = self.realized_pnl + self.unrealized_pnl
            
            # Update timestamp
            self.last_updated = datetime.now(timezone.utc)
    
    def add_trade(self, quantity: Decimal, price: Decimal) -> Decimal:
        """
        Add a trade to this position and update metrics.
        
        @param quantity Trade quantity (positive = buy, negative = sell)
        @param price Trade price
        @returns Realized P&L from this trade
        
        @performance <2ms calculation
        @sideEffects Updates position metrics
        
        @tradingImpact CRITICAL - Position and P&L updates
        @riskLevel HIGH - Financial calculations
        """
        
        realized_pnl = Decimal(0)
        
        # Handle first trade
        if not self.quantity or self.quantity == 0:
            self.quantity = quantity
            self.avg_cost = price
            self.first_trade_at = datetime.now(timezone.utc)
        else:
            # Check if trade closes or reduces position
            if (self.quantity > 0 and quantity < 0) or (self.quantity < 0 and quantity > 0):
                # Closing or reducing position - calculate realized P&L
                close_quantity = min(abs(quantity), abs(self.quantity))
                
                if self.avg_cost:
                    if self.quantity > 0:  # Closing long position
                        realized_pnl = close_quantity * (price - self.avg_cost)
                    else:  # Closing short position
                        realized_pnl = close_quantity * (self.avg_cost - price)
                
                # Update realized P&L
                self.realized_pnl += realized_pnl
                
                # Update position quantity
                if abs(quantity) >= abs(self.quantity):
                    # Position fully closed or reversed
                    remaining_quantity = abs(quantity) - abs(self.quantity)
                    if remaining_quantity > 0:
                        # Position reversed
                        self.quantity = remaining_quantity if quantity > 0 else -remaining_quantity
                        self.avg_cost = price
                    else:
                        # Position fully closed
                        self.quantity = Decimal(0)
                        self.avg_cost = None
                else:
                    # Position partially closed
                    self.quantity += quantity
            else:
                # Adding to position - update average cost
                total_cost = (abs(self.quantity) * self.avg_cost) + (abs(quantity) * price)
                self.quantity += quantity
                self.avg_cost = total_cost / abs(self.quantity)
        
        # Update total P&L
        self.total_pnl = self.realized_pnl + self.unrealized_pnl
        
        # Update timestamp
        self.last_updated = datetime.now(timezone.utc)
        
        return realized_pnl 