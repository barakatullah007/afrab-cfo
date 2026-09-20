from __future__ import annotations

from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.memory import MemoryType


class ConversationMemory(Base):
    __tablename__ = "conversation_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    role: Mapped[str] = mapped_column(String(50), nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=False)

    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    memory_type: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'short_term'"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()"))

    user = relationship("User", backref="conversation_memory")
