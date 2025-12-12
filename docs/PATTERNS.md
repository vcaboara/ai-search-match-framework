# Framework Structure

## Core Patterns

### 1. Provider Pattern
All data sources implement a common interface for consistency:

```python
class BaseProvider:
    def search(self, query: str, **kwargs) -> List[Dict]:
        """Execute search and return standardized results"""
        pass
    
    def validate(self, item: Dict) -> bool:
        """Validate item meets quality standards"""
        pass
```

### 2. Aggregator Pattern
Coordinates multiple providers with deduplication:

```python
class Aggregator:
    def __init__(self, providers: List[BaseProvider]):
        self.providers = providers
    
    def search(self, query: str, count: int) -> List[Dict]:
        results = []
        for provider in self.providers:
            results.extend(provider.search(query))
        return self.deduplicate(results)[:count]
```

### 3. Tracker Pattern
Manages state and persistence:

```python
class Tracker:
    def track(self, item: Dict) -> str:
        """Add item with unique ID"""
        pass
    
    def update_status(self, id: str, status: str):
        """Update item status"""
        pass
    
    def get_all(self, status: Optional[str] = None) -> List[Dict]:
        """Retrieve items by status"""
        pass
```

### 4. Evaluator Pattern
AI-powered scoring and filtering:

```python
class AIEvaluator:
    def rank_items(self, items: List[Dict], criteria: str) -> List[Tuple[Dict, float]]:
        """Score items based on criteria"""
        pass
    
    def filter_items(self, items: List[Dict], threshold: float) -> List[Dict]:
        """Remove items below threshold"""
        pass
```

## Configuration Management

### Layered Configuration
1. **Defaults** - Hardcoded fallbacks
2. **Environment** - `.env` file for secrets
3. **Config File** - `config.json` for user preferences
4. **Runtime** - API parameters override all

### Block List Pattern
```python
def is_blocked(item: Dict, blocked_entities: List[Dict]) -> bool:
    for block in blocked_entities:
        if block["type"] == "site" and block["value"] in item.get("link", ""):
            return True
        if block["type"] == "employer" and block["value"].lower() in item.get("company", "").lower():
            return True
    return False
```

## AI Integration

### Multi-Provider Fallback
```python
PROVIDERS = [
    ("openai", "gpt-4o"),
    ("anthropic", "claude-3-sonnet"),
    ("gemini", "gemini-pro"),
    ("ollama", "qwen2.5:32b")
]

def query_with_fallback(prompt: str) -> str:
    for provider, model in PROVIDERS:
        try:
            return query_llm(prompt, provider=provider, model=model)
        except Exception as e:
            logging.warning(f"{provider} failed: {e}")
    raise Exception("All providers failed")
```

### Batch Evaluation
```python
def batch_evaluate(items: List[Dict], batch_size: int = 10) -> List[float]:
    scores = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        prompt = f"Score these {len(batch)} items:\n{json.dumps(batch)}"
        response = query_llm(prompt)
        scores.extend(parse_scores(response))
    return scores
```

## Testing Strategy

### Test Categories
1. **Unit Tests** - Individual components
2. **Integration Tests** - Multi-component workflows
3. **Slow Tests** - External API calls (marked)
4. **Regression Tests** - Bug fixes

### Fixture Pattern
```python
@pytest.fixture
def sample_items():
    return [
        {"id": "1", "title": "Item 1", "link": "https://example.com/1"},
        {"id": "2", "title": "Item 2", "link": "https://example.com/2"}
    ]

@pytest.fixture
def mock_provider(mocker):
    provider = mocker.Mock(spec=BaseProvider)
    provider.search.return_value = sample_items()
    return provider
```

## Error Handling

### Standard Error Response
```python
{
    "success": False,
    "error": "Description of error",
    "error_type": "ValidationError",
    "timestamp": "2025-01-15T10:30:00Z"
}
```

### Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_with_retry(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text
```

## Performance Optimization

### Caching Pattern
```python
from functools import lru_cache
from datetime import datetime, timedelta

# In-memory cache with TTL
_cache = {}
_cache_ttl = timedelta(hours=1)

def cached_query(key: str, fetch_fn):
    if key in _cache:
        value, timestamp = _cache[key]
        if datetime.now() - timestamp < _cache_ttl:
            return value
    
    value = fetch_fn()
    _cache[key] = (value, datetime.now())
    return value
```

### Rate Limiting
```python
import time

class RateLimiter:
    def __init__(self, calls_per_second: float):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
    
    def wait(self):
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()
```

## Deployment

### Docker Support
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install -e .
COPY src/ src/
CMD ["uv", "run", "python", "-m", "src.app.main"]
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional
GEMINI_API_KEY=...
OLLAMA_HOST=http://localhost:11434
LOG_LEVEL=INFO
```

## Monitoring

### Logging Pattern
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Metrics Collection
```python
class Metrics:
    def __init__(self):
        self.stats = {
            "searches": 0,
            "items_found": 0,
            "items_filtered": 0,
            "api_calls": 0,
            "errors": 0
        }
    
    def record(self, metric: str, value: int = 1):
        self.stats[metric] = self.stats.get(metric, 0) + value
    
    def report(self) -> Dict:
        return self.stats.copy()
```
