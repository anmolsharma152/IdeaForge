"""Diverge node — call muses to generate diverse idea candidates."""

import json
import logging
from concurrent.futures import ThreadPoolExecutor

from ideaforge.llm.providers import create_provider
from ideaforge.memory.sources import format_search_context, web_search
from ideaforge.models.state import AgentState, IdeaCandidate

log = logging.getLogger(__name__)

MUSE_PROMPT = """You are a creative muse. Your job is to generate novel, non-obvious ideas.

CONTEXT:
{context}

TASK: Generate {count} diverse, creative ideas that address the goal above.

Requirements:
- Each idea should be genuinely novel, not a restatement of the obvious
- Include at least one unconventional or contrarian angle
- Be specific and actionable, not vague platitudes
- Tags should be 2-3 words each describing the idea's domain

Output ONLY valid JSON array with this shape:
[
  {{"title": "short title", "body": "2-3 sentence description", "tags": ["tag1", "tag2"]}},
  ...
]

Generate exactly {count} ideas. No explanation, no markdown, just the JSON array."""


async def diverge_node(state: AgentState) -> dict:
    provider = create_provider()
    count = state.get("muse_count", 5)
    iteration = state.get("iteration", 0) + 1

    existing_titles = [c["title"] for c in state.get("candidates", [])]

    # On first iteration, search the web for grounding context
    search_context = ""
    if iteration == 1:
        goal = state.get("goal", "")
        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                results = pool.submit(web_search, goal).result(timeout=10)
            search_context = format_search_context(results)
        except Exception:
            log.warning("Web search timed out or failed")

    context = state.get("context", "")
    if search_context:
        context = f"{context}\n\n{search_context}"

    prompt = MUSE_PROMPT.format(context=context, count=count)
    if existing_titles:
        prompt += f"\n\nAVOID these ideas already generated: {', '.join(existing_titles)}"

    try:
        result = await provider.complete(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=2048,
        )
        candidates = _parse_candidates(result.content, count)
    except Exception:
        log.exception("Diverge LLM call failed")
        candidates = []

    if not candidates:
        log.warning("No candidates generated, stopping")
        return {
            "candidates": [],
            "iteration": iteration,
            "next_step": "stop",
        }

    return {
        "candidates": candidates,
        "iteration": iteration,
        "next_step": "evaluate",
    }


def _parse_candidates(content: str | None, expected: int) -> list[IdeaCandidate]:
    if not content:
        return []

    # Strip markdown code fences if present
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
        # Try to find JSON array in the response
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            try:
                parsed = json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return []
        else:
            return []

    candidates = []
    for item in parsed[:expected]:
        if isinstance(item, dict) and "title" in item and "body" in item:
            candidates.append(
                IdeaCandidate(
                    title=item["title"],
                    body=item["body"],
                    tags=item.get("tags", []),
                )
            )
    return candidates
