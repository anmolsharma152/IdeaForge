"""Test Pydantic models."""

import uuid

import pytest
from pydantic import ValidationError

from ideaforge.models.idea import Connection, Evaluation, Idea, IdeaWithScore, Session


@pytest.mark.unit
def test_idea_defaults():
    idea = Idea(title="Test Idea", body="Test Body")
    assert isinstance(idea.id, uuid.UUID)
    assert idea.title == "Test Idea"
    assert idea.body == "Test Body"
    assert idea.workflow == "general"
    assert idea.scores == {}
    assert idea.parent_ids == []
    assert idea.tags == []
    assert idea.created_at is None


@pytest.mark.unit
def test_evaluation_defaults():
    idea_id = uuid.uuid4()
    eval = Evaluation(idea_id=idea_id)
    assert isinstance(eval.id, uuid.UUID)
    assert eval.idea_id == idea_id
    assert eval.rubric == "default"
    assert eval.scores == {}
    assert eval.judge_notes == ""
    assert eval.model == ""


@pytest.mark.unit
def test_connection_defaults():
    from_id = uuid.uuid4()
    to_id = uuid.uuid4()
    conn = Connection(from_id=from_id, to_id=to_id)
    assert isinstance(conn.id, uuid.UUID)
    assert conn.from_id == from_id
    assert conn.to_id == to_id
    assert conn.relation == "related"


@pytest.mark.unit
def test_session_defaults():
    session = Session(workflow="research", goal="To find something new")
    assert isinstance(session.id, uuid.UUID)
    assert session.workflow == "research"
    assert session.goal == "To find something new"
    assert session.idea_ids == []


@pytest.mark.unit
def test_idea_with_score():
    idea = Idea(title="T", body="B")
    scored = IdeaWithScore(idea=idea, similarity=0.85)
    assert scored.idea.title == "T"
    assert scored.similarity == 0.85


@pytest.mark.unit
def test_missing_required_fields():
    with pytest.raises(ValidationError):
        Idea(title="Only Title")  # missing body

    with pytest.raises(ValidationError):
        Connection(from_id=uuid.uuid4())  # missing to_id
