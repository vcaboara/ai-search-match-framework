# AI Search Match Framework - Quick Start

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ai-search-match-framework.git
cd ai-search-match-framework

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .

# Install dev dependencies
uv pip install -e ".[dev]"
```

## Configuration

1. **Create `.env` file** with API keys:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
OLLAMA_HOST=http://localhost:11434
```

2. **Create `config.json`** from template:
```bash
cp docs/CONFIGURATION.md config.json
# Edit config.json with your settings
```

## Basic Usage

### 1. Simple Search Workflow

```python
from src.providers.base_provider import BaseProvider
from src.aggregator.aggregator import Aggregator
from src.tracker.tracker import get_tracker

# Initialize providers (implement your own)
providers = [
    YourProvider1(),
    YourProvider2(),
]

# Create aggregator
aggregator = Aggregator(providers, blocked_entities=[])

# Search
results = aggregator.search("python developer", count=20)

# Track results
tracker = get_tracker()
for result in results:
    tracker.track(result)

# Update status
tracker.update_status(results[0]["id"], "in_progress")
```

### 2. AI Evaluation

```python
from src.ai.llm_interface import LLMInterface

llm = LLMInterface()

# Evaluate items
scored_items = llm.batch_evaluate(
    results,
    criteria="Evaluate for relevance to senior Python roles",
    batch_size=10
)

# Filter by threshold
filtered = [(item, score) for item, score in scored_items if score >= 0.7]
```

### 3. Status Tracking

```python
from src.tracker.tracker import get_tracker

tracker = get_tracker()

# Get all items
all_items = tracker.get_all()

# Filter by status
new_items = tracker.get_all(status="new")
completed = tracker.get_all(status="completed")

# Statistics
stats = tracker.get_stats()
print(f"New: {stats['new']}, Completed: {stats['completed']}")

# Export
tracker.export_csv("output.csv", status="completed")
```

## Running Tests

```bash
# Fast tests only
uv run pytest -m "not slow"

# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test file
uv run pytest tests/test_aggregator.py
```

## Project Structure

```
ai-search-match-framework/
├── src/
│   ├── providers/       # Data source providers
│   ├── aggregator/      # Multi-provider coordination
│   ├── ai/              # LLM interface
│   └── tracker/         # State management
├── examples/            # Usage examples
├── tests/               # Test suite
├── docs/                # Documentation
├── data/                # Storage (tracked items)
├── logs/                # Application logs
├── config.json          # User configuration
├── .env                 # API keys (not committed)
└── pyproject.toml       # Dependencies
```

## Next Steps

1. **Implement Providers**: Create provider classes extending `BaseProvider`
2. **Configure Filtering**: Set up `blocked_entities` in `config.json`
3. **Customize Evaluation**: Update `system_instructions` for your use case
4. **Add Tests**: Write tests for custom providers
5. **Build UI**: Optional Flask UI for status tracking

## Examples

See `examples/` directory for:
- Web scraper provider
- API provider template
- Complete workflow examples
- Custom evaluation criteria

## Documentation

- [Configuration Guide](docs/CONFIGURATION.md)
- [Design Patterns](docs/PATTERNS.md)
- [API Reference](docs/API.md) (TODO)
- [Extending the Framework](docs/EXTENDING.md) (TODO)

## Common Tasks

### Add a New Provider

```python
from src.providers.base_provider import BaseProvider

class MyProvider(BaseProvider):
    def search(self, query: str, count: int = 10, **kwargs):
        # Implement search logic
        return results
```

### Custom Block List

```json
{
  "blocked_entities": [
    {"type": "site", "value": "spam.com"},
    {"type": "keyword", "value": "unwanted"}
  ]
}
```

### Change LLM Provider

```json
{
  "llm": {
    "default_provider": "anthropic",
    "fallback_chain": ["anthropic", "openai", "ollama"]
  }
}
```

## Troubleshooting

### No API Key Error
```bash
# Set in .env file
OPENAI_API_KEY=your-key-here
```

### Import Errors
```bash
# Reinstall in editable mode
uv pip install -e .
```

### Test Failures
```bash
# Run with verbose output
uv run pytest -v

# Check specific test
uv run pytest tests/test_specific.py::test_function -v
```

## Support

- GitHub Issues: [Create an issue](https://github.com/yourusername/ai-search-match-framework/issues)
- Documentation: See `docs/` directory
- Examples: See `examples/` directory
