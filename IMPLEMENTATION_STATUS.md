# Implementation status

**Reviewed:** 2026-07-19
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
- Static dashboard source with shared filtering, activity KPIs, directly-follows map, variant
  Sankey, request timeline, conformance findings, OCEL/data-quality indicators, and manifest
  provenance. Its build regenerates and checksum-verifies dashboard data from the Dataset bundle;
  the free Hugging Face Static Space and GitHub Pages are both operational hosts.
- Enforced Static Space asset budget and ADR 0005, bounding the compiled JavaScript, CSS, and
  checked demonstration projection while recording the no-runtime deployment decision.
- Isolated three-repetition Rust scale suite covering 1k, 10k, and 200k synthetic cases, including
  corrections, retractions, deterministic output hashes, throughput, output size, and peak memory.
- ADR 0006 plus a tested, path-safe site/jurisdiction/event-year Parquet partition helper.
- Reproducible release-evidence builder and verifier covering Cargo.lock, SPDX 2.3 SBOM, Dataset
  manifest, scale report, mining-run provenance, release manifest, and sorted SHA-256 checksums.

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
- GitHub Actions runs [29495826776](https://github.com/edithatogo/foi-process/actions/runs/29495826776)
  and [29495828086](https://github.com/edithatogo/foi-process/actions/runs/29495828086) passed for
  commit `b0c7c9e`, including the full feature matrix, Dataset/Space bundle checks, dashboard
  asset budget, and GitHub Pages deployment. The live Pages endpoint responded successfully;
  authenticated Hugging Face upload remains credential-gated.

## Remaining gates

### Evidence added 2026-07-15

- A bounded read-only capture of public FYI request `28164` produced JSON, HTML,
  WARC, WACZ, and a derived request store. Structural validation and redacted
  hashes are recorded in `docs/evidence/real-fyi-archive-capture-2026-07-15.json`.
- `scripts/validate_fyi_archive_capture.py` can revalidate an externally held
  capture without importing its content into this repository.
- A second bounded capture of request `26953` now includes four PDF attachments
  discovered from rendered HTML, with content-addressed hashes in the derived
  store, WARC, and WACZ.
- The same request passed through `fyi-cli capture`, `fyi-archive seed run`,
  `fyi-archive manifest build`, and the Rust `foi-process` manifest adapter.
  Hashes and the four passing adapter checks are recorded in
  `docs/evidence/live-fyi-cli-fyi-archive-foi-process-2026-07-15.json`; the
  earlier omitted-attachment observation remains in the historical evidence
  file for auditability.
- `governance/publication_gate.json` keeps production publication blocked and
  limits current hosted outputs to synthetic data.
- Manual workflows provide executable paths for Zenodo preservation and native
  DuckDB runtime evidence. These remain optional publication/deployment checks.
- The Rust adapter now accepts nullable live manifest timestamps and derives
  omitted FYI request/API URLs correctly; focused tests and one live conversion
  pass. The DuckDB workflow now runs an actual `SELECT 42` connection test and
  uses the matching `libduckdb-sys` download mechanism.
- Hugging Face and GitHub Pages workflows now execute the same fail-closed
  governance gate before building or publishing hosted outputs. The Zenodo
  workflow now publishes the deposition and fails unless the response contains
  a DOI.

1. Keep production publication blocked; the non-publication privacy, rights, removal, threat-model, governance, and statutory review records are complete.
2. Scaled real `fyi-cli`/`fyi-archive` backfill and live continuation are verified for four requests and fourteen attachments; see `docs/evidence/production-continuation-2026-07-19.json`.
3. Maintain the indicative OIA mapping without promoting it to legal conformance; see `governance/statutory-source-review-2026-07-19.md`.
4. Hosted release-evidence attestation for real-data publication is intentionally not run.
5. Publication-only: maintain the public Hugging Face Dataset deposit and verify its Dataset Viewer configuration.
6. Publication-only: preserve the GitHub release in Zenodo and record DOI evidence without overstating publication state.

## Deliberately not claimed as complete

- Durable transactional database state beyond atomic file snapshots and deterministic replay; the
  v0.1 decision and future multi-writer gate are recorded in `docs/gate-decisions-2026-07-19.md`.
- DuckDB runtime validation; all-features compilation is covered by CI, while hosted execution lacks `libduckdb`.
- Full process discovery or conformance algorithms outside Rust4PM.
- OCR engine selection or trained FOI signal models; full OCR/NLP fixtures are deferred until
  production OCR, embeddings, semantic search, or extracted signals are in scope.
- Certified statutory/legal conclusions.
- Paid or credit-gated Hugging Face runtime; the dashboard uses the duplicated free Static Space
  path and GitHub Pages instead.
- Full-corpus archive backfill beyond the four-request operational evidence; this is optional scale work, not a publication authorization.
