"""Base AI provider interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseAIProvider(ABC):
    """Base class for AI providers (Gemini, Ollama)."""

    def __init__(self, **kwargs):
        """Initialize the provider.

        Args:
            **kwargs: Provider-specific configuration options
        """
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

    def _format_prompt_with_context(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format prompt with context dictionary.

        Args:
            prompt: The base prompt text
            context: Optional context dictionary to prepend

        Returns:
            Formatted prompt string with context prepended
        """
        if not context:
            return prompt

        context_str = "\n\n".join(
            f"{k}: {v}" for k, v in context.items()
        )
        return f"{context_str}\n\n{prompt}"
