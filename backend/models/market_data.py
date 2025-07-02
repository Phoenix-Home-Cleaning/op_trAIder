"""
@fileoverview Market data models for TRAIDER V1
@module backend.models.market_data

@description
SQLAlchemy models for market data storage with TimescaleDB optimizations.
Supports real-time tick data, Level-2 order book capture, and historical
data analysis for institutional-grade trading operations.

@performance
- TimescaleDB hypertables for time-series optimization
- Compressed storage for historical data
- Indexed queries for real-time access

@risk
- Failure impact: CRITICAL - No market data storage
- Recovery strategy: Data feed replay from exchange

@compliance
- Audit requirements: All market data logged
- Data retention: Market data retained 7 years

@see {@link docs/architecture/market-data-schema.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, String, DateTime, Numeric, Integer, Index, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

from database import Base


class MarketData(Base):
    """
    Market data model for tick-level price and volume data.
    
    @description
    Stores real-time and historical market data with TimescaleDB
    optimization for high-frequency data ingestion and analysis.
    
    @attributes
    - timestamp: Data timestamp (partition key)
    - symbol: Trading symbol (e.g., BTC-USD)
    - price: Last trade price
    - volume: Trade volume
    - bid: Best bid price
    - ask: Best ask price
    - spread: Bid-ask spread
    - trade_count: Number of trades
    - vwap: Volume-weighted average price
    - metadata: Additional market data fields
    
    @tradingImpact CRITICAL - All trading decisions depend on this data
    @riskLevel HIGH - Data quality affects trading performance
    """
    
    __tablename__ = "market_data"
    
    # Time-series partition key (TimescaleDB)
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    symbol = Column(String(20), primary_key=True, nullable=False, index=True)
    
    # Price data
    price = Column(Numeric(20, 8), nullable=False)
    volume = Column(Numeric(20, 8), nullable=False, default=0)
    
    # Order book data
    bid = Column(Numeric(20, 8), nullable=True)
    ask = Column(Numeric(20, 8), nullable=True)
    spread = Column(Numeric(20, 8), nullable=True)
    
    # Aggregated data
    trade_count = Column(Integer, nullable=False, default=1)
    vwap = Column(Numeric(20, 8), nullable=True)
    
    # Additional metadata
    extra_data = Column(JSONB, nullable=False, default=dict)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_market_data_timestamp_symbol', 'timestamp', 'symbol'),
        Index('ix_market_data_symbol_timestamp', 'symbol', 'timestamp'),
        Index('ix_market_data_price', 'price'),
    )
    
    def __repr__(self) -> str:
        """String representation of market data."""
        return f"<MarketData(symbol='{self.symbol}', timestamp='{self.timestamp}', price={self.price})>"
    
    def to_dict(self) -> dict:
        """
        Convert market data to dictionary representation.
        
        @returns Dictionary representation of market data
        
        @performance <0.5ms serialization
        @sideEffects None
        
        @tradingImpact MEDIUM - Data serialization for API
        @riskLevel LOW - Read-only data conversion
        """
        
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "symbol": self.symbol,
            "price": float(self.price) if self.price else None,
            "volume": float(self.volume) if self.volume else None,
            "bid": float(self.bid) if self.bid else None,
            "ask": float(self.ask) if self.ask else None,
            "spread": float(self.spread) if self.spread else None,
            "trade_count": self.trade_count,
            "vwap": float(self.vwap) if self.vwap else None,
            "extra_data": self.extra_data,
        }
    
    @property
    def mid_price(self) -> Optional[Decimal]:
        """
        Calculate mid price from bid/ask.
        
        @returns Mid price if bid/ask available
        
        @performance <0.1ms calculation
        @sideEffects None
        
        @tradingImpact HIGH - Used for fair value calculations
        @riskLevel LOW - Simple calculation
        """
        
        if self.bid and self.ask:
            return (self.bid + self.ask) / 2
        return None


class OrderBookLevel2(Base):
    """
    Level-2 order book data model for full market depth.
    
    @description
    Stores complete order book snapshots and updates for institutional-grade
    market microstructure analysis and execution optimization.
    
    @attributes
    - timestamp: Order book snapshot timestamp
    - symbol: Trading symbol
    - side: Order side (bid/ask)
    - price_level: Price level (0 = best, 1 = second best, etc.)
    - price: Price at this level
    - size: Total size at this level
    - order_count: Number of orders at this level
    - exchange: Source exchange identifier
    - sequence: Exchange sequence number
    
    @tradingImpact HIGH - Used for execution optimization
    @riskLevel MEDIUM - Large data volume impact
    """
    
    __tablename__ = "order_book_l2"
    
    # Composite primary key
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    symbol = Column(String(20), primary_key=True, nullable=False)
    side = Column(String(4), primary_key=True, nullable=False)  # 'bid' or 'ask'
    price_level = Column(Integer, primary_key=True, nullable=False)
    
    # Order book data
    price = Column(Numeric(20, 8), nullable=False)
    size = Column(Numeric(20, 8), nullable=False)
    order_count = Column(Integer, nullable=False, default=1)
    
    # Source information
    exchange = Column(String(20), nullable=False, default="coinbase")
    sequence = Column(BigInteger, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_order_book_l2_timestamp_symbol', 'timestamp', 'symbol'),
        Index('ix_order_book_l2_symbol_timestamp', 'symbol', 'timestamp'),
        Index('ix_order_book_l2_price', 'price'),
        Index('ix_order_book_l2_side_price_level', 'side', 'price_level'),
    )
    
    def __repr__(self) -> str:
        """String representation of order book level."""
        return f"<OrderBookL2(symbol='{self.symbol}', {self.side}@{self.price}x{self.size})>"
    
    def to_dict(self) -> dict:
        """
        Convert order book level to dictionary representation.
        
        @returns Dictionary representation of order book level
        
        @performance <0.5ms serialization
        @sideEffects None
        
        @tradingImpact MEDIUM - Data serialization for API
        @riskLevel LOW - Read-only data conversion
        """
        
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "symbol": self.symbol,
            "side": self.side,
            "price_level": self.price_level,
            "price": float(self.price) if self.price else None,
            "size": float(self.size) if self.size else None,
            "order_count": self.order_count,
            "exchange": self.exchange,
            "sequence": self.sequence,
        } 