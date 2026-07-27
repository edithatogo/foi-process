# Optional full-corpus operations runbook

## Purpose and boundary

This runbook governs an optional recurring rebuild of the public-safe FYI process-mining projection. It is not required for the accepted representative integration path, does not authorize publication of production-derived data, and does not replace source-specific rights, privacy, removal, or governance decisions.

The operational path is:

```text
fyi-cli/fyi-archive immutable manifest -> foi-process deterministic replay ->
public-safe aggregate and event-log projection -> verification evidence
```

Raw WARC/WACZ material, attachments, OCR text, embeddings, correspondence, and confidential source-to-pseudonym mappings remain outside this repository and outside public dashboard assets.

## Preconditions and stop conditions

Start a run only when all conditions are met:

- Pin the input `fyi-archive` manifest revision, controller state, source ordering, and producer versions.
- Confirm the release is limited to the approved public-safe projection profile.
- Confirm a current removal/takedown input and a source-rights record are available.
- Confirm the runner has sufficient local or CI storage and compute allocation without enabling paid hosting, credits, GPUs, or paid data services.

Stop and quarantine the run when any of the following occurs:

- manifest counts, digests, sequence order, or snapshot revisions are inconsistent;
- privacy classification, allowlist, or takedown validation fails;
- replay produces a different canonical snapshot hash from the equivalent incremental continuation;
- a source, rights, retention, or removal decision is missing or ambiguous;
- the bounded dashboard payload or no-cost hosting assumptions are exceeded.

A stopped run is evidence of a failed precondition, not evidence that the corpus is complete or publishable.

## Cost controls

The baseline operation must remain zero-cost:

- use the existing public archive inputs and local or included GitHub Actions capacity;
- use GitHub Pages for the dashboard and the existing public Hugging Face Dataset only where its free public surface remains available;
- do not enable Hugging Face credits, PRO-only hardware, Docker/Gradio runtime, ZeroGPU, paid storage, paid APIs, or a paid transactional backend;
- run bounded smoke or representative checks before a full replay; schedule a full replay only when monitoring or an approved release requires it.

Record runner duration, peak disk use, input count, output size, and any failed or deferred work in the acceptance evidence. If a provider changes its free allowance or requires billing, stop rather than substituting a paid service.

## Retention and handling

| Material | Location and retention rule |
| --- | --- |
| Raw WARC/WACZ, attachment bytes, OCR, embeddings, correspondence | Retain only in the approved source/archive environment under source-specific rights and retention controls; never commit or publish here. |
| Source-to-pseudonym mapping and review records containing personal information | Access-controlled external secret/governance system; never export to logs, manifests, datasets, or dashboard assets. |
| Input manifest revision, source sequence, digests, replay hashes, benchmark summary, coverage and exclusion counts | Retain as public-safe, revision-pinned acceptance evidence. |
| Public-safe event logs, OCEL tables, aggregates, schemas, and dashboard projection | Retain only when the applicable publication gate approves the exact revision; replace or withdraw through the removal workflow. |
| Temporary runner inputs and derived working files | Delete after verification unless a documented source/archive retention obligation applies. |

The Apache-2.0 licence covers repository code only. It never changes the rights of source-derived records or gives permission to retain or republish them.

## Procedure

1. Create an operation record with the requested scope, input manifest revision, controller state, projection policy, takedown revision, runner budget, and accountable operator.
2. Validate manifest structure, attachment/WARC linkage where applicable, source ordering, and input digests before replay.
3. Run deterministic full replay and ordered incremental continuation over the same pinned input. Retain only redacted metrics and canonical hashes in this repository.
4. Compare final active-state hashes, coverage counts, exclusions, revision/takedown propagation, and public-output privacy validation.
5. Build the bounded aggregate/dashboard projection only after the replay checks pass. Keep detailed rows in the approved dataset surface; do not put raw evidence in the dashboard.
6. Measure duration, peak disk, output size, and payload budget. Record any provider, quota, or access limitation.
7. Produce an acceptance record containing input/output revisions, digests, counts, hashes, privacy/takedown results, benchmark measures, and the decision to retain, withdraw, or defer publication.
8. Publish or replace an external revision only after the separate release-specific governance and hosted-verification gates are satisfied.

## Acceptance evidence

A successful optional operation requires all of the following:

- pinned input manifest and controller-state identifiers, counts, source ordering, and SHA-256 digests;
- deterministic full-replay and incremental-continuation final hashes that match;
- coverage reconciliation, quarantine count, exclusion count, and revision/takedown propagation result;
- recursive public-output privacy validation with no raw correspondence, identity-bearing fields, attachment bytes, OCR text, or confidential mapping material;
- benchmark duration, peak disk, output size, and static dashboard payload evidence;
- a revision-pinned public Dataset Viewer/dashboard verification only when an external revision is released;
- a recorded source-rights, retention, removal, and governance decision for that exact release.

Without the final release-specific evidence, the operation may be accepted as an internal or redacted operational run but must not be described as a public production-data release.

## Related records

- `docs/production-release-checklist.md`
- `docs/removal-and-takedown.md`
- `conductor/tracks/T10-full-corpus-process-mining/`
- GitHub issues #9, #39, and #64