# Configuration Template

Copy this to `config.json` and customize for your use case.

```json
{
  "system_instructions": "You are evaluating items for relevance based on specific criteria. Focus on quality, relevance, and alignment with user goals.",
  
  "blocked_entities": [
    {
      "type": "site",
      "value": "example-spam-site.com",
      "reason": "Low quality content"
    },
    {
      "type": "employer",
      "value": "Bad Company Inc",
      "reason": "Known issues"
    },
    {
      "type": "keyword",
      "value": "unpaid internship",
      "reason": "Not interested"
    }
  ],
  
  "providers": {
    "linkedin": {
      "enabled": true,
      "max_results": 50,
      "priority": 1
    },
    "indeed": {
      "enabled": true,
      "max_results": 50,
      "priority": 2
    },
    "custom_api": {
      "enabled": false,
      "api_key": "your-api-key",
      "base_url": "https://api.example.com",
      "max_results": 30
    }
  },
  
  "evaluation": {
    "score_threshold": 0.7,
    "batch_size": 10,
    "criteria": "Evaluate items based on:\n- Relevance to user goals\n- Quality indicators\n- Source credibility"
  },
  
  "deduplication": {
    "enabled": true,
    "method": "url",
    "similarity_threshold": 0.85
  },
  
  "tracking": {
    "storage_path": "data/tracked_items.json",
    "auto_backup": true,
    "backup_interval_hours": 24
  },
  
  "llm": {
    "default_provider": "openai",
    "fallback_chain": ["openai", "anthropic", "gemini", "ollama"],
    "max_tokens": 2000,
    "temperature": 0.7
  },
  
  "rate_limiting": {
    "enabled": true,
    "calls_per_second": 2,
    "retry_attempts": 3,
    "retry_delay_seconds": 5
  },
  
  "logging": {
    "level": "INFO",
    "file": "logs/framework.log",
    "max_bytes": 10485760,
    "backup_count": 5
  }
}
```

## Configuration Fields

### system_instructions
AI evaluation criteria. Customize based on your specific use case.

### blocked_entities
Filter unwanted items by:
- `site`: Block by domain/URL
- `employer`: Block by company name
- `keyword`: Block by content keywords

### providers
Configure data sources:
- `enabled`: Whether to use this provider
- `max_results`: Maximum items per search
- `priority`: Search order (lower = higher priority)

### evaluation
AI scoring settings:
- `score_threshold`: Minimum score to accept (0.0-1.0)
- `batch_size`: Items to evaluate per batch
- `criteria`: Custom evaluation instructions

### deduplication
Duplicate detection:
- `method`: "url" (exact) or "content" (fuzzy)
- `similarity_threshold`: For content-based dedup

### tracking
State persistence:
- `storage_path`: Where to save tracked items
- `auto_backup`: Enable automatic backups
- `backup_interval_hours`: Backup frequency

### llm
AI provider settings:
- `default_provider`: Primary LLM
- `fallback_chain`: Providers to try in order
- `max_tokens`: Response length limit
- `temperature`: Response randomness (0-1)

### rate_limiting
API throttling:
- `calls_per_second`: Maximum request rate
- `retry_attempts`: Retries on failure
- `retry_delay_seconds`: Wait between retries

### logging
Application logging:
- `level`: DEBUG, INFO, WARNING, ERROR
- `file`: Log file path
- `max_bytes`: Max log file size
- `backup_count`: Number of rotated logs

## Environment Variables

### LLM Provider Configuration

**Cloud Providers** (at least one recommended for fallback):

```bash
# Google Gemini (recommended cloud provider)
GEMINI_API_KEY=your-gemini-key-here

# OpenAI (if using custom configurations)
OPENAI_API_KEY=sk-...

# Anthropic Claude (if using custom configurations)
ANTHROPIC_API_KEY=sk-ant-...
```

**Local Provider - Ollama** (privacy-focused, cost-free):

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434  # Default Ollama endpoint
OLLAMA_MODEL=qwen2.5:14b-q4  # Model to use
OLLAMA_TIMEOUT=5.0  # Connection timeout in seconds

# Provider Priority
PREFER_LOCAL=true  # Try Ollama first, fallback to cloud
```

**Setup Ollama:**
1. Install from [ollama.ai/download](https://ollama.ai/download)
2. Pull a model: `ollama pull qwen2.5:14b-q4`
3. Or run: `python scripts/setup_ollama.py`

See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for detailed setup guide including:
- Model recommendations by GPU/VRAM
- Performance optimization
- Troubleshooting
- Docker deployment

**Additional Settings:**

```bash
# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development

# Custom provider keys (if needed)
CUSTOM_API_KEY=...
```

## Usage Examples

### Minimal Configuration
```json
{
  "system_instructions": "Evaluate items for quality",
  "llm": {
    "default_provider": "openai"
  }
}
```

### Full-Featured Configuration
See complete example above.

### Dynamic Configuration
```python
from config_manager import ConfigManager

config = ConfigManager("config.json")

# Update at runtime
config.update("evaluation.score_threshold", 0.8)
config.add_blocked_entity("site", "spam.com")
config.save()
```
