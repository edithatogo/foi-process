param(
    [string[]]$Workspaces = @(
        "cli-legislation-nz",
        "corpus-cases-medilegal-nz",
        "corpus-law-nz",
        "corpus-nz-hansard",
        "hathi-nz",
        "nlp-policy-nz",
        "sm-govt-nz"
    ),
    [string]$Root = (Resolve-Path ".").Path
)

$ErrorActionPreference = "Stop"
function Quote-Arg([string]$s) { '"' + ($s -replace '"','\"') + '"' }

$runner = Join-Path $Root "scripts\run_swarm_agent_process.ps1"
$agents = @(
    @{ Name = "general_coder"; Kind = "cline"; Provider = "deepseek"; Model = "deepseek-v4-flash" },
    @{ Name = "architect_oracle"; Kind = "cline"; Provider = "deepseek"; Model = "deepseek-v4-flash" },
    @{ Name = "codex_gpt55_engineer"; Kind = "codex"; Provider = ""; Model = "gpt-5.5" },
    @{ Name = "chrome_operator"; Kind = "codex"; Provider = ""; Model = "gpt-5.5" },
    @{ Name = "quality_validator"; Kind = "cline"; Provider = "deepseek"; Model = "deepseek-v4-flash" }
)

$supervisorRunId = Get-Date -Format "yyyyMMdd-HHmmss"
$supervisorRoot = Join-Path $Root ".swarm\subdir-supervisor\$supervisorRunId"
New-Item -ItemType Directory -Force -Path $supervisorRoot | Out-Null
$statusPath = Join-Path $supervisorRoot "status.jsonl"

foreach ($name in $Workspaces) {
    $workspace = Join-Path $Root $name
    if (-not (Test-Path -LiteralPath $workspace)) {
        @{ ts=(Get-Date).ToUniversalTime().ToString("o"); workspace=$name; event="skipped"; reason="missing directory" } | ConvertTo-Json -Compress | Add-Content -LiteralPath $statusPath
        continue
    }
    if (-not (Test-Path -LiteralPath (Join-Path $workspace "task_plan.md"))) {
        @{ ts=(Get-Date).ToUniversalTime().ToString("o"); workspace=$name; event="skipped"; reason="missing task_plan.md" } | ConvertTo-Json -Compress | Add-Content -LiteralPath $statusPath
        continue
    }

    $runId = Get-Date -Format "yyyyMMdd-HHmmss"
    $runRoot = Join-Path $workspace ".swarm\runs\$runId"
    $promptRoot = Join-Path $workspace ".swarm\prompts"
    New-Item -ItemType Directory -Force -Path $runRoot,$promptRoot | Out-Null
    $manifest = [ordered]@{ run_id=$runId; workspace=$workspace; started_at=(Get-Date).ToUniversalTime().ToString("o"); agents=@() }
    @{ ts=(Get-Date).ToUniversalTime().ToString("o"); workspace=$name; event="workspace_started"; run_id=$runId } | ConvertTo-Json -Compress | Add-Content -LiteralPath $statusPath

    $processes = @()
    foreach ($agent in $agents) {
        $promptPath = Join-Path $promptRoot "$($agent.Name)_subdir_swarm.md"
        @"
You are $($agent.Name) in the Antigravity subdirectory swarm for `$name`.

Workspace: `$workspace`

Mission:
- Use local `task_plan.md`, `subagents.yaml` when present, `swarm-config.yaml` when present, and `conductor/tracks.md` as source of truth.
- Run outstanding local, non-gated Conductor work for this subdirectory only.
- Preserve repo boundaries and user changes.
- Record evidence in the relevant local Conductor/status surface.

Gate rules:
- Do not commit, push, upload, publish, mutate external accounts/services, edit/sync `.env`, use browser profiles, or perform Chrome/account work unless the user explicitly approves that specific gate.
- If this lane is `chrome_operator`, handle only explicitly approved Chrome/browser-profile tasks; otherwise queue them as gated.
- If all local non-gated work is complete, report that clearly with the evidence checked.
"@ | Set-Content -LiteralPath $promptPath -NoNewline

        $stdout = Join-Path $runRoot "$($agent.Name).out.log"
        $stderr = Join-Path $runRoot "$($agent.Name).err.log"
        $last = Join-Path $runRoot "$($agent.Name).last.md"
        $parts = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Quote-Arg $runner), "-Kind", (Quote-Arg $agent.Kind), "-Model", (Quote-Arg $agent.Model), "-Workspace", (Quote-Arg $workspace), "-PromptPath", (Quote-Arg $promptPath), "-OutputLastMessage", (Quote-Arg $last))
        if ($agent.Provider) { $parts += @("-Provider", (Quote-Arg $agent.Provider)) }
        if ($agent.Kind -eq "cline") {
            $dataDir = Join-Path $workspace ".swarm\cline_state\$($agent.Name)"
            $parts += @("-DataDir", (Quote-Arg $dataDir))
        }
        $process = Start-Process -FilePath "powershell" -ArgumentList ($parts -join " ") -WorkingDirectory $workspace -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
        $processes += $process
        $manifest.agents += [ordered]@{ name=$agent.Name; kind=$agent.Kind; model=$agent.Model; pid=$process.Id; stdout=$stdout; stderr=$stderr; prompt=$promptPath; started_at=(Get-Date).ToUniversalTime().ToString("o") }
        @{ ts=(Get-Date).ToUniversalTime().ToString("o"); workspace=$name; event="agent_started"; agent=$agent.Name; pid=$process.Id; run_id=$runId } | ConvertTo-Json -Compress | Add-Content -LiteralPath $statusPath
        Start-Sleep -Milliseconds 750
    }

    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $runRoot "manifest.json") -NoNewline
    foreach ($p in $processes) { Wait-Process -Id $p.Id -ErrorAction SilentlyContinue }
    @{ ts=(Get-Date).ToUniversalTime().ToString("o"); workspace=$name; event="workspace_finished"; run_id=$runId } | ConvertTo-Json -Compress | Add-Content -LiteralPath $statusPath
    Start-Sleep -Seconds 5
}

@{ ts=(Get-Date).ToUniversalTime().ToString("o"); event="supervisor_finished"; run_id=$supervisorRunId } | ConvertTo-Json -Compress | Add-Content -LiteralPath $statusPath
