"""link transactions to users

Revision ID: b762d0ee8b8b
Revises: 3a54b662185a
Create Date: 2026-08-02 14:18:25.794856

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b762d0ee8b8b"
down_revision: Union[str, Sequence[str], None] = "3a54b662185a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "transactions",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_transactions_user_id",
        "transactions",
        ["user_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_transactions_user_id",
        "transactions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_transactions_user_id",
        "transactions",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_transactions_user_id",
        table_name="transactions",
    )

    op.drop_column(
        "transactions",
        "user_id",
    )