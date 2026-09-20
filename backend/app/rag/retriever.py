from __future__ import annotations

from app.rag.embeddings import EmbeddingModel
from app.rag.schemas import RetrievedChunk
from app.rag.vector_store import VectorStore


class Retriever:
    """Embeds a user question and retrieves the top-k most similar chunks."""

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
        top_k: int = 5,
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        vector = self.embedding_model.encode_one(query)
        results = self.vector_store.search(vector, top_k or self.top_k)

        return [
            RetrievedChunk(
                chunk_id=result.chunk_id,
                document_name=result.metadata.get(
                    "document_name", "unknown"
                ),
                page_number=result.metadata.get("page_number"),
                text=result.text,
                retrieval_score=result.score,
            )
            for result in results
        ]
