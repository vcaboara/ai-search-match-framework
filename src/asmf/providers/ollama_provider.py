"""Ollama AI provider implementation."""

import os
from typing import Optional, Dict, Any
import logging
import httpx

from .base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseAIProvider):
    """Ollama local AI provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize Ollama provider.

        Args:
            api_key: Not used for Ollama
            model: Model name (default: qwen2.5-coder:32b)
            base_url: Ollama base URL (default: http://localhost:11434)
        """
        self.base_url = base_url or os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
        self.model = model or "qwen2.5-coder:32b"
        self._available = False

        # Test connection
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            self._available = response.status_code == 200
            if self._available:
                logger.info(
                    f"Ollama provider initialized with model: {self.model}")
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")

    def analyze_text(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Analyze text with Ollama.

        Args:
            prompt: The prompt/question for Ollama
            context: Optional context dictionary

        Returns:
            AI response as string

        Raises:
            RuntimeError: If provider is not available
        """
        if not self.is_available():
            raise RuntimeError("Ollama provider is not available")

        try:
            # Add context to prompt if provided
            full_prompt = prompt
            if context:
                context_str = "\n\n".join(
                    f"{k}: {v}" for k, v in context.items()
                )
                full_prompt = f"{context_str}\n\n{prompt}"

            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model,
                      "prompt": full_prompt, "stream": False},
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama analysis failed: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Ollama is available.

        Returns:
            True if Ollama is running and accessible
        """
        return self._available
