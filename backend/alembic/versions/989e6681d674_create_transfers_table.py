"""create transfers table

Revision ID: 989e6681d674
Revises: 0001_add_conversation_memory
Create Date: 2026-09-20 22:22:32.279366

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "989e6681d674"
down_revision: Union[str, Sequence[str], None] = "0001_add_conversation_memory"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "transfers",
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
            "source_account_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "destination_account_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "transfer_date",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["destination_account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_transfers_id"),
        "transfers",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_transfers_user_id"),
        "transfers",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_transfers_source_account_id"),
        "transfers",
        ["source_account_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_transfers_destination_account_id"),
        "transfers",
        ["destination_account_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_transfers_destination_account_id"),
        table_name="transfers",
    )

    op.drop_index(
        op.f("ix_transfers_source_account_id"),
        table_name="transfers",
    )

    op.drop_index(
        op.f("ix_transfers_user_id"),
        table_name="transfers",
    )

    op.drop_index(
        op.f("ix_transfers_id"),
        table_name="transfers",
    )

    op.drop_table("transfers")