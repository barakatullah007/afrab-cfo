from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.account import Account


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    source_account_id: Mapped[int] = mapped_column(
        ForeignKey(
            "accounts.id",
            ondelete="CASCADE",
    ),
        nullable=False,
        index=True,
    )

    destination_account_id: Mapped[int] = mapped_column(
        ForeignKey(
            "accounts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    transfer_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(
        back_populates="transfers",
    )

    source_account: Mapped["Account"] = relationship(
        foreign_keys=[source_account_id],
        back_populates="outgoing_transfers",
    )

    destination_account: Mapped["Account"] = relationship(
        foreign_keys=[destination_account_id],
        back_populates="incoming_transfers",
    )