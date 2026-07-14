# Status — 2026-07-09

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

## Mandatory pre-merge gates

- `cargo fmt`, `clippy`, `test`, `doc`, Rust4PM feature compilation, and `Cargo.lock` generation on Rust 1.88+
- Real `fyi-archive` sample adapter
- Generated-schema reconciliation
- privacy review and benchmark baseline
