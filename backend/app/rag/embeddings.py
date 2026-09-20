from __future__ import annotations

import logging
import threading

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Lazy wrapper around a sentence-transformers embedding model.

    The model is only loaded on first use (not at import or app-startup
    time), so the rest of the application keeps working even if
    sentence-transformers/torch aren't installed until RAG is actually used.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model = None
        self._lock = threading.Lock()

    @property
    def dimension(self) -> int:
        return self._get_model().get_sentence_embedding_dimension()

    def encode(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        model = self._get_model()
        vectors = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def encode_one(self, text: str) -> list[float]:
        return self.encode([text])[0]

    def _get_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    try:
                        from sentence_transformers import SentenceTransformer
                    except ImportError as exc:
                        raise RuntimeError(
                            "sentence-transformers is required for the "
                            "Financial Knowledge Engine. Install it with "
                            "`uv add sentence-transformers`."
                        ) from exc

                    logger.info(
                        "rag_loading_embedding_model model=%s",
                        self.model_name,
                    )
                    self._model = SentenceTransformer(self.model_name)

        return self._model
