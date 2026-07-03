param(
    [Parameter(ParameterSetName = "launch")]
    [string]$Workspace = (Resolve-Path ".").Path,

    [Parameter(ParameterSetName = "launch")]
    [string[]]$AgentFilter = @(),

    [Parameter(ParameterSetName = "launch")]
    [switch]$Wait,

    [Parameter(ParameterSetName = "launch")]
    [int]$WaitTimeoutSeconds = 86400,

    [Parameter(ParameterSetName = "stop")]
    [switch]$Stop,

    [Parameter(ParameterSetName = "stop")]
    [string]$StopRunId = "",

    [Parameter(ParameterSetName = "status")]
    [switch]$Status,

    [Parameter(ParameterSetName = "status")]
    [string]$StatusWorkspace = (Resolve-Path ".").Path
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Get-LatestRunId {
    param([string]$Workspace)
    $latestPath = Join-Path $Workspace ".swarm\runs\latest-run.txt"
    if (Test-Path -LiteralPath $latestPath) {
        return (Get-Content -LiteralPath $latestPath -Raw).Trim()
    }
    return $null
}

function Get-RunManifest {
    param([string]$RunRoot)
    $manifestPath = Join-Path $RunRoot "manifest.json"
    if (Test-Path -LiteralPath $manifestPath) {
        return Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    }
    return $null
}

function Write-StatusEvent {
    param([string]$EventPath, [hashtable]$Payload)
    $Payload.ts = (Get-Date).ToUniversalTime().ToString("o")
    $Payload | ConvertTo-Json -Compress | Add-Content -LiteralPath $EventPath -Encoding UTF8
}

# ===========================================================================
# ACTION: Status (show status of latest run)
# ===========================================================================
if ($Status) {
    $ws = if ($StatusWorkspace) { $StatusWorkspace } else { $Workspace }
    $runId = Get-LatestRunId -Workspace $ws
    if (-not $runId) { Write-Warning "No latest swarm run found."; exit 0 }
    $runRoot = Join-Path $ws ".swarm\runs\$runId"
    $manifest = Get-RunManifest -RunRoot $runRoot
    if (-not $manifest) { Write-Warning "Manifest not found"; exit 1 }

    Write-Host "=== Antigravity Swarm Run $runId ===" -ForegroundColor Cyan
    Write-Host "Started : $($manifest.started_at)"
    Write-Host "Agents  : $($manifest.agents.Count)`n"

    $rows = foreach ($agent in $manifest.agents) {
        $proc = Get-Process -Id $agent.pid -ErrorAction SilentlyContinue
        $outSize = if (Test-Path $agent.stdout) { (Get-Item $agent.stdout).Length } else { 0 }
        $errSize = if (Test-Path $agent.stderr) { (Get-Item $agent.stderr).Length } else { 0 }
        [PSCustomObject]@{ Agent=$agent.name; Kind=$agent.kind; Model=$agent.model; PID=$agent.pid; Running=[bool]$proc; OutBytes=$outSize; ErrBytes=$errSize }
    }
    $rows | Format-Table -AutoSize

    foreach ($agent in $manifest.agents) {
        $errSize = if (Test-Path $agent.stderr) { (Get-Item $agent.stderr).Length } else { 0 }
        if ($errSize -gt 0) {
            $lastErr = Get-Content $agent.stderr -Tail 3 -ErrorAction SilentlyContinue
            if ($lastErr) { Write-Host "-- $($agent.name) stderr --" -ForegroundColor Yellow; $lastErr | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkYellow } }
        }
    }
    exit 0
}

# ===========================================================================
# ACTION: Stop (terminate all agent processes from a previous run)
# ===========================================================================
if ($Stop) {
    if ($StopRunId) { $runRoot = Join-Path $Workspace ".swarm\runs\$StopRunId" }
    else {
        $runId = Get-LatestRunId -Workspace $Workspace
        if (-not $runId) { Write-Warning "No latest run to stop."; exit 0 }
        $runRoot = Join-Path $Workspace ".swarm\runs\$runId"
    }
    $manifest = Get-RunManifest -RunRoot $runRoot
    if (-not $manifest) { Write-Warning "No manifest found at $runRoot"; exit 1 }

    $stopped = 0
    foreach ($agent in $manifest.agents) {
        $proc = Get-Process -Id $agent.pid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Stopping $($agent.name) (PID $($agent.pid))..." -NoNewline
            try { $proc.Kill(); $proc.WaitForExit(5000) | Out-Null; Write-Host " done" -ForegroundColor Green; $stopped++ }
            catch { Write-Host " failed: $_" -ForegroundColor Red }
        }
        else { Write-Host "$($agent.name) (PID $($agent.pid)) - not running" -ForegroundColor DarkGray }
    }
    Write-Host "Stopped $stopped agent(s)." -ForegroundColor Cyan
    exit 0
}

# ===========================================================================
# ACTION: Launch (default)
# ===========================================================================
$runId = Get-Date -Format "yyyyMMdd-HHmmss"
$runRoot = Join-Path $Workspace ".swarm\runs\$runId"
$statusPath = Join-Path $runRoot "status.jsonl"
New-Item -ItemType Directory -Force -Path $runRoot | Out-Null

$runnerScript = Join-Path $PSScriptRoot "run_swarm_agent_process.ps1"
if (-not (Test-Path -LiteralPath $runnerScript)) { throw "Runner script not found at $runnerScript" }

$agentDefs = @(
    @{ Name="general_coder"; Kind="cline"; Provider="deepseek"; Model="deepseek-v4-flash"; Prompt=".swarm\prompts\general_coder_all_conductor.md"; DataDir=".swarm\cline_state\general_coder" },
    @{ Name="architect_oracle"; Kind="cline"; Provider="deepseek"; Model="deepseek-v4-flash"; Prompt=".swarm\prompts\architect_oracle_all_conductor.md"; DataDir=".swarm\cline_state\architect_oracle" },
    @{ Name="codex_gpt55_engineer"; Kind="codex"; Model="gpt-5.5"; Prompt=".swarm\prompts\codex_gpt55_all_conductor.md" },
    @{ Name="chrome_operator"; Kind="codex"; Model="gpt-5.5"; Prompt=".swarm\prompts\chrome_operator_all_conductor.md" },
    @{ Name="quality_validator"; Kind="cline"; Provider="deepseek"; Model="deepseek-v4-flash"; Prompt=".swarm\prompts\quality_validator_all_conductor.md"; DataDir=".swarm\cline_state\quality_validator" }
)

if ($AgentFilter.Count -gt 0) {
    $agentDefs = $agentDefs | Where-Object { $_.Name -in $AgentFilter }
    if ($agentDefs.Count -eq 0) { Write-Warning "No agents matched filter"; exit 1 }
}

$manifest = [ordered]@{ run_id=$runId; workspace=$Workspace; started_at=(Get-Date).ToUniversalTime().ToString("o"); agents=@() }
$processes = @()
Write-Host "Launching antigravity swarm run $runId in $Workspace" -ForegroundColor Cyan
Write-Host "Agents: $($agentDefs.Name -join ', ')`n"

foreach ($agent in $agentDefs) {
    $promptPath = Join-Path $Workspace $agent.Prompt
    if (-not (Test-Path $promptPath)) {
        $promptPath = Join-Path (Split-Path $PSScriptRoot -Parent) $agent.Prompt
    }
    if (-not (Test-Path $promptPath)) { Write-Warning "Prompt not found for $($agent.Name): $promptPath"; continue }

    $stdout = Join-Path $runRoot "$($agent.Name).out.log"
    $stderr = Join-Path $runRoot "$($agent.Name).err.log"

    try {
        if ($agent.Kind -eq "cline") {
            $dataDir = Join-Path $Workspace $agent.DataDir
            New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
            $argList = @("-NoProfile","-ExecutionPolicy","Bypass","-File",$runnerScript,"-Kind","cline","-Workspace",$Workspace,"-PromptPath",$promptPath,"-Provider",$agent.Provider,"-Model",$agent.Model,"-DataDir",$dataDir)
            Write-Host "  [start] $($agent.Name) (cline, $($agent.Model))" -ForegroundColor Green
            $process = Start-Process -FilePath "powershell" -ArgumentList $argList -WorkingDirectory $Workspace -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
        }
        elseif ($agent.Kind -eq "codex") {
            $argList = @("-NoProfile","-ExecutionPolicy","Bypass","-File",$runnerScript,"-Kind","codex","-Workspace",$Workspace,"-PromptPath",$promptPath,"-Model",$agent.Model,"-OutputLastMessage",(Join-Path $runRoot "$($agent.Name).last.md"))
            Write-Host "  [start] $($agent.Name) (codex, $($agent.Model))" -ForegroundColor Green
            $process = Start-Process -FilePath "powershell" -ArgumentList $argList -WorkingDirectory $Workspace -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
        }
        else { Write-Warning "Unknown kind '$($agent.Kind)' for $($agent.Name)"; continue }

        $processes += $process
        $manifest.agents += [ordered]@{ "name"=$agent.Name; "kind"=$agent.Kind; "model"=$agent.Model; "pid"=$process.Id; "stdout"=$stdout; "stderr"=$stderr; "prompt"=$promptPath; "started_at"=(Get-Date).ToUniversalTime().ToString("o") }
        Write-StatusEvent -EventPath $statusPath -Payload @{ "event"="agent_started"; "agent"=$agent.Name; "pid"=$process.Id }
        Start-Sleep -Milliseconds 750
    }
    catch {
        Write-Warning "Failed to launch $($agent.Name): $_"
        Write-StatusEvent -EventPath $statusPath -Payload @{ event="agent_failed"; agent=$agent.Name; reason=$_.ToString() }
    }
}

$manifestPath = Join-Path $runRoot "manifest.json"
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

$latestPath = Join-Path $Workspace ".swarm\runs\latest-run.txt"
Set-Content -LiteralPath $latestPath -Value $runId -Encoding UTF8

Write-StatusEvent -EventPath $statusPath -Payload @{ event="launch_complete"; run_id=$runId; agents=$manifest.agents.Count }
Write-Host "`nSwarm launched - manifest: $manifestPath" -ForegroundColor Cyan

# Optional: Wait for agents to finish
if ($Wait -and $processes.Count -gt 0) {
    Write-Host "Waiting for $($processes.Count) agent(s) (timeout: ${WaitTimeoutSeconds}s)..." -ForegroundColor Yellow
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $remaining = $processes | ForEach-Object { $_.Id }
    while ($remaining.Count -gt 0 -and $sw.Elapsed.TotalSeconds -lt $WaitTimeoutSeconds) {
        $stillRunning = @()
        foreach ($pid in $remaining) {
            if (Get-Process -Id $pid -ErrorAction SilentlyContinue) { $stillRunning += $pid }
            else {
                $entry = $manifest.agents | Where-Object { $_.pid -eq $pid }
                Write-Host "  [done] $($entry.name) exited" -ForegroundColor Green
                Write-StatusEvent -EventPath $statusPath -Payload @{ event="agent_exited"; agent=$entry.name; pid=$pid }
            }
        }
        $remaining = $stillRunning
        if ($remaining.Count -gt 0) { Start-Sleep -Seconds 5 }
    }
    if ($remaining.Count -gt 0) { Write-Host "Timeout - $($remaining.Count) still running" -ForegroundColor Yellow }
    Write-Host "Wait complete ($($sw.Elapsed))" -ForegroundColor Cyan
}

Write-Output $manifestPath
