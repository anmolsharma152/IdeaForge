"""FastAPI REST API server for IdeaForge Web UI."""

import uuid as _uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import ideaforge.workflows  # noqa: F401
from ideaforge.db.schema import ensure_schema
from ideaforge.graph.build import build_graph
from ideaforge.memory.store import (
    create_session,
    get_connections,
    list_ideas,
    list_sessions,
    search_similar,
)
from ideaforge.utils.security import sanitize_prompt_input
from ideaforge.workflows.base import get_workflow, list_workflows


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_schema()
    yield


app = FastAPI(
    title="IdeaForge API",
    description="REST API for IdeaForge Creative Synthesis Engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    goal: str = Field(..., max_length=1000, description="Creative goal or prompt")
    workflow: str = Field("general", description="Workflow template key")
    muses: int = Field(5, ge=1, le=10, description="Number of muses")
    rounds: int = Field(3, ge=1, le=5, description="Max iteration rounds")


@app.get("/api/workflows")
def get_workflows_api():
    """List available workflow templates."""
    workflows = []
    for key in list_workflows():
        wf = get_workflow(key)
        if wf:
            workflows.append({"key": key, "name": wf.name, "description": wf.description})
    return {"workflows": workflows}


@app.post("/api/run")
async def run_workflow_api(req: RunRequest):
    """Run an autonomous ideation synthesis graph."""
    clean_goal = sanitize_prompt_input(req.goal, max_length=1000)
    if not clean_goal:
        raise HTTPException(status_code=400, detail="Invalid or empty creative goal.")

    graph = build_graph()
    initial_state = {
        "goal": clean_goal,
        "workflow": req.workflow,
        "muse_count": req.muses,
        "max_iterations": req.rounds,
    }

    try:
        final_state = await graph.ainvoke(initial_state)
        idea_ids = [_uuid.UUID(i) for i in final_state.get("idea_ids", [])]
        await create_session(workflow=req.workflow, goal=clean_goal, idea_ids=idea_ids)

        return {
            "status": "success",
            "refined": final_state.get("refined"),
            "idea_ids": final_state.get("idea_ids", []),
            "eval_notes": final_state.get("eval_notes", ""),
            "candidates": final_state.get("candidates", []),
            "scores": final_state.get("scores", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ideas")
async def list_ideas_api(
    workflow: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """List stored ideas from Postgres."""
    try:
        ideas = await list_ideas(workflow=workflow, limit=limit)
        return {
            "ideas": [
                {
                    "id": str(i.id),
                    "title": i.title,
                    "body": i.body,
                    "workflow": i.workflow,
                    "scores": i.scores,
                    "tags": i.tags,
                    "created_at": i.created_at,
                }
                for i in ideas
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ideas/search")
async def search_ideas_api(
    query: str = Query(...),
    workflow: str | None = Query(None),
    limit: int = Query(5, ge=1, le=20),
):
    """Vector similarity search via pgvector."""
    clean_query = sanitize_prompt_input(query, max_length=500)
    if not clean_query:
        return {"results": []}

    try:
        results = await search_similar(query=clean_query, limit=limit, workflow=workflow)
        return {
            "results": [
                {
                    "similarity": round(r.similarity, 4),
                    "idea": {
                        "id": str(r.idea.id),
                        "title": r.idea.title,
                        "body": r.idea.body,
                        "workflow": r.idea.workflow,
                        "scores": r.idea.scores,
                        "tags": r.idea.tags,
                        "created_at": r.idea.created_at,
                    },
                }
                for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/connections/{idea_id}")
async def get_connections_api(idea_id: str):
    """Get bidirectional connections for an idea."""
    try:
        uid = _uuid.UUID(idea_id)
        conns = await get_connections(uid)
        return {
            "connections": [
                {
                    "id": str(c["id"]),
                    "from_id": str(c["from_id"]),
                    "to_id": str(c["to_id"]),
                    "relation": c["relation"],
                    "created_at": c["created_at"],
                    "linked_title": c["linked_title"],
                    "linked_workflow": c["linked_workflow"],
                }
                for c in conns
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/metrics")
async def metrics_api():
    """Get overall analytics and compounding memory metrics."""
    try:
        sessions = await list_sessions(limit=100)
        ideas = await list_ideas(limit=100)

        wf_counts = {}
        for i in ideas:
            wf_counts[i.workflow] = wf_counts.get(i.workflow, 0) + 1

        novelties = [i.scores.get("novelty", 0.5) for i in ideas if isinstance(i.scores, dict)]
        avg_novelty = round(sum(novelties) / len(novelties), 3) if novelties else 0.0

        return {
            "total_sessions": len(sessions),
            "total_ideas": len(ideas),
            "avg_novelty": avg_novelty,
            "workflow_counts": wf_counts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Static Assets Setup
WEB_DIR = Path(__file__).parent / "web"
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="static")
