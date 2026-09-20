from typing import Any

from pydantic import BaseModel


class LLMGenerationResult(BaseModel):

    answer: str

    provider: str

    model: str | None = None

    latency_ms: int | None = None

    token_usage: dict[str, Any] | None = None
