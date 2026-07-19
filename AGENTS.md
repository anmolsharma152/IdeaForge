# AGENTS.md

Guidance for coding agents working in **IdeaForge**.

## Product scope

IdeaForge is a **creative synthesis engine**: diverge → evaluate → synthesize → persist novel ideas with compounding memory.

**Out of scope here** (other repos):

| Domain | Product |
|--------|---------|
| Gmail / GitHub / tasks / kicks | Ozyman |
| Job scrape / LPA scoring | Disha |
| FSRS / study digests | Scholar-Loop |
| Clinical / wellness | MedPal / WellnessMate |

Canonical split: [docs/portfolio-product-boundaries.md](./docs/portfolio-product-boundaries.md).  
Resume: [docs/STATUS.md](./docs/STATUS.md). Design: [docs/design.md](./docs/design.md).

## Current reality

- **No application source tree yet** — docs and charter only.  
- Prefer implementing MVP as **Python + CLI + LangGraph (or light agent loop)** before any web UI.  
- Reuse patterns from CodexEngine (workspace memory) and Disha (multi-agent graphs); do not copy Ozyman ops code into this repo.

## Engineering norms

- Docs-only changes are welcome; product code should follow [design.md](./docs/design.md).  
- Atomic commits; never commit secrets.  
- Keep IdeaForge’s identity: **invent**, don’t operate accounts or rank job posts.  
- When adding memory, treat ideas as personal data.
