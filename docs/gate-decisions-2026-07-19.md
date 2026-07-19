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

## Still external or human-controlled

Production publication remains blocked pending privacy, licensing, removal,
threat-model, data-governance, and owner review. Statutory-source review remains
required before the indicative OIA trace can be promoted or described as legal
conformance. The production-shaped runner was exercised on one real public
request on 2026-07-19: four attachment digests verified in both phases, the
backfill accepted, the update accepted at revision 2 and source sequence 2, and
no quarantine rows. Larger-scale backfill remains an operational run.
