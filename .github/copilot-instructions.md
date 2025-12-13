# AI Search Match Framework (ASMF)

## Project Overview

This is a reusable Python framework for building AI-powered search and analysis applications. It provides core infrastructure that can be shared across multiple domain-specific projects (patent analysis, grant finding, contract analysis, etc.).

## Core Components

### 1. AI Providers (`asmf.providers`)
- **BaseAIProvider**: Abstract interface for AI providers
- **GeminiProvider**: Google Gemini API integration
- **OllamaProvider**: Local Ollama integration
- **AIProviderFactory**: Automatic provider selection with fallback chain (Gemini → Ollama)

### 2. Document Parsers (`asmf.parsers`)
- **PDFParser**: Generic PDF text extraction (pypdf + pdfplumber)
- **DocumentParser**: Base class for document parsing
- Support for various document formats (PDF, DOCX, TXT)

### 3. Base Analyzers (`asmf.analyzers`)
- **BaseAnalyzer**: Abstract analyzer pattern
- Reusable analysis workflows
- Result formatting and scoring patterns

### 4. Utilities (`asmf.utils`)
- Configuration management
- Logging setup
- Common helper functions

## Technology Stack

- **Python**: 3.12+
- **AI**: google-generativeai (Gemini), httpx (Ollama)
- **PDF**: pypdf, pdfplumber
- **Data**: pydantic for models
- **Testing**: pytest, pytest-cov
- **Packaging**: uv for fast installs
- **Containers**: Docker support

## Package Structure

```
ai-search-match-framework/
├── src/
│   └── asmf/
│       ├── __init__.py
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base_provider.py
│       │   ├── gemini_provider.py
│       │   ├── ollama_provider.py
│       │   └── provider_factory.py
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── base_parser.py
│       │   └── pdf_parser.py
│       ├── analyzers/
│       │   ├── __init__.py
│       │   └── base_analyzer.py
│       └── utils/
│           ├── __init__.py
│           ├── config.py
│           └── logging.py
├── tests/
├── pyproject.toml
├── README.md
└── Dockerfile
```

## Development Guidelines

### Code Style
- **PEP 8** compliance
- **Type hints** for all public APIs
- **Docstrings** (Google style) for all public functions/classes
- **Black** for formatting (line length 120)
- **isort** for import sorting

### Testing
- Unit tests for all public APIs
- pytest fixtures for common test data
- Mock external APIs (Gemini, Ollama)
- Aim for >80% code coverage

### Documentation
- Clear README with usage examples
- Docstrings for all public APIs
- Type hints for IDE support

### API Design
- Keep interfaces generic and extensible
- Domain-specific logic should NOT be in this framework
- Configuration via environment variables or constructor args
- Graceful error handling with informative messages

## Usage Example

```python
# Install
pip install ai-search-match-framework

# Use providers
from asmf.providers import AIProviderFactory

provider = AIProviderFactory.create_provider()
result = provider.analyze_text("Analyze this document...")

# Use parsers
from asmf.parsers import PDFParser

parser = PDFParser()
text = parser.extract_text("document.pdf")

# Extend for domain-specific use
from asmf.analyzers import BaseAnalyzer

class MyDomainAnalyzer(BaseAnalyzer):
    def analyze(self, data):
        # Domain-specific logic here
        pass
```

## Projects Using ASMF

1. **ai-patent-eval**: Patent analysis for pyrolysis technologies
2. **ai-grant-finder** (planned): Grant opportunity matching
3. **ai-contract-analyzer** (planned): Contract review and risk analysis

## Development Workflow

1. Changes to framework → PR to `main`
2. Version bump after merge
3. Dependent projects update their `pyproject.toml` dependency version
