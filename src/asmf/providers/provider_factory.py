"""AI provider factory with fallback support."""

import logging
import os

from .base_provider import BaseAIProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)


class AIProviderFactory:
    """Factory for creating AI providers with fallback chain."""

    @staticmethod
    def create_provider(prefer_local: bool = False) -> BaseAIProvider:
        """Create an AI provider with automatic fallback.

        This factory tries to initialize providers in order of preference and returns
        the first available one. It supports seamless fallback between local (Ollama)
        and cloud (Gemini) providers.

        Args:
            prefer_local: If True, try Ollama first, then fallback to Gemini (default: False)
                         If False, try Gemini first, then fallback to Ollama

        Returns:
            First available AI provider instance

        Raises:
            RuntimeError: If no providers are available with helpful setup instructions

        Examples:
            >>> # Local-first (privacy, cost-free, requires Ollama setup)
            >>> provider = AIProviderFactory.create_provider(prefer_local=True)
            
            >>> # Cloud-first (default, requires GEMINI_API_KEY)
            >>> provider = AIProviderFactory.create_provider()
            
            >>> # Check which provider was selected
            >>> print(f"Using: {provider.__class__.__name__}")
        """
        # Determine provider order based on preference
        provider_classes = (
            [OllamaProvider, GeminiProvider]
            if prefer_local
            else [GeminiProvider, OllamaProvider]
        )

        tried_providers = []
        errors = {}

        for provider_cls in provider_classes:
            # Get provider name safely (works with both real classes and mocks)
            provider_name = getattr(provider_cls, '__name__', provider_cls.__class__.__name__)
            tried_providers.append(provider_name)
            
            try:
                provider = provider_cls()
                if provider.is_available():
                    logger.info(f"✓ Using AI provider: {provider_name}")
                    return provider
                else:
                    error_msg = f"{provider_name} instantiated but not available"
                    logger.warning(f"✗ {error_msg}")
                    errors[provider_name] = error_msg
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"✗ Failed to initialize {provider_name}: {error_msg}")
                errors[provider_name] = error_msg
                continue

        # Build helpful error message with setup instructions
        error_lines = [
            f"No AI providers available. Tried: {', '.join(tried_providers)}",
            "",
            "Setup Instructions:",
        ]

        if "OllamaProvider" in errors:
            error_lines.extend([
                "",
                "For Ollama (local, free, private):",
                "  1. Install: https://ollama.ai/download",
                "  2. Pull model: ollama pull qwen2.5:14b-q4",
                "  3. Or run: python scripts/setup_ollama.py",
                f"  Error: {errors['OllamaProvider']}",
            ])

        if "GeminiProvider" in errors:
            error_lines.extend([
                "",
                "For Gemini (cloud, requires API key):",
                "  1. Get API key: https://makersuite.google.com/app/apikey",
                "  2. Set: export GEMINI_API_KEY=your-key",
                "  3. Or add to .env: GEMINI_API_KEY=your-key",
                f"  Error: {errors['GeminiProvider']}",
            ])

        error_lines.extend([
            "",
            "See docs/OLLAMA_SETUP.md for detailed setup guide.",
        ])

        raise RuntimeError("\n".join(error_lines))

