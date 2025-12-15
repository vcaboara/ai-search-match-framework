#!/usr/bin/env python3
"""
Ollama PR Review Webhook Server

Receives GitHub webhooks for PR ready_for_review events and triggers
automated code review using Ollama LLM with CODE_REVIEW_PATTERNS.md guidance.
"""

import hashlib
import hmac
import logging
import os
import subprocess
import sys
from typing import Any

import requests
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b-q4")
REVIEW_SCRIPT_PATH = os.getenv("REVIEW_SCRIPT_PATH", "./scripts/ollama_pr_review.py")

# Validate required configuration (only when running as main, not during imports for tests)
def _validate_config():
    """Validate required configuration."""
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN environment variable is required")
        sys.exit(1)


def verify_webhook_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature for security."""
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning("GITHUB_WEBHOOK_SECRET not set - skipping signature verification")
        return True

    if not signature_header:
        logger.error("No signature header provided")
        return False

    hash_algorithm, github_signature = signature_header.split("=")
    if hash_algorithm != "sha256":
        logger.error(f"Unsupported hash algorithm: {hash_algorithm}")
        return False

    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = mac.hexdigest()

    if not hmac.compare_digest(expected_signature, github_signature):
        logger.error("Signature verification failed")
        return False

    return True


def post_pr_comment(repo_full_name: str, pr_number: int, comment_body: str) -> bool:
    """Post a comment on the PR."""
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Ollama-PR-Reviewer",
    }

    payload = {"body": comment_body}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully posted comment on PR #{pr_number}")
    except requests.RequestException:
        logger.exception("Failed to post comment")
        return False
    else:
        return True


def is_copilot_authored(pr_data: dict[str, Any]) -> bool:
    """Check if PR was created by GitHub Copilot."""
    user = pr_data.get("user", {})
    username = user.get("login", "")

    # Check for Copilot user patterns
    copilot_patterns = ["copilot", "github-actions[bot]", "dependabot[bot]"]

    # Check username
    if any(pattern in username.lower() for pattern in copilot_patterns):
        return True

    # Check if PR body mentions Copilot
    body = pr_data.get("body", "") or ""
    return "copilot" in body.lower()


def review_pr_with_ollama(
    repo_full_name: str, pr_number: int, pr_data: dict[str, Any]  # noqa: ARG001
) -> str | None:
    """
    Run Ollama PR review script and return the review result.

    Args:
        repo_full_name: Full repository name (owner/repo)
        pr_number: PR number
        pr_data: Full PR data from webhook

    Returns:
        Review result string or None on failure
    """
    try:
        # Prepare environment for review script
        env = os.environ.copy()
        env["OLLAMA_BASE_URL"] = OLLAMA_BASE_URL
        env["OLLAMA_MODEL"] = OLLAMA_MODEL
        env["GITHUB_TOKEN"] = GITHUB_TOKEN

        # Build command
        cmd = [
            sys.executable,
            REVIEW_SCRIPT_PATH,
            "--repo",
            repo_full_name,
            "--pr",
            str(pr_number),
        ]

        logger.info(f"Running review script: {' '.join(cmd)}")

        # Run the review script
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            check=False,
        )

        if result.returncode != 0:
            logger.error(f"Review script failed with code {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            return None

        review_result = result.stdout.strip()
        logger.info("Review script completed successfully")

    except subprocess.TimeoutExpired:
        logger.exception("Review script timed out after 5 minutes")
        return None
    except Exception:
        logger.exception("Error running review script")
        return None
    else:
        return review_result


@app.route("/webhook", methods=["POST"])
def webhook_handler() -> tuple[dict[str, Any], int]:
    """Handle incoming GitHub webhooks."""
    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_webhook_signature(request.data, signature):
        logger.error("Webhook signature verification failed")
        return jsonify({"error": "Invalid signature"}), 403

    # Parse event type
    event_type = request.headers.get("X-GitHub-Event")
    logger.info(f"Received webhook event: {event_type}")

    if event_type != "pull_request":
        return jsonify({"message": "Event type not handled"}), 200

    try:
        payload = request.json
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})
        repo_data = payload.get("repository", {})

        repo_full_name = repo_data.get("full_name")
        pr_number = pr_data.get("number")
        is_draft = pr_data.get("draft", False)

        logger.info(
            f"PR event - Action: {action}, Repo: {repo_full_name}, "
            f"PR: #{pr_number}, Draft: {is_draft}"
        )

        # Only handle ready_for_review and opened events for non-draft PRs
        if action not in ["ready_for_review", "opened", "synchronize"]:
            logger.info(f"Ignoring action: {action}")
            return jsonify({"message": f"Action {action} not handled"}), 200

        # Skip draft PRs
        if is_draft:
            logger.info("Skipping draft PR")
            return jsonify({"message": "Draft PR - skipping review"}), 200

        # Check if PR is from Copilot (optional filter)
        is_copilot = is_copilot_authored(pr_data)
        logger.info(f"Copilot-authored: {is_copilot}")

        # Run Ollama review
        logger.info(f"Triggering Ollama review for PR #{pr_number}")
        review_result = review_pr_with_ollama(repo_full_name, pr_number, pr_data)

        if not review_result:
            error_comment = (
                "⚠️ **Automated Review Failed**\n\n"
                "The Ollama PR review encountered an error. "
                "Please check the webhook server logs for details."
            )
            post_pr_comment(repo_full_name, pr_number, error_comment)
            return jsonify({"error": "Review failed"}), 500

        # Post review as comment
        success = post_pr_comment(repo_full_name, pr_number, review_result)

        if success:
            return jsonify({"message": "Review completed and posted", "pr_number": pr_number}), 200
        return jsonify({"error": "Failed to post review comment"}), 500

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check() -> tuple[dict[str, Any], int]:
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "ollama_url": OLLAMA_BASE_URL,
        "model": OLLAMA_MODEL,
        "github_token_configured": bool(GITHUB_TOKEN),
        "webhook_secret_configured": bool(GITHUB_WEBHOOK_SECRET),
    }
    return jsonify(health_status), 200


@app.route("/", methods=["GET"])
def root() -> tuple[dict[str, Any], int]:
    """Root endpoint with service information."""
    return (
        jsonify(
            {
                "service": "Ollama PR Review Webhook Server",
                "version": "1.0.0",
                "endpoints": {"webhook": "/webhook", "health": "/health"},
            }
        ),
        200,
    )


if __name__ == "__main__":
    # Validate configuration before starting server
    _validate_config()
    
    # Production configuration
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    logger.info(f"Starting webhook server on port {port}")
    logger.info(f"Ollama URL: {OLLAMA_BASE_URL}")
    logger.info(f"Ollama Model: {OLLAMA_MODEL}")
    logger.info(f"Review Script: {REVIEW_SCRIPT_PATH}")

    app.run(host="0.0.0.0", port=port, debug=debug)
