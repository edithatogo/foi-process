# FOI Process Workpack v3

**Review date:** 2026-07-15  
**Status:** `v0.1.0` released Rust-first integration workpack; hosted CI passes, with external governance and live-adapter gates remaining.

This workpack is the reviewed successor to v2. It keeps the strategic direction—Rust-first, OCEL-first, event-sourced, FOI-O bounded—but corrects several implementation assumptions and reduces the new maintenance surface.

## What is implemented here

- One Rust library/binary rather than seven publishable microcrates.
- Validated identifiers, RFC 8785 canonical content IDs, SHA-256 digests, RFC 3339 timestamps, and bounded confidence values.
- Normalised, reference-based evidence/object/event contracts suitable for Parquet and OCEL.
- `EvidenceDelta` revisions, stream positions, supersession, retraction, integrity-checked snapshots, checkpoints, gap/conflict detection, and deterministic replay.
- A shared normaliser for archive records and future live `fyi-cli` deltas.
- Revision-aware live dashboard roll-ups that remain correct under out-of-order revisions and do not double-count corrected events.
- A portable OCEL projection and a direct optional adapter to Rust4PM 0.6's existing `AppendableOCEL` trait.
- Document/OCR contracts that separate `fe-reader` extraction from `nlp-policy-nz` semantic signals.
- Privacy classification and a public projection that prevents unreviewed OCR/text from being amplified.
- Resume-safe append-only NDJSON journals, complete normalized table outputs, quarantine records, and commit-last checkpoint semantics.
- Mining-run provenance, replay fixtures, schema snapshots, Python development oracle, and semantic tests.
- Conductor tracks, GitHub parent/sub-issue payloads, per-repo export packets, and funding work packages.

## Repository boundaries

```text
fyi-cli                 capture, polling, WARC/WACZ, EvidenceDelta emission
fyi-archive             immutable snapshots, manifests, publication/mirrors
foi-process             deterministic integration, replay, projection, live roll-ups
foi-o                   canonical FOI semantics, vocabulary, schema/SHACL profiles
Rust4PM                 generic OCEL/process-mining algorithms
fe-reader               document/PDF extraction, rendering, OCR orchestration, evidence geometry
nlp-policy-nz           semantic/NLP signals grounded in DocumentBundle evidence
Axiom + RuleSpec NZ     deterministic statutory/deadline results and traces
Propel                  Rust/WASM process-mining user interface
Kairos                  simulation, synthetic logs, counterfactual process models
Sourceright             source verification and review-queue patterns
rulesandprocesses       background contract/adoption research; never a runtime dependency
```

## First commands after export

```bash
cargo fmt --all -- --check
cargo clippy --locked --all-targets -- -D warnings
cargo test --locked --all-targets
cargo check --locked --all-targets --features rust4pm
cargo test --locked --all-targets --features rust4pm
cargo check --locked --all-targets --features parquet
cargo run --locked --bin schema-gen -- schemas/generated
python scripts/reference_pipeline.py
python scripts/validate_workpack.py
python scripts/test_reference_semantics.py
```

The default, Rust4PM, and Parquet paths have been compiled locally with the installed GNU Rust
toolchain. The pinned 1.88 MSVC toolchain and the optional all-feature matrix remain CI follow-up
gates on this workstation.

## Key folders

```text
src/                     Rust implementation
schemas/portable/        independently validated portable schema drafts
examples/input/          archive/live delta and event fixtures
examples/generated/      replay, OCEL, dashboard, privacy, OCR, manifest outputs
scripts/                  development oracle and validation
conductor/               source-of-truth project tracks for the new repo
github/                  parent/sub-issue and Project planning material
repo-exports/             changes to promote into existing repositories
docs/                    review, architecture, privacy, OCR, scaling, promotion
```

See `IMPLEMENTATION_STATUS.md`, `CHANGELOG.md`, `docs/REVIEW_AND_DECISIONS.md`, and `docs/canonical-identifiers.md` for the audit, completed implementation, and remaining gates.
