# Implementation status

**Reviewed:** 2026-07-15  
**Release state:** `v0.1.0` is published on GitHub; Zenodo preservation remains a human-controlled gate

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
- `CITATION.cff` and `.zenodo.json` release metadata for the citable `v0.1.0` workpack.
- Deterministic Hugging Face Dataset publication bundle and fail-closed upload workflow, covering
  event logs, revision history, EvidenceDelta streams, process edges and variants, OCEL tables,
  conformance findings, schemas, dashboard artefacts, and checksums. The reviewed fixture bundle
  is locally verified; live upload awaits Hugging Face authentication.
- Static Hugging Face Space dashboard with shared filtering, activity KPIs, directly-follows map,
  variant Sankey, request timeline, conformance findings, OCEL/data-quality indicators, and
  manifest provenance. Its build regenerates and checksum-verifies dashboard data from the Dataset
  bundle; live Space upload awaits Hugging Face authentication.

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
- GitHub Actions run [29339015413](https://github.com/edithatogo/foi-process/actions/runs/29339015413):
  contracts, dependency policy, Rust 1.88, stable Rust, and feature-matrix jobs all passed.
  The matrix compiles all features and executes all self-contained feature tests; DuckDB runtime
  linking remains excluded because the hosted runner does not provide `libduckdb`.

## Remaining gates

1. Compare Rust-generated schemas with the portable compatibility schemas and record intentional differences.
2. Run RFC 8785 parity vectors in Rust and at least one independent implementation.
3. Map and validate a real, representative `fyi-archive-nz` sample, including WARC/WACZ and attachment records.
4. Complete privacy, tikanga/data-governance, and threat-model review before publishing OCR text, embeddings, or semantic search.
5. Complete production `fyi-cli`/`fyi-archive` adapter integration and validate live evidence flows.
6. Authenticate Hugging Face publication, deploy the Dataset and Static Space, and verify Dataset
   Viewer configurations plus the public Space URL.
7. Preserve the GitHub release in Zenodo and record DOI evidence without overstating publication state.

## Deliberately not claimed as complete

- Production `fyi-cli` emitter or `fyi-archive` adapter.
- Durable transactional database state beyond atomic file snapshots and deterministic replay.
- DuckDB runtime validation; all-features compilation is covered by CI, while hosted execution lacks `libduckdb`.
- Full process discovery or conformance algorithms outside Rust4PM.
- OCR engine selection or trained FOI signal models.
- Certified statutory/legal conclusions.
- Publicly deployed Propel/Hugging Face dashboard; the complete Static Space is repository-built
  and CI-gated but not yet uploaded.
- Live GitHub issues, branches, pull requests, or releases.
