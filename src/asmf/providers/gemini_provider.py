"""Gemini AI provider implementation."""

import os
from typing import Optional, Dict, Any
import logging

try:
    import google.generativeai as genai
except ImportError:
    genai = None

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
        super().__init__(api_key=api_key, model=model)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or "gemini-1.5-pro"
        self._client = None

        if genai is None:
            logger.error("google-generativeai package not installed")
            return

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
                logger.info(
                    f"Gemini provider initialized with model: {self.model}")
            except Exception as e:
                logger.exception(f"Failed to initialize Gemini: {e}")
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

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            # Use base class helper to format prompt with context
            full_prompt = self._format_prompt_with_context(prompt, context)

            response = self._client.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.exception(f"Gemini analysis failed: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Gemini is available.

        Returns:
            True if configured and ready
        """
        return self._client is not None
