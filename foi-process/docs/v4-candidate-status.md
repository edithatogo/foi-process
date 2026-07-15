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

The candidate has since been compiled and tested with the GNU Rust toolchain and hosted Rust 1.88
and stable matrices. Release-profile synthetic scale evidence now covers one million active events,
and the repository includes verified Dataset, Static Space, Parquet partition, and release-evidence
paths. Real archive integration, privacy/governance approval, authenticated Hub publication, and
hosted artifact attestation remain external gates.
