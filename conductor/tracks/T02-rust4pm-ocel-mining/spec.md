# Rust4PM and OCEL

## Goal

Use Rust4PM directly and upstream only generic missing capabilities.

## Non-goals

Do not duplicate capabilities owned by another repository or promote an untested contract.

## Exit criteria

- Compile AppendableOCEL adapter
- Compare OCEL round-trip
- Benchmark streaming/mining candidates

## Serde suitability and dependency disposition — 18 November 2026

The root crate already uses `serde` derive, `serde_json`, `schemars`, and `serde_json_canonicalizer`. `src/ocel.rs` defines typed OCEL projection rows with explicit `#[serde(deny_unknown_fields)]`; optional `process_mining` (Rust4PM) supplies OCEL/process-mining capabilities. Arrow/Parquet remain optional tabular formats. This is appropriate; replacing any of those semantics with Serde is neither feasible nor warranted.

Within **existing T02**:
- [ ] Reconcile actual typed OCEL event/object/link roundtrip and `schemars` schemas with Rust4PM imports, using independent fixture corpora and malformed/duplicate-key input.
- [ ] Confirm JCS canonical bytes/digests, float and integer precision, timestamp/qualifier fidelity, schema versions, rights/identity and loss ledger remain invariant across serialization and optional Parquet.
- [ ] Maintain security and supply-chain qualification for Rust4PM/XML dependencies independently; Serde does not cure XML advisories or certify analytical mining outputs.
- [ ] Only create a bounded code-replacement leaf after identifying repeated, demonstrably redundant hand-written JSON. Record baseline/reduction/perf, exact-head tests and integration approval; no-go is valid. Do not alter T13's completed historical evidence.
