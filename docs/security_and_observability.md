# IdeaForge — Security, MLOps, & Observability Architecture

This document provides a comprehensive technical reference for the security hardening, MLOps analytics, prompt injection defenses, observability tracing, and agent orchestration patterns implemented in **IdeaForge**.

---

## 1. Agent Orchestration Architecture

IdeaForge implements a dual-process creative synthesis engine orchestrating autonomous agent roles via **LangGraph**.

```
                  ┌──────────────┐
                  │    intake    │ (Normalizes prompt & web search context)
                  └──────┬───────┘
                         │
                  ┌──────▼───────┐
             ┌───►│   diverge    │ (Muse personas generate diverse candidates)
             │    └──────┬───────┘
             │           │
     (Re-try │    ┌──────▼───────┐
  If Low     └────┤   evaluate   ├────┐ (Scores Novelty, Coherence, Usefulness)
   Score)         └──────────────┘    │ (Boosts novelty via pgvector distance)
                                      │
                              ┌───────▼──────┐
                              │  synthesize  │ (Merges winners into concept card)
                              └───────┬──────┘
                                      │
                              ┌───────▼──────┐
                              │   persist    │ (Writes to Postgres + pgvector)
                              └───────┬──────┘
                                      │
                                    [ END ]
```

### Agent Roles:
1. **Intake Agent** ([src/ideaforge/graph/nodes/intake.py](file:///home/anmol/Projects/IdeaForge/src/ideaforge/graph/nodes/intake.py)): Prepares state dictionary, normalizes goal inputs, and injects workflow context.
2. **Diverge Muses Agent** ([src/ideaforge/graph/nodes/diverge.py](file:///home/anmol/Projects/IdeaForge/src/ideaforge/graph/nodes/diverge.py)): Runs DuckDuckGo grounding web search (`ddgs`) on iteration 1 and executes high-temperature LLM generation.
3. **Evaluator Agent** ([src/ideaforge/graph/nodes/evaluate.py](file:///home/anmol/Projects/IdeaForge/src/ideaforge/graph/nodes/evaluate.py)): Evaluates candidates on Rubrics and calculates embedding distance against existing memory.
4. **Synthesizer Agent** ([src/ideaforge/graph/nodes/synthesize.py](file:///home/anmol/Projects/IdeaForge/src/ideaforge/graph/nodes/synthesize.py)): Blends complementary candidates into a refined concept.
5. **Memory Librarian Agent** ([src/ideaforge/graph/nodes/persist.py](file:///home/anmol/Projects/IdeaForge/src/ideaforge/graph/nodes/persist.py)): Writes vector embeddings (`BAAI/bge-small-en-v1.5`) to PostgreSQL and auto-links related concepts.

---

## 2. Security Hardening & Prompt Injection Defense

### Prompt Injection Mitigation
All untrusted user inputs (creative goals, custom context, and DuckDuckGo web search snippets) pass through `sanitize_prompt_input()` in [`src/ideaforge/utils/security.py`](file:///home/anmol/Projects/IdeaForge/src/ideaforge/utils/security.py) before prompt interpolation:
- **Control Character Scrubbing**: Removes non-printable characters except standard whitespace.
- **Override Keyword Filtering**: Neutralizes common system prompt injection attack strings (e.g. `ignore previous instructions`, `system prompt:`, `<|im_start|>`, `[INST]`).
- **Input Boundaries**: Enforces strict maximum length caps across goals (1,000 chars), titles (100 chars), and search snippets (250 chars).

### Secrets & API Key Pre-Validation
- Provider initialization in [`src/ideaforge/llm/providers.py`](file:///home/anmol/Projects/IdeaForge/src/ideaforge/llm/providers.py#L127-L133) validates that required API keys (`GROQ_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`) are present and non-empty. Missing keys raise an informative `ValueError` before network requests occur.

### SQL Parameterization
- Database operations in [`src/ideaforge/memory/store.py`](file:///home/anmol/Projects/IdeaForge/src/ideaforge/memory/store.py) strictly utilize SQLAlchemy parameter bindings (`:id`, `:wf`, `:emb`, `:limit`), preventing SQL injection vectors. Vector formatting explicitly converts floats to strict float array literals.

---

## 3. MLOps & Compounding Memory

### Embeddings & Vector Search
- **Provider**: `fastembed` with `BAAI/bge-small-en-v1.5` (384 dimensions).
- **Storage**: PostgreSQL with `pgvector` extension.
- **Cosine Distance Metric**: `1.0 - (embedding <=> CAST(:emb AS vector))` used for novelty scoring and similarity search.

### Memory Compounding
- When new ideas are evaluated, `score_novelty()` calculates cosine distance against all previously stored ideas in the database.
- Repeated or similar prompts produce lower novelty scores over time, forcing the system to diverge further or trigger additional iteration rounds.

---

## 4. Web Application & REST API

IdeaForge provides a modern **Single Page Application (SPA)** web interface served via **FastAPI** & **Uvicorn**:

### Starting the Server
```bash
ideaforge web --port 8000
```

### Endpoints
- `GET /api/workflows`: List registered workflow templates.
- `POST /api/run`: Trigger async LangGraph ideation session.
- `GET /api/ideas`: List ideas from persistent store.
- `GET /api/ideas/search`: Perform vector similarity search.
- `GET /api/connections/{idea_id}`: Query bidirectional graph edges.
- `GET /api/metrics`: Retrieve compounding memory analytics.
