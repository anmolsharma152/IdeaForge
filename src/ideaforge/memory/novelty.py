"""Novelty scoring — embedding distance to existing ideas."""

from __future__ import annotations

from ideaforge.memory.embeddings import get_embedding_provider
from ideaforge.memory.store import search_similar


async def score_novelty(
    text: str,
    workflow: str | None = None,
    top_k: int = 5,
) -> dict:
    """Score how novel a piece of text is relative to existing ideas.

    Returns:
        {
            "novelty_score": float  (0.0 = duplicate, 1.0 = completely novel),
            "nearest_similarity": float,
            "nearest_title": str | None,
            "nearest_count": int,
        }
    """
    results = await search_similar(text, limit=top_k, workflow=workflow)

    if not results:
        return {
            "novelty_score": 1.0,
            "nearest_similarity": 0.0,
            "nearest_title": None,
            "nearest_count": 0,
        }

    nearest = results[0]
    # Novelty = 1 - best similarity (cosine distance)
    # High similarity to existing idea = low novelty
    novelty = max(0.0, 1.0 - nearest.similarity)

    return {
        "novelty_score": round(novelty, 4),
        "nearest_similarity": round(nearest.similarity, 4),
        "nearest_title": nearest.idea.title,
        "nearest_count": len(results),
    }


async def score_diversity(texts: list[str]) -> dict:
    """Score diversity among a batch of candidate texts.

    Returns:
        {
            "avg_pairwise_distance": float,
            "min_similarity": float,
            "max_similarity": float,
        }
    """
    if len(texts) < 2:
        return {"avg_pairwise_distance": 0.0, "min_similarity": 1.0, "max_similarity": 1.0}

    provider = get_embedding_provider()
    embeddings = provider.embed_documents(texts)

    similarities = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            # Cosine similarity via dot product (embeddings are normalized)
            dot = sum(a * b for a, b in zip(embeddings[i], embeddings[j]))
            similarities.append(dot)

    avg_sim = sum(similarities) / len(similarities)
    return {
        "avg_pairwise_distance": round(1.0 - avg_sim, 4),
        "min_similarity": round(min(similarities), 4),
        "max_similarity": round(max(similarities), 4),
    }
