"""Dual sync/async SQLAlchemy engines — adapted from CodexEngine patterns."""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ideaforge.config import get_settings

_sync_engine = None
_async_engine = None


def get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        settings = get_settings()
        _sync_engine = create_engine(settings.database_url)
    return _sync_engine


def get_async_engine() -> AsyncEngine:
    global _async_engine
    if _async_engine is None:
        settings = get_settings()
        _async_engine = create_async_engine(settings.async_database_url)
    return _async_engine
