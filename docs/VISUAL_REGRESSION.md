# Visual Regression Testing

This document describes the visual regression testing feature in ASMF, which enables automated screenshot capture and comparison for UI changes in pull requests.

## Overview

Visual regression testing helps catch unintended visual changes by automatically capturing screenshots before and after code changes. When a PR modifies UI files (HTML, CSS, JS, templates), the system:

1. **Captures screenshots** from the main branch (before)
2. **Captures screenshots** from the PR branch (after)
3. **Generates comparison** data
4. **Posts results** to the PR with artifact links

## Components

### 1. Screenshot Utility (`tools/screenshot_utils.py`)

The core screenshot capture functionality using Playwright:

```python
from tools.screenshot_utils import capture_screenshot, capture_screenshot_async

# Synchronous usage
capture_screenshot(
    url="https://example.com",
    output_path="screenshot.png",
    viewport={"width": 1920, "height": 1080}
)

# Asynchronous usage
await capture_screenshot_async(
    url="https://example.com",
    output_path="screenshot.png",
    viewport={"width": 1280, "height": 720},
    wait_for=".main-content"  # Wait for specific element
)
```

**Features:**
- Full-page screenshots
- Configurable viewport sizes
- Element waiting (CSS selectors)
- Both async and sync interfaces
- CLI interface included

### 2. Configuration (`config/visual-test.yaml`)

Defines pages to screenshot and viewport configurations:

```yaml
base_url: "http://localhost:5000"

viewports:
  desktop:
    width: 1920
    height: 1080
  tablet:
    width: 768
    height: 1024
  mobile:
    width: 375
    height: 667

pages:
  - name: "home"
    path: "/"
    viewports: ["desktop", "tablet", "mobile"]
    wait_for: null
    
  - name: "dashboard"
    path: "/dashboard"
    viewports: ["desktop"]
    wait_for: ".dashboard-container"

settings:
  timeout: 30000
  full_page: true
  diff_threshold: 0.01
  output_dir: "visual-tests"
```

### 3. PR Screenshot Script (`scripts/take_pr_screenshots.py`)

Captures screenshots for a specific branch:

```bash
# Capture from main branch
python scripts/take_pr_screenshots.py --config config/visual-test.yaml --branch main

# Capture from PR branch
python scripts/take_pr_screenshots.py --config config/visual-test.yaml --branch pr

# Override base URL
python scripts/take_pr_screenshots.py \
  --config config/visual-test.yaml \
  --branch pr \
  --base-url http://localhost:8000
```

### 4. GitHub Workflow (`.github/workflows/visual-regression.yml`)

Automatically runs on PRs that modify UI files:

**Triggers:**
- HTML, CSS, JS, JSX, TSX, Vue files
- Template or static directories
- Workflow or config file changes

**Process:**
1. Checkout PR branch
2. Install dependencies and Playwright
3. Capture PR screenshots
4. Checkout main branch
5. Capture main screenshots
6. Compare results
7. Upload artifacts
8. Post PR comment

## Setup

### 1. Install Dependencies

Add Playwright to your project:

```bash
pip install playwright>=1.40.0
playwright install chromium
```

### 2. Configure Pages

Edit `config/visual-test.yaml` to define your pages:

```yaml
pages:
  - name: "my-page"
    path: "/my-page"
    viewports: ["desktop", "mobile"]
    wait_for: ".page-loaded"
```

### 3. Start Your Application

The workflow assumes your application is accessible at the configured `base_url`. You may need to:

- Start a local server in the workflow
- Use a preview environment
- Mock API responses

**Example workflow modification:**

```yaml
- name: Start application server
  run: |
    python app.py &
    sleep 5  # Wait for server
```

## Usage

### Manual Testing

```bash
# Capture screenshots locally
python scripts/take_pr_screenshots.py \
  --config config/visual-test.yaml \
  --branch main \
  --base-url http://localhost:5000
```

### CLI Tool

The screenshot utility has a CLI interface:

```bash
# Basic usage
python -m tools.screenshot_utils https://example.com output.png

# Custom viewport
python -m tools.screenshot_utils https://example.com output.png --width 1280 --height 720

# Wait for element
python -m tools.screenshot_utils https://example.com output.png --wait-for ".content"

# Viewport only (no full page)
python -m tools.screenshot_utils https://example.com output.png --no-full-page
```

### In Python Code

```python
from tools.screenshot_utils import ScreenshotCapture

# Create capture instance
capture = ScreenshotCapture(
    viewport={"width": 1920, "height": 1080},
    timeout=30000
)

# Capture single screenshot
await capture.capture_async(
    url="https://example.com",
    output_path="screenshot.png",
    full_page=True,
    wait_for=".main-content"
)
```

## Workflow Output

When the workflow completes, you'll see a PR comment like:

```
📸 Visual Regression Test Results

Total pages tested: 3
Screenshot pairs captured: 5

Screenshots

Download artifacts to view before/after comparisons:
- Visual Regression Screenshots

Pages captured:
- home: desktop, tablet, mobile
- dashboard: desktop
- analysis: desktop

---
Note: Visual differences require manual review. Download the artifacts to compare screenshots.
```

### Viewing Results

1. Click the workflow run link in the PR comment
2. Download the "visual-regression-screenshots" artifact
3. Extract and review:
   - `*_main.png` - Screenshots from main branch
   - `*_pr.png` - Screenshots from PR branch
   - `results_main.json` - Metadata for main screenshots
   - `results_pr.json` - Metadata for PR screenshots
   - `comparison.json` - Comparison summary

## Advanced Configuration

### Custom Viewports

Add custom viewports in `config/visual-test.yaml`:

```yaml
viewports:
  ultrawide:
    width: 2560
    height: 1440
  4k:
    width: 3840
    height: 2160
```

### Conditional Elements

Wait for specific elements before capturing:

```yaml
pages:
  - name: "slow-page"
    path: "/slow"
    wait_for: "#data-loaded"  # Wait for this element
```

### Multiple Environments

Use environment variables to test different environments:

```bash
python scripts/take_pr_screenshots.py \
  --config config/visual-test.yaml \
  --branch pr \
  --base-url "$PREVIEW_URL"
```

### Parallel Execution

Modify the script to capture screenshots in parallel for faster execution:

```python
import asyncio

async def capture_all():
    tasks = [
        capture.capture_async(url1, output1),
        capture.capture_async(url2, output2),
        capture.capture_async(url3, output3),
    ]
    await asyncio.gather(*tasks)
```

## Integration with Downstream Projects

Downstream projects using ASMF can enable visual regression testing:

### 1. Install ASMF with Playwright

```bash
pip install "ai-search-match-framework[dev]"
playwright install chromium
```

### 2. Copy Configuration

Copy `config/visual-test.yaml` to your project and customize:

```yaml
base_url: "http://localhost:8080"  # Your app URL

pages:
  - name: "your-page"
    path: "/your-route"
    viewports: ["desktop"]
```

### 3. Copy Workflow

Copy `.github/workflows/visual-regression.yml` and adjust paths:

```yaml
- name: Start your application
  run: |
    python your_app.py &
    sleep 5
```

### 4. Use ASMF Tools

Import screenshot utilities from ASMF:

```python
from asmf.tools.screenshot_utils import capture_screenshot

# Your testing code
```

## Troubleshooting

### Screenshots Fail to Capture

**Issue:** Timeout errors or blank screenshots

**Solutions:**
- Increase timeout in config: `settings.timeout: 60000`
- Add `wait_for` selector to ensure page is loaded
- Check application logs for errors

### Workflow Doesn't Trigger

**Issue:** No workflow runs on PR

**Solutions:**
- Verify PR modifies UI files (HTML, CSS, JS, etc.)
- Check workflow file path: `.github/workflows/visual-regression.yml`
- Ensure workflow is on the target branch

### Missing Dependencies

**Issue:** Playwright not found

**Solutions:**
```bash
pip install playwright>=1.40.0
playwright install chromium
playwright install-deps chromium  # System dependencies
```

### Application Not Running

**Issue:** Connection refused errors

**Solutions:**
- Add application startup to workflow
- Use preview environment URL
- Check port configuration

## Best Practices

1. **Minimal Screenshots**: Only capture pages likely to have visual changes
2. **Stable Selectors**: Use reliable CSS selectors for `wait_for`
3. **Appropriate Timeouts**: Balance between reliability and speed
4. **Version Control**: Commit config changes with UI changes
5. **Manual Review**: Always review visual changes, don't rely solely on automation

## Limitations

- **Manual Comparison**: Automated visual diff not implemented (future enhancement)
- **Server Required**: Requires running application server
- **No Baseline**: Doesn't store baseline screenshots (uses main branch)
- **Single Browser**: Only tests Chromium (can be extended to Firefox/WebKit)

## Future Enhancements

- Automated visual diff with pixel comparison
- Integration with visual diff services (Percy, Chromatic, Argos)
- Baseline screenshot storage
- Multi-browser support (Firefox, Safari)
- Responsive design testing automation
- Integration with Playwright Test Runner

## Related Documentation

- [Playwright Python Docs](https://playwright.dev/python/)
- [GitHub Actions Artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
- [ASMF Contributing Guide](../CONTRIBUTING.md)

## Support

For issues or questions:
1. Check [troubleshooting section](#troubleshooting)
2. Review [examples](../examples/)
3. Open an issue on GitHub
