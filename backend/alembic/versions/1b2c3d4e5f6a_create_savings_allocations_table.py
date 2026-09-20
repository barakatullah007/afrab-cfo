"""create savings allocations table

Revision ID: 1b2c3d4e5f6a
Revises: 989e6681d674
Create Date: 2026-09-21 02:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b2c3d4e5f6a"
down_revision: Union[str, Sequence[str], None] = "989e6681d674"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "savings_allocations",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "allocation_type",
            sa.Enum(
                "emergency_fund",
                "investment",
                "other",
                name="savingsallocationtype",
            ),
            nullable=False,
        ),
        sa.Column(
            "amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "month",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "year",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "current_value",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
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
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_savings_allocations_id"),
        "savings_allocations",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_savings_allocations_user_id"),
        "savings_allocations",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_savings_allocations_month"),
        "savings_allocations",
        ["month"],
        unique=False,
    )

    op.create_index(
        op.f("ix_savings_allocations_year"),
        "savings_allocations",
        ["year"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_savings_allocations_year"),
        table_name="savings_allocations",
    )

    op.drop_index(
        op.f("ix_savings_allocations_month"),
        table_name="savings_allocations",
    )

    op.drop_index(
        op.f("ix_savings_allocations_user_id"),
        table_name="savings_allocations",
    )

    op.drop_index(
        op.f("ix_savings_allocations_id"),
        table_name="savings_allocations",
    )

    op.drop_table("savings_allocations")

    sa.Enum(
        "emergency_fund",
        "investment",
        "other",
        name="savingsallocationtype",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )
