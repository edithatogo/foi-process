# Canonical identifiers and hashes

All generated logical and revision identifiers use SHA-256 over **RFC 8785 JSON Canonicalization Scheme (JCS)** bytes. This replaces the v2/v3-preview ad-hoc key sorter and makes the contract suitable for Rust/Python/JavaScript parity, signed manifests, and reproducible archive reprocessing.

Rules:

- identifiers supplied by an upstream system remain namespaced stable identifiers;
- generated IDs are `urn:<namespace>:sha256:<lowercase-hex>`;
- integers that cannot be represented safely in interoperable JSON remain strings in contracts;
- decimal/money values are strings with an explicit datatype/profile;
- arrays retain order; unordered semantic collections must be sorted before hashing;
- source bytes receive their own SHA-256 digest and are never replaced by a hash of parsed JSON;
- schema version, mapping profile, and algorithm version are included whenever they affect identity.

The Rust implementation is canonical. The Python fixture generator intentionally uses only the JCS-compatible subset of JSON until a cross-language parity suite is promoted from `rulesandprocesses`.

The repository includes an independent Python oracle at
`scripts/verify_jcs_vectors.py`. It verifies the checked-in ASCII/integer/string/
boolean/null/array/object vectors. This is a parity check for the portable fixture
subset, not a claim that the small oracle replaces a full RFC 8785 implementation
for arbitrary Unicode or number edge cases.
