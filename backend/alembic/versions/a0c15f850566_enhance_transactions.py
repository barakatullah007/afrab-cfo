"""enhance transactions

Revision ID: a0c15f850566
Revises: e033cee9d40d
Create Date: 2026-08-02 15:35:20.459999
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a0c15f850566"
down_revision: Union[str, Sequence[str], None] = "e033cee9d40d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ----------------------------
    # Accounts table
    # ----------------------------
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "CASH",
                "BANK",
                "WALLET",
                "CREDIT_CARD",
                "SAVINGS",
                "INVESTMENT",
                name="accounttype",
            ),
            nullable=False,
        ),
        sa.Column(
            "balance",
            sa.Numeric(12, 2),
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(length=10),
            nullable=False,
        ),
        sa.Column(
            "icon",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "color",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_accounts_id"),
        "accounts",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_accounts_user_id"),
        "accounts",
        ["user_id"],
        unique=False,
    )

    # ----------------------------
    # Transactions table changes
    # ----------------------------
    op.add_column(
        "transactions",
        sa.Column(
            "account_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.add_column(
        "transactions",
        sa.Column(
            "category_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.add_column(
        "transactions",
        sa.Column(
            "merchant",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "transactions",
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "transactions",
        sa.Column(
            "transaction_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index(
        op.f("ix_transactions_account_id"),
        "transactions",
        ["account_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_transactions_category_id"),
        "transactions",
        ["category_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_transactions_account",
        "transactions",
        "accounts",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_transactions_category",
        "transactions",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_transactions_category",
        "transactions",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_transactions_account",
        "transactions",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_transactions_category_id"),
        table_name="transactions",
    )

    op.drop_index(
        op.f("ix_transactions_account_id"),
        table_name="transactions",
    )

    op.drop_column(
        "transactions",
        "transaction_date",
    )

    op.drop_column(
        "transactions",
        "notes",
    )

    op.drop_column(
        "transactions",
        "merchant",
    )

    op.drop_column(
        "transactions",
        "category_id",
    )

    op.drop_column(
        "transactions",
        "account_id",
    )

    op.drop_index(
        op.f("ix_accounts_user_id"),
        table_name="accounts",
    )

    op.drop_index(
        op.f("ix_accounts_id"),
        table_name="accounts",
    )

    op.drop_table("accounts")