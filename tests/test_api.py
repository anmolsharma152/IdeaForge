"""Test FastAPI endpoints for IdeaForge Web App."""

import pytest
from fastapi.testclient import TestClient

from ideaforge.api import app
from ideaforge.db.schema import ensure_schema


@pytest.fixture(autouse=True)
def setup_test_db():
    ensure_schema()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.unit
def test_get_workflows_api(client):
    res = client.get("/api/workflows")
    assert res.status_code == 200
    data = res.json()
    assert "workflows" in data
    assert len(data["workflows"]) >= 3


@pytest.mark.unit
def test_get_ideas_api(client):
    res = client.get("/api/ideas")
    assert res.status_code == 200
    data = res.json()
    assert "ideas" in data


@pytest.mark.unit
def test_get_metrics_api(client):
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "total_sessions" in data
    assert "total_ideas" in data
    assert "avg_novelty" in data


@pytest.mark.unit
def test_search_ideas_api(client):
    res = client.get("/api/ideas/search?query=test")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
