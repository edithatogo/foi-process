# NZ corpus completion plan

## Current evidence

- The canonical `fyi-archive` manifest has 33,217 captured requests.
- The retained Internet Archive CDX discovery snapshot is complete: 208,826 capture records over
  209 pages, recorded by `fyi-archive` run `30395825959`.
- Its current reconciled request queue has 31,749 logical requests. That does not reconcile to the
  captured manifest and is a hard stop for full-corpus processing.
- The accepted bounded release remains 75 requests, 425 events, and 179 attachments. It is useful
  operating evidence, not full-corpus evidence.

Internet Archive CDX establishes historical discovery and corroboration. It cannot substitute for
the canonical captured request record, attachment bytes, or a complete fyi-cli event log.

## Delivery order

1. Reconcile the 1,468-request queue/manifest gap in `fyi-archive`, retaining both the archive
   discovery receipt and the canonical request locator for every resulting queue entry.
2. Run one bounded real NZ batch against the reconciled source. Require manifest, case, event,
   attachment, source-record, checksum, and takedown parity before accepting it.
3. Continue in bounded, rate-limited batches with no automatic publication. Merge only verified
   batch artefacts, requeue failures from their retained ledgers, and keep a versioned controller
   state.
4. Merge the verified batch outputs, generate the versioned full projection, and prove exact
   manifest/case/event/attachment/source-record parity.
5. Rebuild the static dashboard from that pinned projection. Its coverage view must surface the
   source revision, all five parity counts, exclusions, and a clear unavailable state until the
   full projection exists.
6. Prepare the release evidence, takedown inventory revision, and external host receipts. Release
   remains an explicit owner decision, not an effect of a successful pipeline.

## Canonical data topology

`fyi-archive-nz` is the canonical source layer for raw correspondence, WARC/WACZ material, and
attachments. `foi-process` consumes its immutable manifest and emits event logs, aggregate process
metrics, and case-level source records. A case-level source record contains a canonical locator,
integrity digest, WARC identifiers, attachment count, and source rights/attribution metadata. The
dashboard presents system measures by default and links out to the canonical archive when useful.

For future confidential material, the same contract uses an access-controlled source layer and a
keyed pseudonymous case identifier. The mapping never enters a public dataset or dashboard.

## Automated review and DSPy

The immediate NZ controls are deterministic: schema and checksum verification, source ordering,
manifest parity, recursive privacy validation, takedown propagation, and fixed-rubric adversarial
review of a stratified operational slice. The automated panel is advisory evidence; it is not a
substitute for a legal or rights determination.

DSPy is deferred until a sufficiently large, independently adjudicated NZ review set exists. At
that point it may optimise a fixed review signature for provenance, event-boundary, ordering, and
privacy-risk flags. It must use held-out cases, retain prompts and scorecards, emit explanations,
and never automatically promote, publish, or suppress a case. No DSPy dependency is added before
that evidence exists.

## Owner decisions still required

- Whether to authorise a bounded live capture after the reconciliation guard passes, including its
  batch size, delay, and total cap.
- Whether a verified full projection should be externally released after the governance evidence is
  complete.
- Whether to approve the later DSPy pilot after an adjudicated NZ review corpus has been deposited.
