# Reusable GitHub Actions Workflows

This directory contains reusable workflows that can be shared across downstream projects.

## Available Workflows

### `auto-tag.yml` - Semantic Auto-Tagging

Automatically creates version tags based on commit messages.

**Usage in downstream projects:**
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

jobs:
  auto-tag:
    uses: vcaboara/ai-search-match-framework/.github/workflows-reusable/auto-tag.yml@main
    secrets:
      github-token: ${{ secrets.GITHUB_TOKEN }}
```

**Versioning Rules:**
- **MAJOR**: `BREAKING CHANGE`, `major:`, `[major]` → v1.0.0 → v2.0.0
- **MINOR**: `feat:`, `feature:`, `minor:` → v1.0.0 → v1.1.0
- **PATCH**: All other commits → v1.0.0 → v1.0.1

**Inputs:**
- `bump-major-pattern`: Regex for major bumps (optional)
- `bump-minor-pattern`: Regex for minor bumps (optional)

### `dependabot-auto-merge.yml` - Dependabot Auto-Merge

Automatically merges dependabot PRs when checks pass.

**Usage:**
```yaml
# .github/workflows/dependabot.yml
name: Dependabot Auto-Merge

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
  pull_request_review:
    types: [submitted]
  check_suite:
    types: [completed]

jobs:
  auto-merge:
    uses: vcaboara/ai-search-match-framework/.github/workflows-reusable/dependabot-auto-merge.yml@main
    secrets:
      github-token: ${{ secrets.GITHUB_TOKEN }}
```

**Inputs:**
- `auto-merge-dependabot`: Enable auto-merge (default: true)

## Implementation in Downstream Projects

### Option 1: Use Reusable Workflows (Recommended)

Replace local workflows with calls to ASMF reusable workflows:

```yaml
# Old: .github/workflows/auto-tag.yml (50+ lines)
# New: Just call the reusable workflow (10 lines)
jobs:
  auto-tag:
    uses: vcaboara/ai-search-match-framework/.github/workflows-reusable/auto-tag.yml@main
```

**Benefits:**
- ✅ Single source of truth for workflow logic
- ✅ Bug fixes propagate automatically
- ✅ Consistent behavior across all projects
- ✅ Reduced maintenance overhead

### Option 2: Copy Workflows Locally

For projects that need customization:

```bash
# Copy to your project
cp .github/workflows-reusable/auto-tag.yml .github/workflows/auto-tag.yml
# Customize as needed
```

## Version Pinning

### Use Latest (Auto-Update)
```yaml
uses: vcaboara/ai-search-match-framework/.github/workflows-reusable/auto-tag.yml@main
```

### Pin to Specific Version (Stable)
```yaml
uses: vcaboara/ai-search-match-framework/.github/workflows-reusable/auto-tag.yml@v1.0.0
```

### Pin to Commit SHA (Most Secure)
```yaml
uses: vcaboara/ai-search-match-framework/.github/workflows-reusable/auto-tag.yml@48cb60b
```

## Testing Reusable Workflows

Test in ASMF first:
```yaml
# .github/workflows/test-reusable.yml
name: Test Reusable Workflows

on: [workflow_dispatch]

jobs:
  test-auto-tag:
    uses: ./.github/workflows-reusable/auto-tag.yml
```

## Downstream Projects

- **ai-patent-eval-standalone**: Patent analysis framework
- **job-lead-finder**: Job application tracking
- **ai-grant-finder**: Grant opportunity discovery

## Contributing

When updating reusable workflows:
1. Create a PR in ASMF
2. Test with `workflow_dispatch` trigger
3. Version bump after merge (v1.0.0 → v1.1.0)
4. Downstream projects auto-update if using `@main`

## References

- [GitHub Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Conventional Commits](https://www.conventionalcommits.org/)
