# Review summary — 2026-07-09

## Where the work now stands

The v2 direction was sound but still mostly an architectural skeleton. The reviewed v3 workpack is an export candidate with a coherent Rust-first event spine, deterministic replay model, direct Rust4PM boundary, reference fixtures, portable schemas, Conductor tracks, and repo-specific promotion packets.

It is intentionally one Rust package with modules rather than a collection of new libraries. Generic mining remains in Rust4PM; FOI semantics remain in FOI-O; capture remains in `fyi-cli`; archive publication remains in `fyi-archive`; document extraction/OCR belongs in `fe-reader`; semantic signals belong in `nlp-policy-nz`; statutory reasoning belongs in Axiom/RuleSpec; UI belongs in Propel; simulation belongs in Kairos; and `rulesandprocesses` remains the background adoption/contract laboratory.

## Additional improvements incorporated during this review

1. Re-scoped appendable OCEL work to integration and targeted upstream extensions because Rust4PM 0.6 already provides `AppendableOCEL`.
2. Collapsed seven proposed crates into one library/binary with optional features.
3. Added validated IDs, RFC 8785 canonical JSON, typed timestamps/digests/confidence, revisions, causation, and privacy.
4. Separated evidence and object tables from event references to avoid corpus-scale duplication.
5. Converged archive and live records on one deterministic delta/replay path.
6. Added revision-aware corrections/retractions, partition positions, quarantine, restart snapshots, integrity verification, and checkpoint discipline.
7. Made live summaries deterministic under out-of-order revisions and prevented correction double-counting.
8. Added stdin NDJSON, complete append-only streaming journals, state-before-checkpoint commit ordering, and Unix parent-directory sync.
9. Added explicit document/OCR boundaries, model/runtime/license provenance, evidence geometry, and human review records.
10. Added privacy-safe public projections so public archival status does not automatically authorize OCR/search amplification.
11. Added direct Rust4PM adapter code and a feature-gated recording-sink integration test.
12. Added duplicate/reference/conflicting-revision validation across normalized bundles.
13. Made Conductor and issue exports repo-aware, including `fyi-cli`'s existing `.conductor` and `master` conventions.
14. Added CI, supply-chain, schema-drift, replay, performance, privacy/tikanga, and promotion quality gates.

## Readiness judgment

**Ready for a Git branch and compilation review; not yet ready for a public release.**

The portable schemas, generated fixtures, Python development oracle, semantic checks, configuration files, shell scripts, and Rust syntax have been validated in this environment. A Rust compiler was unavailable, so Cargo compilation—including the direct Rust4PM adapter—is the first mandatory export gate. A real `fyi-archive-nz` sample, bounded Parquet writers, full-scale benchmarks, and privacy/tikanga review remain required before corpus publication or dashboard deployment.

## Recommended first export sequence

1. Create a branch or new `foi-process` repository and run `scripts/ci-local.sh` on Rust 1.88+.
2. Resolve compilation or Rust4PM API differences, commit `Cargo.lock`, and run `cargo deny check`.
3. Reconcile Rust-generated schemas with `schemas/portable/` and record intentional differences.
4. Map a representative archive sample through the same replay path used by live deltas.
5. Promote stable contracts only after fixture, consumer, and owner-repository gates pass.
6. Implement bounded Arrow/Parquet sinks and benchmark revision-heavy 1k, 10k, and 200k-request workloads.
7. Wire the experimental `EvidenceDelta` emitter into `fyi-cli`, then add the Propel/Hugging Face profile only after public-projection review.
