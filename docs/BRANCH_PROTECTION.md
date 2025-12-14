# Branch Protection Configuration

## Current Settings (Main Branch)

**Status:** ✅ Enabled

### Pull Request Requirements
- **Required approving reviews:** 0 (allows self-approval for sole maintainer)
- **Dismiss stale reviews:** No
- **Require code owner reviews:** No
- **Require review from last push:** No

### Additional Protections
- **Enforce admins:** No (admins bypass protection)
- **Require linear history:** No
- **Allow force pushes:** No ❌
- **Allow deletions:** No ❌
- **Block creations:** No
- **Require conversation resolution:** No
- **Required status checks:** None (CI runs but isn't required)
- **Lock branch:** No

## What This Means

### ✅ Enforced
1. **All changes must go through PRs** - No direct pushes to main
2. **Force pushes are blocked** - History cannot be rewritten
3. **Branch deletion is blocked** - Main cannot be deleted

### ⚠️ Not Enforced
1. **CI passing** - Tests don't have to pass to merge
2. **Admin bypass** - Repository admins (you) can bypass if needed
3. **Self-approval** - You can approve your own PRs (reasonable for solo maintainer)

## Recommended Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/my-feature
   ```

3. **Create PR via GitHub or CLI:**
   ```bash
   gh pr create --title "Add new feature" --body "Description"
   ```

4. **Wait for CI to pass** (optional but recommended)

5. **Self-approve and merge:**
   ```bash
   gh pr review --approve
   gh pr merge --squash
   ```

6. **Delete branch:**
   ```bash
   git branch -d feature/my-feature
   git push origin --delete feature/my-feature
   ```

## Future Enhancements

As the project grows, consider:

1. **Require status checks:** Make CI passing mandatory
   ```bash
   # Add after CI workflow is stable
   gh api repos/vcaboara/ai-search-match-framework/branches/main/protection -X PUT \
     --field required_status_checks[strict]=true \
     --field required_status_checks[contexts][]=test
   ```

2. **Add collaborators:** When you have contributors
   ```bash
   # Require 1 approval from others
   gh api repos/vcaboara/ai-search-match-framework/branches/main/protection/required_pull_request_reviews -X PATCH \
     --field required_approving_review_count=1
   ```

3. **Enforce admins:** Remove ability to bypass protection
   ```bash
   gh api repos/vcaboara/ai-search-match-framework/branches/main/protection/enforce_admins -X POST
   ```

## Emergency Override

If you need to bypass protection (emergencies only):

1. Temporarily disable protection:
   ```bash
   gh api repos/vcaboara/ai-search-match-framework/branches/main/protection -X DELETE
   ```

2. Make emergency fix:
   ```bash
   git add .
   git commit -m "fix: emergency hotfix"
   git push origin main
   ```

3. Re-enable protection:
   ```bash
   # Run the original setup command from this doc
   ```

## Verification

Check current protection status:
```bash
gh api repos/vcaboara/ai-search-match-framework/branches/main/protection | jq
```

Try direct push (should fail):
```bash
git push origin main
# Error: GH006: Protected branch update failed
```

## Documentation

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub API Reference](https://docs.github.com/en/rest/branches/branch-protection)
