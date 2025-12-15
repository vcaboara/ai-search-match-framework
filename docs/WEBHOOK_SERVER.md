# Ollama PR Review Webhook Server

Automated code review system that uses Ollama LLM to review GitHub pull requests based on the anti-patterns defined in [CODE_REVIEW_PATTERNS.md](../.github/CODE_REVIEW_PATTERNS.md).

## Overview

This webhook server receives GitHub pull request events and automatically reviews the code changes using a local Ollama instance. It's designed to run between GitHub Copilot PR creation and human review, catching common anti-patterns early.

### Workflow

1. Developer (or Copilot) creates a PR
2. PR is marked as ready for review (non-draft)
3. GitHub sends webhook to the server
4. Ollama reviews code using CODE_REVIEW_PATTERNS.md guidance
5. Review posted as PR comment
6. Human reviewer sees both Ollama's review and code changes

## Architecture

```
GitHub PR Event → Webhook Server → Ollama PR Review Script → Ollama LLM
                       ↓                                          ↓
                 Post Comment ←─────────── Analyze Code ─────────┘
```

### Components

1. **Webhook Server** (`webhook_server.py`): Flask app that receives GitHub webhooks
2. **Review Script** (`scripts/ollama_pr_review.py`): Analyzes PR diffs using Ollama
3. **Docker Container**: Isolated environment with all dependencies
4. **Ollama**: Local LLM for code analysis (runs on host)

## Prerequisites

- Docker and Docker Compose
- Ollama installed on host machine (see [OLLAMA_SETUP.md](./OLLAMA_SETUP.md))
- GitHub Personal Access Token with `repo` scope
- (Optional) ngrok or Cloudflare tunnel for exposing webhook endpoint

## Quick Start

### 1. Set Up Ollama

First, ensure Ollama is running on your host machine:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the recommended model
ollama pull qwen2.5:14b-q4

# Start Ollama (runs on port 11434 by default)
ollama serve
```

### 2. Configure Environment

Create a `.env` file with your GitHub token:

```bash
# GitHub Configuration (REQUIRED)
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here  # Optional but recommended

# Ollama Configuration (defaults shown)
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:14b-q4
OLLAMA_TIMEOUT=120.0

# Server Configuration
PORT=5000
FLASK_DEBUG=false
```

**Getting a GitHub Token:**

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope (full control of private repositories)
3. Copy the token to your `.env` file

### 3. Start the Webhook Server

```bash
# Copy example docker-compose
cp docker-compose.example.yml docker-compose.yml

# Start the webhook server
docker-compose up -d ollama-reviewer

# Check logs
docker-compose logs -f ollama-reviewer
```

### 4. Expose Webhook Endpoint

You need to expose your local webhook server to the internet so GitHub can reach it.

#### Option A: ngrok (Recommended for testing)

```bash
# Install ngrok: https://ngrok.com/download

# Start ngrok tunnel
ngrok http 5000

# Note the public URL (e.g., https://abc123.ngrok.io)
```

#### Option B: Cloudflare Tunnel (Recommended for production)

```bash
# Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Create tunnel
cloudflared tunnel create pr-reviewer

# Configure tunnel
cloudflared tunnel route dns pr-reviewer pr-reviewer.yourdomain.com

# Run tunnel
cloudflared tunnel run pr-reviewer
```

### 5. Configure GitHub Webhook

1. Go to your repository on GitHub
2. Navigate to Settings → Webhooks → Add webhook
3. Configure webhook:
   - **Payload URL**: Your public URL + `/webhook` (e.g., `https://abc123.ngrok.io/webhook`)
   - **Content type**: `application/json`
   - **Secret**: Same as `GITHUB_WEBHOOK_SECRET` in `.env` (optional but recommended)
   - **Events**: Select "Let me select individual events"
     - ✅ Pull requests
   - **Active**: ✅ Checked

4. Click "Add webhook"

### 6. Test the Setup

Create a test PR in your repository:

```bash
git checkout -b test-pr-review
echo "print('hello')" > test.py
git add test.py
git commit -m "Test PR review"
git push origin test-pr-review
```

Then:
1. Create a PR from `test-pr-review` to `main`
2. Mark it as ready for review (if draft)
3. Check webhook server logs: `docker-compose logs -f ollama-reviewer`
4. Look for automated review comment on the PR

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | Yes | - | GitHub Personal Access Token with `repo` scope |
| `GITHUB_WEBHOOK_SECRET` | No | - | Webhook secret for signature verification |
| `OLLAMA_BASE_URL` | No | `http://host.docker.internal:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | No | `qwen2.5:14b-q4` | Ollama model to use for review |
| `OLLAMA_TIMEOUT` | No | `120.0` | Timeout for Ollama requests (seconds) |
| `PORT` | No | `5000` | Webhook server port |
| `FLASK_DEBUG` | No | `false` | Enable Flask debug mode |
| `REVIEW_SCRIPT_PATH` | No | `/app/scripts/ollama_pr_review.py` | Path to review script |

### Ollama Models

Recommended models based on available VRAM:

| VRAM | Recommended Model | Command |
|------|-------------------|---------|
| 12GB+ | `qwen2.5:32b-q4` | `ollama pull qwen2.5:32b-q4` |
| 8GB | `qwen2.5:14b-q4` | `ollama pull qwen2.5:14b-q4` |
| 6GB | `qwen2.5:7b-q4` | `ollama pull qwen2.5:7b-q4` |
| <6GB | `llama3.2:3b` | `ollama pull llama3.2:3b` |

See [OLLAMA_SETUP.md](./OLLAMA_SETUP.md) for more model details.

### Review Patterns

The review is guided by [CODE_REVIEW_PATTERNS.md](../.github/CODE_REVIEW_PATTERNS.md), which documents 18 common anti-patterns across:

- Performance issues (regex in loops, repeated lookups, string concatenation, etc.)
- Code quality (imports, nesting, exceptions, type conversions, etc.)
- Python-specific patterns (comprehensions, assertions, context managers, etc.)
- Security vulnerabilities (SQL injection, unsafe deserialization, hardcoded credentials, etc.)

You can customize the patterns by editing the file. The Ollama model will use this as guidance when reviewing code.

## Usage

### Manual Testing

You can test the review script manually:

```bash
# Inside the container
docker-compose exec ollama-reviewer python scripts/ollama_pr_review.py \
  --repo owner/repo \
  --pr 123

# Or on host (requires Python dependencies)
export GITHUB_TOKEN=your_token
export OLLAMA_BASE_URL=http://localhost:11434
python scripts/ollama_pr_review.py --repo owner/repo --pr 123
```

### Webhook Testing

Test the webhook endpoint:

```bash
# Health check
curl http://localhost:5000/health

# Manual webhook (requires proper payload)
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -d @test_webhook_payload.json
```

### Docker Commands

```bash
# Start all services (including Ollama)
docker-compose up -d

# Start only webhook server (assumes Ollama on host)
docker-compose up -d ollama-reviewer

# View logs
docker-compose logs -f ollama-reviewer

# Restart server
docker-compose restart ollama-reviewer

# Stop server
docker-compose stop ollama-reviewer

# Remove containers
docker-compose down

# Rebuild and start
docker-compose up -d --build ollama-reviewer
```

## Monitoring

### Health Check

The server includes a health check endpoint:

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "ollama_url": "http://host.docker.internal:11434",
  "model": "qwen2.5:14b-q4",
  "github_token_configured": true,
  "webhook_secret_configured": true
}
```

### Logs

View webhook server logs:

```bash
docker-compose logs -f ollama-reviewer
```

Key log messages:
- `Received webhook event: pull_request` - Webhook received
- `Triggering Ollama review for PR #123` - Review started
- `Review script completed successfully` - Review finished
- `Successfully posted comment on PR #123` - Comment posted

### Troubleshooting

#### Webhook not triggering

1. Check GitHub webhook delivery status (Settings → Webhooks → Recent Deliveries)
2. Verify webhook URL is accessible from internet
3. Check webhook secret matches (if configured)
4. Ensure server is running: `curl http://localhost:5000/health`

#### Ollama connection failed

1. Verify Ollama is running on host: `curl http://localhost:11434/api/tags`
2. Check `OLLAMA_BASE_URL` is correct (use `host.docker.internal` for Docker on Mac/Windows)
3. For Linux, use `--add-host=host.docker.internal:host-gateway` in docker-compose
4. Check firewall settings

#### Review timeout

1. Increase `OLLAMA_TIMEOUT` (default: 120s)
2. Use a smaller/faster model (e.g., `qwen2.5:7b-q4` or `llama3.2:3b`)
3. Check Ollama model is pulled: `ollama list`
4. Monitor Ollama logs: `journalctl -u ollama -f`

#### GitHub API rate limit

1. Verify `GITHUB_TOKEN` is set correctly
2. Check token has `repo` scope
3. Monitor rate limit: `curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/rate_limit`

## Security Considerations

### Webhook Secret

Always configure `GITHUB_WEBHOOK_SECRET` in production to prevent unauthorized webhook deliveries:

```bash
# Generate secure secret
openssl rand -hex 32

# Add to .env
GITHUB_WEBHOOK_SECRET=your_generated_secret
```

Then configure the same secret in GitHub webhook settings.

### GitHub Token

- Use a token with minimal required permissions (`repo` scope)
- Consider using a GitHub App instead of Personal Access Token for better security
- Rotate tokens regularly
- Never commit tokens to version control

### Network Security

- Use HTTPS for webhook endpoint (ngrok/Cloudflare provide this automatically)
- Consider IP whitelisting for GitHub webhook IPs
- Use firewall rules to restrict access to Ollama port (11434)

## Deployment

### Production Deployment

For production use:

1. **Use a proper domain with HTTPS**:
   - Set up Cloudflare tunnel or reverse proxy (nginx/Traefik)
   - Configure SSL/TLS certificates

2. **Enable webhook secret verification**:
   - Generate strong secret: `openssl rand -hex 32`
   - Configure in both `.env` and GitHub webhook settings

3. **Set resource limits**:
   - Already configured in `docker-compose.example.yml`
   - Adjust based on your server capacity

4. **Monitor and log**:
   - Set up log aggregation (ELK, Grafana Loki, etc.)
   - Configure alerts for failures
   - Monitor Ollama resource usage

5. **Backup and recovery**:
   - Back up `.env` file securely
   - Document deployment steps
   - Test disaster recovery procedure

### Multi-Repository Setup

To use the webhook server across multiple repositories:

1. Deploy once with a single `GITHUB_TOKEN` that has access to all repos
2. Configure webhook in each repository pointing to the same server
3. The server automatically handles PRs from all configured repos

### Scaling

For high-volume usage:

1. **Horizontal scaling**: Deploy multiple webhook servers behind a load balancer
2. **Queue system**: Add Redis + Celery for async review processing
3. **Distributed Ollama**: Run multiple Ollama instances and load balance requests
4. **Caching**: Cache review patterns and common analysis results

## Integration with Existing Workflows

### With GitHub Actions

You can trigger the review from GitHub Actions:

```yaml
name: PR Review
on:
  pull_request:
    types: [opened, ready_for_review, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Ollama Review
        run: |
          curl -X POST ${{ secrets.WEBHOOK_URL }}/webhook \
            -H "Content-Type: application/json" \
            -H "X-GitHub-Event: pull_request" \
            -d '{"action": "${{ github.event.action }}", ...}'
```

### With CI/CD Pipelines

Integrate with your CI/CD:

```bash
# In your CI script
curl -X POST "${WEBHOOK_URL}/webhook" \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  --data-binary @webhook_payload.json
```

## Future Enhancements

Potential improvements (not yet implemented):

- [ ] Auto-fix common issues (create commits with fixes)
- [ ] Review comment suggestions (inline code suggestions)
- [ ] Custom rule configuration per repository
- [ ] Integration with GitHub Code Scanning API
- [ ] Slack/Discord notifications for review results
- [ ] Review statistics and analytics dashboard
- [ ] Support for GitHub Apps (better security and permissions)
- [ ] Multi-LLM support (GPT-4, Claude, etc. as alternatives)

## Contributing

To contribute improvements:

1. Test changes locally with the webhook server
2. Update documentation if adding new features
3. Add tests for new functionality
4. Follow the project's commit conventions

## References

- [CODE_REVIEW_PATTERNS.md](../.github/CODE_REVIEW_PATTERNS.md) - Anti-patterns guide
- [OLLAMA_SETUP.md](./OLLAMA_SETUP.md) - Ollama installation and configuration
- [GitHub Webhooks Documentation](https://docs.github.com/en/webhooks)
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License

Same as parent project (MIT License).
