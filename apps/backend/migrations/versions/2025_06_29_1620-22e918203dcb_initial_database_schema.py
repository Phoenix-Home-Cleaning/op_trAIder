"""Initial database schema

Revision ID: 22e918203dcb
Revises:
Create Date: 2025-06-29 16:20:39.893351+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "22e918203dcb"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema - Create initial TRAIDER database tables.
    
    Creates all tables required for the TRAIDER V1 trading platform
    including users, market data, positions, trades, and signals.
    """
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('login_attempts', sa.Integer(), nullable=False),
        sa.Column('profile', sa.JSON(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create market_data table (will be converted to hypertable)
    op.create_table(
        'market_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('exchange', sa.String(length=20), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('volume', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('bid', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('ask', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('bid_size', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('ask_size', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('trade_count', sa.Integer(), nullable=True),
        sa.Column('vwap', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('high', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('low', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('open_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('close_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_data_id'), 'market_data', ['id'], unique=False)
    op.create_index(op.f('ix_market_data_symbol'), 'market_data', ['symbol'], unique=False)
    op.create_index(op.f('ix_market_data_timestamp'), 'market_data', ['timestamp'], unique=False)
    
    # Create order_book_level2 table
    op.create_table(
        'order_book_level2',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('exchange', sa.String(length=20), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('bids', sa.JSON(), nullable=False),
        sa.Column('asks', sa.JSON(), nullable=False),
        sa.Column('sequence', sa.BigInteger(), nullable=True),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_book_level2_id'), 'order_book_level2', ['id'], unique=False)
    op.create_index(op.f('ix_order_book_level2_symbol'), 'order_book_level2', ['symbol'], unique=False)
    
    # Create positions table
    op.create_table(
        'positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('exchange', sa.String(length=20), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('size', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('entry_price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('current_price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('unrealized_pnl', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('realized_pnl', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('fees_paid', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('margin_used', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('leverage', sa.Float(), nullable=True),
        sa.Column('liquidation_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('stop_loss', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('take_profit', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('opened_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_positions_id'), 'positions', ['id'], unique=False)
    op.create_index(op.f('ix_positions_user_id'), 'positions', ['user_id'], unique=False)
    op.create_index(op.f('ix_positions_symbol'), 'positions', ['symbol'], unique=False)
    
    # Create trades table (will be converted to hypertable)
    op.create_table(
        'trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('position_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('exchange', sa.String(length=20), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('order_type', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('executed_quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('executed_price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('fees', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('fee_currency', sa.String(length=10), nullable=False),
        sa.Column('commission', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('slippage', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('order_id', sa.String(length=100), nullable=False),
        sa.Column('trade_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trades_id'), 'trades', ['id'], unique=False)
    op.create_index(op.f('ix_trades_user_id'), 'trades', ['user_id'], unique=False)
    op.create_index(op.f('ix_trades_symbol'), 'trades', ['symbol'], unique=False)
    op.create_index(op.f('ix_trades_order_id'), 'trades', ['order_id'], unique=False)
    
    # Create signals table
    op.create_table(
        'signals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('strategy', sa.String(length=50), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('exchange', sa.String(length=20), nullable=False),
        sa.Column('signal_type', sa.String(length=20), nullable=False),
        sa.Column('direction', sa.String(length=10), nullable=False),
        sa.Column('strength', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('target_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('stop_loss', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('risk_reward_ratio', sa.Float(), nullable=True),
        sa.Column('timeframe', sa.String(length=10), nullable=False),
        sa.Column('indicators', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_signals_id'), 'signals', ['id'], unique=False)
    op.create_index(op.f('ix_signals_symbol'), 'signals', ['symbol'], unique=False)
    op.create_index(op.f('ix_signals_strategy'), 'signals', ['strategy'], unique=False)


def downgrade() -> None:
    """
    Downgrade schema - Drop all TRAIDER database tables.
    
    Removes all tables created in the upgrade, allowing for
    clean rollback of the initial schema migration.
    """
    
    # Drop tables in reverse order of creation (respecting foreign keys)
    op.drop_table('signals')
    op.drop_table('trades')
    op.drop_table('positions')
    op.drop_table('order_book_level2')
    op.drop_table('market_data')
    op.drop_table('users')
