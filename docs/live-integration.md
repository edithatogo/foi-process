# Dynamic integration with fyi-cli

`fyi-cli` is not an NLP or process-mining engine. It emits durable evidence deltas and continues to own capture, watermarks, retries, and WARC/WACZ provenance.

Proposed interface:

```bash
fyi-cli watch --site fyi.org.nz \
  --emit evidence-delta-v1 --format ndjson --capture warc \
| foi-process replay-stream - ./process-state \
  --processed-at 2026-07-09T00:05:00Z
```

A production adapter should use bounded channels or a local append-only journal rather than relying only on a shell pipe. The protocol includes source/partition/sequence positions, revisions, content digests, correlation/causation IDs, and checkpoints. Duplicate delivery is safe; gaps and conflicting revisions are quarantined rather than guessed. `-` is an implemented stdin path for NDJSON. A fresh output directory is required for a fresh run; supplying `--state-in` switches the journals to append/resume mode.

## Derived-store attachment verification

For a captured `fyi-cli` request directory, the Rust adapter can verify attachment bytes from the derived store before producing deltas. The manifest must carry each attachment's relative `path`, SHA-256 digest, and (when captured) byte size. The retriever canonicalizes the configured root and rejects path traversal; it never fetches the public URL and never writes the retrieved bytes to the output.

```bash
cargo run --locked -- fyi-archive-derived-store-to-deltas \
  --input data/raw/requests/manifest.json \
  --derived-root data/raw/requests \
  --output evidence-deltas.ndjson \
  --report attachment-verification.json \
  --captured-at 2026-07-16T00:00:00Z
```

The command fails closed on missing paths, digest mismatches, size mismatches, unreadable files, or a path outside `--derived-root`. The optional JSON report records verification status and counts only; it is not a substitute for retaining the upstream capture manifest and WARC/WACZ provenance.

Live operation maintains:

- latest materialised event revision;
- active request state;
- revision-aware DFG/variant roll-ups;
- deadlines and conformance warnings;
- pending OCR/NLP work;
- watermarks, checkpoint hashes, and dead-letter records.

Heavy discovery runs from snapshots. Live updates focus on monitoring and conformance rather than rediscovering the full model after every message.

## Partition-order invariant

`fyi-cli` assigns a monotonically increasing sequence **after** a delta enters an emitted partition. Event-time lateness is represented by `event_time`/watermarks, not by reusing or regressing stream positions. `foi-process` therefore quarantines position gaps, regressions, and conflicting reuse without advancing the checkpoint. This gives deterministic replay and makes missing transport records observable.

## Durable commit sequence

For each run, accepted outputs, findings, reviews, and quarantine records are flushed and synced first. The replay snapshot is then atomically replaced and its state hash verified on the next restore. `checkpoint.json` is written last and acts as the commit marker. This is intentionally at-least-once: a crash after journal sync but before the checkpoint may repeat deterministic IDs, which downstream materialisers must deduplicate.

The streaming journals include `events`, `evidence`, `objects`, `object-links`, `object-changes`, `document-signals`, `findings`, `human-reviews`, `outcomes`, and `quarantine`.
