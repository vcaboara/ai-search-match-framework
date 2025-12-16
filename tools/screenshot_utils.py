"""Screenshot utility for visual regression testing using Playwright.

This module provides functionality to capture full-page screenshots with configurable
viewport sizes. It can be used for visual regression testing in CI/CD pipelines.

Example:
    Async usage:
        from tools.screenshot_utils import capture_screenshot_async

        await capture_screenshot_async(
            url="https://example.com",
            output_path="screenshot.png",
            viewport={"width": 1920, "height": 1080}
        )

    Sync usage:
        from tools.screenshot_utils import capture_screenshot

        capture_screenshot(
            url="https://example.com",
            output_path="screenshot.png"
        )
"""

import asyncio
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright


class ScreenshotCapture:
    """Class for capturing screenshots using Playwright.

    Attributes:
        viewport (dict[str, int]): Default viewport dimensions
        timeout (int): Page load timeout in milliseconds
    """

    def __init__(
        self,
        viewport: dict[str, int] | None = None,
        timeout: int = 30000,
    ) -> None:
        """Initialize ScreenshotCapture.

        Args:
            viewport: Dictionary with 'width' and 'height' keys.
                     Defaults to 1920x1080.
            timeout: Page load timeout in milliseconds. Defaults to 30000 (30s).
        """
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.timeout = timeout

    async def capture_async(
        self,
        url: str,
        output_path: str,
        full_page: bool = True,
        wait_for: str | None = None,
        viewport: dict[str, int] | None = None,
    ) -> Path:
        """Capture a screenshot asynchronously.

        Args:
            url: URL to capture
            output_path: Path where screenshot will be saved
            full_page: Whether to capture the full scrollable page (default: True)
            wait_for: Optional CSS selector to wait for before capturing
            viewport: Override viewport for this capture (uses instance viewport if not provided)

        Returns:
            Path object of the saved screenshot

        Raises:
            Exception: If screenshot capture fails
        """
        # Use provided viewport or fall back to instance viewport
        viewport_to_use = viewport or self.viewport

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page(viewport=viewport_to_use)
                await page.goto(url, timeout=self.timeout, wait_until="networkidle")

                # Wait for specific element if specified
                if wait_for:
                    await page.wait_for_selector(wait_for, timeout=self.timeout)

                # Capture screenshot
                output = Path(output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(output), full_page=full_page)

                return output
            finally:
                await browser.close()

    def capture_sync(
        self,
        url: str,
        output_path: str,
        full_page: bool = True,
        wait_for: str | None = None,
        viewport: dict[str, int] | None = None,
    ) -> Path:
        """Capture a screenshot synchronously (wrapper around async method).

        Args:
            url: URL to capture
            output_path: Path where screenshot will be saved
            full_page: Whether to capture the full scrollable page (default: True)
            wait_for: Optional CSS selector to wait for before capturing
            viewport: Override viewport for this capture (uses instance viewport if not provided)

        Returns:
            Path object of the saved screenshot
        """
        return asyncio.run(self.capture_async(url, output_path, full_page, wait_for, viewport))


async def capture_screenshot_async(
    url: str,
    output_path: str,
    viewport: dict[str, int] | None = None,
    full_page: bool = True,
    timeout: int = 30000,
    wait_for: str | None = None,
) -> Path:
    """Capture a screenshot asynchronously (convenience function).

    Args:
        url: URL to capture
        output_path: Path where screenshot will be saved
        viewport: Dictionary with 'width' and 'height' keys
        full_page: Whether to capture the full scrollable page (default: True)
        timeout: Page load timeout in milliseconds
        wait_for: Optional CSS selector to wait for before capturing

    Returns:
        Path object of the saved screenshot

    Example:
        await capture_screenshot_async(
            url="https://example.com",
            output_path="screenshot.png",
            viewport={"width": 1280, "height": 720}
        )
    """
    capture = ScreenshotCapture(viewport=viewport, timeout=timeout)
    return await capture.capture_async(url, output_path, full_page, wait_for)


def capture_screenshot(
    url: str,
    output_path: str,
    viewport: dict[str, int] | None = None,
    full_page: bool = True,
    timeout: int = 30000,
    wait_for: str | None = None,
) -> Path:
    """Capture a screenshot synchronously (convenience function).

    Args:
        url: URL to capture
        output_path: Path where screenshot will be saved
        viewport: Dictionary with 'width' and 'height' keys
        full_page: Whether to capture the full scrollable page (default: True)
        timeout: Page load timeout in milliseconds
        wait_for: Optional CSS selector to wait for before capturing

    Returns:
        Path object of the saved screenshot

    Example:
        capture_screenshot(
            url="https://example.com",
            output_path="screenshot.png",
            viewport={"width": 1280, "height": 720}
        )
    """
    return asyncio.run(
        capture_screenshot_async(url, output_path, viewport, full_page, timeout, wait_for)
    )


# CLI interface
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Capture screenshots using Playwright")
    parser.add_argument("url", help="URL to capture")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--width", type=int, default=1920, help="Viewport width (default: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height (default: 1080)")
    parser.add_argument(
        "--timeout", type=int, default=30000, help="Page load timeout in ms (default: 30000)"
    )
    parser.add_argument("--wait-for", help="CSS selector to wait for before capturing")
    parser.add_argument(
        "--no-full-page", action="store_true", help="Capture viewport only (not full page)"
    )

    args = parser.parse_args()

    try:
        viewport = {"width": args.width, "height": args.height}
        result = capture_screenshot(
            url=args.url,
            output_path=args.output,
            viewport=viewport,
            full_page=not args.no_full_page,
            timeout=args.timeout,
            wait_for=args.wait_for,
        )
        print(f"Screenshot saved to: {result}")
        sys.exit(0)
    except Exception as e:
        print(f"Error capturing screenshot: {e}", file=sys.stderr)
        sys.exit(1)
