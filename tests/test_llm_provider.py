"""Test LLM provider logic and retry behavior."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from openai import APIStatusError, RateLimitError

from ideaforge.llm.providers import OpenAICompatible, create_provider


@pytest.fixture
def mock_openai_client():
    with patch("ideaforge.llm.providers.AsyncOpenAI") as mock:
        client_instance = AsyncMock()
        mock.return_value = client_instance
        yield client_instance


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openai_compatible_success(mock_openai_client):
    provider = OpenAICompatible(api_key="test", base_url="http://test", model="test-model")
    
    # Mock successful response
    mock_choice = AsyncMock()
    mock_choice.message.content = "Success content"
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    
    mock_openai_client.chat.completions.create.return_value = mock_response
    
    result = await provider.complete([{"role": "user", "content": "hi"}])
    assert result.content == "Success content"
    assert mock_openai_client.chat.completions.create.call_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
@patch("ideaforge.llm.providers.asyncio.sleep")
async def test_openai_compatible_retry_on_rate_limit(mock_sleep, mock_openai_client):
    provider = OpenAICompatible(api_key="test", base_url="http://test", model="test-model")
    
    # Mock RateLimitError then success
    mock_choice = AsyncMock()
    mock_choice.message.content = "Success content after retry"
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    
    err = RateLimitError(
        message="Rate limit exceeded",
        response=httpx.Response(status_code=429, request=httpx.Request("POST", "http://test")),
        body=None
    )
    
    mock_openai_client.chat.completions.create.side_effect = [err, mock_response]
    
    result = await provider.complete([{"role": "user", "content": "hi"}])
    assert result.content == "Success content after retry"
    assert mock_openai_client.chat.completions.create.call_count == 2
    assert mock_sleep.call_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
@patch("ideaforge.llm.providers.asyncio.sleep")
async def test_openai_compatible_retry_on_500(mock_sleep, mock_openai_client):
    provider = OpenAICompatible(api_key="test", base_url="http://test", model="test-model")
    
    mock_choice = AsyncMock()
    mock_choice.message.content = "Success content after 500"
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    
    err = APIStatusError(
        message="Internal Server Error",
        response=httpx.Response(status_code=502, request=httpx.Request("POST", "http://test")),
        body=None
    )
    
    mock_openai_client.chat.completions.create.side_effect = [err, mock_response]
    
    result = await provider.complete([{"role": "user", "content": "hi"}])
    assert result.content == "Success content after 500"
    assert mock_openai_client.chat.completions.create.call_count == 2
    assert mock_sleep.call_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openai_compatible_no_retry_on_400(mock_openai_client):
    provider = OpenAICompatible(api_key="test", base_url="http://test", model="test-model")
    
    err = APIStatusError(
        message="Bad Request",
        response=httpx.Response(status_code=400, request=httpx.Request("POST", "http://test")),
        body=None
    )
    
    mock_openai_client.chat.completions.create.side_effect = err
    
    with pytest.raises(APIStatusError):
        await provider.complete([{"role": "user", "content": "hi"}])
    
    assert mock_openai_client.chat.completions.create.call_count == 1


@pytest.mark.unit
def test_create_provider():
    # Test fallback behavior when provider doesn't match
    provider = create_provider(provider="unknown", model="test-model")
    assert isinstance(provider, OpenAICompatible)
    assert provider.model == "test-model"
