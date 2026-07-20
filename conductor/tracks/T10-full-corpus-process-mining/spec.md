# Specification: Full-corpus ingestion, mining, and static dashboard

GitHub issue: https://github.com/edithatogo/foi-process/issues/37  
Parent epic: https://github.com/edithatogo/foi-process/issues/36  
Upstream issues: https://github.com/edithatogo/fyi-cli/issues/231 and
https://github.com/edithatogo/fyi-archive/issues/196

## Overview

Consume versioned, public-safe archive process projections and produce deterministic
full-replay and incremental process-mining outputs for the free Static Hugging Face
Space. The browser receives bounded aggregate assets; detailed case/event rows are
queried through paged Dataset Viewer APIs.

## Functional requirements

- Validate source schemas, revisions, checksums, rights metadata, and coverage manifests.
- Ingest partitioned cases, events, attachment metadata, and revisions with bounded memory.
- Preserve source order in normalization, variants, durations, and dashboard calculations.
- Reconcile full replay with incremental continuation and correction/takedown semantics.
- Mine activities, edges, variants, durations, authority/period/outcome cubes, OCEL, and qualified conformance indicators.
- Generate bounded dashboard aggregates plus Dataset Viewer query metadata.
- Report freshness, source coverage, timestamp coverage, revisions, exclusions, and pipeline health.

## User experience

The Static Space should prioritize process maps, authority comparison, timelines,
variants, duration distributions, outcome/state views, statutory-clock indicators,
coverage, and provenance. It must distinguish observed platform activity from legal
conclusions and make incomplete coverage visible.

## Acceptance criteria

- Dashboard totals reconcile to pinned projection checksums.
- Full replay and incremental continuation yield identical active state and hashes.
- Source ordering is preserved and timestamp ties cannot reorder events silently.
- Full-corpus benchmark records time, memory, rows/second, correction overhead, and output size.
- Static assets stay within the repository budget and require no paid runtime.
- Detailed rows are paged rather than embedded as an unbounded browser payload.
- Recursive privacy validation and takedown tests pass.

## Out of scope

- Publishing raw correspondence, identity, WARC bodies, OCR, embeddings, or attachment bytes.
- Paid Hugging Face runtime, ZeroGPU, or a hosted transactional database.
- Publication without the existing separate release gate.
