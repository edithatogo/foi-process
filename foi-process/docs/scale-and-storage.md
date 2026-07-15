# Scale and storage

Two hundred thousand requests are modest for Rust/Arrow/Parquet, but messages, attachments, OCR segments, object links, revisions, and conformance findings can produce millions of rows.

Recommended layout:

```text
site=<site>/jurisdiction=<jurisdiction>/event_year=<year>/part-*.parquet
```

ADR 0006 makes this layout normative. Partition components are percent-encoded and the year is
derived from deterministic mining time through `event_partition_directory()`. The current writer
atomically emits one bounded partition; production orchestration is responsible for grouping,
compaction, and cross-partition correction cleanup.

Use dictionary encoding for activities, object types, qualifiers, jurisdictions, and assertion states. Keep text blobs and embeddings outside the hot event table. Preserve a stable row ID and source digest in every table.

The CLI includes a streaming replay command and a revision-aware summary. Production Parquet writers should flush bounded row groups rather than build one in-memory bundle. Rust4PM receives snapshots or bounded append streams through its native APIs.

Benchmarks must report wall time, peak memory, rows/second, correction/retraction overhead, output size, and deterministic output hashes at 1k, 10k, and full-corpus scales.
