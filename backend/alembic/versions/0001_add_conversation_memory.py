"""add conversation_memory table

Revision ID: 0001_add_conversation_memory
Revises: 
Create Date: 2026-08-02
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_add_conversation_memory'
down_revision = "d7a6c9e8b1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'conversation_memory',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('session_id', sa.String(length=255), nullable=True, index=True),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('memory_type', sa.String(length=50), nullable=False, server_default=sa.text("'short_term'")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('conversation_memory')
