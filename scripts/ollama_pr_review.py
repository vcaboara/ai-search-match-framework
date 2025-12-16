#!/usr/bin/env python3
"""
Ollama PR Review Script

Analyzes GitHub PR code changes using Ollama LLM with CODE_REVIEW_PATTERNS.md guidance.
Outputs structured review findings that can be posted as PR comments.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

import httpx
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-coder:6.7b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "300.0"))


# Load CODE_REVIEW_PATTERNS.md content
# Maximum diff size for analysis (~50KB)
MAX_DIFF_SIZE = 50000


def load_review_patterns() -> str:
    """Load the CODE_REVIEW_PATTERNS.md content for AI guidance."""
    # Look for patterns file in .github directory
    patterns_paths = [
        Path(__file__).parent.parent / ".github" / "CODE_REVIEW_PATTERNS.md",
        Path.cwd() / ".github" / "CODE_REVIEW_PATTERNS.md",
    ]

    for patterns_path in patterns_paths:
        if patterns_path.exists():
            logger.info(f"Loading review patterns from: {patterns_path}")
            return patterns_path.read_text()

    logger.warning("CODE_REVIEW_PATTERNS.md not found - using basic review mode")
    return ""


def get_pr_diff(repo_full_name: str, pr_number: int) -> str | None:
    """Fetch the PR diff from GitHub API."""
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN not set")
        return None

    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff",
        "User-Agent": "Ollama-PR-Reviewer",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to fetch PR diff")
        return None
    else:
        return response.text


def get_pr_files(repo_full_name: str, pr_number: int) -> list[dict[str, Any]] | None:
    """Fetch the list of changed files in the PR."""
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN not set")
        return None

    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Ollama-PR-Reviewer",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to fetch PR files")
        return None
    else:
        return response.json()


def analyze_with_ollama(prompt: str) -> str | None:
    """Send analysis request to Ollama and return the response."""
    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # Lower temperature for more consistent reviews
            "top_p": 0.9,
        },
    }

    try:
        logger.info(f"Sending request to Ollama at {url}")
        with httpx.Client(timeout=OLLAMA_TIMEOUT) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")

    except httpx.TimeoutException:
        logger.exception(f"Ollama request timed out after {OLLAMA_TIMEOUT}s")
        return None
    except httpx.HTTPError:
        logger.exception("Ollama HTTP error")
        return None
    except Exception:
        logger.exception("Ollama request failed")
        return None


def format_review_prompt(pr_diff: str, pr_files: list[dict[str, Any]], review_patterns: str) -> str:
    """Format the review prompt for Ollama."""
    files_summary = "\n".join(
        [f"- {f['filename']} (+{f['additions']} -{f['deletions']})" for f in pr_files]
    )

    prompt = f"""You are an expert code reviewer analyzing a GitHub pull request. Your task is to identify code quality issues, performance problems, and security vulnerabilities based on established anti-patterns.

## Review Guidelines

{review_patterns if review_patterns else "Review the code for common Python anti-patterns, performance issues, and security vulnerabilities."}

## Pull Request Changes

### Changed Files:
{files_summary}

### Code Diff:
```diff
{pr_diff}
```

## Your Task

1. Review the code changes against the anti-patterns guide
2. Identify specific issues with file names and line numbers when possible
3. Provide clear, actionable feedback
4. Suggest fixes for each issue found
5. Highlight any security vulnerabilities

## Output Format

Please format your review as follows:

### Summary
[Brief overview of the review - number of issues found by category]

### Issues Found

#### [Category: Performance/Quality/Security]
**File:** `filename.py` (line X-Y if applicable)
**Issue:** [Description of the anti-pattern]
**Suggestion:** [How to fix it]

[Repeat for each issue]

### Positive Observations
[Highlight any well-written code that follows best practices]

### Recommendation
[Overall recommendation: Approve / Request Changes / Comment]

---

Begin your review:
"""

    return prompt


def review_pr(repo_full_name: str, pr_number: int) -> str:
    """
    Main function to review a PR and return formatted results.

    Args:
        repo_full_name: Full repository name (owner/repo)
        pr_number: PR number to review

    Returns:
        Formatted review result string
    """
    logger.info(f"Starting review for {repo_full_name} PR #{pr_number}")

    # Load review patterns
    review_patterns = load_review_patterns()

    # Fetch PR data
    logger.info("Fetching PR diff...")
    pr_diff = get_pr_diff(repo_full_name, pr_number)
    if not pr_diff:
        return "❌ Failed to fetch PR diff"

    logger.info("Fetching PR files...")
    pr_files = get_pr_files(repo_full_name, pr_number)
    if not pr_files:
        return "❌ Failed to fetch PR files"

    # Check if diff is too large
    if len(pr_diff) > MAX_DIFF_SIZE:
        logger.warning("PR diff is very large - truncating for analysis")
        pr_diff = pr_diff[:MAX_DIFF_SIZE] + "\n\n[... diff truncated due to size ...]"

    # Build review prompt
    logger.info("Building review prompt...")
    prompt = format_review_prompt(pr_diff, pr_files, review_patterns)

    # Analyze with Ollama
    logger.info("Analyzing with Ollama...")
    review_result = analyze_with_ollama(prompt)

    if not review_result:
        return "❌ Failed to analyze with Ollama"

    # Format final output
    return f"""## 🤖 Automated Code Review (Ollama)

{review_result}

---
*Reviewed by Ollama ({OLLAMA_MODEL}) • [Learn more about review patterns](.github/CODE_REVIEW_PATTERNS.md)*
"""


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Review GitHub PR using Ollama LLM")
    parser.add_argument("--repo", required=True, help="Repository full name (e.g., owner/repo)")
    parser.add_argument("--pr", required=True, type=int, help="PR number to review")

    args = parser.parse_args()

    # Validate configuration
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN environment variable is required")
        return 1

    # Run review
    result = review_pr(args.repo, args.pr)

    # Output result
    print(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
