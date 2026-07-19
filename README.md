# IdeaForge

> **Persistent Agentic Creative Synthesis Engine**  
> Turn raw thoughts into novel, evaluated, and compounding ideas through structured dual-process reasoning.

IdeaForge is a personal AI system for the hard parts of creativity: deliberate **divergence**, rigorous **evaluation**, intelligent **recombination**, and **long-term memory** of ideas.

It is **not** a temperature slider with an “imagine” button.  
It is an agentic workspace that treats creativity as a **process**, not a single model generation.

| | |
|--|--|
| **Status** | Scaffold + vision / design (implementation not started) |
| **Path** | `~/Projects/IdeaForge` |
| **Origin** | Grok ideation: [AI Creativity / System 1–2](https://grok.com/c/5a36d763-a625-44ba-8bdb-d10e44f93f33) |
| **Working names** | Forge · ConceptualForge · IdeaWeaver · **IdeaForge** |

---

## Docs (start here)

| Doc | Purpose |
|-----|---------|
| **[docs/STATUS.md](./docs/STATUS.md)** | **Handoff** — what exists, next steps, non-goals |
| [docs/design.md](./docs/design.md) | Architecture, dual-process loop, workflows, stack |
| [docs/setup.md](./docs/setup.md) | Planned env / how to open the scaffold |
| [docs/portfolio-product-boundaries.md](./docs/portfolio-product-boundaries.md) | IdeaForge vs Ozyman / Disha / Scholar-Loop |
| [docs/ORIGIN.md](./docs/ORIGIN.md) | Pointer to the Grok ideation thread |
| [AGENTS.md](./AGENTS.md) | Guidance for coding agents |

---

## Why IdeaForge exists

Most AI “creative” tools share the same limits:

- Shallow divergence (higher temperature ≠ structured exploration)
- No meaningful evaluation of novelty or usefulness
- Ideas vanish after the chat session ends
- Little recombination across time or domains
- Weak grounding in the user’s knowledge and goals

Real creative work — research hypotheses, product ideation, conceptual learning, career strategy, technical writing — needs:

1. **Divergence** (System 1 flavor): many options, distant connections, multi-branch exploration  
2. **Evaluation** (System 2 flavor): novelty, surprise, coherence, usefulness  
3. **Synthesis**: combine strongest elements into refined concepts  
4. **Persistence**: store ideas with provenance so future sessions compound  

IdeaForge implements this full loop as a **stateful multi-agent system with long-term memory**.

---

## Core philosophy

Creativity is an **iterative dual-process system**:

| Phase | Cognitive mode | Role in IdeaForge |
|-------|----------------|-------------------|
| **Diverge** | Fast / associative (System 1) | Multi-agent generation, cross-domain RAG, forced recombination, ToT/GoT-style branching |
| **Evaluate** | Deliberate / analytical (System 2) | Multi-criteria scoring (novelty, coherence, usefulness), neuro-symbolic checks, pruning |
| **Synthesize** | Integration | Aggregate strong candidates, iterative refinement |
| **Persist & reflect** | Memory + meta | Store ideas + connections; schedule review; surface distant links over time |

Hybrid by design: neural generation for breadth; structured evaluation and memory for control and compounding value.

---

## What this is / is not

### In scope (product thesis)

- Dual-process agentic loop (diverge → evaluate → synthesize → persist)
- Persistent idea memory (ideas, evaluations, provenance, relationships)
- Workflow templates (research, product, learning analogies, career pivots, technical writing)
- CLI-first; optional web/Tauri later
- Deep links / exports to sibling systems — not absorbing their core loops

### Explicit non-goals (other products)

| Not this | Goes to |
|----------|---------|
| Gmail / GitHub / tasks / morning kicks | **Ozyman** (`~/Projects/Ozyman`) |
| Job scrape / LPA fit / apply ranking | **Disha** (`~/Projects/Disha`) |
| FSRS learn/quiz digests | **Scholar-Loop** (`~/Projects/Scholar-Loop`) |
| Health / clinical companion | **WellnessMate** / **MedPal** |
| Multimodal image/sound gen as v1 identity | Optional tools later only |

Do **not** implement those loops here. Do **not** implement IdeaForge’s core engine inside the other repos.

---

## High-level architecture (planned)

```text
┌─────────────────────────────────────────────────────────────────┐
│                        IdeaForge Core                           │
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │   Intake    │───▶│   Diverge    │───▶│    Evaluate      │   │
│  │  + Context  │    │  (Muse       │    │  (Novelty +      │   │
│  │  Retrieval  │    │   Agents)    │    │   Coherence +    │   │
│  └─────────────┘    └──────────────┘    │   Usefulness)    │   │
│         ▲                  │             └────────┬─────────┘   │
│         │                  ▼                      ▼             │
│  ┌──────┴──────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  Persist &  │◀───│  Synthesize  │◀───│   Ranking &      │   │
│  │  Reflect    │    │  + Refine    │    │   Pruning        │   │
│  └─────────────┘    └──────────────┘    └──────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Persistent Memory (pgvector + Postgres)       │   │
│  │  Ideas · Evaluations · Connections · Provenance · Tags  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

Stateful graph (LangGraph or equivalent) with clear phase nodes. Memory is first-class — not just chat history.

Details: [docs/design.md](./docs/design.md).

---

## Planned workflows

| Workflow | Primary goal | Example output |
|----------|--------------|----------------|
| **Research hypothesis** | Novel, testable questions across literature | Ranked hypotheses + next experiments |
| **Product ideation** | Differentiated features / models | Idea cards with novelty + feasibility notes |
| **Learning synthesis** | Mental models & analogies | Analogy sets, concept maps |
| **Career strategy** | Non-obvious pivots (not job scoring) | Option trees + experiment plans |
| **Technical writing** | Stronger frames and structures | Outlines, alternative framings |
| **Custom** | User-defined goals | Configurable rubric + sources |

---

## Tech stack (planned)

| Layer | Technology | Notes |
|-------|------------|-------|
| Orchestration | LangGraph | Dual-process agent graph, ToT/GoT-style topologies |
| Memory | PostgreSQL + pgvector | Idea store, hybrid search, relationships (CodexEngine patterns) |
| Backend | FastAPI / Python | Async, production-shaped |
| LLM | Provider-agnostic | Groq, Gemini, local, OpenRouter, etc. |
| Evaluation | Embeddings + LLM judges + symbolic rules | Novelty, diversity, coherence, usefulness |
| Interface | CLI first | Optional web/Tauri later |

---

## Relationship to existing projects

| Project | What IdeaForge reuses (conceptually) |
|---------|--------------------------------------|
| **CodexEngine** | Persistent workspace / retrieval backbone patterns |
| **Disha** | Multi-agent LangGraph orchestration patterns |
| **Scholar-Loop** | Optional future review of *valuable ideas* (not FSRS ownership) |
| **MedPal** | Neuro-symbolic evaluation / override patterns |
| **Ozyman** | Sibling only — operate accounts, not invent ideas |

Goal: a **personal creative layer** on top of systems already built — not a disconnected chat toy.

---

## Design principles

1. Creativity is a **process**, not a sampling parameter.  
2. **Memory must compound** — ideas more valuable over months.  
3. Divergence without evaluation is noise; evaluation without divergence is conservative.  
4. Hybrid reasoning > pure neural generation for *useful* novelty.  
5. **Personal knowledge first** — strongest when grounded in your corpus and goals.  
6. CLI and local-first where possible; clear path to richer UI.  
7. **Measurable** — track novelty, diversity, usefulness; don’t just assert them.

---

## Current status & roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **Vision & design** | Dual-process model, workflows, architecture, portfolio charter | ✅ Current |
| **MVP** | Core loop + basic memory + 2–3 templates + CLI | Planned |
| **V1** | Full evaluation suite, relationship graph, CodexEngine-style integration | Planned |
| **V1.5** | Advanced recombination, metrics | Planned |
| **V2** | Multi-user / multimodal hooks / polished UI | Future |

Handoff detail: [docs/STATUS.md](./docs/STATUS.md).

---

## Layout (today)

```text
IdeaForge/
├── README.md                 # this file (merged vision + ops)
├── AGENTS.md
├── docs/
│   ├── STATUS.md
│   ├── design.md
│   ├── setup.md
│   ├── ORIGIN.md
│   └── portfolio-product-boundaries.md
├── notes/                    # freeform planning notes
└── .gitignore
```

No application code yet.

---

## Getting started

```bash
cd ~/Projects/IdeaForge
# Read docs/STATUS.md then docs/design.md
# Implementation instructions will land in docs/setup.md as code appears
```

---

## Sibling products

| Repo | Role |
|------|------|
| `~/Projects/Ozyman` | Operate *today* (mail, GitHub, tasks, kicks) |
| `~/Projects/Disha` | Job market fit (India AI/ML) |
| `~/Projects/Scholar-Loop` | FSRS retain / learn+quiz digests |
| **IdeaForge** | **Invent** — structured creativity with memory that compounds |

---

**IdeaForge** — structured creativity with memory that compounds.  
Built by [Anmol Sharma](https://github.com/anmolsharma152).
