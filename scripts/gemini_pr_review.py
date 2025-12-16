#!/usr/bin/env python3
"""
Gemini PR Review Script
Quick architectural review using Gemini API.
"""

import argparse
import os
import sys

try:
    import google.generativeai as genai
    from github import Github
except ImportError:
    print("Error: Required packages not installed")
    print("Run: pip install google-generativeai PyGithub")
    sys.exit(1)


def review_pr(repo_name: str, pr_number: int) -> str:
    """Review a PR using Gemini."""

    # Configure Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "❌ GEMINI_API_KEY environment variable required"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    # Get PR info
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        return "❌ GITHUB_TOKEN environment variable required"

    gh = Github(github_token)
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    # Get files
    files = list(pr.get_files())
    files_summary = "\n".join(
        [f"{f.filename} (+{f.additions} -{f.deletions})" for f in files[:30]]
    )

    # Build prompt
    prompt = f"""Review this Flask blueprint refactoring PR:

**Repository**: {repo_name}
**PR #{pr_number}**: {pr.title}

**Changed Files** ({len(files)} total, showing first 30):
{files_summary}

**PR Description**:
{pr.body[:500] if pr.body else 'No description'}

**Key Architecture Changes**:
- Refactored monolithic server.py into Flask blueprints
- Created modular structure with blueprints for different concerns
- Added middleware and services layers
- Updated tests for new architecture

**Communication Style**:
- Be concise and direct. Optimize for token efficiency and human readability.
- Keep responses brief - focus on critical architectural issues only.
- Avoid verbose explanations. Target 1-2 sentences per point when possible.
- Skip unnecessary framing phrases.

**Review Focus**:
1. **Architecture**: Is the blueprint organization logical and maintainable?
2. **Code Quality**: Any anti-patterns or code smells?
3. **Testing**: Are tests properly updated for the new structure?
4. **Documentation**: What documentation needs updating?
5. **Migration**: Any backwards compatibility concerns?

Provide **specific, actionable feedback** with:
- ✅ What's working well
- ⚠️ Potential issues
- 💡 Suggestions for improvement

Be constructive and focus on architectural decisions."""

    try:
        response = model.generate_content(prompt)
        return f"""## 🤖 Gemini Architectural Review

{response.text}

---
*Reviewed by Gemini 2.0 Flash Exp • Architectural Analysis*
"""
    except Exception as e:
        return f"❌ Gemini API error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Review PR using Gemini API")
    parser.add_argument("--repo", required=True,
                        help="Repository (owner/repo)")
    parser.add_argument("--pr", type=int, required=True, help="PR number")

    args = parser.parse_args()

    result = review_pr(args.repo, args.pr)
    print(result)

    return 0 if "❌" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
