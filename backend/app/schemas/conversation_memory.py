from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class ConversationMemoryCreate(BaseModel):
    user_id: int
    session_id: str | None = None
    role: Literal["user", "assistant", "system"] = "user"
    message: str = Field(min_length=1)
    memory_type: Literal[
        "short_term",
        "long_term",
        "preference",
        "financial_context",
    ] = "short_term"


class ConversationMemoryResponse(BaseModel):
    id: int
    user_id: int
    session_id: str | None = None
    role: str
    message: str
    summary: str | None = None
    memory_type: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
