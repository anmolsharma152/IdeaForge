"""Test configuration loading and parsing."""

import pytest

from ideaforge.config import Settings, get_settings


@pytest.mark.unit
def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    
    settings = Settings(_env_file=None)
    assert settings.llm_provider == "groq"
    assert settings.llm_model == "llama-3.3-70b-versatile"
    assert settings.embedding_provider == "fastembed"
    assert settings.embedding_model == "BAAI/bge-small-en-v1.5"


@pytest.mark.unit
def test_async_database_url():
    settings = Settings(database_url="postgresql+psycopg://user:pass@localhost:5432/db")
    assert settings.async_database_url == "postgresql+asyncpg://user:pass@localhost:5432/db"

    # Testing that it doesn't break if already using asyncpg
    settings = Settings(database_url="postgresql+asyncpg://user:pass@localhost:5432/db")
    assert settings.async_database_url == "postgresql+asyncpg://user:pass@localhost:5432/db"


@pytest.mark.unit
def test_env_var_override(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("GROQ_API_KEY", "test-key-123")
    
    settings = Settings(_env_file=None)
    assert settings.llm_provider == "openai"
    assert settings.groq_api_key == "test-key-123"


@pytest.mark.unit
def test_get_settings_singleton(monkeypatch):
    # Ensure get_settings returns the same instance
    import ideaforge.config
    ideaforge.config._settings = None
    
    settings_1 = get_settings()
    settings_2 = get_settings()
    
    assert settings_1 is settings_2
