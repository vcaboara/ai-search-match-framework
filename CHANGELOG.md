# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-12-18

### Added
- Automated PyPI publishing via GitHub Actions
- Version synchronization between pyproject.toml and git tags
- Enhanced auto-tag workflow to read version from pyproject.toml

### Changed
- Publishing process now fully automated on merge to main
- No manual tagging required for releases

## [0.2.0] - 2025-12-14

### Added
- BaseAnalyzer abstract class for domain-specific analyzers
- Automated CI/CD with GitHub Actions
- Docker-based testing with pytest-xdist for parallel execution
- Automated version tagging and GitHub Releases
- PyPI publishing workflow with trusted publishing
- Security scanning (Bandit, pip-audit, TruffleHog)
- Comprehensive documentation (PUBLISHING.md, RELEASE_CHECKLIST.md)
- Code coverage reporting (75% minimum threshold)
- Multi-version Python testing (3.10, 3.11, 3.12)

### Changed
- Restructured project: moved app code to `examples/job_finder/`
- Rewrote README focusing on framework (not job application)
- Updated metadata in pyproject.toml (author, keywords, URLs)
- Improved PDF parser title extraction logic
- Enhanced provider tests with comprehensive mocking

### Fixed
- PDF parser now correctly handles all-caps titles
- PDF parser returns empty list instead of error when claims missing

## [0.1.0] - 2024-XX-XX

### Added
- Initial framework structure
- AI Provider system (Gemini, Ollama)
- PDF parsing for patent documents
- Basic analyzers
- Test suite with pytest
- Example job finder application

[0.2.0]: https://github.com/vcaboara/ai-search-match-framework/releases/tag/v0.2.0
[0.1.0]: https://github.com/vcaboara/ai-search-match-framework/releases/tag/v0.1.0
