# Git aliases for AI-generated commits (PowerShell)
#
# This script provides convenient git aliases for creating commits
# with AI attribution following the ASMF commit conventions.
#
# Usage:
#   . .\scripts\git-aliases.ps1
#   git aic "feat(providers): add new provider"
#
# Or add to your PowerShell profile:
#   Add-Content $PROFILE "`n. `"$PWD\scripts\git-aliases.ps1`""

# AI commit alias - creates a commit with [AI] prefix and attribution footer
# Usage: git aic "feat(providers): add new provider"
git config --global alias.aic '!f() { git commit -m "[AI] $1" -m "---" -m "AI-Generated-By: GitHub Copilot (Claude Sonnet 4.5)"; }; f'

# AI commit with custom tool/model - allows specifying different AI tools
# Usage: git aic-custom "feat(parsers): add DOCX support" "Cursor (Claude Opus)"
git config --global alias.aic-custom '!f() { git commit -m "[AI] $1" -m "---" -m "AI-Generated-By: $2"; }; f'

# AI commit with body - allows multi-line commit messages
# Usage: git aic-body "feat: add feature" "Detailed description here"
git config --global alias.aic-body '!f() { git commit -m "[AI] $1" -m "$2" -m "---" -m "AI-Generated-By: GitHub Copilot (Claude Sonnet 4.5)"; }; f'

Write-Host "✓ AI commit aliases installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Available aliases:"
Write-Host "  git aic <message>                    - Create AI commit with standard attribution"
Write-Host "  git aic-custom <message> <tool>      - Create AI commit with custom tool/model"
Write-Host "  git aic-body <subject> <body>        - Create AI commit with detailed body"
Write-Host ""
Write-Host "Examples:"
Write-Host "  git aic 'feat(providers): add Claude provider'"
Write-Host "  git aic-custom 'fix(parsers): handle edge case' 'Cursor (Claude Opus)'"
Write-Host "  git aic-body 'feat: add feature' 'Detailed explanation of changes'"
Write-Host ""
Write-Host "To make these aliases permanent, add this to your PowerShell profile:" -ForegroundColor Yellow
Write-Host "  Add-Content `$PROFILE `"`n. `"$PWD\scripts\git-aliases.ps1`"`""
