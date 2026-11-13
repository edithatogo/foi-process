# Rust dependency rationalisation — foi-process (2026-11-13)

**Status:** scoped Conductor adoption contract; code substitutions not yet implemented or certified by this file.

## Repository-specific decisions

- Reconcile existing OCEL, replay, interoperability and quality tracks; no new parser ownership.
- **Verified:** uses Anyhow, Clap, Serde, Thiserror, Criterion, Proptest, optional Rust4PM `process_mining`, Arrow/Parquet and DuckDB.
- **Retain:** Rust4PM interoperability, optional feature boundaries and canonical event provenance; do not duplicate Mailweft EML parsing.
- **Extend:** Proptest for duplicate/idempotent replay, monotonic event ordering, identifier retention and bounded resource handling; Criterion for fixed realistic OCEL workloads.
- **Conditional:** Polars only if current Rust4PM dataframes/Arrow cannot meet analytical needs and parity benchmarks show net value; Rayon only when replay order remains stable.
- **Reject now:** extra SQLx DB layer, Ratatui, Tokio, PyO3, Syn/Quote or Crossbeam without demonstrated use.

## Delivery and acceptance contract
- Reconcile existing Conductor tracks and ownership before editing code; do not duplicate completed tasks.
- Write a failing behavioural/regression test first for each runtime change; preserve APIs, schema versions, stdout/stderr, exit codes, error codes and MSRV or explicitly version breaking changes.
- Run the existing repo gates: targeted tests, full workspace tests, fmt, clippy and contract/interop checks. Record actual passing CI SHA; this document is planning, not validation.
- Inventory duplicate crate versions/features with `cargo tree -d` and `cargo tree -e features`; review unused dependencies, `cargo audit`, `cargo deny`, licence, MSRV, SBOM and release implications where applicable.
- Benchmark performance proposals with fixed fixtures and baseline/candidate receipts, including correctness, memory, CPU and determinism.
- Decision for each candidate must be recorded as adopt, retain, reject or defer with evidence, risks and rollback.
- Do not expose identifiable, secret, copyrighted or otherwise restricted raw data in tracing, snapshots, benchmarks or CI artifacts.
