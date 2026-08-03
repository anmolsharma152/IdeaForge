"""Test workflow registration and retrieval."""

import pytest

from ideaforge.workflows.base import (
    WORKFLOWS,
    WorkflowConfig,
    get_workflow,
    list_workflows,
    register_workflow,
)


@pytest.fixture(autouse=True)
def clean_workflow_registry():
    """Ensure the workflow registry is restored after each test."""
    original_workflows = WORKFLOWS.copy()
    yield
    WORKFLOWS.clear()
    WORKFLOWS.update(original_workflows)


@pytest.mark.unit
def test_register_and_get_workflow():
    config = WorkflowConfig(
        name="test_wf",
        description="A test workflow",
        system_prompt="You are a tester."
    )
    
    assert get_workflow("test_wf") is None
    register_workflow(config)
    
    retrieved = get_workflow("test_wf")
    assert retrieved is not None
    assert retrieved.name == "test_wf"
    assert retrieved.description == "A test workflow"


@pytest.mark.unit
def test_list_workflows():
    config1 = WorkflowConfig(name="wf1", description="", system_prompt="")
    config2 = WorkflowConfig(name="wf2", description="", system_prompt="")
    
    register_workflow(config1)
    register_workflow(config2)
    
    workflows = list_workflows()
    assert "wf1" in workflows
    assert "wf2" in workflows


@pytest.mark.unit
def test_workflow_config_defaults():
    config = WorkflowConfig(name="def", description="", system_prompt="")
    assert config.muse_count == 5
    assert config.max_iterations == 3
    assert config.min_overall_score == 0.65
    assert "novelty" in config.rubric
    assert config.rubric["novelty"] == 0.35
