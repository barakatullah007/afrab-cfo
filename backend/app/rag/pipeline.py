from __future__ import annotations

import logging

from app.core.config import settings
from app.rag.chunking import ChunkingConfig
from app.rag.embeddings import EmbeddingModel
from app.rag.ingestion import IngestionService
from app.rag.reranker import CrossEncoderReranker
from app.rag.retriever import Retriever
from app.rag.schemas import SearchResult
from app.rag.vector_store import FAISSVectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Financial Knowledge Engine.

    Question -> Retriever -> Reranker -> Relevant Context

    Everything ML-related (embedding model, cross-encoder, FAISS index) is
    initialized lazily on first use, so importing/constructing this class is
    cheap and never blocks app startup even if the optional RAG dependencies
    aren't installed yet.
    """

    def __init__(
        self,
        *,
        knowledge_dir: str | None = None,
        index_dir: str | None = None,
        embedding_model_name: str | None = None,
        cross_encoder_model_name: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        top_k: int | None = None,
    ):
        self.knowledge_dir = knowledge_dir or settings.rag_knowledge_dir
        self.index_dir = index_dir or settings.rag_index_dir
        self.top_k = top_k or settings.rag_top_k

        self.embedding_model = EmbeddingModel(
            embedding_model_name or settings.rag_embedding_model
        )
        self.reranker = CrossEncoderReranker(
            cross_encoder_model_name or settings.rag_cross_encoder_model
        )
        self.chunking_config = ChunkingConfig(
            chunk_size=chunk_size or settings.rag_chunk_size,
            chunk_overlap=chunk_overlap or settings.rag_chunk_overlap,
        )

        self._vector_store: FAISSVectorStore | None = None
        self._retriever: Retriever | None = None
        self._ingestion_service: IngestionService | None = None

    @property
    def vector_store(self) -> FAISSVectorStore:
        if self._vector_store is None:
            self._vector_store = FAISSVectorStore(
                dimension=self.embedding_model.dimension,
                index_dir=self.index_dir,
            )
        return self._vector_store

    @property
    def retriever(self) -> Retriever:
        if self._retriever is None:
            self._retriever = Retriever(
                embedding_model=self.embedding_model,
                vector_store=self.vector_store,
                top_k=self.top_k,
            )
        return self._retriever

    @property
    def ingestion_service(self) -> IngestionService:
        if self._ingestion_service is None:
            self._ingestion_service = IngestionService(
                knowledge_dir=self.knowledge_dir,
                embedding_model=self.embedding_model,
                vector_store=self.vector_store,
                chunking_config=self.chunking_config,
            )
        return self._ingestion_service

    def ingest(self, *, force: bool = False) -> int:
        """Ingest all documents under `knowledge_dir` into the vector store."""

        return self.ingestion_service.ingest_all(force=force)

    def search(
        self,
        question: str,
        top_k: int | None = None,
    ) -> SearchResult:
        """Retrieve and rerank the most relevant knowledge chunks for a question."""

        candidates = self.retriever.retrieve(question, top_k=top_k)

        if not candidates:
            return SearchResult(query=question, chunks=[], used_reranker=False)

        reranked = self.reranker.rerank(
            question,
            candidates,
            top_n=top_k or self.top_k,
        )

        return SearchResult(query=question, chunks=reranked, used_reranker=True)
