"""create goals table

Revision ID: f0c7a1d2e3b4
Revises: 94c4e138a4f8
Create Date: 2026-08-02 19:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f0c7a1d2e3b4"
down_revision: Union[str, Sequence[str], None] = "94c4e138a4f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "target_amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "current_amount",
            sa.Numeric(precision=12, scale=2),
            server_default=sa.text("0.00"),
            nullable=False,
        ),
        sa.Column(
            "target_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "priority",
            sa.Enum(
                "low",
                "medium",
                "high",
                name="goalpriority",
            ),
            server_default="medium",
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "completed",
                "cancelled",
                name="goalstatus",
            ),
            server_default="active",
            nullable=False,
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
        op.f("ix_goals_id"),
        "goals",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_goals_user_id"),
        "goals",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_goals_user_id"),
        table_name="goals",
    )

    op.drop_index(
        op.f("ix_goals_id"),
        table_name="goals",
    )

    op.drop_table("goals")

    sa.Enum(
        "active",
        "completed",
        "cancelled",
        name="goalstatus",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )

    sa.Enum(
        "low",
        "medium",
        "high",
        name="goalpriority",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )
