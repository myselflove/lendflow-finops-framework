<#
.SYNOPSIS
    LendFlow FinOps Platform - Local Development Runner
.DESCRIPTION
    Launches both the FastAPI backend and Vite frontend development server.
#>

[CmdletBinding()]
param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$VenvPython = Join-Path $RootDir "app\backend\.venv\Scripts\python.exe"
$FrontendDir = Join-Path $RootDir "app\frontend"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  Starting LendFlow FinOps Development Servers" -ForegroundColor Cyan
Write-Host "  Backend:  http://127.0.0.1:$BackendPort (API and Swagger Docs at /docs)" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:$FrontendPort" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan

# Start Backend Job or Process
$BackendScript = @"
Set-Location '$RootDir'
& '$VenvPython' -m uvicorn app.backend.main:app --host 127.0.0.1 --port $BackendPort --reload
"@

Write-Host "`nLaunching FastAPI Backend in background job..." -ForegroundColor Gray
$BackendJob = Start-Job -ScriptBlock {
    param($root, $py, $port)
    Set-Location $root
    & $py -m uvicorn app.backend.main:app --host 127.0.0.1 --port $port --reload
} -ArgumentList $RootDir, $VenvPython, $BackendPort

Write-Host "Starting Frontend (Vite)... Press Ctrl+C to terminate both servers." -ForegroundColor Gray
Push-Location $FrontendDir
try {
    npm run dev -- --port $FrontendPort
}
finally {
    Pop-Location
    Write-Host "`nStopping background backend job..." -ForegroundColor Yellow
    Stop-Job $BackendJob -ErrorAction SilentlyContinue
    Remove-Job $BackendJob -ErrorAction SilentlyContinue
    Write-Host "Servers stopped." -ForegroundColor Green
}
