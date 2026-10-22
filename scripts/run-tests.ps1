<#
.SYNOPSIS
    LendFlow FinOps Platform - Test Runner Script
.DESCRIPTION
    Executes pytest across all test suites with verbose output and coverage checks.
#>

[CmdletBinding()]
param(
    [string]$TestSuite = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$VenvPython = Join-Path $RootDir "app\backend\.venv\Scripts\python.exe"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  LendFlow FinOps - Test Suite Runner" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

Push-Location $RootDir
try {
    $env:PYTHONPATH = $RootDir
    if ($TestSuite) {
        Write-Host "Running specific test suite: $TestSuite" -ForegroundColor Yellow
        & $VenvPython -m pytest $TestSuite -v
    } else {
        Write-Host "Running all test suites in tests/..." -ForegroundColor Yellow
        & $VenvPython -m pytest -v
    }
}
finally {
    Pop-Location
}
