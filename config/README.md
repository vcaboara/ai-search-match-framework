# Configuration Files

This directory contains configuration files for various ASMF features.

## Visual Regression Testing

### `visual-test.yaml`

Default configuration for visual regression testing. This file defines:
- Pages to screenshot
- Viewport sizes (desktop, tablet, mobile)
- Screenshot settings (timeout, full-page, format)
- UI file patterns that trigger visual regression testing

**Usage:**
```bash
python scripts/take_pr_screenshots.py --config config/visual-test.yaml --branch main
```

### `visual-test.example.yaml`

Minimal example configuration for downstream projects. Copy this to your project and customize:

```bash
cp config/visual-test.example.yaml your-project/config/visual-test.yaml
```

## Documentation

For detailed information about visual regression testing, see:
- [docs/VISUAL_REGRESSION.md](../docs/VISUAL_REGRESSION.md) - Complete guide
- [tools/screenshot_utils.py](../tools/screenshot_utils.py) - Screenshot utility API
- [scripts/take_pr_screenshots.py](../scripts/take_pr_screenshots.py) - PR screenshot script

## Adding New Configuration

When adding new configuration files:
1. Document the configuration format in comments
2. Provide an example file (`.example.yaml` or `.example.json`)
3. Update this README
4. Add validation in the consuming code
