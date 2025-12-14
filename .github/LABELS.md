# GitHub Labels Setup

Run these commands to create the standard label set for the repository:

```bash
# Type labels
gh label create "bug" --description "Something isn't working" --color "d73a4a"
gh label create "enhancement" --description "New feature or request" --color "a2eeef"
gh label create "documentation" --description "Improvements or additions to documentation" --color "0075ca"
gh label create "refactor" --description "Code restructuring without functional changes" --color "fbca04"

# Priority labels
gh label create "priority:low" --description "Low priority" --color "e4e669"
gh label create "priority:medium" --description "Medium priority" --color "ffb347"
gh label create "priority:high" --description "High priority" --color "ff6b6b"
gh label create "priority:critical" --description "Critical priority" --color "b60205"

# Component labels
gh label create "component:provider" --description "AI provider related" --color "c5def5"
gh label create "component:parser" --description "Document parser related" --color "c5def5"
gh label create "component:analyzer" --description "Analyzer related" --color "c5def5"
gh label create "component:utils" --description "Utility functions" --color "c5def5"

# Provider-specific labels
gh label create "provider:gemini" --description "Google Gemini" --color "4285f4"
gh label create "provider:ollama" --description "Ollama" --color "000000"

# Status labels
gh label create "needs-triage" --description "Needs initial review" --color "ededed"
gh label create "needs-investigation" --description "Requires investigation" --color "fef2c0"
gh label create "blocked" --description "Blocked by another issue" --color "b60205"
gh label create "work-in-progress" --description "Work in progress" --color "fbca04"
gh label create "ready-for-review" --description "Ready for review" --color "0e8a16"
gh label create "stale" --description "No recent activity" --color "cccccc"

# Community labels
gh label create "good-first-issue" --description "Good for newcomers" --color "7057ff"
gh label create "help-wanted" --description "Extra attention is needed" --color "008672"

# CI/CD labels
gh label create "ci" --description "CI/CD related" --color "0052cc"
gh label create "dependencies" --description "Dependency updates" --color "0366d6"
gh label create "testing" --description "Testing related" --color "1d76db"
gh label create "performance" --description "Performance improvements" --color "ff6f00"
gh label create "security" --description "Security related" --color "d93f0b"

# Special labels
gh label create "breaking-change" --description "Breaking API changes" --color "b60205"
gh label create "pinned" --description "Should not become stale" --color "cccccc"
gh label create "roadmap" --description "Roadmap item" --color "8b5cf6"
gh label create "python" --description "Python code changes" --color "3572A5"
```

## Bulk Creation

Or create all at once:

```bash
gh label create "bug" --description "Something isn't working" --color "d73a4a"
gh label create "enhancement" --description "New feature or request" --color "a2eeef"
gh label create "documentation" --description "Improvements or additions to documentation" --color "0075ca"
gh label create "refactor" --description "Code restructuring without functional changes" --color "fbca04"
gh label create "priority:low" --description "Low priority" --color "e4e669"
gh label create "priority:medium" --description "Medium priority" --color "ffb347"
gh label create "priority:high" --description "High priority" --color "ff6b6b"
gh label create "priority:critical" --description "Critical priority" --color "b60205"
gh label create "component:provider" --description "AI provider related" --color "c5def5"
gh label create "component:parser" --description "Document parser related" --color "c5def5"
gh label create "component:analyzer" --description "Analyzer related" --color "c5def5"
gh label create "component:utils" --description "Utility functions" --color "c5def5"
gh label create "provider:gemini" --description "Google Gemini" --color "4285f4"
gh label create "provider:ollama" --description "Ollama" --color "000000"
gh label create "needs-triage" --description "Needs initial review" --color "ededed"
gh label create "needs-investigation" --description "Requires investigation" --color "fef2c0"
gh label create "blocked" --description "Blocked by another issue" --color "b60205"
gh label create "work-in-progress" --description "Work in progress" --color "fbca04"
gh label create "ready-for-review" --description "Ready for review" --color "0e8a16"
gh label create "stale" --description "No recent activity" --color "cccccc"
gh label create "good-first-issue" --description "Good for newcomers" --color "7057ff"
gh label create "help-wanted" --description "Extra attention is needed" --color "008672"
gh label create "ci" --description "CI/CD related" --color "0052cc"
gh label create "dependencies" --description "Dependency updates" --color "0366d6"
gh label create "testing" --description "Testing related" --color "1d76db"
gh label create "performance" --description "Performance improvements" --color "ff6f00"
gh label create "security" --description "Security related" --color "d93f0b"
gh label create "breaking-change" --description "Breaking API changes" --color "b60205"
gh label create "pinned" --description "Should not become stale" --color "cccccc"
gh label create "roadmap" --description "Roadmap item" --color "8b5cf6"
gh label create "python" --description "Python code changes" --color "3572A5"
```
