"""Test graph logic and utility functions."""

import pytest

from ideaforge.graph.build import route_after_evaluate
from ideaforge.graph.nodes.intake import intake_node
from ideaforge.memory.sources import format_search_context


@pytest.mark.unit
@pytest.mark.asyncio
async def test_intake_node(agent_state_factory):
    # Missing optional fields
    state = agent_state_factory(goal="Find X")
    del state["workflow"]
    
    result = await intake_node(state)
    assert result["workflow"] == "general"
    assert "Find X" in result["context"]
    assert result["iteration"] == 0
    assert result["next_step"] == "diverge"
    assert result["candidates"] == []
    
    # Provided optional fields
    state2 = agent_state_factory(goal="Find Y", workflow="research", max_iterations=5)
    result2 = await intake_node(state2)
    assert result2["workflow"] == "research"
    assert result2["max_iterations"] == 5
    assert "Workflow: research" in result2["context"]


@pytest.mark.unit
def test_route_after_evaluate(agent_state_factory):
    state1 = agent_state_factory(next_step="synthesize")
    assert route_after_evaluate(state1) == "synthesize"
    
    state2 = agent_state_factory(next_step="diverge")
    assert route_after_evaluate(state2) == "diverge"
    
    # Default to stop if not set
    state3 = agent_state_factory()
    if "next_step" in state3:
        del state3["next_step"]
    assert route_after_evaluate(state3) == "stop"


@pytest.mark.unit
def test_format_search_context():
    # Empty
    assert format_search_context([]) == ""
    
    # Results
    results = [
        {"title": "Title 1", "snippet": "Snippet 1", "url": "url1"},
        {"title": "Title 2", "snippet": "Snippet 2", "url": "url2"},
    ]
    formatted = format_search_context(results)
    assert "Recent research and context:" in formatted
    assert "1. Title 1" in formatted
    assert "Snippet 1" in formatted
    assert "2. Title 2" in formatted
