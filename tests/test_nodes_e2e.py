"""Test complete execution of individual nodes with mocked LLM."""

from unittest.mock import patch

import pytest

from ideaforge.db.schema import ensure_schema
from ideaforge.graph.nodes.diverge import diverge_node
from ideaforge.graph.nodes.evaluate import evaluate_node
from ideaforge.graph.nodes.persist import persist_node
from ideaforge.graph.nodes.synthesize import synthesize_node
from ideaforge.memory.store import delete_idea


@pytest.fixture(autouse=True)
def setup_test_db():
    ensure_schema()


@pytest.mark.llm
@pytest.mark.asyncio
@patch("ideaforge.graph.nodes.diverge.create_provider")
async def test_diverge_node_success(mock_create_provider, mock_llm, agent_state_factory):
    mock_llm.responses = [
        '[{"title": "Idea 1", "body": "Body 1", "tags": ["t1"]}]'
    ]
    mock_create_provider.return_value = mock_llm
    
    state = agent_state_factory(goal="Test goal", iteration=0)
    result = await diverge_node(state)
    
    assert result["next_step"] == "evaluate"
    assert len(result["candidates"]) == 1
    assert result["candidates"][0]["title"] == "Idea 1"
    assert result["iteration"] == 1


@pytest.mark.llm
@pytest.mark.asyncio
@patch("ideaforge.graph.nodes.evaluate.create_provider")
async def test_evaluate_node_success(mock_create_provider, mock_llm, agent_state_factory):
    mock_llm.responses = [
        '[{"novelty": 0.9, "coherence": 0.8, "usefulness": 0.7}]'
    ]
    mock_create_provider.return_value = mock_llm
    
    state = agent_state_factory(
        candidates=[{"title": "Idea 1", "body": "Body 1", "tags": []}],
        iteration=1,
        max_iterations=3,
        workflow="test_workflow"
    )
    result = await evaluate_node(state)
    
    assert "scores" in result
    assert len(result["scores"]) == 1
    # Check if the score falls back if parsing fails or uses our mock
    assert "best_indices" in result
    assert len(result["best_indices"]) == 1
    
    # overall >= 0.65 goes to synthesize
    assert result["next_step"] == "synthesize"


@pytest.mark.llm
@pytest.mark.asyncio
@patch("ideaforge.graph.nodes.synthesize.create_provider")
async def test_synthesize_node_success(mock_create_provider, mock_llm, agent_state_factory):
    mock_llm.responses = [
        '{"title": "Refined Idea", "body": "Refined body", "tags": ["t1"]}'
    ]
    mock_create_provider.return_value = mock_llm
    
    state = agent_state_factory(
        candidates=[{"title": "Idea 1", "body": "Body 1", "tags": []}],
        best_indices=[0],
        goal="Test goal"
    )
    
    result = await synthesize_node(state)
    
    assert "refined" in result
    assert result["refined"]["title"] == "Refined Idea"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_persist_node(agent_state_factory):
    state = agent_state_factory(
        refined={"title": "Refined Idea", "body": "Refined body", "tags": ["t1"]},
        scores=[{"novelty": 0.9, "coherence": 0.8, "usefulness": 0.7, "overall": 0.8}],
        best_indices=[0],
        workflow="test_workflow"
    )
    
    result = await persist_node(state)
    
    assert "idea_ids" in result
    assert len(result["idea_ids"]) == 1
    
    # Cleanup
    import uuid
    await delete_idea(uuid.UUID(result["idea_ids"][0]))
