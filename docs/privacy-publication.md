# Privacy, ethics, and publication

A record being publicly accessible on an FOI platform does not automatically make every extracted name, address, health detail, OCR fragment, embedding, or cross-linked entity appropriate for amplified search and dashboard publication.

The v3 contracts therefore distinguish:

- sensitivity class;
- access tier;
- publication disposition;
- human-review status and reason codes.

The public projection omits events marked `withhold` or `needs_review`, strips evidence from metadata-only events, filters event attributes through an allowlist, and only exposes evidence links that are independently assessed as public. Full-text search and embeddings should operate in access-controlled indexes with a separately generated public index.

The public reporting policy is documented in `docs/traceability-policy.md`: public views default to
system-level reporting, groups below six cases are suppressed or combined, and confidential-source
dashboards use keyed pseudonymous case identifiers whose mapping is never published.
