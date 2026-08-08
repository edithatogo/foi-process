# Plan

- [x] Test fixtures and property cases
- [x] Persist checkpoint/dead-letter state
- [x] Map real FYI archive sample
- [x] Update promotion/adoption ledger
- [x] Close with benchmark, fixtures, and decision record

- [x] Quarantine partition position gaps, regressions, and conflicting reuse.
- [x] Prevent quarantined records from advancing checkpoints.
- [x] Flush/sync deterministic outputs before atomically replacing replay state.
- [x] Add restart snapshots and duplicate-delivery property tests.
- [x] Decide whether a transactional persistent state backend is needed; defer it until multi-writer deployment.
