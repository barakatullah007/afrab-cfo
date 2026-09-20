import json
import logging
import time
from typing import Any

from app.ai.prompts.system_prompt import SYSTEM_PROMPT
from app.core.config import settings
from app.llm.providers.groq_provider import GroqProvider
from app.llm.schemas import LLMGenerationResult

logger = logging.getLogger(__name__)


class LLMService:
    """Build prompts and call the configured LLM provider."""

    def __init__(self):
        self.groq_provider = GroqProvider()

    def generate_answer(
        self,
        *,
        user_message: str,
        tool_output: Any,
        fallback_answer: str,
    ) -> LLMGenerationResult:
        """Generate a natural-language answer from tool output.

        Args:
            user_message: Original user question.
            tool_output: JSON-serializable tool output.
            fallback_answer: Deterministic answer to use if LLM fails.

        Returns:
            LLM generation result, or fallback result if unavailable.
        """

        if settings.llm_provider != "groq":
            return self._fallback(
                fallback_answer,
            )

        try:
            return self.groq_provider.generate(
                messages=self._build_messages(
                    user_message,
                    tool_output,
                ),
                model=settings.llm_model,
            )
        except Exception as exc:
            logger.warning(
                "llm_provider=%s model=%s failed=%s",
                settings.llm_provider,
                settings.llm_model,
                exc.__class__.__name__,
            )

            return self._fallback(
                fallback_answer,
            )

    def _build_messages(
        self,
        user_message: str,
        tool_output: Any,
    ) -> list[dict[str, str]]:
        tool_output_json = json.dumps(
            tool_output,
            indent=2,
            default=str,
        )

        return [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "User asked:\n"
                    f"{user_message}\n\n"
                    "Tool returned JSON:\n"
                    f"{tool_output_json}\n\n"
                    "Explain this naturally. Do not invent numbers. "
                    "Only use values provided. If information is missing, "
                    "say so."
                ),
            },
        ]

    def _fallback(
        self,
        fallback_answer: str,
    ) -> LLMGenerationResult:
        start = time.perf_counter()
        latency_ms = int(
            (time.perf_counter() - start) * 1000
        )

        logger.info(
            "llm_provider=fallback model=None latency_ms=%s token_usage=None",
            latency_ms,
        )

        return LLMGenerationResult(
            answer=fallback_answer,
            provider="fallback",
            model=None,
            latency_ms=latency_ms,
        )
