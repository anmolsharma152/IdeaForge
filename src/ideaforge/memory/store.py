"""Idea store — CRUD + connection tracking for ideas in Postgres + pgvector."""

from __future__ import annotations

import json
import uuid

from sqlalchemy import text

from ideaforge.db.engine import get_async_engine
from ideaforge.memory.embeddings import get_embedding_provider
from ideaforge.models.idea import Connection, Idea, IdeaWithScore, Session


def _to_pgvector(vec: list[float]) -> str:
    """Convert Python list to pgvector literal: '[0.1,0.2,...]'"""
    return "[" + ",".join(f"{v:.8f}" for v in vec) + "]"


def _to_uuid(val) -> uuid.UUID:
    """Handle both native uuid.UUID and asyncpg's UUID type."""
    return uuid.UUID(str(val))


async def create_idea(
    title: str,
    body: str,
    workflow: str = "general",
    tags: list[str] | None = None,
    scores: dict | None = None,
) -> Idea:
    """Create an idea, embed it, and store in Postgres."""
    provider = get_embedding_provider()
    embedding = provider.embed_query(f"{title}\n{body}")

    idea = Idea(title=title, body=body, workflow=workflow, tags=tags or [], scores=scores or {})

    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                INSERT INTO ideas (id, title, body, workflow, scores, tags, embedding)
                VALUES (:id, :title, :body, :workflow, CAST(:scores AS jsonb), :tags, CAST(:embedding AS vector))
                """
            ),
            {
                "id": str(idea.id),
                "title": idea.title,
                "body": idea.body,
                "workflow": idea.workflow,
                "scores": json.dumps(idea.scores),
                "tags": idea.tags,
                "embedding": _to_pgvector(embedding),
            },
        )
    return idea


async def get_idea(idea_id: uuid.UUID) -> Idea | None:
    engine = get_async_engine()
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT id, title, body, workflow, scores, tags, created_at FROM ideas WHERE id = :id"),
            {"id": str(idea_id)},
        )
        row = result.fetchone()
        if not row:
            return None
        return Idea(
            id=_to_uuid(row[0]),
            title=row[1],
            body=row[2],
            workflow=row[3],
            scores=row[4] or {},
            tags=row[5] or [],
            created_at=row[6],
        )


async def list_ideas(workflow: str | None = None, limit: int = 50) -> list[Idea]:
    engine = get_async_engine()
    async with engine.connect() as conn:
        if workflow:
            result = await conn.execute(
                text(
                    "SELECT id, title, body, workflow, scores, tags, created_at "
                    "FROM ideas WHERE workflow = :wf ORDER BY created_at DESC LIMIT :limit"
                ),
                {"wf": workflow, "limit": limit},
            )
        else:
            result = await conn.execute(
                text(
                    "SELECT id, title, body, workflow, scores, tags, created_at "
                    "FROM ideas ORDER BY created_at DESC LIMIT :limit"
                ),
                {"limit": limit},
            )
        return [
            Idea(
                id=_to_uuid(r[0]),
                title=r[1],
                body=r[2],
                workflow=r[3],
                scores=r[4] or {},
                tags=r[5] or [],
                created_at=r[6],
            )
            for r in result.fetchall()
        ]


async def search_similar(query: str, limit: int = 5, workflow: str | None = None) -> list[IdeaWithScore]:
    """Find ideas most similar to the query via pgvector cosine distance."""
    provider = get_embedding_provider()
    query_emb = provider.embed_query(query)

    engine = get_async_engine()
    async with engine.connect() as conn:
        if workflow:
            result = await conn.execute(
                text(
                    """
                    SELECT id, title, body, workflow, scores, tags, created_at,
                           1.0 - (embedding <=> CAST(:emb AS vector)) AS similarity
                    FROM ideas
                    WHERE workflow = :wf AND embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:emb AS vector)
                    LIMIT :limit
                    """
                ),
                {"emb": str(query_emb), "wf": workflow, "limit": limit},
            )
        else:
            result = await conn.execute(
                text(
                    """
                    SELECT id, title, body, workflow, scores, tags, created_at,
                           1.0 - (embedding <=> CAST(:emb AS vector)) AS similarity
                    FROM ideas
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:emb AS vector)
                    LIMIT :limit
                    """
                ),
                {"emb": str(query_emb), "limit": limit},
            )
        return [
            IdeaWithScore(
                idea=Idea(
                    id=_to_uuid(r[0]),
                    title=r[1],
                    body=r[2],
                    workflow=r[3],
                    scores=r[4] or {},
                    tags=r[5] or [],
                    created_at=r[6],
                ),
                similarity=float(r[7]),
            )
            for r in result.fetchall()
        ]


async def delete_idea(idea_id: uuid.UUID) -> bool:
    engine = get_async_engine()
    async with engine.begin() as conn:
        result = await conn.execute(
            text("DELETE FROM ideas WHERE id = :id"), {"id": str(idea_id)}
        )
        return result.rowcount > 0


async def create_connection(
    from_id: uuid.UUID,
    to_id: uuid.UUID,
    relation: str = "related",
) -> Connection:
    """Create a directional connection between two ideas."""
    engine = get_async_engine()
    conn_obj = Connection(from_id=from_id, to_id=to_id, relation=relation)
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                INSERT INTO connections (id, from_id, to_id, relation)
                VALUES (:id, :from_id, :to_id, :relation)
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "id": str(conn_obj.id),
                "from_id": str(from_id),
                "to_id": str(to_id),
                "relation": relation,
            },
        )
    return conn_obj


async def get_connections(idea_id: uuid.UUID) -> list[dict]:
    """Get all connections for an idea (both directions), with linked idea info."""
    engine = get_async_engine()
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                """
                SELECT c.id, c.from_id, c.to_id, c.relation, c.created_at,
                       i.title, i.workflow
                FROM connections c
                JOIN ideas i ON i.id = CASE WHEN c.from_id = :id THEN c.to_id ELSE c.from_id END
                WHERE c.from_id = :id OR c.to_id = :id
                ORDER BY c.created_at DESC
                """
            ),
            {"id": str(idea_id)},
        )
        return [
            {
                "id": _to_uuid(r[0]),
                "from_id": _to_uuid(r[1]),
                "to_id": _to_uuid(r[2]),
                "relation": r[3],
                "created_at": r[4],
                "linked_title": r[5],
                "linked_workflow": r[6],
            }
            for r in result.fetchall()
        ]


async def auto_connect(
    idea_id: uuid.UUID,
    workflow: str | None = None,
    similarity_threshold: float = 0.5,
    max_connections: int = 3,
) -> list[Connection]:
    """Auto-link a new idea to its most similar existing ideas via embedding distance."""
    idea = await get_idea(idea_id)
    if not idea:
        return []

    similar = await search_similar(
        f"{idea.title}\n{idea.body}",
        limit=max_connections + 1,
        workflow=workflow,
    )

    created = []
    for result in similar:
        if _to_uuid(result.idea.id) == idea_id:
            continue
        if result.similarity < similarity_threshold:
            break
        rel = "builds_on" if result.similarity > 0.7 else "related"
        conn = await create_connection(idea_id, result.idea.id, relation=rel)
        created.append(conn)

    return created


async def create_session(
    workflow: str,
    goal: str,
    idea_ids: list[uuid.UUID] | None = None,
) -> Session:
    """Record a workflow run session."""
    session = Session(workflow=workflow, goal=goal, idea_ids=idea_ids or [])
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                INSERT INTO sessions (id, workflow, goal, idea_ids)
                VALUES (:id, :workflow, :goal, :idea_ids)
                """
            ),
            {
                "id": str(session.id),
                "workflow": workflow,
                "goal": goal,
                "idea_ids": [str(i) for i in session.idea_ids],
            },
        )
    return session


async def list_sessions(workflow: str | None = None, limit: int = 20) -> list[Session]:
    """List recent sessions."""
    engine = get_async_engine()
    async with engine.connect() as conn:
        if workflow:
            result = await conn.execute(
                text(
                    "SELECT id, workflow, goal, idea_ids, created_at "
                    "FROM sessions WHERE workflow = :wf "
                    "ORDER BY created_at DESC LIMIT :limit"
                ),
                {"wf": workflow, "limit": limit},
            )
        else:
            result = await conn.execute(
                text(
                    "SELECT id, workflow, goal, idea_ids, created_at "
                    "FROM sessions ORDER BY created_at DESC LIMIT :limit"
                ),
                {"limit": limit},
            )
        return [
            Session(
                id=_to_uuid(r[0]),
                workflow=r[1],
                goal=r[2],
                idea_ids=[_to_uuid(i) for i in (r[3] or [])],
                created_at=r[4],
            )
            for r in result.fetchall()
        ]
