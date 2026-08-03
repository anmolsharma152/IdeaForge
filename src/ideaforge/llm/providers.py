"""LLM provider abstraction — OpenAI-compatible with retry.

Adapted from CodexEngine's provider pattern.
Works with Groq, OpenAI, Together, and any OpenAI-compatible API.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from openai import APIStatusError, AsyncOpenAI, RateLimitError

from ideaforge.config import get_settings

log = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_DELAY = 2.0  # seconds


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str


@dataclass
class LLMResult:
    content: str | None = None
    tool_calls: list[ToolCall] | None = None


class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResult: ...


class OpenAICompatible(LLMProvider):
    """Works with any OpenAI-compatible API (Groq, OpenAI, Together)."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.model = model
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResult:
        last_err = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                choice = response.choices[0]
                return LLMResult(content=choice.message.content or "")
            except RateLimitError as e:
                last_err = e
                delay = BASE_DELAY * (2 ** attempt)
                log.warning(
                    "Rate limited (attempt %d/%d), retrying in %.1fs",
                    attempt + 1, MAX_RETRIES, delay,
                )
                await asyncio.sleep(delay)
            except APIStatusError as e:
                if e.status_code >= 500:
                    last_err = e
                    delay = BASE_DELAY * (2 ** attempt)
                    log.warning(
                        "Server error %d (attempt %d/%d), retrying in %.1fs",
                        e.status_code, attempt + 1, MAX_RETRIES, delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    raise
        raise last_err  # type: ignore[misc]


_PROVIDER_CONFIGS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_attr": "groq_api_key",
        "default_model": "llama-3.3-70b-versatile",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "key_attr": "openai_api_key",
        "default_model": "gpt-4o",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_attr": "gemini_api_key",
        "default_model": "gemini-2.5-flash",
    },
}


def create_provider(provider: str | None = None, model: str | None = None) -> LLMProvider:
    settings = get_settings()
    provider = provider or settings.llm_provider
    model = model or settings.llm_model

    config = _PROVIDER_CONFIGS.get(provider)
    if config:
        api_key = getattr(settings, config["key_attr"])
        base_url = config["base_url"]
        if not model:
            model = config["default_model"]
    else:
        # Fallback: treat as OpenAI-compatible with Groq settings
        api_key = settings.groq_api_key
        base_url = "https://api.groq.com/openai/v1"
        model = model or "llama-3.3-70b-versatile"

    if not api_key or not api_key.strip():
        raise ValueError(
            f"API key for LLM provider '{provider}' is missing or empty. "
            f"Please set the corresponding environment variable (e.g. GROQ_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY) or define it in .env."
        )

    return OpenAICompatible(api_key=api_key, base_url=base_url, model=model)
