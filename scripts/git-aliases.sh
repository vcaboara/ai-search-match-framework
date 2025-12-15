#!/bin/bash
# Git aliases for AI-generated commits
#
# This script provides convenient git aliases for creating commits
# with AI attribution following the ASMF commit conventions.
#
# Usage:
#   source scripts/git-aliases.sh
#   git aic "feat(providers): add new provider"
#
# Or add to your shell configuration (~/.bashrc or ~/.zshrc):
#   echo 'source /path/to/ai-search-match-framework/scripts/git-aliases.sh' >> ~/.bashrc

# AI commit alias - creates a commit with [AI] prefix and attribution footer
# Usage: git aic "feat(providers): add new provider"
git config --global alias.aic '!f() { 
    git commit -m "[AI] $1" -m "---" -m "AI-Generated-By: GitHub Copilot (Claude Sonnet 4.5)"; 
}; f'

# AI commit with custom tool/model - allows specifying different AI tools
# Usage: git aic-custom "feat(parsers): add DOCX support" "Cursor (Claude Opus)"
git config --global alias.aic-custom '!f() { 
    git commit -m "[AI] $1" -m "---" -m "AI-Generated-By: $2"; 
}; f'

# AI commit with body - allows multi-line commit messages
# Usage: git aic-body "feat: add feature" "Detailed description here"
git config --global alias.aic-body '!f() { 
    git commit -m "[AI] $1" -m "$2" -m "---" -m "AI-Generated-By: GitHub Copilot (Claude Sonnet 4.5)"; 
}; f'

echo "✓ AI commit aliases installed successfully!"
echo ""
echo "Available aliases:"
echo "  git aic <message>                    - Create AI commit with standard attribution"
echo "  git aic-custom <message> <tool>      - Create AI commit with custom tool/model"
echo "  git aic-body <subject> <body>        - Create AI commit with detailed body"
echo ""
echo "Examples:"
echo "  git aic 'feat(providers): add Claude provider'"
echo "  git aic-custom 'fix(parsers): handle edge case' 'Cursor (Claude Opus)'"
echo "  git aic-body 'feat: add feature' 'Detailed explanation of changes'"
echo ""
echo "To make these aliases permanent, add this to your ~/.bashrc or ~/.zshrc:"
echo "  source $(pwd)/scripts/git-aliases.sh"
