"""Database schema DDL — auto-creates tables on startup.

Pattern from CodexEngine: ensure_schema() runs at import time.
No Alembic for MVP; schema lives here as raw SQL.
"""

from sqlalchemy import text

from ideaforge.db.engine import get_sync_engine

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(512) NOT NULL,
    body TEXT NOT NULL,
    workflow VARCHAR(128) NOT NULL DEFAULT 'general',
    scores JSONB DEFAULT '{}',
    parent_ids UUID[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    embedding vector(384),
    created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
    updated_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT
);

CREATE INDEX IF NOT EXISTS idx_ideas_workflow ON ideas (workflow);
CREATE INDEX IF NOT EXISTS idx_ideas_created ON ideas (created_at);
CREATE INDEX IF NOT EXISTS idx_ideas_tags ON ideas USING GIN (tags);

CREATE TABLE IF NOT EXISTS evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    rubric VARCHAR(128) NOT NULL DEFAULT 'default',
    scores JSONB DEFAULT '{}',
    judge_notes TEXT DEFAULT '',
    model VARCHAR(128) DEFAULT '',
    created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT
);

CREATE INDEX IF NOT EXISTS idx_evaluations_idea ON evaluations (idea_id);

CREATE TABLE IF NOT EXISTS connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    to_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    relation VARCHAR(128) NOT NULL DEFAULT 'related',
    created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT
);

CREATE INDEX IF NOT EXISTS idx_connections_from ON connections (from_id);
CREATE INDEX IF NOT EXISTS idx_connections_to ON connections (to_id);

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow VARCHAR(128) NOT NULL,
    goal TEXT NOT NULL,
    idea_ids UUID[] DEFAULT '{}',
    created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT
);

CREATE TABLE IF NOT EXISTS provenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    sources JSONB DEFAULT '[]',
    prompts JSONB DEFAULT '[]',
    tool_trace JSONB DEFAULT '[]',
    created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT
);

CREATE INDEX IF NOT EXISTS idx_provenance_idea ON provenance (idea_id);
"""


def ensure_schema():
    engine = get_sync_engine()
    with engine.connect() as conn:
        for statement in SCHEMA_SQL.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
