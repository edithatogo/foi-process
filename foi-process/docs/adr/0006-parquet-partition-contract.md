# ADR 0006: Partition production Parquet by site, jurisdiction, and event year

Status: accepted.

## Context

A production corpus can contain millions of event, evidence, object-link, revision, and finding
rows. Full-table rewrites and unbounded in-memory grouping would undermine the replay and
publication architecture.

## Decision

Partition event-led analytical datasets using the Hive-style path:

```text
site=<percent-encoded-site>/jurisdiction=<percent-encoded-jurisdiction>/event_year=<YYYY>/part-*.parquet
```

Partition values use uppercase percent encoding for every byte outside the RFC 3986 unreserved
set. The year comes from the event's deterministic mining time. `event_partition_directory()` is
the normative path helper and has a cross-platform test.

The ingestion/orchestration layer groups a bounded bundle by this key and invokes the existing
atomic Parquet writer once per partition. Evidence and object tables are deposited beside the event
partition when they are referenced there; global deduplication remains identifier-based rather than
path-based.

## Consequences

- site/jurisdiction/year pruning works in DuckDB, Arrow, and common lakehouse readers;
- partition paths cannot escape the dataset root through URI or slash characters;
- corrected events retain stable logical identifiers even if a changed mining time moves the latest
  revision to a different partition;
- compaction, orphan cleanup, and cross-partition correction handling belong to the production
  archive adapter, not the bounded table writer.
