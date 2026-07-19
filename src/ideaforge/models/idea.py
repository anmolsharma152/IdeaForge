"""Pydantic models for IdeaForge domain objects."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field


class Idea(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    body: str
    workflow: str = "general"
    scores: dict[str, Any] = Field(default_factory=dict)
    parent_ids: list[uuid.UUID] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    created_at: int | None = None
    updated_at: int | None = None


class Evaluation(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    idea_id: uuid.UUID
    rubric: str = "default"
    scores: dict[str, Any] = Field(default_factory=dict)
    judge_notes: str = ""
    model: str = ""
    created_at: int | None = None


class Connection(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    from_id: uuid.UUID
    to_id: uuid.UUID
    relation: str = "related"
    created_at: int | None = None


class Session(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow: str
    goal: str
    idea_ids: list[uuid.UUID] = Field(default_factory=list)
    created_at: int | None = None


class Provenance(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    idea_id: uuid.UUID
    sources: list[dict[str, Any]] = Field(default_factory=list)
    prompts: list[str] = Field(default_factory=list)
    tool_trace: list[dict[str, Any]] = Field(default_factory=list)
    created_at: int | None = None


class IdeaWithScore(BaseModel):
    """Idea with its novelty score from similarity search."""

    idea: Idea
    similarity: float
