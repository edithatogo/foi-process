# Gate decisions: 2026-07-19

## Current bounded evidence

- A real public FYI request (`26953`) has been captured through `fyi-cli` and
  `fyi-archive`, producing WARC/WACZ artefacts and four attachment records.
- `scripts/validate_fyi_archive_capture.py` now verifies attachment byte length,
  SHA-256, safe paths, and WARC record linkage in addition to WARC/WACZ structure.
- The Rust adapter converts the manifest to one deterministic EvidenceDelta without
  writing raw bytes. The bounded run is recorded in
  `docs/evidence/live-archive-benchmark-2026-07-19.json`.

## RFC 8785 and schema parity

The CI contract suite now runs three independent Python `rfc8785` vectors against
the Rust `content-id` command. Rust-generated schemas are compared with portable
schemas on every supported toolchain. The only accepted required-field differences
are `schema_version` and `privacy`, which Rust supplies through defaults while the
portable compatibility schemas require explicit wire-level values.

## Transactional state decision

No transactional database backend is required for the v0.1 single-process,
file-backed vertical slice. Atomic replacement, fsync, append-only journals,
integrity-checked snapshots, and commit-last checkpoints provide the required
failure semantics for this release. A transactional backend becomes a release gate
before multi-writer production ingestion, shared workers, or cross-process leasing.

## OCR/NLP fixture decision

Full OCR/NLP fixtures are not required for the current process-mining dashboard,
which publishes synthetic process events and metadata-only projections. Born-digital
and scanned-PDF fixtures become required before production OCR text, embeddings,
semantic search, or extracted FOI signals are published. Until then, the existing
document/signal contracts and fail-closed privacy gate remain the boundary.

## Still external or publication-controlled

Production publication remains blocked by decision. The non-publication technical
review and indicative statutory-source mapping are complete in
`governance/non-publication-review-2026-07-19.json` and
`governance/statutory-source-review-2026-07-19.md`. The scaled runner was
exercised on four real public requests on 2026-07-19: fourteen attachment
digests verified, four continuation deltas accepted at revision 2 and source
sequences 2-5, and no quarantine rows. Source rights, personal-data exposure,
and legal conformance remain deliberately outside any publication permission.
