"""AI Search Match Framework - Reusable AI-powered analysis components."""

__version__ = "0.1.0"

from .providers import (
    BaseAIProvider,
    GeminiProvider,
    OllamaProvider,
    AIProviderFactory,
)
from .parsers import (
    PDFPatentParser,
    PatentClaim,
    PatentDocument,
)

__all__ = [
    # Version
    "__version__",
    # Providers
    "BaseAIProvider",
    "GeminiProvider",
    "OllamaProvider",
    "AIProviderFactory",
    # Parsers
    "PDFPatentParser",
    "PatentClaim",
    "PatentDocument",
]
