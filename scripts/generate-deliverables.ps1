<#
.SYNOPSIS
    LendFlow FinOps Platform - Generate All Deliverables Script
.DESCRIPTION
    Executes automated generators for Excel workbooks, PPTX presentation deck,
    core governance docs, daily logs, and demo assets.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$VenvPython = Join-Path $RootDir "app\backend\.venv\Scripts\python.exe"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  LendFlow FinOps - Generating All Deliverables" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

Push-Location $RootDir
try {
    $env:PYTHONPATH = $RootDir

    Write-Host "`n[1/3] Generating Excel and PPTX Deliverables..." -ForegroundColor Yellow
    & $VenvPython (Join-Path $RootDir "scripts\generate_deliverables.py")

    Write-Host "`n[2/3] Generating Core FinOps Documentation Suite..." -ForegroundColor Yellow
    & $VenvPython (Join-Path $RootDir "scripts\generate_docs.py")

    Write-Host "`n[3/3] Generating 15 Daily Logs and Demo Assets..." -ForegroundColor Yellow
    & $VenvPython (Join-Path $RootDir "scripts\generate_daily_logs_and_demo.py")

    Write-Host "`n=================================================================" -ForegroundColor Cyan
    Write-Host "  All deliverables successfully generated and up to date!" -ForegroundColor Green
    Write-Host "=================================================================" -ForegroundColor Cyan
}
finally {
    Pop-Location
}
