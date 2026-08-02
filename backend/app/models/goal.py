from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.enums.goal import (
    GoalPriority,
    GoalStatus,
)

if TYPE_CHECKING:
    from app.models.user import User


class Goal(Base):
    __tablename__ = "goals"

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

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    target_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    target_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    priority: Mapped[GoalPriority] = mapped_column(
        Enum(
            GoalPriority,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=GoalPriority.MEDIUM,
    )

    status: Mapped[GoalStatus] = mapped_column(
        Enum(
            GoalStatus,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=GoalStatus.ACTIVE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="goals",
    )
