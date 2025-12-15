# Ollama Setup Guide

This guide covers setting up Ollama for local LLM inference with the AI Search Match Framework (ASMF).

## Table of Contents
- [Why Ollama?](#why-ollama)
- [Installation](#installation)
- [Model Recommendations](#model-recommendations)
- [Configuration](#configuration)
- [Provider Priority & Fallback](#provider-priority--fallback)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

## Why Ollama?

Ollama provides:
- **Privacy**: Run AI models locally without sending data to external services
- **Cost**: No API costs after initial setup
- **Speed**: Low-latency inference for local models
- **Offline**: Works without internet connection
- **Flexibility**: Easy model switching and customization

ASMF integrates Ollama seamlessly with automatic fallback to cloud providers (Gemini) when needed.

## Installation

### Windows

**Option 1: Installer (Recommended)**
1. Download from [ollama.ai/download](https://ollama.ai/download)
2. Run the installer
3. Ollama runs as a background service on `http://localhost:11434`

**Option 2: Manual**
```powershell
# Download and run
winget install Ollama.Ollama

# Verify installation
ollama --version
```

### macOS

**Option 1: Installer (Recommended)**
1. Download from [ollama.ai/download](https://ollama.ai/download)
2. Move Ollama.app to Applications
3. Launch Ollama from Applications

**Option 2: Homebrew**
```bash
brew install ollama

# Start service
brew services start ollama
```

### Linux

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start service
sudo systemctl start ollama
sudo systemctl enable ollama  # Start on boot

# Verify
ollama --version
```

### Docker

See [docker-compose.example.yml](../docker-compose.example.yml) for containerized setup.

## Model Recommendations

Choose models based on your available VRAM:

### High-End (12GB+ VRAM)
**Recommended: `qwen2.5:32b-q4` or `qwen2.5:14b-q4`**
```bash
ollama pull qwen2.5:32b-q4
# or
ollama pull qwen2.5:14b-q4
```

**Characteristics:**
- Excellent reasoning and code generation
- Best for document analysis, patent evaluation
- ~20-30 GB disk space
- Inference: 2-5 tokens/sec

**Alternatives:**
- `llama3.1:70b-q4` - Strong general purpose
- `mixtral:8x7b-q4` - Good balance of speed/quality

### Mid-Range (8GB VRAM)
**Recommended: `qwen2.5:14b-q4` or `llama3.2:3b`**
```bash
ollama pull qwen2.5:14b-q4
# or
ollama pull llama3.2:3b
```

**Characteristics:**
- Good balance of quality and speed
- Suitable for most ASMF use cases
- ~8-15 GB disk space
- Inference: 5-10 tokens/sec

**Alternatives:**
- `mistral:7b-q4` - Fast, general purpose
- `phi3:14b` - Microsoft's efficient model

### Low-End (<8GB VRAM or CPU-only)
**Recommended: `llama3.2:3b` or `qwen2.5:7b-q4`**
```bash
ollama pull llama3.2:3b
# or
ollama pull qwen2.5:7b-q4
```

**Characteristics:**
- Fast inference on limited hardware
- Good for simple analysis tasks
- ~2-4 GB disk space
- Inference: 10-20 tokens/sec (GPU), 2-5 tokens/sec (CPU)

**Alternatives:**
- `phi3:mini` - Efficient 3.8B model
- `gemma:2b` - Smallest option, still capable

### Specialized Models

**For Code-Heavy Tasks:**
```bash
ollama pull qwen2.5-coder:32b  # High-end
ollama pull qwen2.5-coder:7b   # Mid/low-end
```

**For Multilingual:**
```bash
ollama pull aya:35b  # Supports 101 languages
```

## Task-Specific Model Selection

ASMF includes a `ModelSelector` for automatic task-specific model recommendations:

### Using ModelSelector

```python
from asmf.llm import ModelSelector, TaskType

# Auto-detect GPU and get recommendations
selector = ModelSelector()

# Get best model for code review
code_review_model = selector.select_model(TaskType.CODE_REVIEW)
print(f"Best for code review: {code_review_model}")

# Get best model for document analysis
doc_model = selector.select_model(TaskType.DOCUMENT_ANALYSIS)
print(f"Best for documents: {doc_model}")

# See all recommendations for a task
selector.print_recommendations(TaskType.CODE_GENERATION)
```

### Task Types and Optimized Models

| Task Type | Description | Optimized Models |
|-----------|-------------|------------------|
| **CODE_REVIEW** | Reviewing PRs, finding bugs, suggesting improvements | `qwen2.5-coder:32b`, `qwen2.5-coder:14b`, `qwen2.5-coder:7b` |
| **CODE_GENERATION** | Writing code, implementing features, generating boilerplate | `qwen2.5-coder:32b`, `qwen2.5-coder:14b`, `qwen2.5-coder:7b` |
| **DOCUMENT_ANALYSIS** | Patent analysis, grant evaluation, contract review | `qwen2.5:32b-q4`, `qwen2.5:14b-q4`, `llama3.2:3b` |
| **GENERAL** | General-purpose tasks, Q&A, summarization | `qwen2.5:32b-q4`, `qwen2.5:14b-q4`, `mistral:7b-q4` |

### Examples by Use Case

#### Code Review Workflow
```python
from asmf.llm import ModelSelector, TaskType
from asmf.providers import OllamaProvider

# Select optimal code review model
selector = ModelSelector()
model = selector.select_model(TaskType.CODE_REVIEW, check_availability=True)

# Use with OllamaProvider
provider = OllamaProvider(model=model)
result = provider.analyze_text("""
Review this Python code for potential issues:

def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
""")
print(result)
```

#### Document Analysis Workflow
```python
from asmf.llm import ModelSelector, TaskType
from asmf.providers import OllamaProvider
from asmf.parsers import PDFParser

# Setup with task-specific model
selector = ModelSelector()
model = selector.select_model(TaskType.DOCUMENT_ANALYSIS)
provider = OllamaProvider(model=model)
parser = PDFParser()

# Analyze patent document
patent_text = parser.extract_text("patent.pdf")
analysis = provider.analyze_text(f"""
Evaluate this patent for prior art conflicts:

{patent_text[:2000]}
""")
print(analysis)
```

#### Batch Code Generation
```python
from asmf.llm import ModelSelector, TaskType
from asmf.providers import OllamaProvider

# Use fastest code generation model
selector = ModelSelector()
model = selector.select_model(TaskType.CODE_GENERATION)
provider = OllamaProvider(model=model)

prompts = [
    "Write a Python function to validate email addresses",
    "Create a REST API endpoint for user registration",
    "Generate unit tests for a sorting function"
]

for prompt in prompts:
    code = provider.analyze_text(prompt)
    print(f"\n{'='*60}")
    print(prompt)
    print(f"{'='*60}")
    print(code)
```

### Manual Override

```python
from asmf.llm import ModelSelector

# Override VRAM detection (useful for testing)
selector = ModelSelector(vram_gb=4.0)  # Simulate 4GB GPU

# Get recommendations for low-end hardware
recs = selector.get_recommendations(TaskType.CODE_REVIEW)
for rec in recs:
    print(f"{rec.name}: {rec.description}")
```

### Hardware-Aware Recommendations

The `ModelSelector` automatically considers your hardware:

```python
from asmf.llm import ModelSelector, TaskType

selector = ModelSelector()
print(f"Detected: {selector.vram_gb}GB VRAM ({selector.gpu_vendor})")

# Automatically gets appropriate models for your GPU
if selector.vram_gb >= 12:
    # High-end: qwen2.5-coder:32b for code tasks
    pass
elif selector.vram_gb >= 8:
    # Mid-range: qwen2.5-coder:14b for code tasks
    pass
else:
    # Low-end: qwen2.5-coder:7b for code tasks
    pass

# Just call select_model() - it handles everything
model = selector.select_model(TaskType.CODE_REVIEW)
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=5.0  # Connection timeout in seconds
OLLAMA_MODEL=qwen2.5:14b-q4  # Default model

# Provider Priority
PREFER_LOCAL=true  # Try Ollama first, fallback to Gemini

# Gemini Fallback (optional)
GEMINI_API_KEY=your-gemini-key-here
```

### Python Configuration

```python
from asmf.providers import OllamaProvider, AIProviderFactory

# Direct Ollama usage
provider = OllamaProvider(
    model="qwen2.5:14b-q4",
    base_url="http://localhost:11434",
    timeout=5.0
)

# With automatic fallback
provider = AIProviderFactory.create_provider(prefer_local=True)
# Tries Ollama first, falls back to Gemini if unavailable
```

### Automated Setup

Use the provided setup script:

```bash
# Python script (cross-platform)
python scripts/setup_ollama.py

# PowerShell (Windows)
./scripts/setup_ollama.ps1
```

The script will:
1. Detect your GPU and VRAM
2. Recommend optimal models
3. Pull selected models
4. Create/update your `.env` file
5. Verify installation

## Provider Priority & Fallback

ASMF supports automatic provider fallback for resilience:

### Local-First (Recommended for Development)

```python
from asmf.providers import AIProviderFactory

# Try Ollama first, fallback to Gemini
provider = AIProviderFactory.create_provider(prefer_local=True)
```

**Priority Chain:** Ollama → Gemini

**Use When:**
- Developing locally
- Privacy is important
- You have adequate hardware
- Cost optimization is priority

### Cloud-First (Default)

```python
from asmf.providers import AIProviderFactory

# Try Gemini first, fallback to Ollama
provider = AIProviderFactory.create_provider(prefer_local=False)
# or simply
provider = AIProviderFactory.create_provider()
```

**Priority Chain:** Gemini → Ollama

**Use When:**
- Running in production
- Need consistent quality
- Limited local resources
- Don't want to manage models

### Manual Provider Selection

```python
from asmf.providers import OllamaProvider, GeminiProvider

# Force Ollama only (no fallback)
try:
    provider = OllamaProvider()
    if not provider.is_available():
        raise RuntimeError("Ollama required but not available")
except Exception as e:
    print(f"Failed to initialize Ollama: {e}")
    exit(1)

# Force Gemini only
provider = GeminiProvider(api_key="your-key")
```

## Usage Examples

### Basic Analysis

```python
from asmf.providers import AIProviderFactory

# Initialize with fallback
provider = AIProviderFactory.create_provider(prefer_local=True)

# Analyze text
result = provider.analyze_text(
    "Analyze this patent for prior art conflicts...",
    context={"patent_id": "US1234567", "field": "pyrolysis"}
)

print(result)
```

### Document Processing Pipeline

```python
from asmf.providers import AIProviderFactory
from asmf.parsers import PDFParser

# Setup
parser = PDFParser()
provider = AIProviderFactory.create_provider(prefer_local=True)

# Process documents
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
results = []

for doc_path in documents:
    # Extract text
    text = parser.extract_text(doc_path)
    
    # Analyze with AI
    analysis = provider.analyze_text(
        f"Evaluate this document for relevance:\n\n{text[:2000]}"
    )
    
    results.append({
        "document": doc_path,
        "analysis": analysis
    })

print(f"Processed {len(results)} documents")
```

### Batch Processing with Error Handling

```python
from asmf.providers import AIProviderFactory, OllamaProvider, GeminiProvider
import logging

logger = logging.getLogger(__name__)

def process_batch(items, prefer_local=True):
    """Process items with provider fallback."""
    try:
        provider = AIProviderFactory.create_provider(prefer_local=prefer_local)
        provider_name = provider.__class__.__name__
        logger.info(f"Using provider: {provider_name}")
    except RuntimeError as e:
        logger.error(f"No AI providers available: {e}")
        return []
    
    results = []
    for item in items:
        try:
            result = provider.analyze_text(f"Evaluate: {item}")
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to process item: {e}")
            continue
    
    return results
```

### Streaming Responses (Advanced)

For large documents, you may want streaming:

```python
import httpx
from asmf.providers import OllamaProvider

provider = OllamaProvider()
if not provider.is_available():
    raise RuntimeError("Ollama not available")

# Stream response
url = f"{provider.base_url}/api/generate"
data = {
    "model": provider.model,
    "prompt": "Analyze this large document...",
    "stream": True
}

with httpx.stream("POST", url, json=data, timeout=120.0) as response:
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            print(chunk.get("response", ""), end="", flush=True)
```

## Troubleshooting

### Ollama Not Available

**Symptoms:**
```
WARNING:asmf.providers.ollama_provider:Ollama not available: Connection refused
```

**Solutions:**

1. **Check if Ollama is running:**
   ```bash
   # Test connection
   curl http://localhost:11434/api/tags
   
   # Should return list of models
   ```

2. **Start Ollama service:**
   ```bash
   # Windows: Already running if installed
   # macOS: Launch Ollama.app
   # Linux:
   sudo systemctl start ollama
   ```

3. **Check port binding:**
   ```bash
   # Verify Ollama is listening on 11434
   netstat -an | grep 11434
   # or
   lsof -i :11434
   ```

4. **Firewall issues:**
   ```bash
   # Allow localhost connections
   # Windows: Windows Defender Firewall → Allow an app
   # macOS: System Preferences → Security & Privacy → Firewall
   # Linux: sudo ufw allow 11434
   ```

### Model Not Found

**Symptoms:**
```
Error: model 'qwen2.5:14b-q4' not found
```

**Solutions:**

1. **Pull the model:**
   ```bash
   ollama pull qwen2.5:14b-q4
   ```

2. **List available models:**
   ```bash
   ollama list
   ```

3. **Use correct model name:**
   ```python
   # Check available models
   import httpx
   response = httpx.get("http://localhost:11434/api/tags")
   models = [m["name"] for m in response.json()["models"]]
   print("Available models:", models)
   ```

### Slow Performance

**Symptoms:**
- Inference taking >30 seconds
- High CPU usage
- System freezing

**Solutions:**

1. **Use smaller model:**
   ```bash
   # Switch from 32b to 7b
   ollama pull qwen2.5:7b-q4
   ```

2. **Check GPU usage:**
   ```bash
   # NVIDIA
   nvidia-smi
   
   # AMD
   rocm-smi
   
   # Should show GPU memory usage during inference
   ```

3. **Optimize for CPU-only:**
   ```bash
   # Use CPU-optimized models
   ollama pull llama3.2:3b
   ```

4. **Increase context window (if needed):**
   ```python
   # Reduce context size
   provider = OllamaProvider()
   # Keep prompts under 2000 tokens
   short_prompt = long_text[:2000]
   ```

### Out of Memory (OOM)

**Symptoms:**
```
Error: failed to load model: out of memory
```

**Solutions:**

1. **Use quantized model:**
   ```bash
   # Q4 quantization (smaller)
   ollama pull qwen2.5:7b-q4
   
   # Instead of full precision
   # ollama pull qwen2.5:7b
   ```

2. **Close other applications:**
   - Free up VRAM by closing browsers, games, etc.

3. **Switch to smaller model:**
   ```bash
   ollama pull llama3.2:3b
   ```

4. **Use CPU inference:**
   ```bash
   # Set environment variable
   export OLLAMA_USE_GPU=false
   ```

### Connection Timeout

**Symptoms:**
```
httpx.ConnectTimeout: timed out after 5.0 seconds
```

**Solutions:**

1. **Increase timeout:**
   ```python
   provider = OllamaProvider(timeout=30.0)
   # or set environment variable
   # OLLAMA_TIMEOUT=30.0
   ```

2. **First request is slow:**
   ```python
   # Model loading can take 10-30 seconds
   # Subsequent requests are fast
   provider = OllamaProvider(timeout=60.0)  # Generous for first load
   _ = provider.analyze_text("warmup")  # Warm up model
   ```

### Environment Variable Issues

**Symptoms:**
```
Using default Ollama URL: http://localhost:11434
```

**Solutions:**

1. **Verify .env file is loaded:**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()  # Load .env file
   print(os.getenv("OLLAMA_BASE_URL"))
   ```

2. **Check .env file location:**
   ```bash
   # Should be in project root
   ls -la .env
   ```

3. **Manual override:**
   ```python
   import os
   os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
   
   from asmf.providers import OllamaProvider
   provider = OllamaProvider()
   ```

## Performance Optimization

### GPU Acceleration

**NVIDIA:**
```bash
# Verify CUDA is available
nvidia-smi

# Ollama automatically uses GPU if available
# No configuration needed
```

**AMD:**
```bash
# Install ROCm support
# Ollama supports AMD GPUs via ROCm
```

**Apple Silicon (M1/M2/M3):**
```bash
# Ollama uses Metal by default
# Excellent performance on Apple Silicon
```

### Memory Management

```bash
# Limit number of concurrent requests
# Use smaller batch sizes
# Close models when not in use
ollama rm <model-name>
```

### Model Selection Strategy

1. **Development:** Use `llama3.2:3b` for fast iteration
2. **Testing:** Use `qwen2.5:14b-q4` for balanced quality
3. **Production:** Use `qwen2.5:32b-q4` or cloud provider

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def analyze_cached(text):
    """Cache repeated analyses."""
    return provider.analyze_text(text)
```

## Advanced Configuration

### Custom Model Files

```bash
# Create Modelfile
cat > Modelfile << EOF
FROM qwen2.5:14b-q4
PARAMETER temperature 0.7
PARAMETER top_p 0.9
SYSTEM "You are a patent analysis expert..."
EOF

# Create custom model
ollama create patent-analyzer -f Modelfile

# Use in ASMF
provider = OllamaProvider(model="patent-analyzer")
```

### Remote Ollama

```python
# Connect to Ollama on another machine
provider = OllamaProvider(
    base_url="http://192.168.1.100:11434",
    timeout=10.0
)
```

### Multiple Models

```python
# Use different models for different tasks
fast_provider = OllamaProvider(model="llama3.2:3b")
accurate_provider = OllamaProvider(model="qwen2.5:32b-q4")

# Quick screening
quick_result = fast_provider.analyze_text("Is this relevant?")

if "yes" in quick_result.lower():
    # Detailed analysis
    detailed = accurate_provider.analyze_text("Detailed evaluation...")
```

## Resources

- **Ollama Documentation:** [github.com/ollama/ollama](https://github.com/ollama/ollama)
- **Model Library:** [ollama.ai/library](https://ollama.ai/library)
- **ASMF Documentation:** [docs/CONFIGURATION.md](CONFIGURATION.md)
- **Docker Setup:** [docker-compose.example.yml](../docker-compose.example.yml)

## Getting Help

1. **Check logs:**
   ```bash
   # Ollama logs
   # macOS: ~/Library/Logs/Ollama/server.log
   # Linux: journalctl -u ollama
   # Windows: Event Viewer → Application logs
   ```

2. **ASMF Issues:** [GitHub Issues](https://github.com/vcaboara/ai-search-match-framework/issues)

3. **Ollama Discord:** [discord.gg/ollama](https://discord.gg/ollama)

4. **Enable debug logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

## Next Steps

- [ ] Run setup script: `python scripts/setup_ollama.py`
- [ ] Pull recommended model: `ollama pull qwen2.5:14b-q4`
- [ ] Test integration: `python -c "from asmf.providers import OllamaProvider; print(OllamaProvider().is_available())"`
- [ ] Review [CONFIGURATION.md](CONFIGURATION.md) for more options
- [ ] Check [examples/](../examples/) for usage patterns

---

**Need Help?** Open an issue on [GitHub](https://github.com/vcaboara/ai-search-match-framework/issues) with:
- Your OS and hardware specs
- Ollama version (`ollama --version`)
- ASMF version
- Full error message and stack trace
