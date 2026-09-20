"""Financial Knowledge Engine (RAG) for the Personal CFO agent.

Question -> Retriever -> Reranker -> Relevant Context -> Planner -> LLM
"""

from app.rag.pipeline import RAGPipeline
from app.rag.schemas import (
    Chunk,
    KnowledgeDocument,
    RetrievedChunk,
    SearchResult,
    VectorSearchResult,
)

__all__ = [
    "RAGPipeline",
    "Chunk",
    "KnowledgeDocument",
    "RetrievedChunk",
    "SearchResult",
    "VectorSearchResult",
]
