from __future__ import annotations

import logging
from pathlib import Path

from app.rag.chunking import ChunkingConfig, TextChunker
from app.rag.document_loader import DocumentLoader
from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class IngestionService:
    """Loads knowledge documents, chunks them, embeds them, and indexes them."""

    def __init__(
        self,
        *,
        knowledge_dir: str | Path,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
        chunking_config: ChunkingConfig | None = None,
    ):
        self.loader = DocumentLoader(knowledge_dir)
        self.chunker = TextChunker(chunking_config)
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def ingest_all(self, *, force: bool = False) -> int:
        """Ingest every supported file under the knowledge directory.

        Args:
            force: If True, clear the existing index and re-ingest even if
                the vector store already has content. If False (default),
                ingestion is skipped whenever the store is non-empty.

        Returns:
            The number of chunks indexed by this call (0 if skipped).
        """

        if self.vector_store.count() > 0 and not force:
            logger.info(
                "rag_ingestion_skipped existing_chunks=%s",
                self.vector_store.count(),
            )
            return 0

        if force:
            self.vector_store.clear()

        loaded_documents = self.loader.load_all()
        total_chunks = 0

        for loaded in loaded_documents:
            chunks = self.chunker.chunk_document(loaded)
            if not chunks:
                continue

            vectors = self.embedding_model.encode(
                [chunk.text for chunk in chunks]
            )
            ids = [chunk.chunk_id for chunk in chunks]
            payloads = [
                {
                    "text": chunk.text,
                    "document_id": chunk.document_id,
                    "document_name": chunk.document_name,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ]

            self.vector_store.add(ids, vectors, payloads)
            total_chunks += len(chunks)

            logger.info(
                "rag_ingested_document document=%s chunks=%s",
                loaded.document.document_name,
                len(chunks),
            )

        logger.info("rag_ingestion_complete total_chunks=%s", total_chunks)
        return total_chunks
