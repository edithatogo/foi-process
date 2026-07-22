# Verification evidence: 2026-07-22

## Cross-repository archive evidence

- fyi-archive historical-source run
  [29908248734](https://github.com/edithatogo/fyi-archive/actions/runs/29908248734)
  produced 4,997 distinct Internet Archive candidates. Reconciliation classified
  all 4,997 as `archive_only_candidate` against the 33,217-record public HF
  manifest; no Internet Archive candidate was treated as a live capture.
- fyi-archive backfill-controller run
  [29908342309](https://github.com/edithatogo/fyi-archive/actions/runs/29908342309)
  found no pending batches because the persisted NZ horizon is complete through
  request ID 250,000. The retained controller state reports 3,074 merged batches
  and 33,244 captured records.
- These figures are operational provenance only. They do not update the public
  HF dataset and do not authorize publication of production-derived events,
  attachments, OCR, embeddings, or unrestricted NLP outputs.
