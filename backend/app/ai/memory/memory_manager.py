from typing import Optional
from app.services.conversation_memory_service import ConversationMemoryService
from app.schemas.conversation_memory import ConversationMemoryCreate
from app.ai.memory.summarizer import summarize_messages
from app.ai.memory.context_builder import ContextBuilder


class MemoryManager:
    """High-level memory manager used by the AI conversation pipeline.

    Responsibilities:
    - store every incoming and outgoing message
    - retrieve recent conversations
    - retrieve preferences and financial context
    - build a combined context for the planner/LLM
    - perform deterministic summarization when needed
    """

    def __init__(self, memory_service: Optional[ConversationMemoryService] = None):
        self.memory_service = memory_service or ConversationMemoryService()
        self.context_builder = ContextBuilder(self.memory_service)

    def record_message(self, db, user_id: int, role: str, message: str, memory_type: str = "short_term", session_id: Optional[str] = None):
        """Store a single message into conversation memory."""
        data = ConversationMemoryCreate(
            user_id=user_id,
            session_id=session_id,
            role=role,
            message=message,
            memory_type=memory_type,
        )
        return self.memory_service.store(db, data)

    def get_context(self, db, user_id: int, recent_limit: int = 30) -> str:
        return self.context_builder.build(db, user_id, recent_limit=recent_limit)

    def summarize_and_compact(self, db, user_id: int, threshold: int = 100):
        """If the user's stored messages exceed threshold, generate a deterministic summary
        and store as a FINANCIAL_CONTEXT or LONG_TERM memory (non-inferential)."""
        recent = self.memory_service.get_recent(db, user_id, limit=threshold + 10)
        if not recent or len(recent) < threshold:
            return None

        messages = [m.message for m in recent]
        summary = summarize_messages(messages)
        # store as financial_context to be available for future context
        return self.record_message(db, user_id, role="system", message=summary, memory_type="financial_context")
