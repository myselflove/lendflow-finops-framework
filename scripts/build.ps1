<#
.SYNOPSIS
    LendFlow FinOps Platform - Production Build and Artifact Verification
.DESCRIPTION
    Compiles the frontend SPA into dist/, validates backend imports,
    and ensures all required deliverables, policies, and docs are intact.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$VenvPython = Join-Path $RootDir "app\backend\.venv\Scripts\python.exe"
$FrontendDir = Join-Path $RootDir "app\frontend"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  LendFlow FinOps - Production Build and Verification" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Compile Frontend
Write-Host "`n[1/3] Compiling React 18 / Vite Frontend..." -ForegroundColor Yellow
Push-Location $FrontendDir
try {
    npm run build
    Write-Host "  [OK] Frontend built successfully to app/frontend/dist" -ForegroundColor Green
}
finally {
    Pop-Location
}

# 2. Verify Backend
Write-Host "`n[2/3] Validating Backend Service..." -ForegroundColor Yellow
Push-Location $RootDir
try {
    $env:PYTHONPATH = $RootDir
    & $VenvPython -c "from app.backend.main import app; print('  [OK] FastAPI app imported successfully.')"
}
finally {
    Pop-Location
}

# 3. Check Deliverables
Write-Host "`n[3/3] Checking Key Deliverable Artifacts..." -ForegroundColor Yellow
$RequiredFiles = @(
    "analysis\billing-analysis.xlsx",
    "analysis\savings-model.xlsx",
    "presentation\cfo-review.pptx",
    "policies\aws\mandatory-tags.json",
    "policies\aws\restrict-gpu.json",
    "policies\aws\approved-regions.json",
    "policies\aws\max-instance-limits.json",
    "policies\opa\finops_guardrails.rego",
    "docs\cost-audit-report.md",
    "docs\requirements-traceability.md"
)

$AllFound = $true
foreach ($rf in $RequiredFiles) {
    $FullPath = Join-Path $RootDir $rf
    if (Test-Path $FullPath) {
        Write-Host "  [OK] $rf" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $rf" -ForegroundColor Red
        $AllFound = $false
    }
}

if ($AllFound) {
    Write-Host "`n=================================================================" -ForegroundColor Cyan
    Write-Host "  Production Build and Artifact Verification: SUCCESS!" -ForegroundColor Green
    Write-Host "=================================================================" -ForegroundColor Cyan
} else {
    Write-Error "One or more required build artifacts are missing."
}
