# Changelog

## Unreleased

### Hugging Face publication

- Added a deterministic, public-safe Dataset bundle containing active event logs, revision logs,
  EvidenceDelta streams, process edges and variants, OCEL tables, conformance findings, schemas,
  dashboard artefacts, and SHA-256 manifests.
- Added a fail-closed GitHub workflow that validates the dataset on every run and uploads only
  when explicitly dispatched with an `HF_TOKEN` secret.
- Marked the initial deposit as synthetic reviewed fixture data; real FOI data remains gated by
  privacy, tikanga/data-governance, licensing, removal/appeal, and threat-model review.
- Added a Static Hugging Face Space with process-map, variant, request-timeline, conformance, data
  quality, and provenance views backed by a checksum-verified browser projection.
- Added a fail-closed Space workflow that builds and archives the application on every dispatch but
  publishes only with an explicit input and Hugging Face token.
- Upgraded the chart runtime to ECharts 6.1.0 to include the upstream XSS fix.

## v3 — 2026-07-09

### Architecture

- Collapsed seven proposed crates into one modular Rust package plus binaries.
- Made archive and live ingestion converge on one delta/replay path.
- Replaced proposed custom mining code with a direct Rust4PM adapter.
- Corrected the Rust4PM roadmap because appendable OCEL already exists upstream.

### Contracts and integrity

- Added typed identifiers, terms, digests, timestamps, confidence, privacy, revisions, stream positions, provenance, object links/changes, document bundles, review records, and run manifests.
- Replaced ad-hoc canonical JSON with RFC 8785 JCS for generated identifiers.
- Separated evidence records from references to avoid row duplication at corpus scale.
- Added schema generation and portable compatibility schemas.
- Added a feature-gated `AppendableOCEL` recording-sink integration test that asserts corrected events are appended once.

### Replay and live processing

- Added duplicate, stale, conflict, revision-gap, position-gap, position-regression, correction, and retraction semantics.
- Added restartable replay snapshots, checkpoints, quarantine output, and revision-aware aggregation.
- Verify replay snapshot state hashes before restoration and reject duplicate snapshot records/partitions.
- Added stdin NDJSON support, complete normalized table journals, append-only resume semantics, and refusal to truncate an existing fresh-run journal.
- Added output sync, parent-directory sync on Unix, state-before-checkpoint commit ordering, and out-of-order revision protection in live summaries.

### Safety and publication

- Added explicit privacy/access/publication disposition and safe public projections.
- Added human review records and a candidate-to-certified fixture.
- Kept statutory and legal certification outside autonomous process mining.

### Repository operations

- Added Conductor tracks/quality gates, repo-layout-aware export packets, parent/sub-issue plans, funding work packages, CI, dependency policy, and reproducibility checks.
