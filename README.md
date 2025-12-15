# AI Search Match Framework (ASMF)

**Lightweight Python framework for building AI-powered document analysis applications.**

Clean abstractions for AI providers, document parsing, and custom analyzers. Build domain-specific tools like patent analyzers, grant finders, or contract reviewers.

## Quick Start

```bash
pip install ai-search-match-framework
```

```python
from asmf.providers import AIProviderFactory
from asmf.parsers import PDFPatentParser
from asmf.analyzers import BaseAnalyzer

# AI Provider with automatic fallback (Gemini → Ollama)
provider = AIProviderFactory.create_provider()
response = provider.analyze_text("Analyze this document...")

# Parse documents
parser = PDFPatentParser()
doc = parser.parse("document.pdf")

# Create custom analyzer
class MyAnalyzer(BaseAnalyzer):
    def analyze(self, data):
        return self.provider.analyze_text(f"Evaluate: {data}")

analyzer = MyAnalyzer(provider)
results = analyzer.batch_analyze([doc1, doc2])
```

## Features

- 🤖 **Multi-provider AI** - Unified interface for Gemini, Ollama with automatic fallback
- 📄 **Document parsing** - Extract structured data from PDFs and other formats
- 🔧 **Extensible analyzers** - Base classes for custom domain logic
- 🔍 **PR Review Webhook** - Automated code review using Ollama with anti-pattern detection
- 🎯 **Type-safe** - Full type hints for excellent IDE support
- ✅ **Well-tested** - 78%+ coverage, production-ready
- 🐳 **Docker support** - Containerized testing and deployment

## Core Components

| Component | Purpose |
|-----------|---------|
| `providers` | AI provider interface (Gemini, Ollama) with failover |
| `parsers` | Document parsing (PDF, etc.) with structured output |
| `analyzers` | Base classes for domain-specific analysis logic |
| `llm` | Task-specific model selection with VRAM detection |
| `utils` | Configuration, logging, common utilities |

## Configuration

### Quick Start with Ollama (Local, Free)

```bash
# 1. Install Ollama: https://ollama.ai/download
# 2. Pull a model
ollama pull qwen2.5:14b-q4

# 3. Configure ASMF
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
echo "PREFER_LOCAL=true" >> .env
```

Or use the automated setup:
```bash
python scripts/setup_ollama.py
```

### Cloud Provider Setup

Set environment variables:
```bash
GEMINI_API_KEY=your_key_here  # For Gemini
PREFER_LOCAL=false  # Cloud-first (default)
```

### Advanced Configuration

```python
# Local-first with fallback
from asmf.providers import AIProviderFactory
provider = AIProviderFactory.create_provider(prefer_local=True)

# Direct provider usage
from asmf.providers import GeminiProvider, OllamaProvider
gemini = GeminiProvider(api_key="...", model="gemini-1.5-pro")
ollama = OllamaProvider(model="qwen2.5:14b-q4", base_url="http://localhost:11434")

# Task-specific model selection (NEW!)
from asmf.llm import ModelSelector, TaskType
selector = ModelSelector()  # Auto-detects GPU
model = selector.select_model(TaskType.CODE_REVIEW)  # Best model for code review
ollama = OllamaProvider(model=model)
```

See [docs/OLLAMA_SETUP.md](docs/OLLAMA_SETUP.md) for comprehensive Ollama setup guide and task-specific model recommendations.

## Use Cases

**Not a general LLM framework** - Use LangChain/LlamaIndex for RAG/chatbots.  
ASMF is for **linear document analysis workflows**:

- ✅ Patent analysis and prior art search
- ✅ Grant/RFP matching and evaluation
- ✅ Contract review and risk assessment
- ✅ Resume screening and candidate matching
- ✅ Research paper analysis and summarization

## Examples

See [examples/job_finder/](https://github.com/vcaboara/ai-search-match-framework/tree/main/examples/job_finder) for a complete application.

## Documentation

- **[Full Documentation](https://github.com/vcaboara/ai-search-match-framework#readme)** - Complete guide
- **[API Reference](https://github.com/vcaboara/ai-search-match-framework/tree/main/docs)** - Detailed docs
- **[Configuration](https://github.com/vcaboara/ai-search-match-framework/blob/main/docs/CONFIGURATION.md)** - Setup guide
- **[Usage Patterns](https://github.com/vcaboara/ai-search-match-framework/blob/main/docs/PATTERNS.md)** - Best practices
- **[Ollama Setup](https://github.com/vcaboara/ai-search-match-framework/blob/main/docs/OLLAMA_SETUP.md)** - Local LLM setup
- **[Webhook Server](https://github.com/vcaboara/ai-search-match-framework/blob/main/docs/WEBHOOK_SERVER.md)** - Automated PR review with Ollama

## Requirements

- Python 3.10+
- Dependencies: `requests`, `beautifulsoup4`, `google-generativeai`, `httpx`, `pypdf`, `pdfplumber`

## License

MIT License - See [LICENSE](https://github.com/vcaboara/ai-search-match-framework/blob/main/LICENSE)

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**AI Contributions**: We track AI-generated commits with `[AI]` prefix for accessibility advocacy and productivity metrics. See [commit conventions](.github/commit-conventions.md) for details.

---

**Why ASMF vs others?**

| Framework | Focus | Best For |
|-----------|-------|----------|
| **ASMF** | Linear document analysis | Domain-specific evaluation tools |
| LangChain | RAG, agents, chains | Chatbots, conversational AI |
| LlamaIndex | Data indexing, retrieval | Knowledge base search |

Built with ❤️ using AI assistance (GitHub Copilot, Gemini, Ollama)
