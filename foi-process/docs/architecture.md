# Architecture

## One event spine, two acquisition modes

```text
Archived
fyi-archive manifest/WARC ─┐
                          ├─> EvidenceDelta ─> ReplayEngine ─> NormalizedBundle
Live                      │                            │
fyi-cli watch/sync ───────┘                            ├─> Rust4PM OCEL/mining
                                                       ├─> FOI-O/Axiom conformance
Document attachments ─> fe-reader DocumentBundle      ├─> Propel artefacts
                         └─> nlp-policy-nz signals ────┘
```

The same deterministic normaliser handles archived and live records. A full replay from immutable evidence must reproduce the same logical events, subject to explicit normaliser/profile versions.

## Canonical analytical tables

- `evidence_records`
- `process_events`
- `objects`
- `event_object_links`
- `object_object_links`
- `object_changes`
- `document_bundles` / page and segment tables
- `document_signals`
- `conformance_findings` / traces
- `stream_checkpoints`
- `mining_run_manifests`

Parquet is the publication/analytics representation; OCEL 2 is the object-centric mining representation; NDJSON is the simple live/interchange representation. XES is compatibility output, not canonical storage.

## Source-of-truth rule

- Raw facts: immutable capture/archive.
- Transport and replay semantics: `foi-process` during incubation, then shared with `fyi-core` where capture-owned.
- FOI vocabulary and certification boundaries: FOI-O.
- Generic mining: Rust4PM.
- Statutory results: Axiom/RuleSpec profiles.
- UI: Propel.
