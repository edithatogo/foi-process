# Status - 2026-08-14

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

### Cross-repository reconciliation — 2026-07-22

- fyi-archive historical-source run
  [29908248734](https://github.com/edithatogo/fyi-archive/actions/runs/29908248734)
  produced 4,997 distinct Internet Archive candidates. All were classified as
  `archive_only_candidate` against the 33,217-record public HF manifest; none
  was treated as a live capture.
- fyi-archive controller run
  [29908342309](https://github.com/edithatogo/fyi-archive/actions/runs/29908342309)
  found no pending batches because the persisted NZ horizon is complete through
  request ID 250,000. Its retained state reports 3,074 merged batches and
  33,244 captured records.
- These figures are operational provenance only. They do not update the public
  HF dataset or authorize publication of production-derived events, attachments,
  OCR, embeddings, or unrestricted NLP outputs.

- `cargo fmt`, `clippy`, `test`, `doc`, Rust4PM feature compilation, and `Cargo.lock` generation on Rust 1.88+
- Production publication remains blocked by explicit gate; non-publication technical review is complete
- Scale beyond the four-request live continuation evidence only if operational monitoring requires it
- Hosted release-evidence attestation for any real-data publication remains intentionally out of scope
- Bounded registry publication is complete at DOI `10.5281/zenodo.21660296`;
  full-corpus registry expansion remains separately deferred in issue #63.
