# Status — 2026-08-01

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
linked governance artefacts. Issue #36 is closed: its repository-owned
full-manifest and replay acceptance is complete. The remaining items are live
external evidence gates, not unimplemented repository work:

- Axiom/RuleSpec vocabulary promotion requires the owning external repositories.
- A revision-pinned external verification of the published Hugging Face Dataset
  Viewer and deployed dashboard remains open in issue #9.
- Any new production-derived public release requires release-specific external
  host, rights, privacy, removal/takedown, and governance evidence; code
  completion and the Apache-2.0 code licence do not supply that authority.
- Bounded event-log registry publication is complete: Zenodo record
  `21660296`, DOI `10.5281/zenodo.21660296`, with DataCite metadata included.
  Full-corpus registry expansion remains deferred in issues #63-#65.
- Optional recurring full-corpus operations remain a `fyi-archive`/`fyi-cli`
  operational decision, not an acceptance or publication prerequisite.

## Validation baseline

- `cargo fmt`, `clippy`, `test`, `doc`, Rust4PM feature compilation, and
  `Cargo.lock` generation on Rust 1.88+
- Real `fyi-archive` sample adapter, generated-schema reconciliation, privacy
  review, and representative live-archive benchmark are completed acceptance
  evidence.
- Hosted release-evidence publication and artifact attestation are completed for
  the accepted synthetic/representative path.
- The bounded Hugging Face Dataset and free Space are published with pinned
  revisions and 75 cases, 425 events, and 179 attachments. Full-corpus HF
  coverage and any new production-derived release remain external gates in
  issue #9.
