from __future__ import annotations

import logging
import threading

from app.rag.schemas import RetrievedChunk

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Lazy wrapper around a sentence-transformers CrossEncoder reranker.

    Re-scores (query, chunk) pairs jointly, which is more accurate than the
    bi-encoder similarity used for initial retrieval, at the cost of being
    more expensive — so it's only run over the retriever's top candidates.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model = None
        self._lock = threading.Lock()

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        top_n: int | None = None,
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        model = self._get_model()
        pairs = [(query, chunk.text) for chunk in chunks]
        scores = model.predict(pairs)

        reranked = [
            chunk.model_copy(update={"rerank_score": float(score)})
            for chunk, score in zip(chunks, scores)
        ]
        reranked.sort(key=lambda chunk: chunk.rerank_score, reverse=True)

        return reranked[:top_n] if top_n else reranked

    def _get_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    try:
                        from sentence_transformers import CrossEncoder
                    except ImportError as exc:
                        raise RuntimeError(
                            "sentence-transformers is required for "
                            "reranking. Install it with "
                            "`uv add sentence-transformers`."
                        ) from exc

                    logger.info(
                        "rag_loading_cross_encoder model=%s",
                        self.model_name,
                    )
                    self._model = CrossEncoder(self.model_name)

        return self._model
