"""Shared test fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def _test_env(monkeypatch):
    """Set test-safe env vars so Settings never reads a real .env.

    Respects DATABASE_URL if already set (e.g. in CI).
    """
    if "DATABASE_URL" not in os.environ:
        monkeypatch.setenv(
            "DATABASE_URL", "postgresql+psycopg://anmol@localhost:5432/ideaforge_test"
        )
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_MODEL", "llama-3.1-8b-instant")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    
    # Reset engines to avoid event loop reuse issues in tests
    import ideaforge.db.engine
    ideaforge.db.engine._async_engine = None
    ideaforge.db.engine._sync_engine = None


@pytest.fixture()
def db_url():
    return os.environ["DATABASE_URL"]


@pytest.fixture()
def fake_embedder(monkeypatch):
    class FakeEmbedProvider:
        def embed_query(self, text: str) -> list[float]:
            return [0.1] * 384

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [[0.1] * 384 for _ in texts]
            
    provider = FakeEmbedProvider()
    monkeypatch.setattr("ideaforge.memory.embeddings.get_embedding_provider", lambda: provider)
    return provider


@pytest.fixture()
def mock_llm():
    from ideaforge.llm.providers import LLMProvider, LLMResult

    class MockLLM(LLMProvider):
        def __init__(self):
            self.responses = []
            
        async def complete(
            self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 4096
        ) -> LLMResult:
            if self.responses:
                return LLMResult(content=self.responses.pop(0))
            return LLMResult(content="Mock response")
    
    return MockLLM()


@pytest.fixture()
def agent_state_factory():
    def _create_state(**kwargs) -> dict:
        state = {
            "goal": "Test goal",
            "workflow": "research",
            "context": "Test context",
            "candidates": [],
            "muse_count": 3,
            "scores": [],
            "best_indices": [],
            "eval_notes": "",
            "next_step": "diverge",
            "refined": {"title": "", "body": "", "tags": []},
            "messages": [],
            "idea_ids": [],
            "iteration": 1,
            "max_iterations": 3,
        }
        state.update(kwargs)
        return state
    return _create_state
