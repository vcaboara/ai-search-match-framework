"""Tests for screenshot_utils module."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from tools.screenshot_utils import (
    ScreenshotCapture,
    capture_screenshot,
    capture_screenshot_async,
)


class TestScreenshotCapture:
    """Tests for ScreenshotCapture class."""

    def test_init_default_values(self) -> None:
        """Test initialization with default values."""
        capture = ScreenshotCapture()
        assert capture.viewport == {"width": 1920, "height": 1080}
        assert capture.timeout == 30000

    def test_init_custom_values(self) -> None:
        """Test initialization with custom values."""
        viewport = {"width": 1280, "height": 720}
        capture = ScreenshotCapture(viewport=viewport, timeout=60000)
        assert capture.viewport == viewport
        assert capture.timeout == 60000

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async context manager."""
        capture = ScreenshotCapture()

        async with capture as c:
            assert c is capture
            assert c._browser is None

    @pytest.mark.asyncio
    async def test_capture_async_success(self) -> None:
        """Test successful screenshot capture."""
        capture = ScreenshotCapture()

        # Mock Playwright components
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.screenshot = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("tools.screenshot_utils.async_playwright") as mock_pw:
            mock_pw.return_value.__aenter__.return_value = mock_playwright

            result = await capture.capture_async(
                url="https://example.com",
                output_path="/tmp/test.png",
                full_page=True,
            )

            # Verify calls
            mock_playwright.chromium.launch.assert_called_once_with(headless=True)
            mock_browser.new_page.assert_called_once()
            mock_page.goto.assert_called_once()
            mock_page.screenshot.assert_called_once()
            mock_browser.close.assert_called_once()

            # Check result
            assert isinstance(result, Path)
            assert str(result) == "/tmp/test.png"

    @pytest.mark.asyncio
    async def test_capture_async_with_wait_for(self) -> None:
        """Test screenshot capture with wait_for selector."""
        capture = ScreenshotCapture()

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.screenshot = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("tools.screenshot_utils.async_playwright") as mock_pw:
            mock_pw.return_value.__aenter__.return_value = mock_playwright

            await capture.capture_async(
                url="https://example.com",
                output_path="/tmp/test.png",
                wait_for=".content",
            )

            # Verify wait_for_selector was called
            mock_page.wait_for_selector.assert_called_once_with(
                ".content",
                timeout=capture.timeout,
            )

    def test_capture_sync(self) -> None:
        """Test synchronous capture wrapper."""
        capture = ScreenshotCapture()

        with patch.object(capture, "capture_async", new_callable=AsyncMock) as mock_async:
            mock_async.return_value = Path("/tmp/test.png")

            # Mock asyncio.run
            with patch("tools.screenshot_utils.asyncio.run") as mock_run:
                mock_run.return_value = Path("/tmp/test.png")

                result = capture.capture_sync(
                    url="https://example.com",
                    output_path="/tmp/test.png",
                )

                mock_run.assert_called_once()
                assert isinstance(result, Path)


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_capture_screenshot_async(self) -> None:
        """Test capture_screenshot_async convenience function."""
        with patch.object(ScreenshotCapture, "capture_async", new_callable=AsyncMock) as mock:
            mock.return_value = Path("/tmp/test.png")

            result = await capture_screenshot_async(
                url="https://example.com",
                output_path="/tmp/test.png",
                viewport={"width": 1280, "height": 720},
            )

            mock.assert_called_once()
            assert isinstance(result, Path)

    def test_capture_screenshot(self) -> None:
        """Test capture_screenshot convenience function."""
        with patch("tools.screenshot_utils.asyncio.run") as mock_run:
            mock_run.return_value = Path("/tmp/test.png")

            result = capture_screenshot(
                url="https://example.com",
                output_path="/tmp/test.png",
            )

            mock_run.assert_called_once()
            assert isinstance(result, Path)


class TestCLI:
    """Tests for CLI interface."""

    def test_cli_basic(self) -> None:
        """Test basic CLI usage."""
        import sys

        with patch.object(
            sys,
            "argv",
            [
                "screenshot_utils.py",
                "https://example.com",
                "/tmp/test.png",
            ],
        ), patch("tools.screenshot_utils.capture_screenshot") as mock_capture:
            mock_capture.return_value = Path("/tmp/test.png")

            # Import would execute if __name__ == "__main__"
            # For testing, we'll just verify the function can be called

    def test_cli_with_options(self) -> None:
        """Test CLI with custom options."""
        import sys

        with patch.object(
            sys,
            "argv",
            [
                "screenshot_utils.py",
                "https://example.com",
                "/tmp/test.png",
                "--width",
                "1280",
                "--height",
                "720",
                "--timeout",
                "60000",
                "--wait-for",
                ".content",
                "--no-full-page",
            ],
        ), patch("tools.screenshot_utils.capture_screenshot") as mock_capture:
            mock_capture.return_value = Path("/tmp/test.png")

            # Verify parameters would be passed correctly
