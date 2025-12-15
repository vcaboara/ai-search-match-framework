# AI-Assisted Development Workflow

## Architecture Overview

This framework provides automated development workflows with multiple AI providers for different tasks.

## AI Provider Responsibilities

### GitHub Copilot (First Drafts Only)
- **Purpose**: Initial code generation via GitHub Copilot Workspace
- **When**: Creating new features, implementing issues
- **How**: Assign issues to Copilot, it creates draft PRs
- **NOT for**: Code review loops

### Ollama (Primary Code Reviews)
- **Purpose**: Code review and quality checks
- **Models**: DeepSeek Coder 6.7B, Qwen2.5:14b (configurable)
- **When**: PR reviews, automated quality checks
- **Benefits**: Local, free, customizable, can be fine-tuned
- **Trigger**: '@copilot review' or '@ai-review' comment on PRs

### Gemini Flash 2.5 (Primary Review Fallback)
- **Purpose**: Advanced code review when Ollama unavailable
- **When**: API quota available, complex reviews
- **Benefits**: Fast, cost-effective, good reasoning

### OpenAI GPT-4o (Secondary Fallback)
- **Purpose**: Backup when Gemini and Ollama fail
- **When**: Critical reviews, API quota available

## Workflows

### 1. AI PR Review (.github/workflows/ai-pr-review.yml)
**Trigger**: Comment '@copilot review' or '@ai-review' on PR

**Process**:
1. Fetches PR diff and comments
2. Analyzes changed files (Python, JS/TS, HTML, CSS)
3. Runs review through AI provider chain:
   - Try Gemini Flash 2.5
   - Fallback to OpenAI GPT-4o
   - Fallback to Ollama DeepSeek Coder
4. Posts review as PR comment

**Required Secrets**:
- `GEMINI_API_KEY`
- `OPENAI_API_KEY` (optional)
- `OLLAMA_BASE_URL` (optional, defaults to localhost)

### 2. Autonomous Execution (.github/workflows/autonomous-execution.yml)
**Trigger**: Schedule (every 2 hours) or manual

**Process**:
1. Scans issues and PRs
2. Prioritizes tasks
3. Executes work autonomously
4. Creates PRs with changes
5. Reports completion

**Use Cases**:
- Automated dependency updates
- Documentation generation
- Test coverage improvements
- Code refactoring

### 3. AI Task Dispatcher (.github/workflows/ai-task-dispatcher.yml)
**Trigger**: Issue labeled 'ai-task'

**Process**:
1. Routes task to appropriate AI provider
2. Executes task
3. Creates PR or updates issue
4. Tags for human review

### 4. Auto-Revert on Failure (.github/workflows/auto-revert-on-failure.yml)
**Trigger**: CI failure on main branch

**Process**:
1. Detects CI failure
2. Identifies failing commit
3. Creates revert PR automatically
4. Notifies team

## Development Flow

### Standard PR Flow (Human-Driven)
1. Create issue describing feature/bug
2. Develop locally or with Copilot IDE assistance
3. Create PR
4. Comment '@copilot review' for AI review
5. Address feedback
6. Human approval + merge

### Autonomous PR Flow (AI-Driven)
1. Create issue labeled 'ai-task'
2. Copilot creates draft PR (first draft)
3. Automatic Ollama/Gemini review runs
4. If approved, human does final review
5. Merge

### Training Custom Models
For domain-specific work (e.g., patent analysis):
1. Collect domain documents (patents, papers)
2. Extract knowledge with learning pipeline
3. Fine-tune Ollama model on domain data
4. Deploy fine-tuned model for reviews
5. Continuous learning from new documents

## Configuration

### Ollama Setup
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull deepseek-coder:6.7b
ollama pull qwen2.5:14b

# Serve (for webhooks)
ollama serve
```

### Secrets Required
- `GEMINI_API_KEY`: Google AI Studio API key
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `GITHUB_TOKEN`: Automatically provided
- `OLLAMA_BASE_URL`: URL to Ollama server (optional, default: localhost)

### Webhook Server (Optional)
For real-time Ollama reviews on PR events:
```bash
docker-compose up webhook
```

See [WEBHOOK_SERVER.md](WEBHOOK_SERVER.md) for details.

## Best Practices

1. **Copilot for drafts**: Use GitHub Copilot Workspace for initial implementation
2. **Ollama for reviews**: Primary review tool, fast and local
3. **Gemini for complex**: Fallback for advanced reasoning
4. **Human final approval**: Always required before merge
5. **Fine-tune models**: For domain-specific expertise (patents, grants, etc.)
6. **Continuous learning**: Feed new documents into knowledge base

## Downstream Projects

This framework is reusable across projects:
- **ai-patent-eval**: Patent analysis and evaluation
- **job-lead-finder**: Job search automation
- **ai-grant-finder**: Grant discovery and matching

Use reusable workflows (.github/workflows-reusable/) to inherit CI, tagging, and auto-merge capabilities.

## Training Patent Review Models

For patent-specific reviews (see ai-patent-eval Issue #27):

1. **Data Collection**: Scrape 100+ patents in domain using scripts/discover_patents.py
2. **Knowledge Extraction**: Run PatentLearner to extract concepts
3. **Training Format**: Convert knowledge_base.json to instruction-tuning format
4. **Fine-tuning**: Use Ollama's built-in fine-tuning or export to GGUF
5. **Deployment**: Load fine-tuned model in webhook server
6. **Continuous Learning**: Weekly updates with new patents

This creates domain-expert models that can review patent claims for technical accuracy, prior art conflicts, and claim quality without expensive API calls.
