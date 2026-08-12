# Instance archive-to-process pipeline consolidation

Issue: [foi-process #114](https://github.com/edithatogo/foi-process/issues/114),
sub-issue of [#39](https://github.com/edithatogo/foi-process/issues/39).
Upstream: [fyi-archive #370](https://github.com/edithatogo/fyi-archive/issues/370).

## Goal

Make the downstream contract explicit: `foi-process` consumes immutable,
versioned, checksummed packages produced by `fyi-archive`; it does not discover,
scrape, or capture source records independently.

## Pipeline

1. `fyi-cli` discovers and captures a source instance and exports ordered
   process-event and attachment sidecars.
2. `fyi-archive` validates and packages raw records, manifests, sidecars,
   revisions, provenance, checksums, and takedown state.
3. `foi-process` fetches a pinned package from an approved `fyi-archive` mirror,
   verifies it, replays it deterministically, and creates derived analytics.
4. Approved workflows publish the derived event-log dataset and static dashboard
   assets to their own Hugging Face repositories.

The archive's Hugging Face dataset is both a raw archive publication target and
a valid transport for a pinned handoff package. The downstream event-log dataset
and Space are separate outputs; this deliberate fan-out is not duplicate source
capture.

## Requirements

- Validate schema version, instance, archive revision, takedown revision,
  source ordering, file digests, row/byte counts, provenance, retention status,
  and compatible contract versions before processing.
- Reject moving `latest` inputs for production unless resolved to and recorded
  as an immutable revision and digest.
- Preserve source ordering through event-log and dashboard calculations.
- Support ordered deltas and compacted snapshots; require full replay and
  incremental continuation to produce the same canonical state.
- Keep raw correspondence and archive material out of derived public outputs
  unless a separately approved publication profile explicitly includes them.
- Complete NZ parity before enabling another instance in the production path.

## Acceptance

- CI proves no production workflow contacts an FOI source site or Internet
  Archive directly.
- Package compatibility fixtures pass in `fyi-archive` and `foi-process`.
- Invalid revision pins, digests, ordering, coverage, takedown state, or schema
  versions fail closed with actionable evidence.
- The bounded dashboard and future complete-corpus dashboard reconcile exactly
  to their declared package coverage and do not overstate scope.
- Capture, transformation, raw publication, derived publication, and legal
  promotion remain independent gates.
