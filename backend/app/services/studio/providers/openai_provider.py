# ============================================
# HERCU Studio - OpenAI Compatible Provider
# Supports: OpenAI, DeepSeek, third-party proxies
# ============================================

import os
from typing import AsyncGenerator
from openai import OpenAI
from .base import LLMProvider, GenerationResult


class OpenAICompatibleProvider(LLMProvider):
    """Provider for OpenAI-compatible APIs (DeepSeek, proxies, etc.)"""

    def __init__(self):
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API_KEY environment variable is required for OpenAI-compatible provider")

        base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = os.getenv("API_MODEL", "gpt-4")
        self.base_url = base_url

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 200000,
        temperature: float = 0.7
    ) -> GenerationResult:
        """Generate content using OpenAI-compatible API"""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        return GenerationResult(
            content=response.choices[0].message.content,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
            model=self.model
        )

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        # Detect provider from base URL
        if "deepseek" in self.base_url.lower():
            return "deepseek"
        elif "openai" in self.base_url.lower():
            return "openai"
        else:
            return "proxy"

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 200000,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Stream content using OpenAI-compatible API"""
        stream = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
