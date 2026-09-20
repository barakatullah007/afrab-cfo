from __future__ import annotations

import json
import logging
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.rag.schemas import VectorSearchResult

logger = logging.getLogger(__name__)


class VectorStore(ABC):
    """Abstract vector database interface.

    Implemented today by FAISSVectorStore. Kept abstract so PgVector,
    Qdrant, or Chroma can be swapped in later without touching the
    retriever, reranker, or pipeline layers.
    """

    @abstractmethod
    def add(
        self,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ) -> None:
        """Add vectors with associated ids and metadata payloads."""

    @abstractmethod
    def search(
        self,
        vector: list[float],
        top_k: int,
    ) -> list[VectorSearchResult]:
        """Return the top_k nearest vectors to `vector`."""

    @abstractmethod
    def count(self) -> int:
        """Return the number of vectors currently indexed."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all vectors from the store."""


class FAISSVectorStore(VectorStore):
    """FAISS-backed vector store using flat, cosine-similarity search.

    Persists the index and chunk payloads to disk (`index_dir`) so
    re-ingestion is only needed when the knowledge base changes.
    """

    def __init__(self, dimension: int, index_dir: str | Path):
        self.dimension = dimension
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self._index_path = self.index_dir / "index.faiss"
        self._payload_path = self.index_dir / "payloads.json"
        self._lock = threading.Lock()

        self._index = None
        self._ids: list[str] = []
        self._payloads: dict[str, dict[str, Any]] = {}

        self._load()

    def add(
        self,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ) -> None:
        import numpy as np

        with self._lock:
            index = self._get_index()
            matrix = np.array(vectors, dtype="float32")
            index.add(matrix)

            self._ids.extend(ids)
            for chunk_id, payload in zip(ids, payloads):
                self._payloads[chunk_id] = payload

            self._save()

    def search(
        self,
        vector: list[float],
        top_k: int,
    ) -> list[VectorSearchResult]:
        import numpy as np

        with self._lock:
            if self._index is None or self._index.ntotal == 0:
                return []

            query = np.array([vector], dtype="float32")
            scores, indices = self._index.search(
                query,
                min(top_k, self._index.ntotal),
            )

        results: list[VectorSearchResult] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._ids):
                continue

            chunk_id = self._ids[idx]
            payload = self._payloads.get(chunk_id, {})
            results.append(
                VectorSearchResult(
                    chunk_id=chunk_id,
                    score=float(score),
                    text=payload.get("text", ""),
                    metadata=payload,
                )
            )

        return results

    def count(self) -> int:
        return len(self._ids)

    def clear(self) -> None:
        with self._lock:
            self._index = None
            self._ids = []
            self._payloads = {}
            self._index_path.unlink(missing_ok=True)
            self._payload_path.unlink(missing_ok=True)

    def _get_index(self):
        if self._index is None:
            try:
                import faiss
            except ImportError as exc:
                raise RuntimeError(
                    "faiss-cpu is required for the Financial Knowledge "
                    "Engine's vector store. Install it with "
                    "`uv add faiss-cpu`."
                ) from exc

            self._index = faiss.IndexFlatIP(self.dimension)

        return self._index

    def _save(self) -> None:
        import faiss

        faiss.write_index(self._index, str(self._index_path))
        self._payload_path.write_text(
            json.dumps({"ids": self._ids, "payloads": self._payloads})
        )

    def _load(self) -> None:
        if not self._index_path.exists() or not self._payload_path.exists():
            return

        try:
            import faiss
        except ImportError:
            logger.warning(
                "rag_faiss_not_installed skipping_persisted_index_load"
            )
            return

        try:
            self._index = faiss.read_index(str(self._index_path))
            data = json.loads(self._payload_path.read_text())
            self._ids = data.get("ids", [])
            self._payloads = data.get("payloads", {})
        except Exception as exc:
            logger.warning(
                "rag_index_load_failed error=%s",
                exc.__class__.__name__,
            )
