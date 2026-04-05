import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.config import settings


@pytest.mark.asyncio
async def test_nanobot_config():
    """Test nanobot configuration is properly loaded"""
    assert settings.MISTRAL_BASE_URL is not None
    assert settings.MISTRAL_MODEL is not None
    assert settings.NANOBOT_ACCESS_KEY is not None
    assert len(settings.NANOBOT_ACCESS_KEY) > 10


@pytest.mark.asyncio
async def test_mistral_api_url():
    """Test Mistral API URL is correctly configured"""
    assert "mistral.ai" in settings.MISTRAL_BASE_URL
    assert settings.MISTRAL_BASE_URL.endswith("/v1")


@pytest.mark.asyncio
async def test_model_configuration():
    """Test model configuration"""
    valid_models = [
        "mistral-small-latest",
        "mistral-medium-latest",
        "mistral-large-latest"
    ]
    assert settings.MISTRAL_MODEL in valid_models


@pytest.mark.asyncio
async def test_llm_client_initialization():
    """Test LLM client can be initialized"""
    from app.llm_client import LLMClient
    client = LLMClient()
    assert client.client is not None
    assert client.client.api_key == settings.MISTRAL_API_KEY
