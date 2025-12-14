# Pre-Release Checklist

Use this checklist before publishing a new release.

## Code Quality

- [ ] All tests pass locally (`pytest`)
- [ ] Coverage meets threshold (≥75%)
- [ ] No linting errors (`black --check`, `isort --check`, `flake8`)
- [ ] Type checking passes (`mypy src/asmf --strict`)
- [ ] No merge conflicts

## Documentation

- [ ] README.md is up to date
- [ ] CHANGELOG.md updated with new version
- [ ] API documentation reflects changes
- [ ] Examples work with new version
- [ ] Migration guide (if breaking changes)

## Version & Metadata

- [ ] Version bumped in `pyproject.toml`
- [ ] Version follows semantic versioning
- [ ] Dependencies are pinned appropriately
- [ ] License information is current
- [ ] Author information is correct

## Security & Privacy

- [ ] No API keys or secrets in code
- [ ] No PII beyond public contact info
- [ ] `.gitignore` covers sensitive files
- [ ] Dependencies have no known vulnerabilities
- [ ] Environment variables documented

## Testing

- [ ] Unit tests cover new functionality
- [ ] Integration tests pass
- [ ] Examples run successfully
- [ ] Fresh install works: `pip install -e .`
- [ ] Docker build succeeds

## CI/CD

- [ ] GitHub Actions workflows pass
- [ ] All PR checks are green
- [ ] No draft commits or WIP code
- [ ] Branch is up to date with main

## Release Notes

- [ ] GitHub Release notes prepared
- [ ] Breaking changes highlighted
- [ ] Migration instructions clear
- [ ] Contributors acknowledged

## Post-Release

After publishing to PyPI:

- [ ] Verify package on PyPI
- [ ] Test fresh install: `pip install ai-search-match-framework`
- [ ] Check package imports work
- [ ] Update downstream projects (e.g., job-lead-finder)
- [ ] Announce release (if applicable)

## Emergency Rollback

If issues are found after release:

1. Yank the version on PyPI (don't delete)
2. Fix the issue immediately
3. Publish a patch release
4. Document the issue and fix
