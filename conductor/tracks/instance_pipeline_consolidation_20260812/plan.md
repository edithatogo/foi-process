# Plan

## Phase 1: Current-state contract

- [ ] Inventory each `foi-process` input and publication workflow.
- [ ] Classify existing Hugging Face downloads as pinned archive handoffs,
  unpinned handoffs, fixtures, or publication verification.
- [ ] Add a machine-readable cross-repository package contract fixture.

## Phase 2: Fail-closed package intake

- [ ] Resolve archive mirror references to immutable revisions and record them.
- [ ] Verify package schema, checksums, provenance, instance, archive and
  takedown revisions, ordering, counts, retention, and compatibility.
- [ ] Reject direct source URLs and unapproved archive repositories.

## Phase 3: Incremental processing

- [ ] Consume ordered deltas from the last accepted package revision.
- [ ] Consume periodic compacted snapshots for bounded recovery.
- [ ] Prove incremental continuation equals full replay for NZ fixtures and a
  hosted bounded real package.

## Phase 4: Publication separation

- [ ] Publish raw archive data only from `fyi-archive` workflows.
- [ ] Publish derived process data and static dashboard assets only from
  `foi-process` workflows using validated package receipts.
- [ ] Display instance, archive revision, takedown revision, coverage, and
  limited/full-corpus scope in the dashboard.

## Phase 5: NZ parity and expansion gate

- [ ] Reconcile case, event, attachment, revision, ordering, and dashboard totals
  against the NZ package produced by the generic upstream controller.
- [ ] Link hosted evidence to #114 and upstream #370.
- [ ] Permit another instance only after NZ parity and that instance's privacy,
  rights, retention, removal, threat-model, and operational gates are complete.
