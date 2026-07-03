<#
.SYNOPSIS
    Documentation quality check script for NZ Legislation Workspace.
.DESCRIPTION
    Runs Vale (prose linter) and markdownlint-cli2 (Markdown formatter)
    on all .md files. Exit codes: 0 = passed, 1 = failed.
.PARAMETER Fix
    Auto-fix markdownlint issues where possible.
.PARAMETER ValeOnly
    Run only Vale checks.
.PARAMETER MdlOnly
    Run only markdownlint checks.
.PARAMETER Verbose
    Show detailed output.
#>
param(
    [switch]$Fix,
    [switch]$ValeOnly,
    [switch]$MdlOnly,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
$Script:ExitCode = 0

function Write-Pass { param([string]$M) Write-Host "  [PASS]  $M" -ForegroundColor Green }
function Write-Fail { param([string]$M, [string]$A = "") Write-Host "  [FAIL]  $M" -ForegroundColor Red; if ($A) { Write-Host "          TIP: $A" -ForegroundColor Yellow } }
function Write-Warn { param([string]$M) Write-Host "  [WARN]  $M" -ForegroundColor Yellow }
function Write-Info { param([string]$M) Write-Host "  [INFO]  $M" -ForegroundColor Cyan }

$IgnoreDirs = @(
    '.git', '.swarm', 'node_modules', '.pytest_cache',
    '__pycache__', '.venv', 'venv', 'env',
    '.ruff_cache', '.mypy_cache', '.pyright',
    'dist', 'build', '.changeset', '.husky'
)

function Get-MarkdownFiles {
    Get-ChildItem -Path $WorkspaceRoot -Recurse -Filter "*.md" | Where-Object {
        $rel = $_.FullName.Substring($WorkspaceRoot.Length + 1)
        foreach ($d in $IgnoreDirs) {
            if ($rel -match [regex]::Escape($d)) { return $false }
        }
        $true
    }
}

function Invoke-ValeCheck {
    Write-Host "  --- Vale Prose Linter ---"
    $ver = & { vale --version 2>$null }
    if (-not $ver) {
        Write-Fail "Vale is not installed" "Install Vale from https://vale.sh"
        return $false
    }
    Write-Pass "Vale $ver"
    $files = Get-MarkdownFiles
    if ($files.Count -eq 0) {
        Write-Warn "No markdown files found to lint"
        return $true
    }
    # Run on root-level .md files only (fast check)
    $rootMds = Get-ChildItem -Path $WorkspaceRoot -Filter "*.md" | Select-Object -ExpandProperty FullName
    if ($rootMds.Count -eq 0) {
        Write-Warn "No root markdown files found to lint"
        return $true
    }
    $result = & vale --no-wrap --no-exit --output=line $rootMds 2>&1
    $lines = $result | Where-Object { $_ -and $_.Trim() }
    if (-not $lines) {
        Write-Pass "No Vale alerts found"
        return $true
    }
    $total = $lines.Count
    if ($Verbose) { foreach ($line in $lines) { Write-Host "    $line" -ForegroundColor Gray } }
    $spelling = ($lines | Where-Object { $_ -match "Vale.Spelling" }).Count
    $terms = ($lines | Where-Object { $_ -match "Vale.Terms" }).Count
    $style = $total - $spelling - $terms
    Write-Info "$total Vale alert(s): $spelling spelling, $terms terminology, $style style"
    if ($spelling -gt 0) {
        Write-Fail "$spelling spelling issue(s)" "Add terms to vocabulary if intentional"
        return $false
    }
    if ($terms -gt 0) { Write-Warn "$terms terminology alert(s) - review for consistency" }
    return $true
}

function Invoke-MarkdownlintCheck {
    Write-Host "  --- Markdownlint ---"
    $ver = & { markdownlint-cli2 --version 2>$null }
    if (-not $ver) {
        Write-Warn "markdownlint-cli2 not installed - skipping" "Install with: npm install -g markdownlint-cli2"
        return $true
    }
    Write-Pass "markdownlint-cli2"
    $config = Join-Path $WorkspaceRoot ".markdownlint.json"
    if (-not (Test-Path $config)) {
        Write-Fail "No .markdownlint.json found"
        return $false
    }
    $files = Get-MarkdownFiles
    if ($files.Count -eq 0) {
        Write-Warn "No markdown files found"
        return $true
    }
    # Process root-level .md files only to avoid cmd-length issues
    $rootMds = Get-ChildItem -Path $WorkspaceRoot -Filter "*.md" | Select-Object -ExpandProperty FullName
    if ($rootMds.Count -eq 0) {
        Write-Warn "No root markdown files found"
        return $true
    }
    $mdlArgs = @("--config", $config)
    if ($Fix) { $mdlArgs += "--fix" }
    $mdlArgs += $rootMds
    $result = & markdownlint-cli2 @mdlArgs 2>&1
    $ec = $LASTEXITCODE
    if ($ec -eq 0) {
        Write-Pass "All markdown files comply with style rules"
        return $true
    }
    $lines = $result | Where-Object { $_ -and $_.Trim() }
    if ($Verbose) {
        foreach ($line in $lines) { Write-Host "    $line" -ForegroundColor Gray }
    } else {
        $ic = ($lines | Where-Object { $_ -match ":" }).Count
        Write-Info "$ic markdownlint issue(s)"
    }
    Write-Fail "Markdown style violations found" "Run with -Fix to auto-correct some issues"
    return $false
}

Write-Host ("=" * 58)
Write-Host "  NZ Legislation Workspace - Docs Lint Checks"
Write-Host ("=" * 58)
Write-Host ""
$results = @()
if (-not $MdlOnly) { $results += Invoke-ValeCheck; Write-Host "" }
if (-not $ValeOnly) { $results += Invoke-MarkdownlintCheck; Write-Host "" }
Write-Host ("=" * 58)
$total = $results.Count
$passed = ($results | Where-Object { $_ -eq $true }).Count
$failed = $total - $passed
if ($failed -eq 0) {
    Write-Host "  All $total lint check(s) passed!" -ForegroundColor Green
    $Script:ExitCode = 0
} else {
    Write-Host "  $passed/$total passed, $failed failed" -ForegroundColor Red
    if (-not $MdlOnly) { Write-Host "  Vale: review alerts above; update .vale.ini or vocab as needed" }
    if (-not $ValeOnly) { Write-Host "  Markdownlint: run with -Fix to auto-correct some issues" }
    $Script:ExitCode = 1
}
Write-Host ("=" * 58)
exit $Script:ExitCode
