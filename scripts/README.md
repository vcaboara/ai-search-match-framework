# Scripts Directory

This directory contains utility scripts for the AI Search Match Framework.

## Scripts

### ollama_pr_review.py

Automated PR code review script using Ollama LLM.

**Purpose:** Analyzes GitHub pull request code changes using Ollama and posts structured review comments based on CODE_REVIEW_PATTERNS.md.

**Usage:**
```bash
export GITHUB_TOKEN=your_token_here
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen2.5:14b-q4

python scripts/ollama_pr_review.py --repo owner/repo --pr 123
```

**Configuration:**
- `GITHUB_TOKEN`: GitHub Personal Access Token with `repo` scope (required)
- `OLLAMA_BASE_URL`: Ollama API endpoint (default: http://localhost:11434)
- `OLLAMA_MODEL`: Ollama model to use (default: qwen2.5:14b-q4)
- `OLLAMA_TIMEOUT`: Request timeout in seconds (default: 120.0)

**Output:** Formatted markdown review suitable for posting as a PR comment.

**See:** [docs/WEBHOOK_SERVER.md](../docs/WEBHOOK_SERVER.md) for automated webhook setup.

---

### setup_ollama.py

Interactive setup script for installing and configuring Ollama.

**Purpose:** Helps users install Ollama, download models, and configure the framework.

**Usage:**
```bash
python scripts/setup_ollama.py
```

**Features:**
- Detects system architecture and available VRAM
- Recommends appropriate models based on hardware
- Guides through Ollama installation
- Tests provider configuration
- Updates .env file

**See:** [docs/OLLAMA_SETUP.md](../docs/OLLAMA_SETUP.md) for manual setup.

---

### git-aliases.sh / git-aliases.ps1

Git aliases for AI-attributed commits.

**Purpose:** Provide convenient git commands for commits with AI attribution footer.

**Usage (Bash):**
```bash
source scripts/git-aliases.sh
git aic "feat: add new feature"
```

**Usage (PowerShell):**
```powershell
. .\scripts\git-aliases.ps1
git aic "feat: add new feature"
```

**See:** [.github/commit-conventions.md](../.github/commit-conventions.md) for AI commit attribution standards.

---

## Adding New Scripts

When adding new scripts to this directory:

1. Add a shebang line (`#!/usr/bin/env python3` for Python)
2. Include a docstring describing purpose and usage
3. Make the script executable: `chmod +x scripts/your_script.py`
4. Update this README with script documentation
5. Add tests in `tests/` if the script has testable logic
6. Use argparse for CLI arguments
7. Follow project code style (black, isort, ruff)

## Related Documentation

- [docs/WEBHOOK_SERVER.md](../docs/WEBHOOK_SERVER.md) - Webhook server setup
- [docs/OLLAMA_SETUP.md](../docs/OLLAMA_SETUP.md) - Ollama installation
- [.github/commit-conventions.md](../.github/commit-conventions.md) - Commit standards
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
