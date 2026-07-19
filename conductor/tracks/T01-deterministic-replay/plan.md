# Plan

- [ ] Test fixtures and property cases
- [ ] Persist checkpoint/dead-letter state
- [ ] Map real FYI archive sample
- [ ] Update promotion/adoption ledger
- [ ] Close with benchmark, fixtures, and decision record

- [x] Quarantine partition position gaps, regressions, and conflicting reuse.
- [x] Prevent quarantined records from advancing checkpoints.
- [x] Flush/sync deterministic outputs before atomically replacing replay state.
- [x] Add restart snapshots and duplicate-delivery property tests.
- [x] Decide that a transactional backend is not required for v0.1; gate it on multi-writer production ingestion.
