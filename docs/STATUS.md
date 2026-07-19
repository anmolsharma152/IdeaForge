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
| Application code | **None** — no Python/TS package yet |
| Runtime / CI | None |

---

## Immediate next work (when you choose to build)

1. **Lock 2–3 MVP workflows** — e.g. research hypothesis + product ideation + learning analogy.  
2. **Skeleton package** — `pyproject.toml`, CLI entry (`ideaforge …`), empty graph stubs.  
3. **LangGraph phases** — intake → diverge → evaluate → synthesize → persist (even with in-memory store).  
4. **Memory backbone** — prefer CodexEngine-class workspace patterns over Ozyman ops shell.  
5. **Eval rubric v0** — novelty (embedding distance), coherence, usefulness (LLM judge + simple rules).

Do **not** start with a full Next.js shell or image gen. CLI first.

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

**Last docs session:** merged “main README” into `README.md`; added STATUS / design / setup / AGENTS.
