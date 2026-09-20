from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    """A source document ingested into the financial knowledge base."""

    document_id: str
    document_name: str
    source_path: str
    file_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Chunk(BaseModel):
    """A single chunk of text produced from a KnowledgeDocument."""

    chunk_id: str
    document_id: str
    document_name: str
    text: str
    page_number: int | None = None
    chunk_index: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class VectorSearchResult(BaseModel):
    """Raw result returned by a VectorStore similarity search."""

    chunk_id: str
    score: float
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """A chunk after retrieval (and optional reranking), with attribution."""

    chunk_id: str
    document_name: str
    page_number: int | None = None
    text: str
    retrieval_score: float
    rerank_score: float | None = None


class SearchResult(BaseModel):
    """Final result returned by the RAG pipeline for a user question."""

    query: str
    chunks: list[RetrievedChunk] = Field(default_factory=list)
    used_reranker: bool = False

    @property
    def context_text(self) -> str:
        """Render retrieved chunks into a single context block for the LLM."""

        return "\n\n".join(
            f"[{chunk.document_name}"
            + (f", p.{chunk.page_number}" if chunk.page_number else "")
            + f"]\n{chunk.text}"
            for chunk in self.chunks
        )
