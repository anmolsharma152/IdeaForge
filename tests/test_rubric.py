"""Test rubric scoring logic."""

import pytest

from ideaforge.eval.rubric import (
    DEFAULT_RUBRIC,
    RESEARCH_RUBRIC,
    Rubric,
    RubricDimension,
    get_rubric,
)


@pytest.mark.unit
def test_get_rubric():
    # Known rubrics
    assert get_rubric("default") is DEFAULT_RUBRIC
    assert get_rubric("research") is RESEARCH_RUBRIC
    
    # Fallback to default
    assert get_rubric("nonexistent") is DEFAULT_RUBRIC
    
    # Empty string fallback
    assert get_rubric("") is DEFAULT_RUBRIC


@pytest.mark.unit
def test_compute_overall_empty_dimensions():
    empty_rubric = Rubric(name="empty", dimensions=[])
    score = empty_rubric.compute_overall({"novelty": 0.8})
    assert score == 0.0


@pytest.mark.unit
def test_compute_overall_missing_scores():
    # If a score is missing from the input, it shouldn't be included in the weighted average
    # Wait, the current implementation computes total += dim.weight * score
    # and weight_sum += dim.weight ONLY if the dim.name is in scores.
    # Let's verify this behavior
    rubric = Rubric(
        name="test",
        dimensions=[
            RubricDimension("a", weight=0.5, description=""),
            RubricDimension("b", weight=0.5, description=""),
        ]
    )
    
    # Both present
    assert rubric.compute_overall({"a": 1.0, "b": 0.5}) == 0.75
    
    # Only one present
    # total = 0.5 * 1.0 = 0.5. weight_sum = 0.5. Result = 1.0
    assert rubric.compute_overall({"a": 1.0}) == 1.0


@pytest.mark.unit
def test_compute_overall_default_rubric():
    scores = {
        "novelty": 0.8,
        "coherence": 0.9,
        "usefulness": 0.7
    }
    
    # Default rubric weights: novelty=0.35, coherence=0.30, usefulness=0.35
    # Total = (0.35 * 0.8) + (0.30 * 0.9) + (0.35 * 0.7) = 0.28 + 0.27 + 0.245 = 0.795
    overall = DEFAULT_RUBRIC.compute_overall(scores)
    assert overall == 0.795


@pytest.mark.unit
def test_compute_overall_research_rubric():
    scores = {
        "novelty": 0.8,
        "coherence": 0.9,
        "usefulness": 0.7
    }
    
    # Research rubric weights: novelty=0.40, coherence=0.25, usefulness=0.35
    # Total = (0.40 * 0.8) + (0.25 * 0.9) + (0.35 * 0.7) = 0.32 + 0.225 + 0.245 = 0.79
    overall = RESEARCH_RUBRIC.compute_overall(scores)
    assert overall == 0.79
