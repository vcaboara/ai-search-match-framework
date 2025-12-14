# Publishing to PyPI

This document describes the automated publishing process for the AI Search Match Framework.

## Overview

The framework uses GitHub Actions with PyPI Trusted Publishing for secure, automated releases.

## Publishing Process

### 1. Automatic Tagging (On Merge to Main)

When code is merged to `main`, the `release.yml` workflow automatically:
- Extracts version from `pyproject.toml`
- Creates a git tag (e.g., `v0.2.0`)
- Creates a GitHub Release with auto-generated notes

### 2. Automated PyPI Publishing (On Release)

When a GitHub Release is published, the `publish.yml` workflow:

1. **Pre-publish Tests**: Runs full test suite to ensure package quality
2. **Version Validation**: Verifies `pyproject.toml` version matches the git tag
3. **Build**: Creates source distribution (.tar.gz) and wheel (.whl) files
4. **Package Validation**: Checks package metadata and structure with `twine check`
5. **Publish**: Uploads to PyPI using Trusted Publishing (no API tokens needed)

## Setup Requirements

### One-Time PyPI Setup

1. **Configure Trusted Publishing on PyPI**:
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new "pending publisher":
     - PyPI Project Name: `ai-search-match-framework`
     - Owner: `vcaboara`
     - Repository name: `ai-search-match-framework`
     - Workflow name: `publish.yml`
     - Environment name: `pypi`

2. **Create PyPI Environment in GitHub**:
   - Go to repository Settings → Environments
   - Create environment named `pypi`
   - Optional: Add protection rules (e.g., required reviewers)

## Publishing Workflow

### Normal Release Process

1. **Update Version**:
   ```bash
   # Edit pyproject.toml version field
   version = "0.3.0"
   ```

2. **Create PR with Changes**:
   ```bash
   git checkout -b release/v0.3.0
   git add pyproject.toml
   git commit -m "chore: bump version to 0.3.0"
   git push origin release/v0.3.0
   # Create PR and get it reviewed
   ```

3. **Merge to Main**:
   - Merge the PR to `main`
   - `release.yml` automatically creates tag `v0.3.0` and GitHub Release

4. **Publish to PyPI**:
   - Go to GitHub Releases
   - Edit the auto-created release (or create manually if needed)
   - Click "Publish release"
   - `publish.yml` runs and publishes to PyPI

### Manual Release (If Needed)

If automatic tagging fails, create manually:

```bash
git tag -a v0.3.0 -m "Release v0.3.0"
git push origin v0.3.0
```

Then create GitHub Release from the tag.

## Testing Locally

Before releasing, test the build locally:

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Inspect contents
tar -tzf dist/ai-search-match-framework-*.tar.gz
unzip -l dist/ai_search_match_framework-*.whl

# Test installation locally
pip install dist/ai_search_match_framework-*.whl
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality, backward compatible
- **PATCH** version (0.0.X): Bug fixes, backward compatible

Examples:
- `0.1.0`: Initial development releases
- `0.2.0`: Added new features (BaseAnalyzer, CI/CD)
- `0.2.1`: Bug fixes
- `1.0.0`: First stable release

## Troubleshooting

### Publishing Fails with "403 Forbidden"

- Verify Trusted Publishing is configured correctly on PyPI
- Check that the workflow name and environment match exactly
- Ensure the release is published (not draft)

### Version Mismatch Error

- Ensure `pyproject.toml` version matches the git tag (without 'v' prefix)
- Tag format: `v0.2.0`, pyproject.toml: `version = "0.2.0"`

### Tests Fail Before Publishing

- Publishing is blocked until all tests pass
- Fix issues and create a new release after merging fixes

## Security Notes

- **No API Tokens**: Uses PyPI Trusted Publishing (OIDC)
- **No Secrets**: All authentication via GitHub's OIDC provider
- **Environment Protection**: Use GitHub environment protection rules for production
- **PII Check**: Automated checks ensure no credentials in repository

## Monitoring

After publishing:

1. **Verify on PyPI**: https://pypi.org/project/ai-search-match-framework/
2. **Test Installation**: `pip install ai-search-match-framework`
3. **Check GitHub Actions**: Review workflow run logs
4. **Verify Package**: Import and test in clean environment

## Rollback

If a bad version is published:

1. **Yank the release on PyPI** (makes it unavailable for new installs)
2. **Fix the issue** in a new version
3. **Publish a patch release** (e.g., 0.2.1)

Note: PyPI does not allow deleting or replacing existing versions.
