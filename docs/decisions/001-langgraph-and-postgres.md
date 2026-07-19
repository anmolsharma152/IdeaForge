# ADR 001: LangGraph + Postgres from day one

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date** | 2026-07-19 |
| **Deciders** | Anmol |

## Context

IdeaForge needs an orchestration framework for its dual-process creative synthesis loop (intake → diverge → evaluate → synthesize → persist) and a vector store for novelty scoring via embedding distance.

## Decision

### Orchestration: LangGraph StateGraph

- IdeaForge's phases map 1:1 to LangGraph nodes
- The evaluate → diverge feedback loop is a natural conditional edge
- State sharing via TypedDict is cleaner than passing dicts manually
- LangGraph's checkpointer gives session persistence for free
- CodexEngine v5's hand-rolled loop is better for freeform agent interaction; IdeaForge needs structured phase transitions
- Disha's supervisor pattern is overkill (IdeaForge is a pipeline, not a star topology)

### Storage: Postgres + pgvector

- User has Postgres installed locally — zero new infrastructure
- Evaluation rubric needs embedding distance (novelty scoring) — requires pgvector
- CodexEngine already proved the Postgres + pgvector pattern works
- At personal scale (hundreds to thousands of ideas), pgvector is more than sufficient
- SQL filtering is powerful (filter by workflow, tags, date range)
- ACID transactions keep relational + vector data consistent
- Alembic skipped for MVP; `ensure_schema()` auto-DDL is simpler

### Embeddings: fastembed (bge-small-en-v1.5, 384-dim)

- Local, free, fast — no API calls needed
- 384 dimensions is compact and fast for pgvector
- Proven in CodexEngine

### LLM: Groq (OpenAI-compatible)

- Llama 3.3 70B Versatile for primary pipeline (best quality on Groq)
- GPT-OSS 120B for budget iteration
- Llama 3.1 8B for fast evaluation scoring
- Groq free tier sufficient for prototyping
- OpenAI-compatible API works with any provider
- Gemini as alternative for multimodal input in V1

## Consequences

- All data in a single Postgres instance — simple operations
- LangGraph dependency adds ~5MB to install size
- `ensure_schema()` means no migration history — acceptable for MVP
- Groq's open-source-only catalog limits model options (no GPT-4, Claude)
