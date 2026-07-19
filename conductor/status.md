# Status — 2026-07-19

## Implemented in workpack

- Core contracts and RFC 8785 deterministic content IDs, with independent parity vectors in CI
- Archive-to-delta adapter
- Deterministic normaliser
- Revision- and partition-order-aware replay/checkpoint engine with snapshot integrity verification, complete append-only resume journals, quarantine, and commit-last checkpoints
- Revisable live dashboard summary
- OCEL table projection, Rust4PM AppendableOCEL adapter, and feature-gated recording-sink integration test
- Privacy-safe public projection
- OCR/document and NLP signal contracts
- Portable schemas, fixtures, development oracle, human-review fixture, semantic and property tests
- Repo promotion and issue packets
- Reviewed Hugging Face event-log Dataset bundle and checksum-verified Static Space dashboard
- Bounded real fyi-cli/fyi-archive WARC/WACZ capture with four attachment byte/digest/linkage checks
- Repeated 1k/10k/200k Rust benchmark, tested Parquet partition contract, and checksummed SPDX/mining release evidence

## Remaining promotion gates

- `cargo fmt`, `clippy`, `test`, `doc`, Rust4PM feature compilation, and `Cargo.lock` generation on Rust 1.88+
- Production publication remains blocked by explicit gate; non-publication technical review is complete
- Scale beyond the four-request live continuation evidence only if operational monitoring requires it
- Hosted release-evidence attestation for any real-data publication remains intentionally out of scope
- Authenticated Dataset Viewer verification and Zenodo preservation where still outstanding
