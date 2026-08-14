# Plan: Full-corpus process-mining acceptance

Status: completed at the repository-owned acceptance boundary recorded in
closed issues [#36](https://github.com/edithatogo/foi-process/issues/36) and
[#37](https://github.com/edithatogo/foi-process/issues/37).

- [x] Consume the pinned 33,217-record public archive manifest through the versioned adapter contract.
- [x] Preserve source ordering and reconcile adapter output counts.
- [x] Prove deterministic full replay and ordered incremental continuation produce the same canonical snapshot hash.
- [x] Validate revision, correction, retraction, takedown, privacy-projection, dashboard, and feature-matrix behavior.
- [x] Retain redacted hosted acceptance evidence without retaining raw archive content in the acceptance workflow.
- [x] Record closeout in issues #36 and #37.

## Boundaries

- Recurring instance acquisition, durable package indexes, and snapshot/delta continuation are active under T12 and issue #114.
- The separately versioned full-corpus registry deposit remains deferred in issue #63.
- Jurisdiction-specific empirical and legal modelling remains active under T11 and issue #39.
- Production publication remains independently governed; T10 acceptance does not authorize it.
