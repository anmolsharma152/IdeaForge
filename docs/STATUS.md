# IdeaForge — status handoff

| Field | Value |
|-------|--------|
| **As of** | 2026-07-19 |
| **Branch** | `main` |
| **Product** | Creative synthesis — diverge → evaluate → synthesize → persist |
| **Not this product** | Ozyman (ops) · Disha (jobs) · Scholar-Loop (FSRS) |

Read this first when resuming. Design: [design.md](./design.md).  
Portfolio split: [portfolio-product-boundaries.md](./portfolio-product-boundaries.md).  
Origin thread: [ORIGIN.md](./ORIGIN.md).

---

## What exists today

| Artifact | Notes |
|----------|--------|
| Repo scaffold | README, AGENTS, docs, notes, `.gitignore` |
| Product charter | Portfolio boundaries (shared with siblings) |
| Vision / architecture | Captured in README + [design.md](./design.md) |
| **Python package** | `src/ideaforge/` — CLI, graph, memory, LLM provider |
| **DB schema** | Postgres + pgvector, 5 tables, `ensure_schema()` auto-DDL |
| **LangGraph graph** | 5 nodes: intake → diverge → evaluate → synthesize → persist |
| **Memory layer** | Idea CRUD, vector search, novelty scoring via fastembed |
| **Connection tracking** | Auto-link related ideas, bidirectional queries |
| **LLM provider** | OpenAI-compatible (Groq default, Gemini, OpenAI) |
| **Error resilience** | Retry on rate limits/5xx, fallback scores on LLM failure |
| **Web search** | DuckDuckGo grounding in diverge phase (first iteration) |
| **Workflows** | 3 templates: research, product, learning |
| **CLI** | `run/list/show/search/connect/sessions/metrics` |
| **Tests** | `test_db.py` — schema creation + CRUD |
| **ADR** | `docs/decisions/001-langgraph-and-postgres.md` |
| **Runtime** | Verified end-to-end — Groq Llama 3.3 70B + fastembed BAAI/bge-small-en-v1.5 |

---

## How to run

```bash
cd ~/Projects/IdeaForge
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # edit with your keys
createdb ideaforge
psql -d ideaforge -c "CREATE EXTENSION IF NOT EXISTS vector;"
ideaforge run -w research -g "Novel approaches to protein folding"
ideaforge list
ideaforge search "cross-domain analogies"
```

Requires: Python 3.14+, Postgres with pgvector extension, Groq API key.

---

## Immediate next work

1. **Connection tracking** — link related ideas across sessions
2. **Eval metrics dashboard** — track novelty/diversity/coherence over time
3. **CI pipeline** — pytest + ruff on push
4. **Gemini provider** — alternative LLM for budget/multimodal workflows
5. **Composio integration** — knowledge source search for diverge phase

---

## Explicit non-goals

- Job boards / LPA scoring → **Disha**
- Gmail/GitHub operator loops → **Ozyman**
- FSRS / daily study emails → **Scholar-Loop**
- Clinical risk / health plans → **MedPal** / **WellnessMate**

---

## Resume protocol

1. Read **this file** + portfolio boundaries.
2. `git status` / `git log -5` on `main`.
3. If implementing: start from [design.md](./design.md) MVP slice only.
4. Atomic commits; no secrets.
5. Keep integrations as deep links/exports, not merged monorepos.

**Last session:** verified full end-to-end — schema, embeddings, store CRUD, Groq LLM, LangGraph graph, CLI. Memory compounding confirmed (novelty scores drop on repeated queries). Fixed asyncpg issues: JSONB serialization, pgvector CAST syntax, UUID type handling, Python 3.14 asyncio.run.
