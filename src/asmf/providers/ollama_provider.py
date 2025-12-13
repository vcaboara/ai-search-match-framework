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
        timeout: Optional[float] = None,
    ):
        """Initialize Ollama provider.

        Args:
            api_key: Not used for Ollama
            model: Model name (default: qwen2.5-coder:32b)
            base_url: Ollama base URL (default: http://localhost:11434)
            timeout: Connection timeout in seconds (default: 5.0, configurable via OLLAMA_TIMEOUT env var)
        """
        super().__init__(api_key=api_key, model=model, base_url=base_url, timeout=timeout)
        self.base_url = base_url or os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
        self.model = model or "qwen2.5-coder:32b"
        self.timeout = timeout or float(os.getenv("OLLAMA_TIMEOUT", "5.0"))
        self._available = False

        # Test connection
        try:
            response = httpx.get(
                f"{self.base_url}/api/tags", timeout=self.timeout)
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

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            # Use base class helper to format prompt with context
            full_prompt = self._format_prompt_with_context(prompt, context)

            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model,
                      "prompt": full_prompt, "stream": False},
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.exception(f"Ollama analysis failed: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Ollama is available.

        Returns:
            True if Ollama is running and accessible
        """
        return self._available
