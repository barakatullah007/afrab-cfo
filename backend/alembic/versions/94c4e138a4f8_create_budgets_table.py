"""create budgets table

Revision ID: 94c4e138a4f8
Revises: 8f78dd104b73
Create Date: 2026-08-02 18:12:23.210813

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "94c4e138a4f8"
down_revision: Union[str, Sequence[str], None] = "8f78dd104b73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "category_id",
            "month",
            "year",
            name="uq_budget_user_category_month_year",
        ),
    )

    op.create_index(
        op.f("ix_budgets_id"),
        "budgets",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_budgets_user_id"),
        "budgets",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_budgets_category_id"),
        "budgets",
        ["category_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_budgets_category_id"),
        table_name="budgets",
    )

    op.drop_index(
        op.f("ix_budgets_user_id"),
        table_name="budgets",
    )

    op.drop_index(
        op.f("ix_budgets_id"),
        table_name="budgets",
    )

    op.drop_table("budgets")