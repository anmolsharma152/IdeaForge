"""Test store operations (CRUD and connections)."""

import uuid

import pytest

from ideaforge.db.schema import ensure_schema
from ideaforge.memory.store import (
    create_connection,
    create_idea,
    create_session,
    delete_idea,
    get_connections,
    get_idea,
    list_ideas,
    list_sessions,
    search_similar,
)


@pytest.fixture(autouse=True)
def setup_test_db():
    ensure_schema()
    # We don't truncate tables here to keep tests simple, but in a real suite
    # we might want to truncate all tables before each test.


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_and_get_idea():
    idea = await create_idea(title="Store Test", body="Test body", tags=["test"])
    assert idea.id is not None
    
    fetched = await get_idea(idea.id)
    assert fetched is not None
    assert fetched.title == "Store Test"
    assert fetched.body == "Test body"
    assert "test" in fetched.tags
    
    # Cleanup
    await delete_idea(idea.id)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_ideas():
    # Insert multiple
    wf = f"wf_{uuid.uuid4().hex[:8]}"
    idea1 = await create_idea(title="Idea 1", body="1", workflow=wf)
    idea2 = await create_idea(title="Idea 2", body="2", workflow=wf)
    
    ideas = await list_ideas(workflow=wf)
    assert len(ideas) == 2
    titles = {i.title for i in ideas}
    assert "Idea 1" in titles
    assert "Idea 2" in titles
    
    # Cleanup
    await delete_idea(idea1.id)
    await delete_idea(idea2.id)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_similar():
    wf = f"wf_{uuid.uuid4().hex[:8]}"
    # "Apple" and "Banana" are fruits
    idea1 = await create_idea(title="Apple", body="A red fruit", workflow=wf)
    idea2 = await create_idea(title="Car", body="A fast vehicle", workflow=wf)
    
    # query for fruit
    similar = await search_similar("fruit", limit=2, workflow=wf)
    
    assert len(similar) > 0
    # Apple should be closer to fruit than Car
    if len(similar) == 2:
        assert similar[0].idea.title == "Apple"
        
    await delete_idea(idea1.id)
    await delete_idea(idea2.id)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_connections():
    idea1 = await create_idea(title="A", body="A")
    idea2 = await create_idea(title="B", body="B")
    
    conn = await create_connection(idea1.id, idea2.id, relation="extends")
    assert conn.from_id == idea1.id
    assert conn.to_id == idea2.id
    
    conns = await get_connections(idea1.id)
    assert len(conns) == 1
    assert conns[0]["relation"] == "extends"
    assert conns[0]["linked_title"] == "B"
    
    await delete_idea(idea1.id)
    await delete_idea(idea2.id)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sessions():
    wf = f"wf_{uuid.uuid4().hex[:8]}"
    session = await create_session(workflow=wf, goal="Test goal")
    assert session.goal == "Test goal"
    
    sessions = await list_sessions(workflow=wf)
    assert len(sessions) == 1
    assert sessions[0].id == session.id
    assert sessions[0].workflow == wf
