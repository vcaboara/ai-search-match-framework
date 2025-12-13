"""Gemini AI provider implementation."""

import os
from typing import Optional, Dict, Any
import logging

from .base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider."""

    def __init__(
        self, api_key: Optional[str] = None, model: Optional[str] = None
    ):
        """Initialize Gemini provider.

        Args:
            api_key: Gemini API key (or uses GEMINI_API_KEY env var)
            model: Model name (default: gemini-1.5-pro)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or "gemini-1.5-pro"
        self._client = None

        if self.api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
                logger.info(
                    f"Gemini provider initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self._client = None

    def analyze_text(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Analyze text with Gemini.

        Args:
            prompt: The prompt/question for Gemini
            context: Optional context dictionary

        Returns:
            AI response as string

        Raises:
            RuntimeError: If provider is not available
        """
        if not self.is_available():
            raise RuntimeError("Gemini provider is not available")

        try:
            # Add context to prompt if provided
            full_prompt = prompt
            if context:
                context_str = "\n\n".join(
                    f"{k}: {v}" for k, v in context.items()
                )
                full_prompt = f"{context_str}\n\n{prompt}"

            response = self._client.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Gemini is available.

        Returns:
            True if configured and ready
        """
        return self._client is not None
