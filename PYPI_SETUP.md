# PyPI Setup Instructions

Follow these steps to complete the PyPI publishing setup:

## Step 1: Configure PyPI Trusted Publishing

1. **Go to PyPI** and sign in:
   https://pypi.org/manage/account/publishing/

2. **Add a new pending publisher**:
   - Click "Add a new pending publisher"
   - Fill in the form:
     - **PyPI Project Name**: `ai-search-match-framework`
     - **Owner**: `vcaboara`
     - **Repository name**: `ai-search-match-framework`  
     - **Workflow name**: `publish.yml`
     - **Environment name**: `pypi`
   - Click "Add"

   This allows GitHub Actions to publish to PyPI without API tokens.

## Step 2: Create GitHub Environment

1. **Go to GitHub repository settings**:
   https://github.com/vcaboara/ai-search-match-framework/settings/environments

2. **Create new environment**:
   - Click "New environment"
   - Name: `pypi`
   - Click "Configure environment"

3. **(Optional) Add protection rules**:
   - Required reviewers: Add yourself if you want manual approval
   - Wait timer: Add delay if desired
   - Click "Save protection rules"

## Step 3: Test the Publishing Workflow

Once the above steps are complete:

1. **Edit the v0.2.0 release**:
   https://github.com/vcaboara/ai-search-match-framework/releases/tag/v0.2.0

2. **Re-publish the release**:
   - The release should already be published, but if you want to trigger the workflow:
   - Click "Edit release"
   - Make a minor change (e.g., add a line to the description)
   - Click "Update release"

3. **Watch the workflow run**:
   https://github.com/vcaboara/ai-search-match-framework/actions/workflows/publish.yml

4. **Verify on PyPI** (after workflow completes):
   https://pypi.org/project/ai-search-match-framework/

## Troubleshooting

### If publishing fails with "403 Forbidden":
- Double-check all fields in PyPI Trusted Publishing match exactly
- Ensure the GitHub environment name is exactly `pypi`
- Verify the workflow name is `publish.yml` (not `.github/workflows/publish.yml`)

### If the workflow doesn't trigger:
- The workflow only runs on release publications (not draft releases)
- Make sure v0.2.0 is published (not in draft state)

### To trigger manually:
- Create a new release from an existing tag
- Or edit and re-save an existing published release

## After First Successful Publish

Once v0.2.0 is successfully published:

1. Test installation:
   ```bash
   pip install ai-search-match-framework
   python -c "import asmf; print('Success!')"
   ```

2. For future releases:
   - Update version in `pyproject.toml`
   - Merge to main (auto-creates tag and release)
   - Publishing happens automatically!

## Links

- PyPI Project: https://pypi.org/project/ai-search-match-framework/
- GitHub Releases: https://github.com/vcaboara/ai-search-match-framework/releases
- Actions: https://github.com/vcaboara/ai-search-match-framework/actions
- Publishing Docs: [docs/PUBLISHING.md](../docs/PUBLISHING.md)
