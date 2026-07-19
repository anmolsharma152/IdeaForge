"""Persist node — store refined idea + evaluations to DB, auto-link related."""

import logging

from ideaforge.memory.store import auto_connect, create_idea
from ideaforge.models.state import AgentState

log = logging.getLogger(__name__)


async def persist_node(state: AgentState) -> dict:
    refined = state.get("refined")
    if not refined or not refined.get("title"):
        return {"idea_ids": []}

    scores = state.get("scores", [])
    best_indices = state.get("best_indices", [])
    overall_score = {}
    if scores and best_indices:
        best_score = scores[best_indices[0]]
        overall_score = best_score

    idea = await create_idea(
        title=refined["title"],
        body=refined["body"],
        workflow=state.get("workflow", "general"),
        tags=refined.get("tags", []),
        scores=overall_score,
    )

    try:
        connections = await auto_connect(
            idea.id,
            workflow=state.get("workflow"),
            similarity_threshold=0.5,
            max_connections=3,
        )
        if connections:
            log.info("Auto-connected idea to %d related ideas", len(connections))
    except Exception:
        log.warning("Auto-connect failed, idea still persisted")

    return {
        "idea_ids": [str(idea.id)],
    }
