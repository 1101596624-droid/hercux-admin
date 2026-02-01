# ============================================
# HERCU Studio - LLM Provider Base Interface
# ============================================

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, AsyncGenerator


@dataclass
class GenerationResult:
    """Result from LLM generation"""
    content: str
    input_tokens: int
    output_tokens: int
    model: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 200000,
        temperature: float = 0.7
    ) -> GenerationResult:
        """Generate content from prompt

        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            GenerationResult with content and token usage
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name being used"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name (e.g., 'anthropic', 'openai')"""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 200000,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Stream content generation from prompt

        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Yields:
            Text chunks as they are generated
        """
        pass
