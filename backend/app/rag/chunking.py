from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.rag.document_loader import LoadedDocument
from app.rag.schemas import Chunk


@dataclass(frozen=True)
class ChunkingConfig:
    """Configurable chunking parameters."""

    chunk_size: int = 800
    chunk_overlap: int = 150

    def __post_init__(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.chunk_overlap < 0 or self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be >= 0 and strictly less than chunk_size"
            )


class TextChunker:
    """Splits document pages into overlapping, fixed-size character chunks.

    A character-based splitter is used (rather than token-based) to keep the
    dependency footprint small; `chunk_size`/`chunk_overlap` are tunable via
    ChunkingConfig or the RAG_CHUNK_SIZE / RAG_CHUNK_OVERLAP settings.
    """

    def __init__(self, config: ChunkingConfig | None = None):
        self.config = config or ChunkingConfig()

    def chunk_document(self, loaded: LoadedDocument) -> list[Chunk]:
        """Chunk every page of a loaded document, preserving page metadata."""

        chunks: list[Chunk] = []
        chunk_index = 0

        for page_number, text in loaded.pages:
            for piece in self._split(text):
                stripped = piece.strip()
                if not stripped:
                    continue

                chunks.append(
                    Chunk(
                        chunk_id=str(uuid.uuid4()),
                        document_id=loaded.document.document_id,
                        document_name=loaded.document.document_name,
                        text=stripped,
                        page_number=page_number,
                        chunk_index=chunk_index,
                        metadata={
                            "source_path": loaded.document.source_path,
                            "file_type": loaded.document.file_type,
                        },
                    )
                )
                chunk_index += 1

        return chunks

    def _split(self, text: str) -> list[str]:
        size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = size - overlap

        if len(text) <= size:
            return [text]

        pieces: list[str] = []
        start = 0
        while start < len(text):
            pieces.append(text[start : start + size])
            start += step

        return pieces
