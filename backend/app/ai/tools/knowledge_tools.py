from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings
from app.rag.pipeline import RAGPipeline

logger = logging.getLogger(__name__)


def search_financial_knowledge(
    question: str,
    rag_pipeline: RAGPipeline | None,
) -> dict[str, Any]:
    """Search the Financial Knowledge Engine for general finance education.

    Used for conceptual/educational questions (e.g. "How does the 50/30/20
    rule work?", "What is an index fund?") rather than questions about the
    user's own financial data, which continue to be answered by the
    Financial Intelligence tools.

    Args:
        question: The user's question.
        rag_pipeline: Configured RAG pipeline, or None if RAG is unavailable.

    Returns:
        JSON-serializable dict with retrieved context text and per-chunk
        source attribution (document_name, page_number, chunk_id).
    """

    if rag_pipeline is None or not settings.rag_enabled:
        return {
            "available": False,
            "context": "",
            "sources": [],
        }

    try:
        result = rag_pipeline.search(question)
    except Exception as exc:
        logger.warning(
            "rag_search_failed error=%s",
            exc.__class__.__name__,
        )
        return {
            "available": False,
            "context": "",
            "sources": [],
        }

    return {
        "available": True,
        "context": result.context_text,
        "sources": [
            {
                "document_name": chunk.document_name,
                "page_number": chunk.page_number,
                "chunk_id": chunk.chunk_id,
                "score": chunk.rerank_score
                if chunk.rerank_score is not None
                else chunk.retrieval_score,
            }
            for chunk in result.chunks
        ],
    }
