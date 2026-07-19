# IdeaForge

> **Creative synthesis engine** (scaffold) — deliberate diverge → evaluate → recombine → persist novel ideas.  
> Not a temperature-slapped chatbot. Not Ozyman, Disha, or Scholar-Loop.

| | |
|--|--|
| **Status** | Scaffold + product charter only |
| **Path** | `~/Projects/IdeaForge` |
| **Origin** | Grok ideation: [AI Creativity / System 1–2](https://grok.com/c/5a36d763-a625-44ba-8bdb-d10e44f93f33) (Forge / IdeaWeaver / IdeaForge) |
| **Portfolio split** | [docs/portfolio-product-boundaries.md](./docs/portfolio-product-boundaries.md) |

---

## What this is

A future home for **computational creativity**:

- System 1–style divergence (stochastic / multi-branch / muse agents)
- System 2–style evaluation (novelty, usefulness, coherence)
- Recombination + persistent idea memory
- Workflow templates (research hypotheses, product ideation, learning analogies, …)

Multimodal image/sound gen is **not** v1 identity (optional tools later).

## What this is not

| Not this | Goes to |
|----------|---------|
| Gmail / GitHub / tasks / morning kicks | **Ozyman** (`~/Projects/Ozyman`) |
| Job scrape / LPA fit / apply ranking | **Disha** (`~/Projects/Disha`) |
| FSRS learn/quiz digests | **Scholar-Loop** (`~/Projects/Scholar-Loop`) |

Do **not** implement those loops here. Do **not** implement IdeaForge’s core engine inside the other three repos.

## Layout

```
IdeaForge/
├── README.md
├── docs/
│   ├── portfolio-product-boundaries.md   # shared charter (keep in sync)
│   └── ORIGIN.md                         # pointer to Grok ideation
├── notes/                                # freeform planning notes (optional)
└── .gitignore
```

## Next (when you choose to build)

1. Lock 2–3 workflow templates (see Grok chat + portfolio doc).
2. Sketch LangGraph (or similar) phases: intake → diverge → evaluate → synthesize → persist.
3. Prefer a memory backbone closer to CodexEngine-class workspaces than Ozyman’s ops shell.
4. Keep integrations as deep links / exports only.

---

**Sibling products:** Ozyman (operate) · Disha (market fit) · Scholar-Loop (retain) · **IdeaForge (invent)**.
