# IdeaForge — setup

| Field | Value |
|-------|--------|
| **As of** | 2026-07-19 |
| **Code status** | Scaffold only — no installable app yet |

---

## Today (docs / planning)

```bash
cd ~/Projects/IdeaForge
# No npm/pip install required for docs work
ls docs/ notes/
```

Read in order: [STATUS.md](./STATUS.md) → [design.md](./design.md) → [ORIGIN.md](./ORIGIN.md).

---

## Planned environment (when MVP lands)

| Variable | Purpose | Required |
|----------|---------|----------|
| `OPENAI_API_KEY` / `GROQ_API_KEY` / `OPENROUTER_API_KEY` | LLM providers (one of) | Yes for live loop |
| `DATABASE_URL` | Postgres (+ pgvector) idea store | Yes for persist phase |
| `EMBEDDING_*` | Embedding provider for novelty | Optional early; mock ok for MVP |

Copy pattern from sibling apps: **never commit** real `.env`; provide `.env.example` when code exists.

---

## Planned commands (not live yet)

```bash
# Illustrative — will match pyproject/CLI when implemented
python -m ideaforge run --workflow product --goal "..."
python -m ideaforge list-ideas
python -m ideaforge show <idea-id>
```

---

## Related setup elsewhere

| Need | Where |
|------|--------|
| Job market tools | `~/Projects/Disha` |
| Daily study digests | `~/Projects/Scholar-Loop` |
| Mail/GitHub operator | `~/Projects/Ozyman` + its `docs/setup.md` |
| Workspace agent patterns | `~/Projects/CodexEngine` |

---

## Agent note

If a coding agent is asked to “set up IdeaForge,” prefer creating the **Python package skeleton + CLI stubs** over inventing a full frontend. See [AGENTS.md](../AGENTS.md).
