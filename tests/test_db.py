"""Test database schema creation and basic operations."""

import uuid
from sqlalchemy import text

from ideaforge.db.engine import get_sync_engine
from ideaforge.db.schema import ensure_schema


def test_ensure_schema_creates_tables():
    """Schema creation should succeed without error."""
    ensure_schema()

    engine = get_sync_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        tables = {row[0] for row in result}

    expected = {"ideas", "evaluations", "connections", "sessions", "provenance"}
    assert expected.issubset(tables), f"Missing tables: {expected - tables}"


def test_insert_and_query_idea():
    """Can insert an idea and read it back."""
    ensure_schema()
    engine = get_sync_engine()

    idea_id = str(uuid.uuid4())
    with engine.connect() as conn:
        conn.execute(
            text(
                "INSERT INTO ideas (id, title, body, workflow) VALUES (:id, :title, :body, :wf)"
            ),
            {"id": idea_id, "title": "Test Idea", "body": "A novel approach to X", "wf": "test"},
        )
        result = conn.execute(text("SELECT title FROM ideas WHERE id = :id"), {"id": idea_id})
        row = result.fetchone()
        conn.commit()

    assert row is not None
    assert row[0] == "Test Idea"

    # Cleanup
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM ideas WHERE id = :id"), {"id": idea_id})
        conn.commit()
