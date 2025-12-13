"""AI provider factory with fallback support."""

import logging
from typing import Optional

from .base_provider import BaseAIProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)


class AIProviderFactory:
    """Factory for creating AI providers with fallback chain."""

    @staticmethod
    def create_provider(prefer_local: bool = False) -> BaseAIProvider:
        """Create an AI provider with fallback.

        Args:
            prefer_local: If True, try Ollama first, then Gemini

        Returns:
            First available AI provider

        Raises:
            RuntimeError: If no providers are available
        """
        providers = (
            [OllamaProvider(), GeminiProvider()]
            if prefer_local
            else [GeminiProvider(), OllamaProvider()]
        )

        for provider in providers:
            if provider.is_available():
                logger.info(
                    f"Using AI provider: {provider.__class__.__name__}")
                return provider

        raise RuntimeError(
            "No AI providers available. "
            "Please configure GEMINI_API_KEY or start Ollama."
        )
