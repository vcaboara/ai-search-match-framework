# AI Search & Match Framework - TODO

## AI/ML Infrastructure & Automation

- [ ] **Fix CI: ModuleNotFoundError for webhook_server (#29)**
  - Priority: P1 (blocking main branch CI)
  - Issue: Docker container can't import webhook_server.py
  - Root cause: webhook_server.py in project root, PYTHONPATH doesn't include it
  - Solution: Add ENV PYTHONPATH="/workspace:${PYTHONPATH}" to Dockerfile  - Files: Dockerfile, .github/workflows/ci.yml, tests/test_webhook_server.py
  - Expected: All tests pass in CI environment

- [ ] **Visual regression testing with Playwright (#30)**
  - Priority: P2 (enhancement)
  - Migrate screenshot_utils.py from job-lead-finder
  - Create workflow for before/after PR screenshots
  - Add playwright>=1.40.0 dependency
  - Document in docs/VISUAL_REGRESSION.md
