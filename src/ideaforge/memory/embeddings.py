"""FastEmbed wrapper — local ONNX embeddings.

Uses bge-small-en-v1.5 (384-dim) by default.
Adapted from CodexEngine's embedding patterns.
"""

from __future__ import annotations

from functools import lru_cache

from ideaforge.config import get_settings

EmbeddingFunction = object  # duck-typed


class FastEmbedProvider:
    """Local ONNX embedding via fastembed."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name)

    def embed_query(self, text: str) -> list[float]:
        results = list(self._model.embed([text]))
        return results[0].tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        results = list(self._model.embed(texts))
        return [r.tolist() for r in results]


@lru_cache(maxsize=1)
def get_embedding_provider() -> FastEmbedProvider:
    settings = get_settings()
    return FastEmbedProvider(model_name=settings.embedding_model)
