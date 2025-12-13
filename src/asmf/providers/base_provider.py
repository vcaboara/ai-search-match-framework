"""Base AI provider interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseAIProvider(ABC):
    """Base class for AI providers (Gemini, Ollama)."""

    @abstractmethod
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the provider."""
        pass

    @abstractmethod
    def analyze_text(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Analyze text with AI model.

        Args:
            prompt: The prompt/question for the AI
            context: Optional context dictionary with additional information

        Returns:
            AI response as string
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and configured.

        Returns:
            True if provider can be used, False otherwise
        """
        pass
