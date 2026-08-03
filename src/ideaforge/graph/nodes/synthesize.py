"""Synthesize node — merge top candidates into a refined concept."""

import json
import logging

from ideaforge.llm.providers import create_provider
from ideaforge.models.state import AgentState, IdeaCandidate

log = logging.getLogger(__name__)

SYNTHESIZE_PROMPT = """You are a creative synthesizer. Merge the best elements of these top candidates into a single, refined idea.

GOAL: {goal}

TOP CANDIDATES (ranked by overall score):
{candidates_text}

TASK: Create ONE refined idea that:
1. Takes the strongest elements from the top candidates
2. Resolves any contradictions between them
3. Is more novel and useful than any single candidate alone
4. Is specific and actionable

Output ONLY valid JSON with this shape:
{{"title": "refined title", "body": "2-3 sentence refined description", "tags": ["tag1", "tag2"]}}

No explanation, no markdown, just the JSON object."""


async def synthesize_node(state: AgentState) -> dict:
    candidates = state.get("candidates", [])
    best_indices = state.get("best_indices", [])
    goal = state.get("goal", "")

    if not candidates or not best_indices:
        return {
            "refined": IdeaCandidate(
                title="No candidates", body="No candidates to synthesize.", tags=[]
            ),
        }

    from ideaforge.utils.security import sanitize_prompt_input

    provider = create_provider()
    goal_clean = sanitize_prompt_input(goal, max_length=500)
    best_text = "\n\n".join(
        f"[Rank {rank+1}] {sanitize_prompt_input(candidates[idx]['title'], 100)}: {sanitize_prompt_input(candidates[idx]['body'], 500)}"
        for rank, idx in enumerate(best_indices)
        if idx < len(candidates)
    )

    try:
        result = await provider.complete(
            messages=[
                {
                    "role": "user",
                    "content": SYNTHESIZE_PROMPT.format(
                        goal=goal_clean, candidates_text=best_text
                    ),
                }
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        refined = _parse_refined(result.content)
    except Exception:
        log.exception("Synthesize LLM call failed, using best candidate")
        best_idx = best_indices[0]
        if best_idx < len(candidates):
            c = candidates[best_idx]
            refined = IdeaCandidate(title=c["title"], body=c["body"], tags=c.get("tags", []))
        else:
            refined = IdeaCandidate(title="Synthesis failed", body="", tags=[])

    return {"refined": refined}


def _parse_refined(content: str | None) -> IdeaCandidate:
    if not content:
        return IdeaCandidate(title="Synthesis failed", body="Could not parse synthesis.", tags=[])

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
        return IdeaCandidate(title="Synthesis failed", body=text[:200], tags=[])

    return IdeaCandidate(
        title=parsed.get("title", "Untitled"),
        body=parsed.get("body", ""),
        tags=parsed.get("tags", []),
    )
