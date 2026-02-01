# ============================================
# HERCU Studio - Anthropic Provider
# ============================================

import os
from typing import AsyncGenerator
import httpx
from anthropic import Anthropic
from .base import LLMProvider, GenerationResult


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic Claude API"""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        # 设置更长的超时时间 (10分钟)
        timeout = httpx.Timeout(600.0, connect=60.0)

        base_url = os.getenv("ANTHROPIC_BASE_URL")
        if base_url:
            self.client = Anthropic(api_key=api_key, base_url=base_url, timeout=timeout)
        else:
            self.client = Anthropic(api_key=api_key, timeout=timeout)

        self.model = os.getenv("API_MODEL", "claude-sonnet-4-20250514")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 200000,
        temperature: float = 0.7
    ) -> GenerationResult:
        """Generate content using Anthropic Claude API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        return GenerationResult(
            content=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=self.model
        )

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "anthropic"

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 200000,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Stream content using Anthropic Claude API"""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                yield text
