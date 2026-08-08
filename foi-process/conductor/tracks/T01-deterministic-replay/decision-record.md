# Replay state backend decision

**Decision:** retain the file-backed replay state backend for the current
single-writer archive continuation and dashboard build.

The existing backend writes a complete snapshot to a temporary file, flushes
and syncs it, then atomically replaces the target. Restore verifies the stored
state digest before use. Duplicate delivery, correction, restart, quarantine,
and position-gap behaviour are covered by the replay test suite.

A transactional database backend is not required for the current deployment
shape. It becomes a promotion gate if the system introduces concurrent writers,
multi-process checkpoint ownership, or online dashboard writes. That future
work must preserve the same canonical state hash, checkpoint monotonicity,
quarantine semantics, and crash-recovery contract.

**Evidence:** `src/replay.rs`, `tests/replay.rs`, and the explicit GNU-target
`cargo test --locked --all-targets` verification recorded in
`docs/verification-2026-07-22.md`.
