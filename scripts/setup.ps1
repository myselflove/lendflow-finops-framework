<#
.SYNOPSIS
    LendFlow FinOps Platform - Setup and Dependency Installation Script
.DESCRIPTION
    Sets up the Python virtual environment, installs backend dependencies,
    installs frontend npm packages, and verifies system prerequisites.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  LendFlow FinOps - Environment Setup and Installation" -ForegroundColor Cyan
Write-Host "  Cloud FinOps Engineering Group" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Check Python
Write-Host "`n[1/4] Checking Python..." -ForegroundColor Yellow
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Error "Python is not installed or not in PATH."
}
$PyVersion = python --version
Write-Host "  Found: $PyVersion" -ForegroundColor Green

# 2. Virtual Environment and Python dependencies
Write-Host "`n[2/4] Setting up Python virtual environment..." -ForegroundColor Yellow
$VenvDir = Join-Path $RootDir "app\backend\.venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "  Creating virtual environment at $VenvDir..." -ForegroundColor Gray
    python -m venv $VenvDir
}

Write-Host "  Installing backend requirements..." -ForegroundColor Gray
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $RootDir "requirements.txt")
Write-Host "  [OK] Python dependencies installed." -ForegroundColor Green

# 3. Check Node and npm, install frontend packages
Write-Host "`n[3/4] Setting up Frontend dependencies..." -ForegroundColor Yellow
$NodeCmd = Get-Command node -ErrorAction SilentlyContinue
$NpmCmd = Get-Command npm -ErrorAction SilentlyContinue

if ($NodeCmd -and $NpmCmd) {
    $NodeVersion = node --version
    $NpmVersion = npm --version
    Write-Host "  Found Node: $NodeVersion, npm: $NpmVersion" -ForegroundColor Green

    $FrontendDir = Join-Path $RootDir "app\frontend"
    Push-Location $FrontendDir
    try {
        Write-Host "  Installing npm packages in app/frontend..." -ForegroundColor Gray
        npm install
        Write-Host "  [OK] Frontend dependencies installed." -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
} else {
    Write-Warning "Node.js or npm not found in PATH. Frontend setup skipped."
}

# 4. Generate datasets if missing
Write-Host "`n[4/4] Verifying synthetic datasets..." -ForegroundColor Yellow
$DataDir = Join-Path $RootDir "data"
$SummaryCsv = Join-Path $DataDir "monthly_cost_summary.csv"

if (-not (Test-Path $SummaryCsv)) {
    Write-Host "  Generating synthetic datasets via scripts/generate_data.py..." -ForegroundColor Gray
    & $VenvPython (Join-Path $RootDir "scripts\generate_data.py")
} else {
    Write-Host "  [OK] Synthetic datasets already exist in data/." -ForegroundColor Green
}

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host "  LendFlow FinOps environment setup COMPLETE!" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan
