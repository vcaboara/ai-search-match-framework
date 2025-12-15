"""Tests for webhook server and PR review functionality."""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Mock GITHUB_TOKEN before importing webhook_server
with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
    from webhook_server import (
        app,
        verify_webhook_signature,
        is_copilot_authored,
        post_pr_comment,
    )


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestWebhookSignatureVerification:
    """Test webhook signature verification."""

    def test_verify_signature_success(self):
        """Test successful signature verification."""
        payload = b'{"test": "data"}'
        secret = "test_secret"
        
        # Generate valid signature
        import hmac
        import hashlib
        mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        with patch("webhook_server.GITHUB_WEBHOOK_SECRET", secret):
            assert verify_webhook_signature(payload, signature)

    def test_verify_signature_failure(self):
        """Test failed signature verification."""
        payload = b'{"test": "data"}'
        signature = "sha256=invalid_signature"
        
        with patch("webhook_server.GITHUB_WEBHOOK_SECRET", "test_secret"):
            assert not verify_webhook_signature(payload, signature)

    def test_verify_signature_no_secret(self):
        """Test signature verification when no secret is configured."""
        payload = b'{"test": "data"}'
        signature = "sha256=anything"
        
        with patch("webhook_server.GITHUB_WEBHOOK_SECRET", None):
            # Should return True (skip verification) with warning logged
            assert verify_webhook_signature(payload, signature)

    def test_verify_signature_no_header(self):
        """Test signature verification with missing header."""
        payload = b'{"test": "data"}'
        
        with patch("webhook_server.GITHUB_WEBHOOK_SECRET", "test_secret"):
            assert not verify_webhook_signature(payload, None)

    def test_verify_signature_wrong_algorithm(self):
        """Test signature verification with wrong algorithm."""
        payload = b'{"test": "data"}'
        signature = "sha1=somehash"
        
        with patch("webhook_server.GITHUB_WEBHOOK_SECRET", "test_secret"):
            assert not verify_webhook_signature(payload, signature)


class TestCopilotAuthorDetection:
    """Test Copilot author detection."""

    def test_is_copilot_by_username(self):
        """Test detection by username."""
        pr_data = {
            "user": {"login": "github-copilot[bot]"}
        }
        assert is_copilot_authored(pr_data)

    def test_is_copilot_by_body(self):
        """Test detection by PR body content."""
        pr_data = {
            "user": {"login": "user123"},
            "body": "This PR was created with GitHub Copilot"
        }
        assert is_copilot_authored(pr_data)

    def test_is_not_copilot(self):
        """Test non-Copilot PR detection."""
        pr_data = {
            "user": {"login": "human_user"},
            "body": "Manual PR"
        }
        assert not is_copilot_authored(pr_data)

    def test_is_copilot_empty_body(self):
        """Test Copilot detection with empty body."""
        pr_data = {
            "user": {"login": "copilot-bot"},
            "body": None
        }
        assert is_copilot_authored(pr_data)


class TestGitHubAPIIntegration:
    """Test GitHub API interaction."""

    @patch("webhook_server.requests.post")
    def test_post_pr_comment_success(self, mock_post):
        """Test successful comment posting."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        with patch("webhook_server.GITHUB_TOKEN", "test_token"):
            result = post_pr_comment("owner/repo", 123, "Test comment")
            assert result is True
            mock_post.assert_called_once()

    @patch("webhook_server.requests.post")
    def test_post_pr_comment_failure(self, mock_post):
        """Test failed comment posting."""
        import requests
        mock_post.side_effect = requests.RequestException("API Error")
        
        with patch("webhook_server.GITHUB_TOKEN", "test_token"):
            result = post_pr_comment("owner/repo", 123, "Test comment")
            assert result is False


class TestWebhookEndpoints:
    """Test webhook server endpoints."""

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "ollama_url" in data
        assert "model" in data

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["service"] == "Ollama PR Review Webhook Server"
        assert "endpoints" in data

    @patch("webhook_server.verify_webhook_signature")
    def test_webhook_invalid_signature(self, mock_verify, client):
        """Test webhook with invalid signature."""
        mock_verify.return_value = False
        
        response = client.post(
            "/webhook",
            data=json.dumps({"action": "opened"}),
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": "sha256=invalid"
            }
        )
        assert response.status_code == 403

    @patch("webhook_server.verify_webhook_signature")
    def test_webhook_non_pr_event(self, mock_verify, client):
        """Test webhook with non-PR event."""
        mock_verify.return_value = True
        
        response = client.post(
            "/webhook",
            data=json.dumps({"action": "opened"}),
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "push",
                "X-Hub-Signature-256": "sha256=valid"
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "not handled" in data["message"]

    @patch("webhook_server.verify_webhook_signature")
    def test_webhook_draft_pr(self, mock_verify, client):
        """Test webhook skips draft PRs."""
        mock_verify.return_value = True
        
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 123,
                "draft": True
            },
            "repository": {
                "full_name": "owner/repo"
            }
        }
        
        response = client.post(
            "/webhook",
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": "sha256=valid"
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "Draft PR" in data["message"]

    @patch("webhook_server.verify_webhook_signature")
    @patch("webhook_server.review_pr_with_ollama")
    @patch("webhook_server.post_pr_comment")
    def test_webhook_successful_review(
        self, mock_post_comment, mock_review, mock_verify, client
    ):
        """Test successful PR review workflow."""
        mock_verify.return_value = True
        mock_review.return_value = "## Review Result\n\nNo issues found."
        mock_post_comment.return_value = True
        
        payload = {
            "action": "ready_for_review",
            "pull_request": {
                "number": 123,
                "draft": False,
                "user": {"login": "testuser"},
                "body": "Test PR"
            },
            "repository": {
                "full_name": "owner/repo"
            }
        }
        
        response = client.post(
            "/webhook",
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": "sha256=valid"
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Review completed and posted"
        assert data["pr_number"] == 123
        
        # Verify review was called
        mock_review.assert_called_once()
        mock_post_comment.assert_called_once()

    @patch("webhook_server.verify_webhook_signature")
    @patch("webhook_server.review_pr_with_ollama")
    @patch("webhook_server.post_pr_comment")
    def test_webhook_review_failure(
        self, mock_post_comment, mock_review, mock_verify, client
    ):
        """Test PR review failure handling."""
        mock_verify.return_value = True
        mock_review.return_value = None  # Review failed
        mock_post_comment.return_value = True
        
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 123,
                "draft": False,
                "user": {"login": "testuser"},
                "body": "Test PR"
            },
            "repository": {
                "full_name": "owner/repo"
            }
        }
        
        response = client.post(
            "/webhook",
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": "sha256=valid"
            }
        )
        
        assert response.status_code == 500
        # Should post error comment
        mock_post_comment.assert_called_once()
        error_comment = mock_post_comment.call_args[0][2]
        assert "Automated Review Failed" in error_comment
