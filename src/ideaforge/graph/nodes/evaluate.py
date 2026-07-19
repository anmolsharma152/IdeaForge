"""Evaluate node — score candidates, decide next step."""

import json
import logging

from ideaforge.llm.providers import create_provider
from ideaforge.memory.novelty import score_novelty
from ideaforge.models.state import AgentState, EvalScores

log = logging.getLogger(__name__)

EVAL_PROMPT = """You are a rigorous idea evaluator. Score each candidate on novelty, coherence, and usefulness.

GOAL: {goal}

CANDIDATES:
{candidates_text}

For EACH candidate, output a JSON object with keys:
- "novelty": 0.0-1.0 (how non-obvious and fresh is this?)
- "coherence": 0.0-1.0 (is it logically sound and well-formed?)
- "usefulness": 0.0-1.0 (would this be actionable or valuable?)
- "notes": brief justification

Output ONLY a JSON array of score objects, one per candidate, in order.
No explanation, no markdown, just the JSON array."""


async def evaluate_node(state: AgentState) -> dict:
    candidates = state.get("candidates", [])
    goal = state.get("goal", "")
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 3)

    if not candidates:
        return {"next_step": "stop", "scores": [], "best_indices": []}

    # LLM-based evaluation with fallback
    provider = create_provider()
    candidates_text = "\n\n".join(
        f"[{i+1}] {c['title']}: {c['body']}" for i, c in enumerate(candidates)
    )
    prompt = EVAL_PROMPT.format(goal=goal, candidates_text=candidates_text)

    try:
        result = await provider.complete(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2048,
        )
        scores = _parse_scores(result.content, len(candidates))
    except Exception:
        log.exception("Evaluate LLM call failed, using default scores")
        scores = [
            EvalScores(novelty=0.5, coherence=0.5, usefulness=0.5)
            for _ in range(len(candidates))
        ]

    # Novelty boost via embedding distance (non-critical)
    for i, candidate in enumerate(candidates):
        try:
            novelty_result = await score_novelty(
                f"{candidate['title']}\n{candidate['body']}",
                workflow=state.get("workflow"),
            )
            if i < len(scores):
                llm_novelty = scores[i].get("novelty", 0.5)
                embed_novelty = novelty_result["novelty_score"]
                scores[i]["novelty"] = round(
                    0.5 * llm_novelty + 0.5 * embed_novelty, 4
                )
        except Exception:
            log.warning("Novelty scoring failed for candidate %d", i)

    # Compute overall score and rank
    for s in scores:
        s["overall"] = round(
            0.35 * s.get("novelty", 0.5)
            + 0.30 * s.get("coherence", 0.5)
            + 0.35 * s.get("usefulness", 0.5),
            4,
        )

    ranked = sorted(range(len(scores)), key=lambda i: scores[i].get("overall", 0), reverse=True)
    best_indices = ranked[:3]

    # Decision: synthesize or diverge again?
    best_score = scores[best_indices[0]]["overall"] if best_indices else 0
    if best_score >= 0.65:
        next_step = "synthesize"
    elif iteration >= max_iterations:
        next_step = "synthesize"
    else:
        next_step = "diverge"

    return {
        "scores": scores,
        "best_indices": best_indices,
        "next_step": next_step,
        "eval_notes": f"Best score: {best_score:.2f}, iteration {iteration}/{max_iterations}",
    }


def _parse_scores(content: str | None, expected: int) -> list[EvalScores]:
    if not content:
        return [{"novelty": 0.5, "coherence": 0.5, "usefulness": 0.5} for _ in range(expected)]

    text = content.strip()
    if text.startswith("```"):
        first_nl = text.find("\n")
        if first_nl != -1:
            text = text[first_nl:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            try:
                parsed = json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return [{"novelty": 0.5, "coherence": 0.5, "usefulness": 0.5} for _ in range(expected)]
        else:
            return [{"novelty": 0.5, "coherence": 0.5, "usefulness": 0.5} for _ in range(expected)]

    scores = []
    for item in parsed[:expected]:
        if isinstance(item, dict):
            scores.append(
                EvalScores(
                    novelty=float(item.get("novelty", 0.5)),
                    coherence=float(item.get("coherence", 0.5)),
                    usefulness=float(item.get("usefulness", 0.5)),
                )
            )
    while len(scores) < expected:
        scores.append(EvalScores(novelty=0.5, coherence=0.5, usefulness=0.5))
    return scores
