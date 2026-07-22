# Status — 2026-07-22

## Implemented in workpack

- Core contracts and RFC 8785 deterministic content IDs
- Archive-to-delta adapter
- Deterministic normaliser
- Revision- and partition-order-aware replay/checkpoint engine with snapshot integrity verification, complete append-only resume journals, quarantine, and commit-last checkpoints
- Revisable live dashboard summary
- OCEL table projection, Rust4PM AppendableOCEL adapter, and feature-gated recording-sink integration test
- Privacy-safe public projection
- OCR/document and NLP signal contracts
- Portable schemas, fixtures, development oracle, human-review fixture, semantic and property tests
- Repo promotion and issue packets
- Reviewed Hugging Face event-log Dataset bundle and checksum-verified free GitHub Pages dashboard
- Repeated 1k/10k/200k Rust benchmark, tested Parquet partition contract, and checksummed SPDX/mining release evidence

## Acceptance state

The repository implementation and the production-shaped integration path are
accepted against the evidence recorded in `foi-process` issue #9 and the
linked governance artefacts. The remaining unchecked items are intentionally
outside the non-publication implementation gate:

- Axiom/RuleSpec vocabulary promotion requires the owning external repositories.
- Production publication and authenticated Hub/Dataset Viewer verification remain
  explicitly deferred.
- The fyi-archive controller has completed its configured NZ ID horizon through
  250,000: 3,074 batches merged and 33,244 captured records in persisted
  controller state. This is operational evidence, not permission to publish
  production-derived projections.

## Mandatory pre-merge gates

- `cargo fmt`, `clippy`, `test`, `doc`, Rust4PM feature compilation, and `Cargo.lock` generation on Rust 1.88+
- Real `fyi-archive` sample adapter (completed; see issue #9 and T03 evidence)
- Generated-schema reconciliation
- privacy review and representative live-archive benchmark
- authenticated Hub publication and public Dataset Viewer/Space verification
  (publication-only, deferred)
- hosted release-evidence publication and artifact attestation (completed for
  the accepted synthetic/representative path; full-corpus public attestation
  remains deferred)
