"""rename balance to opening_balance

Revision ID: 8f78dd104b73
Revises: a0c15f850566
Create Date: 2026-08-02 15:51:53.980971
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f78dd104b73"
down_revision: Union[str, Sequence[str], None] = "a0c15f850566"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "accounts",
        "balance",
        new_column_name="opening_balance",
        existing_type=sa.Numeric(precision=12, scale=2),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "accounts",
        "opening_balance",
        new_column_name="balance",
        existing_type=sa.Numeric(precision=12, scale=2),
        existing_nullable=False,
    )