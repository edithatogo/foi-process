# Implementation status

**Reviewed:** 2026-07-13  
**Release state:** locally compiled/tested integration candidate; not yet a GitHub release

## Implemented

- Single Rust package with library and CLI modules, rather than seven independently maintained crates.
- Typed and validated IDs, RFC 8785 canonical content IDs, SHA-256 digests, RFC 3339 timestamps, confidence, vocabulary terms, privacy, evidence, objects, events, document signals, conformance, review, and run manifests.
- Deterministic archive/live normalisation with revisions, correction, retraction, causation, stream positions, checkpoints, replay snapshots, conflicts, gaps, regressions, and quarantine outputs.
- Restartable stream replay with integrity-checked state, append-only resume journals, complete table outputs, output flush/sync, state-before-checkpoint commit ordering, and atomic JSON replacement.
- Revision-aware dashboard summaries and OCEL projections that materialise only the latest active logical event, even when revisions arrive out of order.
- Direct optional Rust4PM `AppendableOCEL` adapter; no competing general-purpose mining engine.
- Feature-gated bounded Arrow/Parquet export with Zstandard compression, atomic replacement,
  table hashes, row-group counts, and dataset reports.
- Selective OCR/document contracts, evidence geometry, model/runtime/license provenance, NLP signals, and explicit human review records.
- Privacy-safe public projection with publish, metadata-only, withhold, and review dispositions.
- Rust-derived schema generator plus independently validated portable draft schemas.
- Conductor tracks, GitHub issue/sub-issue material, repo-specific promotion packets, funding work packages, CI, dependency policy, and dry-run export scripts.

## Validation completed in this work environment

- All generated JSON and NDJSON fixtures validate against the portable JSON Schemas.
- The Python development oracle passes deterministic replay, revision, position-gap/regression, correction, privacy, dashboard, and OCEL semantic checks.
- Every Rust source file parses without syntax errors using tree-sitter, including the feature-gated Rust4PM adapter test.
- Python syntax, YAML parsing, JSON parsing, and shell syntax checks pass.
- A small Python reference benchmark was run only to exercise fixture-scale algorithm shape. It is **not** a Rust performance claim.
- Rust 1.97 GNU toolchain: default check/test, Rust4PM check/test, Parquet check, formatting,
  clippy, documentation, CLI vertical slice, and scale benchmarks passed. The pinned 1.88 MSVC
  toolchain could not complete Rustup recovery on this workstation; MSVC linking also lacks the
  required linker environment.

## Mandatory first export gates

1. Install Rust 1.88+ and run `scripts/ci-local.sh`.
2. Re-run the feature-gated matrix on the pinned CI toolchain, including Parquet tests and all
   feature combinations.
3. Re-run `cargo deny check` in CI and resolve or explicitly retain the five unmatched
   allow-list warnings reported by cargo-deny 0.20.2.
4. Compare Rust-generated schemas with the portable compatibility schemas and record intentional differences.
5. Run RFC 8785 parity vectors in Rust and at least one independent implementation.
6. Map and validate a real, representative `fyi-archive-nz` sample, including WARC/WACZ and attachment records.
7. Add bounded Parquet/Arrow writers and measure 1k, 10k, 200k-request, and revision-heavy workloads.
8. Complete privacy, tikanga/data-governance, and threat-model review before publishing OCR text, embeddings, or semantic search.

## Deliberately not claimed as complete

- Production `fyi-cli` emitter or `fyi-archive` adapter.
- Durable transactional database state beyond atomic file snapshots and deterministic replay.
- Full all-feature validation, including optional SQLite/DuckDB/dataframe integrations.
- Full process discovery or conformance algorithms outside Rust4PM.
- OCR engine selection or trained FOI signal models.
- Certified statutory/legal conclusions.
- Deployed Propel/Hugging Face dashboard.
- Live GitHub issues, branches, pull requests, or releases.
