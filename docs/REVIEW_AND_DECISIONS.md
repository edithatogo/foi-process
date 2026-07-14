# Review of v2 and decisions incorporated in v3

## Overall assessment

v2 established the correct strategic boundaries and produced useful initial contracts and fixtures. It was, however, still a planning skeleton: its live normaliser was a no-op, its archive adapter only wrapped one manifest record, its dashboard logic loaded complete logs and sorted timestamp strings, and it did not directly use Rust4PM.

## Material findings and incorporated changes

| v2 finding | v3 decision |
|---|---|
| Seven small crates increased maintenance and contradicted the preference for fewer libraries. | Collapse to one `foi-process` package with modules and optional features. Extract a crate only after a second real consumer exists. |
| Rust MSRV was 1.78. | Raise to Rust 1.88, matching Rust4PM 0.6.0. |
| Appendable OCEL was described as missing. | Integrate Rust4PM's existing `AppendableOCEL`; upstream only ordering, transactional/durable delta, and streaming gaps that remain. |
| Hand-rolled OCEL/DFG risked becoming a competing process-mining implementation. | Rust4PM is canonical. Local OCEL rows and counters are transport/live-dashboard projections only. |
| IDs, timestamps, confidence, vocabulary values, and digests were weakly typed. | Add validated newtypes and deterministic content IDs. |
| Ad-hoc JSON key sorting was insufficient for cross-language cryptographic identity. | Use RFC 8785 JCS for canonical bytes and add parity fixtures as a promotion gate. |
| Full evidence objects were repeated inside each event. | Events hold evidence references; evidence, objects, object links, and object changes are separate tables. |
| Corrections and deletions could not be replayed correctly. | Add logical IDs, revisions, operations, supersession/retraction, idempotence, conflict/gap detection, and checkpoints. |
| Archive and live ingestion were separate conceptual paths. | Archive snapshots become deltas and pass through the same deterministic normaliser/replay engine as live `fyi-cli` output. |
| Corrected events would be double-counted in OCEL/dashboard outputs. | Materialise the latest active logical event; revision-aware roll-ups recompute only the affected case and ignore stale out-of-order revisions. |
| OCR was assumed rather than designed. | Add `DocumentBundle`, `PageEvidence`, model/runtime/license provenance, geometry, reading order, and selective OCR boundaries. |
| No explicit publication/privacy layer. | Add sensitivity/access/disposition contracts and a metadata-only/withhold-safe public projection. |
| Hand schemas and Rust-derived schemas could drift. | Rust types are intended to become canonical; `schema-gen` emits snapshots. Portable schemas remain an independently validated compatibility surface until promotion to FOI-O. |
| Conformance mixed structural and legal concepts. | Separate structural, semantic, process, statutory, privacy, and data-quality findings. Legal certification remains external/human bounded. |
| Conductor layout was treated uniformly. | New repo uses `conductor/`; `fyi-cli` export respects its existing `.conductor/` control plane and project-sync script. |
| Streaming CLI output could be truncated or partially omitted on resume. | Fresh runs create journals exclusively; resumed runs append. All normalized tables, findings, reviews, outcomes, and quarantine records are emitted. |
| A checkpoint could be written before restart state, or an altered state could be restored. | Verify snapshot state hashes, persist state before the checkpoint commit marker, and sync the parent directory on Unix. |
| The documented `fyi-cli | foi-process` pipe was not executable. | Treat `-` as stdin for NDJSON replay and streaming commands. |

## Remaining export gates

1. Run Rust compilation, clippy, tests, docs, and `--features rust4pm` in a real Rust 1.88+ environment.
2. Run RFC 8785 identifier parity vectors across Rust and the temporary Python oracle.
3. Compare generated Rust schemas with portable schemas; resolve intentional differences and commit golden snapshots.
4. Test the normaliser against a real sample of `fyi-archive-nz`, not only fixtures.
5. Confirm field names against the current `fyi-cli` storage schema and archive manifest.
6. Benchmark 1k, 10k, and full-corpus snapshots before freezing Parquet partitioning.
7. Conduct a privacy review before publishing OCR text or semantic search.
