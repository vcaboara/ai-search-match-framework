<#
.SYNOPSIS
    Apply enhanced branch protection rules to the main branch.

.DESCRIPTION
    This script applies comprehensive branch protection settings to the main branch
    using the GitHub API. It requires GitHub CLI (gh) to be installed and authenticated.

.EXAMPLE
    .\scripts\apply-branch-protection.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Applying Enhanced Branch Protection Rules ===" -ForegroundColor Cyan

# Check if gh CLI is available
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/"
    exit 1
}

# Check if authenticated
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Not authenticated with GitHub CLI. Run 'gh auth login' first."
    exit 1
}

Write-Host " GitHub CLI authenticated" -ForegroundColor Green

# Get repository info
$repo = gh repo view --json nameWithOwner -q .nameWithOwner
Write-Host "Repository: $repo" -ForegroundColor Yellow

# Apply branch protection
Write-Host "`nApplying branch protection rules to main branch..." -ForegroundColor Cyan

# Build config path properly for PowerShell 5.1
$configPath = Join-Path (Join-Path (Split-Path $PSScriptRoot -Parent) ".github") "branch-protection.json"
if (-not (Test-Path $configPath)) {
    Write-Error "Branch protection config not found at: $configPath"
    exit 1
}

try {
    $result = gh api "repos/$repo/branches/main/protection" `
        --method PUT `
        --input $configPath 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n Branch protection rules applied successfully!" -ForegroundColor Green
        Write-Host "`nProtection settings:" -ForegroundColor Yellow
        Write-Host "   Required PR reviews: 1 approval" -ForegroundColor White
        Write-Host "   Code owner review required" -ForegroundColor White
        Write-Host "   Dismiss stale reviews enabled" -ForegroundColor White
        Write-Host "   Require conversation resolution" -ForegroundColor White
        Write-Host "   Require linear history" -ForegroundColor White
        Write-Host "   Enforce for administrators" -ForegroundColor White
        Write-Host "   Prevent force pushes" -ForegroundColor White
        Write-Host "   Prevent branch deletion" -ForegroundColor White
        
        Write-Host "`nView settings: https://github.com/$repo/settings/branches" -ForegroundColor Cyan
    }
    else {
        Write-Error "Failed to apply branch protection: $result"
        exit 1
    }
}
catch {
    Write-Error "Error applying branch protection: $_"
    exit 1
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
