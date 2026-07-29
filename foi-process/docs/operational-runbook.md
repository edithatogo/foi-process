# Operational runbook

## Real backfill

Use the complete, checksum-verified source-index run ID and dispatch bounded
`nz_real_backfill_batch.yml` runs. Start with a small batch. Each successful
batch must retain its ledger, live manifest, event log, attachment sidecar,
projection, and verification evidence before continuation.

Do not use the Internet Archive CDX discovery queue as a substitute for live
captured request records. A source outage is a normal fail-closed state.

## Retry and requeue

1. Inspect the failed run's `source-health.json` and `ledger.jsonl`.
2. Requeue only failed or uncaptured requests; do not silently discard them.
3. Confirm the source endpoint responds from the hosted runner.
4. Retry a bounded batch with `auto_continue=false` until parity passes.
5. Enable continuation only after exact manifest/case/event/attachment parity.

The recurring monitor cancels stale inventory runs, checks source health, and
refuses to dispatch while another backfill is active.

## Source outage and recovery

During a 4xx/5xx response or timeout, retain the failure artifact and leave
production continuation disabled. Do not publish a partial projection. When
the source recovers, rerun the smallest failed batch, verify parity, then
resume the queue from its recorded offset.

## Deposit preparation

Prepare a local package without publishing:

```powershell
python scripts/prepare_event_log_deposit.py `
  --bundle path/to/verified-bundle `
  --output path/to/new-deposit-package
```

The command verifies the source manifest, copies declared files, writes
`deposit-manifest.json`, Zenodo and DataCite metadata drafts, and
`SHA256SUMS`. It refuses to overwrite an existing package and performs no
network write.

External upload/publication remains a separate, explicitly approved action.
