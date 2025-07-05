"""market data hypertable

Revision ID: 0001_market_data_hypertable
Revises: 22e918203dcb_initial_database_schema
Create Date: 2025-07-05 12:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_market_data_hypertable"
down_revision = "22e918203dcb_initial_database_schema"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "market_data",
        sa.Column("timestamp", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Numeric(20, 8), nullable=False),
        sa.Column("volume", sa.Numeric(20, 8)),
        sa.PrimaryKeyConstraint("timestamp", "symbol"),
    )
    # Convert to Timescale hypertable
    op.execute("SELECT create_hypertable('market_data', 'timestamp', if_not_exists => TRUE);")


def downgrade() -> None:
    op.drop_table("market_data") 