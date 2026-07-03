param([string]$Workspace = (Resolve-Path ".").Path)
$ErrorActionPreference = "Stop"
$mailboxRoot = Join-Path -Path $Workspace -ChildPath ".swarm\mailboxes"

function Send-Task($recipient, $content) {
    $id = -join ((65..90)+(97..122) | Get-Random -Count 8 | ForEach-Object { [char]$_ })
    $ts = [double]((Get-Date -UFormat %s) -replace ',', '.')
    $inbox = Join-Path -Path (Join-Path -Path $mailboxRoot -ChildPath $recipient) -ChildPath "inbox"
    New-Item -ItemType Directory -Force -Path $inbox | Out-Null
    $filepath = Join-Path -Path $inbox -ChildPath ("$([long]($ts*1000))-$id.json")
    $msg = [ordered]@{ msg_id=$id; sender="orchestrator"; recipient=$recipient; msg_type="task"; content=$content; timestamp=$ts; metadata=@{} }
    $msg | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $filepath -Encoding UTF8
    Write-Host "  [sent] $recipient" -ForegroundColor Green
}

Write-Host "=== Dispatch Wave 1: Fix Blockers + Foundation ===" -ForegroundColor Cyan

# ---- Task 1: Fix corpus-nz-hansard CI ----
$t1 = @"
## HIGH PRIORITY: Fix corpus-nz-hansard CI (shared_utils import)

Track: 11 (HF Namespace) - Blocker Resolution
Subrepo: corpus-nz-hansard

### Problem
CI workflow fails with shared_utils import error after root shared_utils.py was removed.

### Tasks
1. Locate CI workflow in corpus-nz-hansard/.github/workflows/
2. Find the shared_utils import reference
3. Update to use scripts/sha256_utils.py or inline
4. Run local validation

### Constraints
- No commit/push/upload/external access
- Keep changes inside corpus-nz-hansard/

### Expected Outcome
Import error resolved. Local tests pass.
"@
Send-Task "general_coder" $t1

# ---- Task 2: Fix hathi-nz Pixi cache-key ----
$t2 = @"
## HIGH PRIORITY: Fix hathi-nz Pixi cache-key

Track: 11 (HF Namespace) - Blocker Resolution
Subrepo: hathi-nz

### Problem
GitHub Actions Pixi cache-key setup is broken, blocking HF sync.

### Tasks
1. Locate hathi-nz/.github/workflows/
2. Find the Pixi cache-key configuration
3. Fix the cache-key to use a valid deterministic pattern
4. Validate workflow YAML syntax

### Constraints
- No commit/push/upload/external access
- Keep changes inside hathi-nz/

### Expected Outcome
Pixi cache-key fixed. Workflow YAML is valid.
"@
Send-Task "general_coder" $t2

# ---- Task 3: Fix medilegal workflow_dispatch ----
$t3 = @"
## HIGH PRIORITY: Fix corpus-cases-medilegal-nz workflow_dispatch

Track: 11 (HF Namespace) - Blocker Resolution
Subrepo: corpus-cases-medilegal-nz

### Problem
workflow_dispatch trigger not recognized despite YAML containing it.

### Tasks
1. Inspect corpus-cases-medilegal-nz/.github/workflows/
2. Fix workflow_dispatch YAML syntax/indentation
3. Validate YAML

### Constraints
- No commit/push/upload/external access
- Keep changes inside corpus-cases-medilegal-nz/

### Expected Outcome
workflow_dispatch trigger properly recognized.
"@
Send-Task "general_coder" $t3

# ---- Task 4: Isaacus inventory doc ----
$t4 = @"
## Create Isaacus Inventory Document

Track: 12 (Isaacus Legal AI Alignment)
Subrepo: nlp-policy-nz

### Task
Create nlp-policy-nz/docs/isaacus-inventory.md with:
1. Upstream Isaacus schemas
2. Benchmark task formats
3. Document metadata conventions
4. Chunking/embedding defaults
5. Haystack component boundaries
6. NZ-specific adaptations needed

### Reference
- huggingface.co/isaacus, github.com/isaacus-dev
- task_plan.md lines 118-151

### Constraints
- No commit/push/upload/external access
- Documentation-only; keep inside nlp-policy-nz/

### Expected Outcome
Markdown inventory for Architect_Oracle review.
"@
Send-Task "xiaomi_mimo_code" $t4

# ---- Task 5: DigitalNZ probe script ----
$t5 = @"
## Implement DigitalNZ Probe Script

Track: 21 (DigitalNZ Discovery Layer)
Subrepo: nlp-policy-nz

### Task
Add read-only DigitalNZ probe script that:
1. Accepts query text, field filters, pagination, output path
2. Queries public DigitalNZ API (no key needed for basic)
3. Writes JSONL results
4. Configurable timeouts and error handling

### API
Base URL: https://api.digitalnz.org/v3/records.json

### Reference
- task_plan.md lines 387-455 (Task 21.5)

### Constraints
- No commit/push/upload/external access except DigitalNZ API
- Keep inside nlp-policy-nz/
- Include --dry-run mode with fixture data

### Expected Outcome
Working probe script with fixture-based tests.
"@
Send-Task "general_coder" $t5

# ---- Task 6: Architect review root ownership ----
$t6 = @"
## Review Root Ownership Migration

Track: 22 (Root Ownership Audit)
Repo: root legal-nz

### Task
Review current migration state:
1. Verify shared_utils.py fully removed
2. Check scripts/sha256_utils.py is self-contained
3. Verify corpus-law-nz/utils.py no longer imports root
4. Identify remaining misplaced root code
5. Record findings in findings.md

### Reference
- task_plan.md lines 457-471
- conductor/tracks/root_ownership_migration_20260614/

### Constraints
- No commit/push/upload/external access
- Read-only review

### Expected Outcome
Clear assessment of remaining migration work.
"@
Send-Task "architect_oracle" $t6

# ---- Standby for Quality_Validator ----
$t7 = @"
## Standby for Validation

Track: All - Validation Queue

Pending implementations to validate:
1. corpus-nz-hansard CI fix (Track 11) - general_coder
2. hathi-nz Pixi cache fix (Track 11) - general_coder
3. corpus-cases-medilegal-nz workflow_dispatch (Track 11) - general_coder
4. nlp-policy-nz Isaacus inventory (Track 12) - xiaomi_mimo_code
5. nlp-policy-nz DigitalNZ probe (Track 21) - general_coder
6. Root ownership review (Track 22) - architect_oracle

Stand by for task-specific validation commands.
"@
Send-Task "quality_validator" $t7

Write-Host "`n=== Wave 1 dispatched ===" -ForegroundColor Cyan
