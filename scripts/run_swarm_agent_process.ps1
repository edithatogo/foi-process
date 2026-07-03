param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("cline", "codex")]
    [string]$Kind,

    [Parameter(Mandatory = $true)]
    [string]$Workspace,

    [Parameter(Mandatory = $true)]
    [string]$PromptPath,

    [string]$Provider = "",
    [Parameter(Mandatory = $true)]
    [string]$Model,
    [string]$DataDir = "",
    [string]$OutputLastMessage = ""
)

$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $Workspace

if ($Kind -eq "cline") {
    $cline = (Get-Command cline.cmd -ErrorAction Stop).Source
    $prompt = Get-Content -LiteralPath $PromptPath -Raw
    & $cline `
        --provider $Provider `
        --model $Model `
        --cwd $Workspace `
        --data-dir $DataDir `
        --auto-approve true `
        --compaction agentic `
        --timeout 86400 `
        $prompt
    exit $LASTEXITCODE
}

if ($Kind -eq "codex") {
    $codex = (Get-Command codex.cmd -ErrorAction Stop).Source
    Get-Content -LiteralPath $PromptPath -Raw | & $codex `
        exec `
        --cd $Workspace `
        --sandbox workspace-write `
        --model $Model `
        --output-last-message $OutputLastMessage `
        -
    exit $LASTEXITCODE
}

