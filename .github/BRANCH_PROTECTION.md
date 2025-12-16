# Branch Protection Rules

This document outlines the branch protection rules configured for the `main` branch to maintain code quality and security.

## Main Branch Protection Settings

### Required Status Checks
-  Require branches to be up to date before merging
-  Status checks must pass before merging

### Pull Request Requirements
-  **Require pull request reviews before merging**
  - Required approvals: 1
  - Dismiss stale pull request approvals when new commits are pushed
  - Require review from Code Owners (CODEOWNERS file)

-  **Require conversation resolution before merging**
  - All review comments must be resolved before merge

### Additional Restrictions
-  **Restrict who can push to matching branches**
  - Only maintainers can push directly (bypasses PRs)
  - Prevent force pushes
  - Prevent deletions

-  **Do not allow bypassing the above settings**
  - Administrators are subject to the same rules

## How to Configure (GitHub UI)

1. Navigate to: Repository Settings  Branches  Add rule
2. Branch name pattern: `main`
3. Enable the following protections:

### Protect matching branches
- [x] Require a pull request before merging
  - [x] Require approvals: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners
  - [x] Restrict who can dismiss pull request reviews (Maintainers only)
  - [x] Require approval of the most recent reviewable push

- [x] Require status checks to pass before merging
  - [x] Require branches to be up to date before merging
  - Status checks (configured):
    - `Build and Test`
    - `Validate PR`

- [x] Require conversation resolution before merging

- [x] Require signed commits (recommended)

- [x] Require linear history

- [x] Include administrators (no bypass for admins)

- [x] Restrict pushes that create matching branches

### Rules applied to everyone including administrators
- [x] Do not allow bypassing the above settings

## Automated Configuration

Use the provided script to apply branch protection settings via GitHub API:

```bash
# Using PowerShell script
.\scripts\apply-branch-protection.ps1
```

Or manually via GitHub CLI:

```bash
gh api repos/vcaboara/ai-search-match-framework/branches/main/protection \
  --method PUT \
  --input .github/branch-protection.json
```

Or via GitHub UI:
1. Go to https://github.com/vcaboara/ai-search-match-framework/settings/branches
2. Click "Add branch protection rule"
3. Apply settings as listed above

## Benefits

- **Code Quality**: Ensures all code is reviewed before merging
- **Security**: Prevents accidental or malicious direct commits to main
- **Collaboration**: Encourages discussion and knowledge sharing via PRs
- **Traceability**: All changes documented through pull requests
- **CI/CD Integration**: Automated testing before merge

## Workflow

1. Create feature branch from `main`
2. Make changes and commit following [commit conventions](.github/commit-conventions.md)
3. Push branch and open Pull Request
4. Code review by Code Owner (automatically requested)
5. Address review comments, resolve conversations
6. Once approved and CI passes, merge to `main`

## References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [CODEOWNERS Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Pull Request Template](.github/pull_request_template.md)
- [Commit Conventions](.github/commit-conventions.md)
