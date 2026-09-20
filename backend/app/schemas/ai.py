from typing import Any, Literal

from pydantic import BaseModel, Field


Confidence = Literal[
    "high",
    "medium",
    "low",
]


class AIChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=2000,
        examples=["How much did I spend on food this month?"],
    )


class AIChatResponse(BaseModel):

    intent: str

    tool_used: str | None = None

    answer: str

    tool_output: Any = None

    confidence: Confidence

    provider: str | None = None

    model: str | None = None

    planning_steps: list[str] = Field(default_factory=list)

    tools_executed: list[str] = Field(default_factory=list)

    advisors_used: list[str] = Field(default_factory=list)

    execution_time_ms: int = 0

    sources: list[dict[str, Any]] = Field(default_factory=list)
