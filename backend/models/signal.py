"""
@fileoverview Signal model for TRAIDER V1 trading signal tracking
@module backend.models.signal

@description
SQLAlchemy model for trading signal generation and tracking.
Records all generated signals with performance metrics and
metadata for strategy analysis and optimization.

@performance
- Indexed timestamp and symbol for fast queries
- Efficient signal performance aggregation
- Optimized strategy analysis queries

@risk
- Failure impact: MEDIUM - Signal history unavailable
- Recovery strategy: Signal regeneration from market data

@compliance
- Audit requirements: All signals logged for analysis
- Data retention: Signal data retained 2 years

@see {@link docs/architecture/signal-tracking.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, String, DateTime, Numeric, Integer, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import JSONB

from ..database import Base


class Signal(Base):
    """
    Signal model for trading signal generation and tracking.
    
    @description
    Records all generated trading signals with strength, confidence,
    and performance metrics for strategy analysis and optimization.
    
    @attributes
    - id: Primary key (auto-increment)
    - timestamp: Signal generation timestamp
    - symbol: Trading symbol
    - strategy: Strategy that generated the signal
    - signal_type: Type of signal (entry, exit, rebalance)
    - signal_strength: Signal strength (-1.0 to 1.0)
    - confidence: Signal confidence (0.0 to 1.0)
    - direction: Signal direction (LONG, SHORT, FLAT)
    - target_price: Target price for the signal
    - stop_loss: Stop loss price
    - take_profit: Take profit price
    - features: Feature values used for signal generation
    - model_version: ML model version (if applicable)
    - executed: Whether signal was executed
    - execution_price: Actual execution price
    - pnl: Realized P&L from this signal
    - status: Signal status
    - metadata: Additional signal information
    
    @tradingImpact HIGH - Signal performance tracking
    @riskLevel MEDIUM - Strategy analysis data
    """
    
    __tablename__ = "signals"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Signal identification
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, default=lambda: datetime.now(timezone.utc))
    symbol = Column(String(20), nullable=False, index=True)
    strategy = Column(String(50), nullable=False, index=True)
    
    # Signal details
    signal_type = Column(String(20), nullable=False, default="entry")  # entry, exit, rebalance
    signal_strength = Column(Numeric(5, 4), nullable=False)  # -1.0 to 1.0
    confidence = Column(Numeric(5, 4), nullable=False)  # 0.0 to 1.0
    direction = Column(String(10), nullable=False)  # LONG, SHORT, FLAT
    
    # Price targets
    target_price = Column(Numeric(20, 8), nullable=True)
    stop_loss = Column(Numeric(20, 8), nullable=True)
    take_profit = Column(Numeric(20, 8), nullable=True)
    
    # Feature data
    features = Column(JSONB, nullable=False, default=dict)
    model_version = Column(String(50), nullable=True)
    
    # Execution tracking
    executed = Column(Boolean, nullable=False, default=False)
    execution_price = Column(Numeric(20, 8), nullable=True)
    execution_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Performance tracking
    pnl = Column(Numeric(20, 8), nullable=False, default=0)
    max_favorable = Column(Numeric(20, 8), nullable=False, default=0)
    max_adverse = Column(Numeric(20, 8), nullable=False, default=0)
    
    # Status and metadata
    status = Column(String(20), nullable=False, default="GENERATED")  # GENERATED, EXECUTED, EXPIRED, CANCELLED
    notes = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=False, default=dict)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_signals_timestamp_symbol', 'timestamp', 'symbol'),
        Index('ix_signals_symbol_timestamp', 'symbol', 'timestamp'),
        Index('ix_signals_strategy_timestamp', 'strategy', 'timestamp'),
        Index('ix_signals_strength_confidence', 'signal_strength', 'confidence'),
        Index('ix_signals_executed_status', 'executed', 'status'),
    )
    
    def __repr__(self) -> str:
        """String representation of signal."""
        return f"<Signal(id={self.id}, {self.direction} {self.symbol} @ {self.signal_strength:.3f})>"
    
    def to_dict(self) -> dict:
        """
        Convert signal to dictionary representation.
        
        @returns Dictionary representation of signal
        
        @performance <1ms serialization
        @sideEffects None
        
        @tradingImpact MEDIUM - Data serialization for API
        @riskLevel LOW - Read-only data conversion
        """
        
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "symbol": self.symbol,
            "strategy": self.strategy,
            "signal_type": self.signal_type,
            "signal_strength": float(self.signal_strength) if self.signal_strength else None,
            "confidence": float(self.confidence) if self.confidence else None,
            "direction": self.direction,
            "target_price": float(self.target_price) if self.target_price else None,
            "stop_loss": float(self.stop_loss) if self.stop_loss else None,
            "take_profit": float(self.take_profit) if self.take_profit else None,
            "features": self.features,
            "model_version": self.model_version,
            "executed": self.executed,
            "execution_price": float(self.execution_price) if self.execution_price else None,
            "execution_timestamp": self.execution_timestamp.isoformat() if self.execution_timestamp else None,
            "pnl": float(self.pnl) if self.pnl else None,
            "max_favorable": float(self.max_favorable) if self.max_favorable else None,
            "max_adverse": float(self.max_adverse) if self.max_adverse else None,
            "status": self.status,
            "notes": self.notes,
            "metadata": self.metadata,
        }
    
    @property
    def is_long(self) -> bool:
        """
        Check if signal is long.
        
        @returns True if signal is long
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact LOW - Signal direction check
        @riskLevel LOW - Simple property
        """
        
        return self.direction.upper() == "LONG"
    
    @property
    def is_short(self) -> bool:
        """
        Check if signal is short.
        
        @returns True if signal is short
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact LOW - Signal direction check
        @riskLevel LOW - Simple property
        """
        
        return self.direction.upper() == "SHORT"
    
    @property
    def is_strong(self) -> bool:
        """
        Check if signal is strong (|strength| > 0.5).
        
        @returns True if signal is strong
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact MEDIUM - Signal strength assessment
        @riskLevel LOW - Simple calculation
        """
        
        return abs(self.signal_strength) > Decimal("0.5") if self.signal_strength else False
    
    @property
    def is_high_confidence(self) -> bool:
        """
        Check if signal has high confidence (> 0.7).
        
        @returns True if signal has high confidence
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact MEDIUM - Signal confidence assessment
        @riskLevel LOW - Simple calculation
        """
        
        return self.confidence > Decimal("0.7") if self.confidence else False
    
    def mark_executed(self, execution_price: Decimal, execution_timestamp: Optional[datetime] = None) -> None:
        """
        Mark signal as executed with execution details.
        
        @param execution_price Price at which signal was executed
        @param execution_timestamp Execution timestamp (defaults to now)
        
        @performance <1ms update
        @sideEffects Updates execution fields and status
        
        @tradingImpact HIGH - Signal execution tracking
        @riskLevel MEDIUM - Status update
        """
        
        self.executed = True
        self.execution_price = execution_price
        self.execution_timestamp = execution_timestamp or datetime.now(timezone.utc)
        self.status = "EXECUTED"
    
    def update_performance(self, current_price: Decimal) -> None:
        """
        Update signal performance metrics based on current price.
        
        @param current_price Current market price
        
        @performance <1ms calculation
        @sideEffects Updates performance metrics
        
        @tradingImpact HIGH - Signal performance tracking
        @riskLevel MEDIUM - Performance calculations
        """
        
        if not self.executed or not self.execution_price:
            return
        
        # Calculate current P&L
        price_diff = current_price - self.execution_price
        
        if self.is_long:
            current_pnl = price_diff
        elif self.is_short:
            current_pnl = -price_diff
        else:
            current_pnl = Decimal(0)
        
        # Update P&L
        self.pnl = current_pnl
        
        # Update max favorable/adverse excursion
        if current_pnl > self.max_favorable:
            self.max_favorable = current_pnl
        
        if current_pnl < self.max_adverse:
            self.max_adverse = current_pnl
    
    def validate_signal(self) -> bool:
        """
        Validate signal data consistency.
        
        @returns True if signal data is valid
        
        @performance <1ms validation
        @sideEffects None
        
        @tradingImpact HIGH - Data integrity check
        @riskLevel MEDIUM - Validation logic
        """
        
        # Basic validation checks
        if not self.symbol or not self.strategy:
            return False
        
        if self.signal_strength is None or abs(self.signal_strength) > 1:
            return False
        
        if self.confidence is None or self.confidence < 0 or self.confidence > 1:
            return False
        
        if self.direction.upper() not in ["LONG", "SHORT", "FLAT"]:
            return False
        
        if self.signal_type not in ["entry", "exit", "rebalance"]:
            return False
        
        return True 