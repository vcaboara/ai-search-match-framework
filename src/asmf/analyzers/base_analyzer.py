"""Base analyzer for AI-powered analysis workflows."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..providers.base_provider import BaseAIProvider


class BaseAnalyzer(ABC):
    """
    Base class for implementing AI-powered analyzers.
    
    Analyzers combine AI providers with domain-specific logic to perform
    structured analysis tasks (e.g., patent evaluation, grant matching).
    
    Example:
        class PatentAnalyzer(BaseAnalyzer):
            def analyze(self, patent_text: str) -> Dict[str, Any]:
                prompt = f"Analyze this patent: {patent_text}"
                response = self.provider.analyze_text(prompt)
                return {"score": 0.8, "summary": response}
    """

    def __init__(self, provider: BaseAIProvider) -> None:
        """
        Initialize analyzer with AI provider.
        
        Args:
            provider: AI provider instance for analysis
        """
        self.provider = provider

    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Perform analysis on input data.
        
        Args:
            data: Input data to analyze (type varies by implementation)
            
        Returns:
            Dictionary containing analysis results with structure
            determined by concrete implementation
        """
        pass

    def batch_analyze(self, items: list[Any]) -> list[Dict[str, Any]]:
        """
        Analyze multiple items sequentially.
        
        Args:
            items: List of items to analyze
            
        Returns:
            List of analysis results in same order as input
        """
        return [self.analyze(item) for item in items]

    def validate_input(self, data: Any) -> bool:
        """
        Validate input data before analysis.
        
        Override this method to add domain-specific validation.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return data is not None
