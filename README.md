# AI Search Match Framework

A reusable framework for AI-assisted development with automated search, filtering, and quality control for job leads, content aggregation, or any search-match-evaluate workflow.

## Overview

This framework implements a pattern for:
1. **Automated Search** - Query multiple data sources (APIs, MCPs, web scraping)
2. **Intelligent Filtering** - AI-powered relevance scoring and deduplication
3. **Quality Control** - Block lists, validation, and iterative refinement
4. **Progress Tracking** - Status management and audit trails

Originally built for job lead discovery but designed to be generalized for any AI development loop requiring search-match-evaluate cycles.

## Architecture

```
┌─────────────────┐
│   Data Sources  │ (APIs, MCPs, Web Scrapers)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Aggregator    │ (Multi-source coordination)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Evaluator  │ (Scoring, filtering, ranking)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Tracker       │ (Status, dedup, persistence)
└─────────────────┘
```

## Core Components

### 1. Provider Pattern
- **Base Provider Interface** - Standard interface for all data sources
- **MCP Integration** - Model Context Protocol support
- **API Adapters** - REST API wrappers
- **Web Scrapers** - HTML/RSS/XML parsers

### 2. AI Evaluation
- **Multi-Provider Support** - OpenAI, Anthropic, Gemini, Ollama, DeepSeek
- **Batch Processing** - Efficient scoring of multiple items
- **Fallback Chain** - Automatic provider failover
- **Custom Prompts** - Configurable evaluation criteria

### 3. Filtering & Validation
- **Block Lists** - Domain, company, keyword filters
- **Deduplication** - Hash-based and fuzzy matching
- **Link Validation** - HTTP checks with caching
- **Quality Thresholds** - Configurable acceptance criteria

### 4. State Management
- **JSON Persistence** - Simple file-based storage
- **Status Tracking** - Multi-state workflow (new, in-progress, applied, etc.)
- **History** - Timestamp and audit trail
- **Export** - Multiple format support

## Key Files

### Configuration
- `.github/copilot-instructions.md` - AI assistant guidelines
- `.github/GEMINI.md` - Gemini-specific instructions
- `config.json` - User preferences, block lists, system instructions
- `pyproject.toml` - Dependencies and project metadata

### Core Logic
- `src/app/job_finder.py` - Main search orchestration
- `src/app/job_tracker.py` - Status and persistence
- `src/app/mcp_providers.py` - MCP integration
- `src/app/ollama_provider.py` - Local AI evaluation
- `src/app/gemini_provider.py` - Gemini API integration

### Utilities
- `tools/llm_api.py` - Multi-provider LLM interface
- `tools/search_engine.py` - Web search integration
- `tools/web_scraper.py` - HTML content extraction
- `tools/screenshot_utils.py` - Visual verification

### UI
- `src/app/ui_server.py` - Flask REST API
- `src/app/templates/index.html` - Web interface

## Usage Patterns

### 1. Search Orchestration
```python
from app.job_finder import generate_job_leads

results = generate_job_leads(
    resume_text="...",
    count=10,
    model="gpt-4o",
    location="United States"
)
```

### 2. AI Evaluation
```python
from app.ollama_provider import OllamaProvider

provider = OllamaProvider()
scores = provider.rank_items(items, criteria="...")
```

### 3. Status Tracking
```python
from app.job_tracker import get_tracker

tracker = get_tracker()
tracker.track_job(job_data)
tracker.update_status(job_id, "applied")
```

### 4. Multi-Provider Aggregation
```python
from app.mcp_providers import MCPAggregator

aggregator = MCPAggregator()
results = aggregator.search_jobs("python developer", count=30)
```

## Configuration System

### Block Lists
```json
{
  "blocked_entities": [
    {"type": "site", "value": "example.com"},
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

- No PII in repository
- API keys via environment variables
- Input validation and sanitization
- Rate limiting on external APIs
- CORS protection on web endpoints

## Documentation

- `docs/` - Technical documentation
- `memory/docs/` - Project context and architecture
- `memory/tasks/` - Task planning and status
- `.github/` - AI assistant instructions

## License

[Specify your license]

## Contributing

1. Follow `.github/copilot-instructions.md` guidelines
2. Use feature branches
3. Include tests for new features
4. Update documentation
5. Add AI attribution in commits

## Credits

Built with AI assistance using:
- GitHub Copilot (Claude Sonnet 4.5)
- Gemini 2.5 Flash
- Ollama (local models)
