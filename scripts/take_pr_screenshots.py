#!/usr/bin/env python3
"""Script to capture PR screenshots for visual regression testing.

This script is designed to be run in a GitHub Actions workflow to capture
screenshots before and after PR changes for visual comparison.

Usage:
    python scripts/take_pr_screenshots.py --config config/visual-test.yaml --branch main
    python scripts/take_pr_screenshots.py --config config/visual-test.yaml --branch pr
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.screenshot_utils import ScreenshotCapture


async def capture_page_screenshots(
    capture: ScreenshotCapture,
    base_url: str,
    page_config: dict[str, Any],
    viewports: dict[str, dict[str, int]],
    output_dir: Path,
    branch: str,
) -> list[dict[str, str]]:
    """Capture screenshots for a single page across multiple viewports.

    Args:
        capture: ScreenshotCapture instance
        base_url: Base URL of the application
        page_config: Page configuration from visual-test.yaml
        viewports: Viewport configurations
        output_dir: Output directory for screenshots
        branch: Branch name (main or pr)

    Returns:
        List of dictionaries with screenshot metadata
    """
    results = []
    page_name = page_config["name"]
    page_path = page_config["path"]
    wait_for = page_config.get("wait_for")

    # Get viewports for this page
    page_viewports = page_config.get("viewports", ["desktop"])

    for viewport_name in page_viewports:
        if viewport_name not in viewports:
            print(f"Warning: Viewport '{viewport_name}' not defined, skipping")
            continue

        viewport = viewports[viewport_name]
        url = f"{base_url}{page_path}"

        # Create output filename
        filename = f"{page_name}_{viewport_name}_{branch}.png"
        output_path = output_dir / filename

        print(f"Capturing {page_name} ({viewport_name}) from {branch}...")

        try:
            # Capture screenshot with specific viewport
            await capture.capture_async(
                url=url,
                output_path=str(output_path),
                full_page=True,
                wait_for=wait_for,
                viewport=viewport,
            )

            results.append(
                {
                    "page": page_name,
                    "viewport": viewport_name,
                    "branch": branch,
                    "path": str(output_path),
                    "url": url,
                }
            )

            print(f"  ✓ Saved to {output_path}")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append(
                {
                    "page": page_name,
                    "viewport": viewport_name,
                    "branch": branch,
                    "error": str(e),
                    "url": url,
                }
            )

    return results


async def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Capture PR screenshots for visual regression testing"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to visual-test.yaml configuration file",
    )
    parser.add_argument(
        "--branch",
        required=True,
        choices=["main", "pr"],
        help="Branch to capture (main or pr)",
    )
    parser.add_argument(
        "--base-url",
        help="Override base URL from config",
    )
    parser.add_argument(
        "--output-dir",
        help="Override output directory from config",
    )

    args = parser.parse_args()

    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        return 1

    with config_path.open() as f:
        config = yaml.safe_load(f)

    # Get settings
    base_url = args.base_url or config.get("base_url", "http://localhost:5000")
    output_dir = Path(
        args.output_dir or config.get("settings", {}).get("output_dir", "visual-tests")
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    viewports = config.get("viewports", {})
    pages = config.get("pages", [])
    timeout = config.get("settings", {}).get("timeout", 30000)

    if not pages:
        print("Error: No pages defined in configuration")
        return 1

    print(f"Starting screenshot capture for branch: {args.branch}")
    print(f"Base URL: {base_url}")
    print(f"Output directory: {output_dir}")
    print(f"Pages to capture: {len(pages)}")
    print()

    # Create screenshot capture instance
    capture = ScreenshotCapture(timeout=timeout)

    # Capture all screenshots
    all_results = []
    for page_config in pages:
        results = await capture_page_screenshots(
            capture=capture,
            base_url=base_url,
            page_config=page_config,
            viewports=viewports,
            output_dir=output_dir,
            branch=args.branch,
        )
        all_results.extend(results)

    # Save results to JSON
    results_file = output_dir / f"results_{args.branch}.json"
    with results_file.open("w") as f:
        json.dump(all_results, f, indent=2)

    print()
    print(f"Results saved to: {results_file}")

    # Check for errors
    errors = [r for r in all_results if "error" in r]
    if errors:
        print(f"\nWarning: {len(errors)} screenshot(s) failed")
        return 1

    print(f"\nSuccess: Captured {len(all_results)} screenshot(s)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
