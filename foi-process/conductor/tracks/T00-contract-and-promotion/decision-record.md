# Contract promotion decision

The portable contracts remain owned by `foi-process` for the current
integration stage. The Rust types, generated examples, JSON schemas, replay
fixtures, public projection, Parquet contracts, and feature-gated Rust4PM
consumer adapter compile and pass their repository test suites.

The independent JCS vector check covers the portable fixture subset and is
documented in `docs/canonical-identifiers.md`. Promotion to downstream owning
repositories remains conditional on their own schema and legal vocabulary
reviews; this repository does not silently claim those external promotions.

**Decision:** promote the local contract surface to repository-verified,
retaining downstream ownership and statutory certification as explicit
acceptance gates.
