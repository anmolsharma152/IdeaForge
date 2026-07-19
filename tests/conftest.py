"""Shared test fixtures."""

import os
import pytest


@pytest.fixture(autouse=True)
def _test_env(monkeypatch):
    """Set test-safe env vars so Settings never reads a real .env."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://anmol@localhost:5432/ideaforge_test")
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_MODEL", "llama-3.1-8b-instant")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")


@pytest.fixture()
def db_url():
    return os.environ["DATABASE_URL"]
