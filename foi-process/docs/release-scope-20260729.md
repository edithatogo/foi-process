# Release scope decision: 2026-07-29

The full fyi.org.nz continuation is intentionally skipped for this release
cycle. The Internet Archive discovery snapshot remains complete, but it is not
treated as captured request data. The live backfill is therefore limited to
the verified bounded real batches already retained in hosted CI.

## Accepted evidence

- Real fyi-cli batches are usable only when their evidence records
  `dry_run=false`, `require_live_manifest=true`, exact request parity, exact
  attachment parity, and a revision-pinned snapshot identifier.
- The dashboard may be validated against the fixture and bounded real-batch
  evidence, but must label the scope and must not claim full-corpus coverage.
- A preservation package may be prepared for the bounded release only if its
  manifest states the scope, source release, source rights, and incompleteness.

## Deferred evidence

Full-corpus parity, production takedown continuation, full-corpus HF refresh,
and closure of the corresponding production governance rows remain deferred.
No archive-only discovery candidate is promoted into a captured request record.

Repository code remains Apache-2.0. Source-derived records, attachments, and
derived data retain their source-declared rights.
