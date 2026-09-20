from typing import List
from sqlalchemy.orm import Session

from app.models.conversation_memory import ConversationMemory
from app.repositories.conversation_memory_repository import ConversationMemoryRepository
from app.schemas.conversation_memory import ConversationMemoryCreate


class ConversationMemoryService:

    def __init__(self):
        self.repository = ConversationMemoryRepository()

    def store(self, db: Session, data: ConversationMemoryCreate) -> ConversationMemory:
        memory = ConversationMemory(
            user_id=data.user_id,
            session_id=data.session_id,
            role=data.role,
            message=data.message,
            memory_type=data.memory_type,
        )
        return self.repository.save(db, memory)

    def get_recent(self, db: Session, user_id: int, limit: int = 50) -> List[ConversationMemory]:
        return self.repository.get_recent_by_user(db, user_id, limit)

    def get_preferences(self, db: Session, user_id: int) -> List[ConversationMemory]:
        return self.repository.get_preferences_by_user(db, user_id)

    def get_financial_context(self, db: Session, user_id: int, limit: int = 50) -> List[ConversationMemory]:
        return self.repository.get_financial_context_by_user(db, user_id, limit)

    def clear_user_memory(self, db: Session, user_id: int) -> None:
        return self.repository.delete_all_for_user(db, user_id)
