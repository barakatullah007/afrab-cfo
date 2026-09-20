from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship
if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.account import Account
    from app.models.category import Category
    from app.models.budget import Budget
    from app.models.goal import Goal
    from app.models.transfer import Transfer
    from app.models.recurring_transaction import RecurringTransaction
from sqlalchemy import DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    auth_provider: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'local'"),
    )

    google_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    profile_picture: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    categories: Mapped[list["Category"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    accounts: Mapped[list["Account"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    budgets: Mapped[list["Budget"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    goals: Mapped[list["Goal"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    recurring_transactions: Mapped[list["RecurringTransaction"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    transfers: Mapped[list["Transfer"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
