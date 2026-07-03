param(
    [string]$Workspace = (Resolve-Path ".").Path
)

$ErrorActionPreference = "Stop"

$latestPath = Join-Path $Workspace ".swarm\runs\latest-run.txt"
if (!(Test-Path -LiteralPath $latestPath)) {
    throw "No latest swarm run found at $latestPath"
}

$runId = (Get-Content -LiteralPath $latestPath -Raw).Trim()
$runRoot = Join-Path $Workspace ".swarm\runs\$runId"
$manifestPath = Join-Path $runRoot "manifest.json"
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

$rows = foreach ($agent in $manifest.agents) {
    $proc = Get-Process -Id $agent.pid -ErrorAction SilentlyContinue
    $outSize = if (Test-Path -LiteralPath $agent.stdout) { (Get-Item -LiteralPath $agent.stdout).Length } else { 0 }
    $errSize = if (Test-Path -LiteralPath $agent.stderr) { (Get-Item -LiteralPath $agent.stderr).Length } else { 0 }
    [pscustomobject]@{
        Agent = $agent.name
        PID = $agent.pid
        Model = $agent.model
        Running = [bool]$proc
        OutBytes = $outSize
        ErrBytes = $errSize
        OutLog = $agent.stdout
        ErrLog = $agent.stderr
    }
}

$rows | Format-Table -AutoSize

