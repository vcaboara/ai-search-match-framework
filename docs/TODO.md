# AI Search & Match Framework - TODO

## High Priority

### Fix CI: ModuleNotFoundError for webhook_server in Docker tests
**Issue**: #29
**Priority**: High - blocking main branch CI
**Description**: CI fails because Docker container can't import webhook_server.py from project root. Tests pass locally but fail in CI.

**Root Cause**:
- webhook_server.py is in project root (not under src/)
- Docker container's PYTHONPATH doesn't include project root
- Tests can import locally but fail in CI Docker environment

**Potential Solutions**:
1. Add project root to PYTHONPATH in Dockerfile (preferred)
   - Modify Dockerfile to include: `ENV PYTHONPATH="/workspace:${PYTHONPATH}"`
2. Move webhook_server.py to src/asmf/
   - Would require updating all imports and documentation
3. Install as package in Docker
   - Add setup.py or use pyproject.toml to install project as editable package

**Files to Check**:
- .github/workflows/ci.yml (line 38)
- Dockerfile (PYTHONPATH configuration)
- tests/test_webhook_server.py (line 11: `from webhook_server import...`)

**Expected Behavior**: All tests including test_webhook_server.py should pass in CI environment
