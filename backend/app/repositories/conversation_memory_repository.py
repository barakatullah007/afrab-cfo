from typing import List

from sqlalchemy.orm import Session

from app.models.conversation_memory import ConversationMemory


class ConversationMemoryRepository:

    def save(
        self,
        db: Session,
        memory: ConversationMemory,
    ) -> ConversationMemory:
        db.add(memory)
        db.commit()
        db.refresh(memory)

        return memory

    def get_recent_by_user(
        self,
        db: Session,
        user_id: int,
        limit: int = 50,
    ) -> List[ConversationMemory]:
        return (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.user_id == user_id,
            )
            .order_by(
                ConversationMemory.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

    def get_preferences_by_user(
        self,
        db: Session,
        user_id: int,
    ) -> List[ConversationMemory]:
        return (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.user_id == user_id,
                ConversationMemory.memory_type.in_(
                    ["preference", "PREFERENCE"],
                ),
            )
            .order_by(
                ConversationMemory.created_at.asc(),
            )
            .all()
        )

    def get_financial_context_by_user(
        self,
        db: Session,
        user_id: int,
        limit: int = 50,
    ) -> List[ConversationMemory]:
        return (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.user_id == user_id,
                ConversationMemory.memory_type.in_(
                    ["financial_context", "FINANCIAL_CONTEXT"],
                ),
            )
            .order_by(
                ConversationMemory.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

    def delete_all_for_user(
        self,
        db: Session,
        user_id: int,
    ) -> None:
        (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.user_id == user_id,
            )
            .delete(
                synchronize_session=False,
            )
        )

        db.commit()