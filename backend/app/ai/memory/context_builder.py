from typing import List

from app.services.conversation_memory_service import ConversationMemoryService


class ContextBuilder:
    """Builds a conversation context for the planner/LLM using recent messages,
    preferences, and financial context.
    """

    def __init__(self, memory_service: ConversationMemoryService):
        self.memory_service = memory_service

    def build(
        self,
        db,
        user_id: int,
        recent_limit: int = 30,
    ) -> str:
        recent = self.memory_service.get_recent(db, user_id, limit=recent_limit)
        prefs = self.memory_service.get_preferences(db, user_id)
        financial = self.memory_service.get_financial_context(db, user_id)

        parts: List[str] = []

        if prefs:
            parts.append("User Preferences:")
            for p in prefs:
                parts.append(f"- {p.message}")

        if financial:
            parts.append("Financial Context:")
            for f in financial:
                parts.append(f"- {f.message}")

        if recent:
            parts.append("Recent Conversation:")
            # order oldest -> newest
            for msg in reversed(recent):
                parts.append(f"{msg.role}: {msg.message}")

        return "\n".join(parts)
