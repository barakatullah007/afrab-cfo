import logging
import time
from typing import Any

from app.core.config import settings
from app.llm.schemas import LLMGenerationResult

logger = logging.getLogger(__name__)


class GroqProvider:
    """Groq SDK backed LLM provider."""

    provider_name = "groq"

    def generate(
        self,
        messages: list[dict[str, str]],
        model: str,
    ) -> LLMGenerationResult:
        """Generate an answer using Groq.

        Args:
            messages: Chat messages for the model.
            model: Groq model name.

        Returns:
            LLM generation result.

        Raises:
            RuntimeError: If the Groq SDK or API key is unavailable.
        """

        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError("Groq SDK is not installed.") from exc

        client = Groq(
            api_key=settings.groq_api_key,
            timeout=settings.llm_timeout_seconds,
        )

        start = time.perf_counter()

        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )

        latency_ms = int(
            (time.perf_counter() - start) * 1000
        )

        token_usage = self._get_token_usage(
            response,
        )

        logger.info(
            "llm_provider=%s model=%s latency_ms=%s token_usage=%s",
            self.provider_name,
            model,
            latency_ms,
            token_usage,
        )

        return LLMGenerationResult(
            answer=response.choices[0].message.content or "",
            provider=self.provider_name,
            model=model,
            latency_ms=latency_ms,
            token_usage=token_usage,
        )

    def _get_token_usage(
        self,
        response: Any,
    ) -> dict[str, Any] | None:
        usage = getattr(
            response,
            "usage",
            None,
        )

        if usage is None:
            return None

        return {
            "prompt_tokens": getattr(
                usage,
                "prompt_tokens",
                None,
            ),
            "completion_tokens": getattr(
                usage,
                "completion_tokens",
                None,
            ),
            "total_tokens": getattr(
                usage,
                "total_tokens",
                None,
            ),
        }
