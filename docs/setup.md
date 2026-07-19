# IdeaForge — setup

| Field | Value |
|-------|--------|
| **As of** | 2026-07-19 |
| **Code status** | MVP working — end-to-end verified |

Read in order: [STATUS.md](./STATUS.md) → [design.md](./design.md) → [ORIGIN.md](./ORIGIN.md).

---

## Prerequisites

- Python 3.14+
- PostgreSQL with `vector` extension (pgvector)
- Groq API key (free at console.groq.com)

---

## Install

```bash
cd ~/Projects/IdeaForge
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configure

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and GROQ_API_KEY
```

## Create the test database (if needed)

```bash
psql -U postgres -c "CREATE DATABASE ideaforge;"
psql -U postgres -c "CREATE DATABASE ideaforge_test;"
psql -U postgres -d ideaforge -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -U postgres -d ideaforge_test -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -U postgres -c "ALTER DATABASE ideaforge OWNER TO anmol;"
psql -U postgres -c "ALTER DATABASE ideaforge_test OWNER TO anmol;"
```

## Run

```bash
# Run a workflow
ideaforge run -w research -g "Novel approaches to protein folding"

# List stored ideas
ideaforge list

# Search by similarity
ideaforge search "cross-domain analogies"

# Show a specific idea
ideaforge show <idea-id>
```

## Test

```bash
pytest tests/
```

---

## Available workflows

| Workflow | Description |
|----------|-------------|
| `research` | Forge novel, testable research hypotheses |
| `product` | Forge differentiated product features and models |
| `learning` | Forge mental models and cross-domain connections |

---

## Environment variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `DATABASE_URL` | Postgres connection (with pgvector) | Yes |
| `GROQ_API_KEY` | Groq API key for LLM | Yes |
| `LLM_PROVIDER` | Provider: `groq`, `openai` | No (default: groq) |
| `LLM_MODEL` | Model name override | No |
| `EMBEDDING_MODEL` | fastembed model | No (default: bge-small-en-v1.5) |

---

## Related setup elsewhere

| Need | Where |
|------|-------|
| Job market tools | `~/Projects/Disha` |
| Daily study digests | `~/Projects/Scholar-Loop` |
| Mail/GitHub operator | `~/Projects/Ozyman` + its `docs/setup.md` |
| Workspace agent patterns | `~/Projects/CodexEngine` |
