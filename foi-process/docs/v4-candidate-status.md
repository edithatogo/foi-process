# V4 candidate status

This tree combines the verified v3 workpack with the recovered v4 implementation work.

Added or strengthened:

- one-crate Rust integration spine;
- compact revision-aware dashboard roll-ups;
- tolerant `fyi-archive` manifest adapter;
- archive/live convergence through `EvidenceDelta`;
- bounded Arrow/Parquet row groups behind the `parquet` feature;
- archive and Parquet CLI vertical-slice commands;
- a scale-smoke binary;
- fixtures and integration tests.

This candidate was assembled in an environment without a Rust compiler. It has static and
contract validation only. Codex must compile it, reconcile it with the current repository,
repair exact dependency/API differences, regenerate schemas/fixtures, and update all status
claims before release.
