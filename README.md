# AI Search Match Framework (ASMF)

**Lightweight Python framework for building AI-powered search and analysis applications.**

ASMF provides clean abstractions for common AI workflows: document parsing, AI provider management with automatic fallback, and extensible analysis patterns. Perfect for building domain-specific tools like patent analyzers, grant finders, or contract review systems.

## Why ASMF?

**The problem:** Building AI apps requires boilerplate for provider management, document parsing, and analysis patterns.

**The solution:** ASMF gives you:
- 🤖 **Multi-provider AI** - Gemini + Ollama with automatic fallback
- 📄 **Document parsing** - PDF extraction with domain-specific parsers
- 🔧 **Extensible analyzers** - Base classes for custom analysis logic
- 🎯 **Type-safe** - Full type hints for IDE support
- ✅ **Well-tested** - 80%+ coverage, production-ready

**Not a general LLM framework** - LangChain and LlamaIndex are better for RAG/chatbots. ASMF is for **linear search-analyze-evaluate workflows**.

## Quick Start

```bash
pip install ai-search-match-framework
```

```python
from asmf.providers import AIProviderFactory
from asmf.parsers import PDFPatentParser
from asmf.analyzers import BaseAnalyzer

# 1. AI Provider with automatic fallback
provider = AIProviderFactory.create_provider()  # Tries Gemini → Ollama
response = provider.analyze_text("Analyze this patent abstract...")

# 2. Document parsing
parser = PDFPatentParser()
patent = parser.parse("patent.pdf")
print(f"Claims: {len(patent.claims)}")

# 3. Custom analyzer
class PatentAnalyzer(BaseAnalyzer):
    def analyze(self, patent_text):
        prompt = f"Rate innovation: {patent_text}"
        return {"score": self.provider.analyze_text(prompt)}

analyzer = PatentAnalyzer(provider)
results = analyzer.batch_analyze([doc1, doc2, doc3])
```

## Core Components

### **AI Providers** (`asmf.providers`)
Unified interface for AI models with automatic fallback:
- `GeminiProvider` - Google Gemini API
- `OllamaProvider` - Local Ollama
- `AIProviderFactory` - Automatic selection (Gemini → Ollama)

```python
# Prefer local-first
provider = AIProviderFactory.create_provider(prefer_local=True)
```

### **Document Parsers** (`asmf.parsers`)
Extract structured data from documents:
- `PDFPatentParser` - Patent claims, abstracts, metadata
- Extensible for custom formats

```python
parExamples

**Patent Analysis:**
```python
from asmf.parsers import PDFPatentParser
from asmf.providers import GeminiProvider

parser = PDFPatentParser()
provider = GeminiProvider(api_key="...")

patent = parser.parse("us_patent.pdf")
for claim in patent.get_independent_claims():
    analysis = provider.analyze_text(
        f"Evaluate novelty: {claim.text}",
        context={"title": patent.title}
    )
    print(analysis)
```

**Grant Matching:**
```python
from asmf.analyzers import BaseAnalyzer

class GrantMatcher(BaseAnalyzer):
    def __init__(self, provider, profile):
        super().__init__(provider)
        self.profile = profile
    
    def analyze(self, grant_text):
        prompt = f"Match grant to profile:\nGrant: {grant_text}\nProfile: {self.profile}"
        score = self.provider.analyze_text(prompt)
        return {"score": score, "grant": grant_text}

matcher = GrantMatcher(provider, profile="biotech research")
matches = matcher.batch_analyze(grant_descriptions)
```

See `examples/job_finder/` for a complete application demonstrating multi-source aggregation and tracking.

## Configuration

**Environment Variables:**
```bash
GEMINI_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434  # optional
OLLAMA_TIMEOUT=5.0  # optional
```

**Provider Selection:**
```python
# Default: Gemini first, then Ollama
provider = AIProviderFactory.create_provider()

# Local-first
provider = AIProviderFactory.create_provider(prefer_local=True)

# Specific provider
provider = GeminiProvider(api_key="...", model="gemini-1.5-pro")
provider = OllamaProvider(model="qwen2.5-coder:32b")te", "value": "example.com"},
    {"type": "employer", "value": "Bad Company"}
  ]
}
```

### System Instructions
```json
{
  "system_instructions": "You are evaluating job leads for..."
}
```

### Provider Settings
```json
{
  "providers": {
    "linkedin": {"enabled": true, "max_results": 50},
    "indeed": {"enabled": true, "max_results": 50}
  }
}
```

## Extensibility

### Adding New Data Sources
1. Implement `BaseProvider` interface
2. Add to `providers/` directory
3. Register in aggregator

### Adding New AI Providers
1. Implement standard interface (rank_items, evaluate)
2. Add to provider chain with fallback
3. Configure in environment

### Custom Evaluation Criteria
1. Update system instructions
2. Modify scoring prompts
3. Adjust threshold values

## Testing

Comprehensive test suite with:
- Unit tests for all components
- Integration tests for workflows
- Slow tests marked separately
- Fixtures for common test data

```bash
# Run fast tests
uv run pytest -m "not slow"

# Run all tests
uv run pytest

# Run specific component
uv run pytest tests/test_job_finder.py
```

## Workflows

### GitHub Actions
- **CI/CD** - Automated testing and validation
- **Version Bump** - Automatic versioning on merge
- **Auto-Revert** - Rollback on CI failure
- **Branch Protection** - Enforce PR workflow

### Pre-commit Hooks
- Code formatting (black, isort)
- Linting (flake8)
- Security checks
- Test execution

## Security

- No PII in repository (automated scans)
- API keys via environment variables only
- Input validation and sanitization
- Rate limiting on external APIs
- CORS protection on web endpoints
- Trusted PyPI publishing (no API tokens)
- Weekly vulnerability scans

## Publishing

This framework is published to PyPI with automated workflows:
- **Auto-tagging**: Merges to `main` create version tags
- **Auto-publishing**: GitHub Releases trigger PyPI uploads
- **Pre-publish tests**: Full test suite runs before publishing

See [docs/PUBLISHING.md](docs/PUBLISHING.md) for details.

## Documentation

- [docs/PUBLISHING.md](docs/PUBLISHING.md) - Release process
- [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) - Pre-release checklist
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) - Configuration guide
- [docs/PATTERNS.md](docs/PATTERNS.md) - Usage patterns
- `.github/copilot-instructions.md` - Development guidelines

## License

MIT License - See LICENSE file for details

## Contributing

1. Follow `.github/copilot-instructions.md` guidelines
2. Use feature branches with descriptive names
3. Include tests for new features (maintain 75%+ coverage)
4. Update documentation for API changes
5. Run pre-commit checks before pushing

## Credits

Built with AI assistance using:
- GitHub Copilot (Claude Sonnet 4.5)
- Gemini 2.5 Flash
- Ollama (local models)
