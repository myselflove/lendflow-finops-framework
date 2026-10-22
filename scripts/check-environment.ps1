<#
.SYNOPSIS
    LendFlow FinOps Framework -- Environment Verification Script
    LendFlow FinOps Platform Group

.DESCRIPTION
    Verifies all required tools and versions are installed.
    Checks project directory structure completeness.
    Reports Portfolio Guard status.

.PARAMETER Quiet
    Suppress verbose output.

.PARAMETER JsonOutput
    Output results as JSON for CI/CD consumption.

.EXAMPLE
    .\scripts\check-environment.ps1
    .\scripts\check-environment.ps1 -JsonOutput
#>
param(
    [switch]$Quiet,
    [switch]$JsonOutput
)

$ErrorActionPreference = "Continue"

# Color helpers
function Write-Pass  { param($msg) Write-Host "  [PASS] $msg" -ForegroundColor Green  }
function Write-Fail  { param($msg) Write-Host "  [FAIL] $msg" -ForegroundColor Red    }
function Write-Warn  { param($msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Info  { param($msg) Write-Host "  [INFO] $msg" -ForegroundColor Cyan   }
function Write-Head  { param($msg) Write-Host "`n$msg" -ForegroundColor Magenta       }

# Results collector
$results   = [System.Collections.Generic.List[hashtable]]::new()
$passCount = 0
$failCount = 0
$warnCount = 0

function Add-Result {
    param([string]$Tool, [string]$Status, [string]$Found, [string]$Required, [string]$Notes)
    $results.Add(@{ Tool=$Tool; Status=$Status; Found=$Found; Required=$Required; Notes=$Notes })
    if ($Status -eq "PASS") { $script:passCount++ }
    elseif ($Status -eq "FAIL") { $script:failCount++ }
    elseif ($Status -eq "WARN") { $script:warnCount++ }
}

function Get-CmdVersion {
    param([string]$Command, [string[]]$Arguments)
    try {
        $out = & $Command $Arguments 2>&1
        if ($out) { return ($out | Select-Object -First 1).ToString().Trim() }
        return $null
    } catch { return $null }
}

function Get-MajorVersion {
    param([string]$VerString)
    $parts = $VerString -split '[.\s]'
    foreach ($p in $parts) {
        $n = 0
        if ([int]::TryParse($p, [ref]$n)) { return $n }
    }
    return 0
}

# ==============================================================================
# HEADER
# ==============================================================================
Write-Host ""
Write-Host "================================================================" -ForegroundColor DarkCyan
Write-Host "  LendFlow FinOps Framework -- Environment Check"                -ForegroundColor Cyan
Write-Host "  Cloud FinOps Engineering Group"                                -ForegroundColor DarkCyan
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"                     -ForegroundColor DarkCyan
Write-Host "================================================================" -ForegroundColor DarkCyan

# ==============================================================================
# 1. PYTHON
# ==============================================================================
Write-Head "1. Python Runtime"

$pyRaw = Get-CmdVersion "python" @("--version")
if (-not $pyRaw) { $pyRaw = Get-CmdVersion "python3" @("--version") }

if ($pyRaw) {
    $pyMajor = Get-MajorVersion ($pyRaw -replace "Python ", "")
    $pyMinor = 0
    $parts   = ($pyRaw -replace "Python ", "") -split "\."
    if ($parts.Count -ge 2) { [int]::TryParse($parts[1], [ref]$pyMinor) | Out-Null }

    if ($pyMajor -ge 3 -and $pyMinor -ge 11) {
        Write-Pass "Python: $pyRaw (>= 3.11 required)"
        Add-Result "Python" "PASS" $pyRaw ">=3.11" ""
    } else {
        Write-Fail "Python too old: $pyRaw (>= 3.11 required)"
        Add-Result "Python" "FAIL" $pyRaw ">=3.11" "Upgrade Python at python.org"
    }
} else {
    Write-Fail "Python not found or not in PATH"
    Add-Result "Python" "FAIL" "not found" ">=3.11" "Install from python.org"
}

$pipRaw = Get-CmdVersion "pip" @("--version")
if ($pipRaw) {
    Write-Pass "pip: $pipRaw"
    Add-Result "pip" "PASS" $pipRaw "any" ""
} else {
    Write-Warn "pip not found (run: python -m ensurepip)"
    Add-Result "pip" "WARN" "not found" "any" "Run: python -m ensurepip"
}

$backendVenv = Join-Path $PSScriptRoot "..\app\backend\.venv"
if (Test-Path $backendVenv) {
    Write-Info "Backend venv found: $backendVenv"
    Add-Result "backend-venv" "PASS" "exists" "optional" ""
} else {
    Write-Info "No backend venv yet (expected until Milestone 3)"
    Add-Result "backend-venv" "WARN" "not found" "optional" "Create with: python -m venv .venv"
}

# ==============================================================================
# 2. NODE.JS
# ==============================================================================
Write-Head "2. Node.js Runtime"

$nodeRaw = Get-CmdVersion "node" @("--version")
if ($nodeRaw) {
    $nodeMajor = Get-MajorVersion ($nodeRaw -replace "v", "")
    if ($nodeMajor -ge 18) {
        Write-Pass "Node.js: $nodeRaw (>= 18 required)"
        Add-Result "Node.js" "PASS" $nodeRaw ">=v18" ""
    } else {
        Write-Fail "Node.js too old: $nodeRaw (>= 18 required)"
        Add-Result "Node.js" "FAIL" $nodeRaw ">=v18" "Upgrade at nodejs.org"
    }
} else {
    Write-Fail "Node.js not found or not in PATH"
    Add-Result "Node.js" "FAIL" "not found" ">=v18" "Install from nodejs.org"
}

# ==============================================================================
# 3. NPM
# ==============================================================================
Write-Head "3. npm Package Manager"

$npmRaw = Get-CmdVersion "npm" @("--version")
if ($npmRaw) {
    $npmMajor = Get-MajorVersion $npmRaw
    if ($npmMajor -ge 9) {
        Write-Pass "npm: $npmRaw (>= 9 required)"
        Add-Result "npm" "PASS" $npmRaw ">=9" ""
    } else {
        Write-Warn "npm may be old: $npmRaw (>= 9 recommended)"
        Add-Result "npm" "WARN" $npmRaw ">=9" "Run: npm install -g npm@latest"
    }
} else {
    Write-Fail "npm not found"
    Add-Result "npm" "FAIL" "not found" ">=9" "Comes with Node.js"
}

# ==============================================================================
# 4. GIT
# ==============================================================================
Write-Head "4. Git Version Control"

$gitRaw = Get-CmdVersion "git" @("--version")
if ($gitRaw) {
    $gitMajor = Get-MajorVersion ($gitRaw -replace "git version ", "")
    if ($gitMajor -ge 2) {
        Write-Pass "Git: $gitRaw (>= 2.x required)"
        Add-Result "Git" "PASS" $gitRaw ">=2.x" ""
    } else {
        Write-Fail "Git too old: $gitRaw"
        Add-Result "Git" "FAIL" $gitRaw ">=2.x" "Upgrade at git-scm.com"
    }
} else {
    Write-Fail "Git not found"
    Add-Result "Git" "FAIL" "not found" ">=2.x" "Install from git-scm.com"
}

# ==============================================================================
# 5. OPTIONAL TOOLS
# ==============================================================================
Write-Head "5. Optional Tools (Recommended for Full Framework)"

Write-Info "PowerShell: $($PSVersionTable.PSVersion)"
Add-Result "PowerShell" "PASS" $PSVersionTable.PSVersion.ToString() ">=5.1" ""

$opaRaw = Get-CmdVersion "opa" @("version")
if ($opaRaw) {
    Write-Pass "OPA found: $($opaRaw -split "`n" | Select-Object -First 1)"
    Add-Result "OPA" "PASS" $opaRaw "optional" ""
} else {
    Write-Warn "OPA not found (optional - needed for policy tests)"
    Write-Info "  Install: winget install OpenPolicyAgent.OPA"
    Add-Result "OPA" "WARN" "not found" "optional" "https://openpolicyagent.org"
}

$tfRaw = Get-CmdVersion "terraform" @("version")
if ($tfRaw) {
    Write-Pass "Terraform found: $($tfRaw -split "`n" | Select-Object -First 1)"
    Add-Result "Terraform" "PASS" "installed" "optional" "Plan-only mode. NEVER run apply."
} else {
    Write-Warn "Terraform not found (optional - needed for IaC policy checks)"
    Add-Result "Terraform" "WARN" "not found" "optional" "https://developer.hashicorp.com/terraform"
}

# ==============================================================================
# 6. PROJECT STRUCTURE VERIFICATION
# ==============================================================================
Write-Head "6. Project Directory Structure"

$root = Split-Path $PSScriptRoot -Parent

$requiredDirs = @(
    "docs",
    "app\frontend",
    "app\backend",
    "analysis\scripts",
    "dashboards\executive",
    "dashboards\engineering-manager",
    "dashboards\team",
    "data",
    "policies\aws",
    "policies\opa",
    "policies\terraform",
    "policies\autoscaling",
    "infrastructure",
    "scripts",
    "tests",
    "presentation\exports",
    "daily-logs",
    "demo"
)

$requiredFiles = @(
    ".gitignore",
    ".env.example",
    "README.md",
    "CHANGELOG.md",
    "docs\requirements-traceability.md",
    "docs\architecture.md",
    "scripts\check-environment.ps1",
    "scripts\prepare-authorized-portfolio.ps1"
)

foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path $root $dir
    if (Test-Path $fullPath -PathType Container) {
        Write-Pass "Dir:  $dir"
        Add-Result "Dir:$dir" "PASS" "exists" "required" ""
    } else {
        Write-Fail "Dir MISSING: $dir"
        Add-Result "Dir:$dir" "FAIL" "missing" "required" "Re-run Milestone 1 setup"
        $failCount++
    }
}

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $root $file
    if (Test-Path $fullPath -PathType Leaf) {
        Write-Pass "File: $file"
        Add-Result "File:$file" "PASS" "exists" "required" ""
    } else {
        Write-Fail "File MISSING: $file"
        Add-Result "File:$file" "FAIL" "missing" "required" "Re-run Milestone 1 and 2 setup"
    }
}

# ==============================================================================
# 7. ENVIRONMENT CONFIGURATION
# ==============================================================================
Write-Head "7. Environment Configuration"

$envFile = Join-Path $root ".env"

if (Test-Path $envFile) {
    Write-Pass ".env file found"
    Add-Result "EnvironmentConfig" "PASS" "Configured" "Configured" ""
} else {
    Write-Info "No .env found - Default settings will be used from .env.example"
    Add-Result "EnvironmentConfig" "INFO" "Default" "Default" "Optional: copy .env.example to .env"
}

# ==============================================================================
# SUMMARY
# ==============================================================================
Write-Host ""
Write-Host "================================================================" -ForegroundColor DarkCyan
Write-Host "  ENVIRONMENT CHECK SUMMARY" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor DarkCyan
Write-Host "  PASS : $passCount" -ForegroundColor Green
Write-Host "  WARN : $warnCount" -ForegroundColor Yellow
Write-Host "  FAIL : $failCount" -ForegroundColor Red
Write-Host "================================================================" -ForegroundColor DarkCyan

if ($failCount -eq 0) {
    Write-Host "`n  STATUS: ENVIRONMENT READY" -ForegroundColor Green
    Write-Host "  All required tools and project files are in place." -ForegroundColor Green
} elseif ($failCount -le 2) {
    Write-Host "`n  STATUS: PARTIALLY READY" -ForegroundColor Yellow
    Write-Host "  Some items are missing. Fix FAIL items before running the framework." -ForegroundColor Yellow
} else {
    Write-Host "`n  STATUS: ENVIRONMENT NOT READY" -ForegroundColor Red
    Write-Host "  Multiple critical items missing. See FAIL items above." -ForegroundColor Red
}
Write-Host ""

if ($JsonOutput) {
    @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        pass      = $passCount
        warn      = $warnCount
        fail      = $failCount
        ready     = ($failCount -eq 0)
        results   = ($results | ForEach-Object { $_ })
    } | ConvertTo-Json -Depth 4
}

exit $failCount
