# Track: Full-corpus ingestion, mining, and static dashboard

- [Specification](./spec.md)
- [Implementation plan](./plan.md)
- [Metadata](./metadata.json)
- [GitHub track issue](https://github.com/edithatogo/foi-process/issues/37)
- [Cross-repository epic](https://github.com/edithatogo/foi-process/issues/36)

Upstream tracks:

- `edithatogo/fyi-cli:.conductor/tracks/process-event-export_20260721/` / [#231](https://github.com/edithatogo/fyi-cli/issues/231)
- `edithatogo/fyi-archive:conductor/tracks/full_corpus_process_projection_20260721/` / [#196](https://github.com/edithatogo/fyi-archive/issues/196)

Local cross-references: T03 archive/live adapters, T07 dashboard/Hugging Face,
and T08 scale/release/governance.

## Acceptance closeout

The track is `acceptance_verified` after the hosted downstream checks recorded
on issues #36 and #9: the pinned public manifest covered 33,217 records, the
Rust adapter produced deterministic output, and full replay matched ordered
incremental continuation at the canonical snapshot hash. Dashboard and
feature-matrix checks also passed. Raw archive content is not retained by the
acceptance workflow. Production publication and jurisdiction-specific legal
modelling remain separate human/source-gated work.
