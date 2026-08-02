"""create recurring transactions table

Revision ID: c4f2f91d7e8a
Revises: f0c7a1d2e3b4
Create Date: 2026-08-02 20:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4f2f91d7e8a"
down_revision: Union[str, Sequence[str], None] = "f0c7a1d2e3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "recurring_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum(
                "income",
                "expense",
                name="recurringtransactiontype",
            ),
            nullable=False,
        ),
        sa.Column(
            "frequency",
            sa.Enum(
                "daily",
                "weekly",
                "monthly",
                "quarterly",
                "yearly",
                name="recurringfrequency",
            ),
            nullable=False,
        ),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_executed_at", sa.DateTime(timezone=True), nullable=True),
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
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_recurring_transactions_id"),
        "recurring_transactions",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_recurring_transactions_user_id"),
        "recurring_transactions",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_recurring_transactions_account_id"),
        "recurring_transactions",
        ["account_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_recurring_transactions_category_id"),
        "recurring_transactions",
        ["category_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_recurring_transactions_next_run_date"),
        "recurring_transactions",
        ["next_run_date"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_recurring_transactions_next_run_date"),
        table_name="recurring_transactions",
    )

    op.drop_index(
        op.f("ix_recurring_transactions_category_id"),
        table_name="recurring_transactions",
    )

    op.drop_index(
        op.f("ix_recurring_transactions_account_id"),
        table_name="recurring_transactions",
    )

    op.drop_index(
        op.f("ix_recurring_transactions_user_id"),
        table_name="recurring_transactions",
    )

    op.drop_index(
        op.f("ix_recurring_transactions_id"),
        table_name="recurring_transactions",
    )

    op.drop_table("recurring_transactions")

    sa.Enum(
        "daily",
        "weekly",
        "monthly",
        "quarterly",
        "yearly",
        name="recurringfrequency",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )

    sa.Enum(
        "income",
        "expense",
        name="recurringtransactiontype",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )
