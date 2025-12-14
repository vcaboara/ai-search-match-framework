# Downstream Project Workflow

## Overview

This framework (ASMF) is designed to be used by downstream projects (e.g., ai-patent-eval, ai-grant-finder). When a downstream project needs a feature or fix from ASMF, follow this workflow.

## For Downstream Project Maintainers

### 1. Identify the Need

When your project needs something from ASMF:
- New feature (e.g., new parser, analyzer capability)
- Bug fix (something broken in ASMF)
- API change (existing interface needs modification)
- Performance improvement

### 2. Create a Downstream Request Issue

Go to: https://github.com/vcaboara/ai-search-match-framework/issues/new/choose

Select: **Downstream Project Request**

Fill out:
- **Project Name:** Your project name
- **Repository:** Link to your repo
- **Issue/PR Link:** Link to the blocked issue/PR in your project
- **Request Type:** Feature/Bug/API change/etc.
- **Priority:** High (blocking) / Medium / Low
- **Description:** What you need and why

### 3. Automated Response

The `downstream-request.yml` workflow will:
- ✅ Add appropriate labels (`downstream`, `priority:high` if blocking)
- 💬 Post a comment with next steps
- 🔗 Extract and link to your downstream repo/issue

### 4. Implementation Options

**Option A: Wait for Maintainer**
- Maintainer will triage and implement
- Track progress on the issue

**Option B: Implement Yourself**
1. Fork ASMF repo
2. Create feature branch: `git checkout -b feature/your-feature`
3. Implement the change
4. Add tests (maintain 75%+ coverage)
5. Create PR linking to the downstream request issue
6. Wait for review and merge

### 5. After Merge

1. **Version Bump:** Maintainer updates version in `pyproject.toml`
2. **Release:** Create GitHub release with new version tag
3. **Auto-Publish:** PyPI publish workflow auto-triggers
4. **Update Downstream:** 
   ```bash
   pip install --upgrade ai-search-match-framework
   # or pin specific version in pyproject.toml
   ai-search-match-framework = "^0.3.0"
   ```

## For ASMF Maintainers

### Triaging Downstream Requests

1. **Review the Issue**
   - Does it fit ASMF's scope? (reusable, domain-agnostic)
   - Is it a breaking change?
   - What's the priority?

2. **Accept or Decline**
   ```bash
   # Accept
   gh issue edit <number> --add-label "accepted" --add-assignee @me
   
   # Decline (with explanation)
   gh issue close <number> --comment "Thanks for the request, but this is better suited for the downstream project because..."
   ```

3. **Implement**
   - Create branch from issue: `git checkout -b feature/<issue-number>-short-description`
   - Implement with tests
   - Create PR with `Closes #<issue-number>`
   - Wait for CI to pass
   - Merge to main

4. **Release**
   ```bash
   # Update version in pyproject.toml
   vim pyproject.toml  # bump version
   
   # Update CHANGELOG
   vim CHANGELOG.md  # add changes
   
   # Create PR or commit directly (if you have admin override)
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: bump version to 0.3.0"
   git push origin main
   
   # Create release (triggers PyPI publish)
   gh release create v0.3.0 --title "v0.3.0" --notes "See CHANGELOG.md"
   ```

5. **Notify Downstream**
   ```bash
   gh issue comment <number> --body "✅ Released in v0.3.0! Update with: \`pip install --upgrade ai-search-match-framework\`"
   ```

## Workflow Diagram

```
Downstream Project
        ↓
    (needs feature)
        ↓
Create Issue in ASMF
  (downstream label)
        ↓
    Automation
  (auto-labels,
   auto-comments)
        ↓
    Triage
  (accept/decline)
        ↓
  Implement
 (PR + tests)
        ↓
  Merge to main
        ↓
  Bump version
  Update CHANGELOG
        ↓
  Create Release
        ↓
  Auto-Publish
   to PyPI
        ↓
Downstream updates
  dependency version
        ↓
   Unblocked!
```

## Labels

- `downstream` - Request from downstream project
- `priority:high` - Blocking a downstream project
- `priority:medium` - Has workaround
- `priority:low` - Nice to have
- `accepted` - Will be implemented
- `breaking-change` - Requires major version bump
- `good-first-issue` - Easy for contributors

## Version Strategy

- **Patch (0.2.x):** Bug fixes, no API changes
- **Minor (0.x.0):** New features, backward compatible
- **Major (x.0.0):** Breaking changes

## Communication

- **Issue Comments:** All coordination happens on the downstream request issue
- **PR References:** Link PRs to issues with `Closes #<number>` or `Fixes #<number>`
- **Release Notes:** CHANGELOG.md tracks all changes

## Examples

### Example 1: New Parser Needed

**Downstream:** ai-grant-finder needs to parse RFP PDFs  
**Request:** "Add RFPParser to extract grant requirements"  
**Priority:** High (blocking development)  
**Outcome:** 
1. Issue created with downstream label
2. Maintainer accepts and implements
3. Merged in PR #15
4. Released as v0.3.0
5. ai-grant-finder updates: `ai-search-match-framework = "^0.3.0"`

### Example 2: API Change

**Downstream:** ai-patent-eval needs batch scoring  
**Request:** "Add batch_score() method to BaseAnalyzer"  
**Priority:** Medium (can loop manually for now)  
**Outcome:**
1. Downstream maintainer forks and implements
2. PR created with tests
3. Reviewed and merged
4. Released as v0.3.0 (minor bump, not breaking)

### Example 3: Bug Fix

**Downstream:** ai-contract-analyzer crashes on certain PDFs  
**Request:** "PDFParser fails on password-protected PDFs"  
**Priority:** High (production issue)  
**Outcome:**
1. Fast-tracked implementation
2. Hotfix released as v0.2.1 (patch bump)
3. Downstream updates immediately

## Automation Features

Current automation:
- ✅ Auto-labeling (`downstream`, `priority:high`)
- ✅ Auto-commenting with next steps
- ✅ Linking to downstream resources
- ✅ Auto-merge for Dependabot PRs
- ✅ Auto-publish to PyPI on release

Potential future automation:
- 🔄 Auto-create branch from issue
- 🔄 Auto-notify downstream when released
- 🔄 Auto-generate PR from issue template
- 🔄 Integration testing with downstream projects

## Best Practices

1. **Keep ASMF Generic:** Domain-specific logic stays in downstream projects
2. **Test Everything:** Maintain 75%+ coverage
3. **Version Carefully:** Follow semver strictly
4. **Document Changes:** Update CHANGELOG.md
5. **Communicate Clearly:** Keep downstream informed
6. **Fast Response:** Triage within 24 hours for high-priority

## Questions?

- Check [.github/copilot-instructions.md](.github/copilot-instructions.md) for development guidelines
- Review [docs/PUBLISHING.md](PUBLISHING.md) for release process
- Open a discussion in GitHub Discussions (if enabled)
