"""AI Search Match Framework - Reusable AI-powered analysis components."""

__version__ = "0.2.0"

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
from .domain import (
    DomainConfig,
    DomainExpert,
    get_domain_config,
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
    # Domain System (NEW in v0.2.0)
    "DomainConfig",
    "DomainExpert",
    "get_domain_config",
]
