# ============================================
# HERCU Studio - Provider Factory
# ============================================

import os
from .base import LLMProvider
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAICompatibleProvider


def create_provider() -> LLMProvider:
    """Create LLM provider based on environment variables

    Environment Variables:
        API_PROVIDER: Provider type (anthropic, openai, deepseek, proxy)

    For Anthropic:
        ANTHROPIC_API_KEY: Anthropic API key
        API_MODEL: Model name (default: claude-sonnet-4-20250514)

    For OpenAI-compatible (DeepSeek, proxies):
        API_KEY: API key
        API_BASE_URL: Base URL (default: https://api.openai.com/v1)
        API_MODEL: Model name (default: gpt-4)

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider type is unknown or required env vars are missing
    """
    provider_type = os.getenv("API_PROVIDER", "anthropic").lower()

    if provider_type == "anthropic":
        return AnthropicProvider()
    elif provider_type in ("openai", "deepseek", "proxy"):
        return OpenAICompatibleProvider()
    else:
        raise ValueError(
            f"Unknown provider: {provider_type}. "
            f"Supported providers: anthropic, openai, deepseek, proxy"
        )


def get_provider_info() -> dict:
    """Get information about the current provider configuration

    Returns:
        Dict with provider info (type, model, base_url if applicable)
    """
    provider_type = os.getenv("API_PROVIDER", "anthropic").lower()
    model = os.getenv("API_MODEL", "claude-sonnet-4-20250514" if provider_type == "anthropic" else "gpt-4")

    info = {
        "provider": provider_type,
        "model": model,
    }

    if provider_type != "anthropic":
        info["base_url"] = os.getenv("API_BASE_URL", "https://api.openai.com/v1")

    return info
