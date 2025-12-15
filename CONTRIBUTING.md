# Contributing to AI Search Match Framework (ASMF)

Thank you for your interest in contributing to ASMF! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Commit Conventions](#commit-conventions)
- [AI Attribution Standards](#ai-attribution-standards)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/ai-search-match-framework.git`
3. Add upstream remote: `git remote add upstream https://github.com/vcaboara/ai-search-match-framework.git`
4. Create a feature branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- Git

### Installation

```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=asmf --cov-report=html

# Run specific test file
pytest tests/test_providers.py
```

### Code Formatting

```bash
# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Check with flake8
flake8 src/ tests/
```

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) with special standards for AI-generated contributions.

### Standard Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**Examples:**
```
feat(providers): add support for Claude API
fix(parsers): handle edge case in PDF extraction
docs(readme): update installation instructions
test(analyzers): add unit tests for BaseAnalyzer
```

For complete commit conventions, see [.github/commit-conventions.md](.github/commit-conventions.md).

## AI Attribution Standards

### Why We Track AI Contributions

We track AI-generated commits for two important reasons:

1. **Accessibility Advocacy**: Demonstrate how AI tools improve productivity for developers with accessibility needs
2. **Productivity Metrics**: Measure the impact of AI assistance on development velocity and code quality

### Using the [AI] Prefix

When AI tools (GitHub Copilot, Claude, Gemini, etc.) generate commits, use the `[AI]` prefix:

```
[AI] <type>(<scope>): <subject>

[optional body]

---
AI-Generated-By: <Tool Name> (<Model>)
```

### When to Use [AI]

Use `[AI]` prefix when AI contributed >50% of the intellectual work:

✅ **Use [AI] when:**
- AI generated the majority of code changes
- AI wrote the commit message
- AI suggested the implementation approach
- You used AI pair programming for the entire feature

❌ **Don't use [AI] when:**
- AI only helped with debugging or understanding code
- You significantly modified AI-generated code
- AI contributed a minor portion of changes
- AI only helped with documentation comments

### AI Attribution Examples

```
[AI] feat(providers): add Azure OpenAI provider

Implement AzureOpenAIProvider class with authentication,
rate limiting, and error handling.

---
AI-Generated-By: GitHub Copilot (Claude Sonnet 4.5)
```

```
[AI] fix(parsers): handle malformed PDF headers

Add validation for PDF header structure and gracefully
handle corrupted files with appropriate error messages.

---
AI-Generated-By: GitHub Copilot (GPT-4)
```

### Git Aliases for AI Commits

We provide convenient git aliases to simplify AI commit creation.

#### Setup for Linux/Mac

```bash
# Install the alias
source scripts/git-aliases.sh

# Or add to your shell config (~/.bashrc or ~/.zshrc)
echo 'source /path/to/ai-search-match-framework/scripts/git-aliases.sh' >> ~/.bashrc
```

#### Setup for Windows PowerShell

```powershell
# Install the alias
. .\scripts\git-aliases.ps1

# Or add to your PowerShell profile
Add-Content $PROFILE "`n. `"$PWD\scripts\git-aliases.ps1`""
```

#### Using the Alias

```bash
# Make changes to your code
git add .

# Use the AI commit alias
git aic "feat(providers): add new provider"

# The alias automatically adds the [AI] prefix and attribution footer
```

The alias expands to:
```
[AI] feat(providers): add new provider

---
AI-Generated-By: GitHub Copilot (Claude Sonnet 4.5)
```

### Manual AI Commits

If you prefer not to use the alias:

```bash
git commit -m "[AI] feat(providers): add new provider" \
           -m "---" \
           -m "AI-Generated-By: GitHub Copilot (Claude Sonnet 4.5)"
```

For detailed AI attribution guidelines, see [.github/commit-conventions.md](.github/commit-conventions.md).

## Pull Request Process

1. **Update your branch** with latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Ensure tests pass**:
   ```bash
   pytest
   ```

3. **Run code formatters**:
   ```bash
   black src/ tests/
   isort src/ tests/
   ```

4. **Create pull request**:
   - Use a descriptive title following commit conventions
   - Fill out the PR template completely
   - Reference related issues
   - Add screenshots/examples if applicable

5. **Respond to review feedback** promptly and professionally

6. **Update documentation** if your changes affect usage or APIs

## Coding Standards

### Style Guidelines

- **PEP 8** compliance
- **Type hints** for all public APIs
- **Docstrings** (Google style) for all public functions/classes
- **Black** for formatting (line length 120)
- **isort** for import sorting

### Documentation

- Clear, concise docstrings for all public APIs
- Include parameter descriptions and return types
- Add usage examples for complex functionality
- Update README.md if adding new features

### API Design

- Keep interfaces generic and extensible
- Domain-specific logic should NOT be in this framework
- Configuration via environment variables or constructor args
- Graceful error handling with informative messages

### Example Code Style

```python
from typing import Optional, Dict, Any


class MyProvider(BaseAIProvider):
    """A custom AI provider implementation.
    
    This provider implements the BaseAIProvider interface for
    integrating with a custom AI service.
    
    Args:
        api_key: The API key for authentication
        model: The model name to use (default: "default-model")
        timeout: Request timeout in seconds (default: 30)
        
    Example:
        >>> provider = MyProvider(api_key="key123")
        >>> result = provider.analyze_text("Analyze this")
        >>> print(result.content)
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "default-model",
        timeout: int = 30
    ) -> None:
        """Initialize the provider."""
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
    
    def analyze_text(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """Analyze text using the AI model.
        
        Args:
            prompt: The text prompt to analyze
            context: Optional context dictionary
            
        Returns:
            AnalysisResult containing the analysis
            
        Raises:
            ProviderError: If the API request fails
        """
        # Implementation here
        pass
```

## Testing Guidelines

### Test Coverage

- Aim for >80% code coverage
- Unit tests for all public APIs
- Integration tests for complex workflows
- Mock external APIs (Gemini, Ollama, etc.)

### Test Structure

```python
import pytest
from asmf.providers import MyProvider


class TestMyProvider:
    """Tests for MyProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create a provider instance for testing."""
        return MyProvider(api_key="test_key")
    
    def test_initialization(self, provider):
        """Test provider initializes correctly."""
        assert provider.api_key == "test_key"
        assert provider.model == "default-model"
    
    def test_analyze_text_success(self, provider, mocker):
        """Test successful text analysis."""
        # Mock external API
        mock_response = mocker.Mock()
        mock_response.text = "Analysis result"
        mocker.patch.object(provider, "_make_request", return_value=mock_response)
        
        result = provider.analyze_text("Test prompt")
        assert result.content == "Analysis result"
    
    def test_analyze_text_error(self, provider, mocker):
        """Test error handling in text analysis."""
        mocker.patch.object(provider, "_make_request", side_effect=Exception("API Error"))
        
        with pytest.raises(ProviderError):
            provider.analyze_text("Test prompt")
```

### Running Specific Tests

```bash
# Run specific test file
pytest tests/test_providers.py

# Run specific test class
pytest tests/test_providers.py::TestMyProvider

# Run specific test method
pytest tests/test_providers.py::TestMyProvider::test_analyze_text_success

# Run with verbose output
pytest -v tests/
```

## Questions or Issues?

- **Bug reports**: Open an issue with reproduction steps
- **Feature requests**: Open an issue describing the use case
- **Questions**: Use GitHub Discussions or open an issue

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to ASMF! Your contributions help make AI-powered document analysis accessible to everyone.
