"""LangGraph state for IdeaForge's dual-process loop."""

from __future__ import annotations

from typing import Annotated, Literal

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class IdeaCandidate(TypedDict):
    title: str
    body: str
    tags: list[str]


class EvalScores(TypedDict, total=False):
    novelty: float
    coherence: float
    usefulness: float
    overall: float


class AgentState(TypedDict, total=False):
    # Intake
    goal: str
    workflow: str
    context: str

    # Diverge
    candidates: list[IdeaCandidate]
    muse_count: int

    # Evaluate
    scores: list[EvalScores]
    best_indices: list[int]
    eval_notes: str
    next_step: Literal["diverge", "synthesize", "stop"]

    # Synthesize
    refined: IdeaCandidate
    messages: Annotated[list, add_messages]

    # Persist
    idea_ids: list[str]

    # Control
    iteration: int
    max_iterations: int
