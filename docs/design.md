# IdeaForge — design

| Field | Value |
|-------|--------|
| **Document** | Design specification (pre-implementation) |
| **As of** | 2026-07-19 |
| **Status** | Vision locked; code not started |

Companion handoff: [STATUS.md](./STATUS.md). Product boundaries: [portfolio-product-boundaries.md](./portfolio-product-boundaries.md).

---

## Problem

LLM chat is fluent but **conservative**. Pure high-temperature sampling is noisy without evaluation or memory. Useful creativity needs an explicit process:

```text
intake → diverge → evaluate → synthesize → persist → (optional) reflect
```

---

## Dual-process model

| Phase | System | Mechanisms (planned) |
|-------|--------|----------------------|
| Diverge | System 1 | Muse personas, temp diversity, cross-domain priming, ToT/GoT branching |
| Evaluate | System 2 | Embedding novelty vs idea store, coherence rules, usefulness judge, prune |
| Synthesize | Integration | Merge top candidates, re-score, optional human pick |
| Persist | Memory | Structured idea records + edges + provenance + tags |
| Reflect | Meta | Surface distant links; optional Scholar-Loop-style *idea review* later |

---

## Agent roles (planned)

| Agent | Job |
|-------|-----|
| **Intake** | Normalize prompt, pull context (user goals, optional RAG) |
| **Muse(s)** | Generate diverse candidates (parallel personas) |
| **Critic / evaluator** | Score novelty, coherence, usefulness; flag junk |
| **Synthesizer** | Recombine winners into refined concept cards |
| **Librarian** | Write/read idea memory; link related ideas |

Orchestration: **LangGraph** (or equivalent stateful graph) with conditional edges after evaluate (continue diverge vs synthesize vs stop).

---

## Data model (sketch)

Not implemented — target shapes:

| Entity | Key fields |
|--------|------------|
| `Idea` | id, title, body, workflow, scores{}, parent_ids[], tags[], created_at |
| `Evaluation` | idea_id, rubric, scores, judge_notes, model |
| `Connection` | from_id, to_id, relation (inspired_by, contradicts, extends) |
| `Session` | id, workflow, goal, idea_ids[] |
| `Provenance` | idea_id, sources[], prompts, tool_trace |

Storage: Postgres + pgvector preferred (align with CodexEngine patterns).

---

## Workflow templates

Configurable **rubric + system prompts + optional RAG sources** per mode:

1. Research hypothesis forge  
2. Product / feature ideation  
3. Learning analogy & mental models  
4. Career pivot explorer (*not* job listing scorer)  
5. Technical writing / argument development  
6. Custom

MVP: implement **two** end-to-end before expanding templates.

---

## Interfaces

| Surface | Priority |
|---------|----------|
| CLI | **P0** — terminal-native loop |
| FastAPI | P1 — if multi-client needed |
| Web / Tauri | P2 |

---

## Evaluation metrics

Track per session and over time:

- **Novelty** — distance from nearest neighbors in idea store  
- **Diversity** — spread among candidates in a diverge batch  
- **Coherence** — structure / constraint pass rate  
- **Usefulness** — human or judge score; optional “shipped / used” feedback later  

---

## Integration policy

| Sibling | Allowed integration |
|---------|---------------------|
| CodexEngine | Memory / retrieval patterns; optional project workspace later |
| Scholar-Loop | Export “idea worth reviewing” — Scholar owns schedule |
| Disha | Career *pivot ideation* only; never job scrape |
| Ozyman | Deep link only; no mail/GH tools in IdeaForge core |

---

## Security & privacy

- Local-first preference for personal idea graphs  
- No commit of API keys  
- Treat idea memory as personal data  

---

## Open decisions

- [ ] Exact graph library (LangGraph vs custom loop à la CodexEngine v5)  
- [ ] Single-user local SQLite vs Postgres from day one  
- [ ] License (MIT vs source-available)  
- [ ] Whether to share a vector DB with CodexEngine or isolate  

Document decisions in ADRs under `docs/decisions/` when code starts.
