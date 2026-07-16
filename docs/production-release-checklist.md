# Production release checklist

This checklist is required before any real FOI-derived record replaces the synthetic fixture
release. The publication gate remains fail-closed until the accountable owner records evidence for
each item.

## Data path

- Capture through the approved fyi-cli/fyi-archive path, including manifest source sequence,
  snapshot revision, WARC identifiers, attachment byte length, and SHA-256 digest.
- Retrieve attachment bytes through the approved archive path and call
  `verify_manifest_attachment_bytes` before emitting deltas.
- Store raw bytes, WARC/WACZ files, OCR, embeddings, and the confidential source-to-pseudonym map
  outside this public repository and outside public Hugging Face assets.
- Use `pseudonymize_case_id` with a secret held by an external secret manager. Never log or export
  the key or the source identifier used to derive the pseudonym.

## Disclosure and release

- Complete requester/third-party privacy, small-cell, differencing, join, and case-timeline tests.
- Complete source-specific rights and attribution records. A source document's rights are never
  inferred from the repository code licence.
- Confirm the public contact and incident owner using the channels in `docs/removal-appeal.md`.
- Record review date, scope, retention period, withdrawal procedure, and the exact source and
  generated revisions in a signed release record.
- Update `governance/publication_gate.json` only after the required human approvals exist.
