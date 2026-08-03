"""Test novelty and diversity scoring."""

import pytest

from ideaforge.db.schema import ensure_schema
from ideaforge.memory.novelty import score_diversity, score_novelty
from ideaforge.memory.store import create_idea, delete_idea


@pytest.fixture(autouse=True)
def setup_test_db():
    ensure_schema()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_score_novelty_empty_db():
    # When DB is empty, novelty should be 1.0
    result = await score_novelty("Something totally new")
    assert result["novelty_score"] == 1.0
    assert result["nearest_similarity"] == 0.0
    assert result["nearest_title"] is None
    assert result["nearest_count"] == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_score_novelty_with_ideas():
    idea1 = await create_idea(title="Existing Idea", body="Very specific text about X.")
    
    # Text that is very similar
    result_similar = await score_novelty("Very specific text about X.")
    # Because they are similar, novelty should be low
    assert result_similar["nearest_title"] == "Existing Idea"
    assert result_similar["novelty_score"] < 0.5
    
    # Text that is different
    result_diff = await score_novelty("Completely unrelated text about Y.")
    # Should have higher novelty
    assert result_diff["novelty_score"] > result_similar["novelty_score"]
    
    await delete_idea(idea1.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_score_diversity():
    # Needs at least 2 texts
    result = await score_diversity(["single text"])
    assert result["avg_pairwise_distance"] == 0.0
    
    texts = ["apple", "banana", "car"]
    result2 = await score_diversity(texts)
    assert 0.0 <= result2["avg_pairwise_distance"] <= 1.0
    assert result2["min_similarity"] <= result2["max_similarity"]
