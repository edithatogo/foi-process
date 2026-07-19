# Production Governance Review Record

Status: `historical_synthetic_review_superseded_for_non_publication_controls`

The current non-publication review is recorded in
`governance/non-publication-review-2026-07-19.json` and
`governance/panel-review-2026-07-19.md`. This historical packet is retained for
auditability; its publication-blocked decisions remain in force.

This record is the review packet for deciding whether any production FOI archive
records, attachments, OCR output, or embeddings may be published. It does not
grant approval. Until every row below has a named reviewer, a decision, and a
linked evidence record, `governance/publication_gate.json` must remain
`synthetic-only`.

## Evidence available

- Bounded live request and attachment flow: `docs/evidence/live-fyi-cli-fyi-archive-foi-process-2026-07-15.json`
- Archive capture structure and hashes: `docs/evidence/real-fyi-archive-capture-2026-07-15.json`
- Native DuckDB runtime: `docs/evidence/duckdb-runtime-2026-07-16.json`
- Published release DOI: `docs/evidence/zenodo-preservation-2026-07-16.json`
- Current fail-closed decision state: `governance/publication_gate.json`

## Accountable-owner narrative decisions

These are recorded as owner direction and do not by themselves approve production
publication. The seven formal review gates below remain pending until each has a
named reviewer, evidence, conditions, and an accountable-owner release decision.

### 1. Publication in principle

Publication of real FOI-derived data is permitted in principle. The accountable
owner has authority to approve proceeding. Publication is not inherently limited
to a pilot, agency, or time period, but must comply with privacy, licensing,
tikanga, security, provenance, and removal safeguards.

### 2. Publication content

The system is intended to report public-service performance at system level.
Public source text may exist in source repositories, but this process-mining
publication should not reuse or surface raw request text unless necessary for
provenance. The dashboard should expose value-adding performance, provenance,
and reproducibility information. Embeddings and NLP extractions may be retained
or published through `fyi-archive` where separately justified, but are not
automatically surfaced by this dashboard.

### 3. Traceability

The current public version may retain pragmatic traceability to already-public
FOI records where that traceability adds provenance value. A future dashboard
using non-public requests must use pseudonymised internal case identifiers, with
the re-identification mapping kept outside GitHub, Hugging Face, and public
dashboard assets.

### 4. Reporting granularity

The public reporting policy is two-tiered:

- retain exact timestamps and source identifiers in auditable data only where
  needed for provenance and reproducibility;
- default public views to dates, reporting periods, and aggregated performance;
- suppress or combine groups with fewer than six cases;
- prevent filter combinations from reconstructing suppressed cells;
- do not join public process data with other datasets in a way that could
  identify a person;
- require a separate disclosure review for case-level timelines in any
  non-public-data version.

This is consistent with New Zealand privacy and statistical disclosure guidance,
including Privacy Act Principle 11 and Stats NZ small-cell confidentiality
practice. See `docs/traceability-policy.md`.

## Recommended positions for upcoming decisions

These are recommendations for the remaining owner decisions and are not recorded
as approvals until the owner confirms them in narrative form.

### 5. OCR, embeddings, and NLP derivatives

Keep raw OCR, embeddings, and unrestricted NLP outputs out of public dashboard
assets by default. Permit controlled retention in `fyi-archive` only where the
source licence, purpose, access control, retention, and removal path are recorded.
Publish derived system-level measures only after checking that they cannot be
used to reconstruct source text or identify a person. **Owner direction:** proceed
with this recommendation. Formal approval remains pending named review evidence.

### 6. Tikanga, Māori data governance, and data sovereignty

There is currently no separate tikanga reviewer because this is a single-person
project. The accountable owner will complete and sign an owner-led assessment
covering custodianship, permitted reuse, hosting jurisdiction, cross-border
replication, retention, and withdrawal. The current synthetic fixture is not
treated as Māori or culturally sensitive source data. If real data contains
Māori-specific, culturally sensitive, or sovereignty-sensitive material that the
owner cannot responsibly assess, publication will pause until appropriate advice
or engagement is obtained. **Owner direction:** no separate reviewer is required
at the current stage; retain this escalation trigger.

### 7. Licensing and attribution

The code and schemas retain their declared open-source licences. Source FOI
records, synthetic fixtures, embeddings, OCR, and derived process metrics are
treated as separate artefacts with source-specific rights and attribution. A
per-source rights and attribution record is required, all `to-be-recorded`
licence values must be replaced, and downstream reuse terms must be explicit.
Public accessibility is not treated as unrestricted redistribution authority.
**Owner direction:** proceed with this recommendation. Formal licensing approval
remains pending completion of the source records.

### 8. Removal, correction, and appeal

The accountable owner will maintain one public contact channel, acknowledge
requests within five business days where practicable, handle urgent privacy or
safety takedowns immediately, and temporarily withdraw disputed material while
it is assessed. Corrections and re-publication will be recorded as new revisions
with a durable removal log covering GitHub, Hugging Face, Zenodo, GitHub Pages,
and known downstream copies. The process will state that downloaded copies,
forks, caches, and mirrors cannot all be forcibly recalled. **Owner direction:**
proceed with this recommendation. The owner remains responsible for the
contact channel, takedown decisions, and incident record.

### 9. Threat model and release authority

The high-severity controls identified by the panel should be closed before any
production-capable publication workflow is enabled: allowlist HF targets, narrow
the HF token scope, pin token-bearing workflow dependencies, validate all public
artifacts recursively, and test re-identification and filter-differencing risks.
The accountable owner will make the final release decision with a defined scope,
review date, and incident-response owner. **Owner direction:** proceed with this
recommendation; formal threat-model sign-off and final release authorization
remain pending the technical controls and the owner's signed release record.

## Required decisions

| Gate | Reviewer and role | Decision | Evidence or conditions | Date |
| --- | --- | --- | --- | --- |
| Requester and third-party privacy | Ohm, independent privacy panel | Pass for synthetic-only; production blocked | Recursive public-output validation; no raw request/attachment output; see `docs/privacy-publication.md` and `scripts/test_public_privacy.py` | 2026-07-16 |
| OCR and embedding amplification | Erdos, independent data-governance panel | Pass for synthetic-only; production blocked | Raw OCR, embeddings and unrestricted NLP remain prohibited; owner direction in decision 5 | 2026-07-16 |
| Tikanga and Māori data governance | Owner-led assessment; no separate reviewer at this stage | Pass for synthetic-only; escalation required for culturally sensitive real data | Owner decision 6; current fixtures are synthetic and not Māori source data | 2026-07-16 |
| Licensing and attribution | Erdos, independent data-governance panel | Pass for synthetic-only; production blocked | Dataset card, source-specific rights rule, and unresolved-marker validation | 2026-07-16 |
| Removal and appeal | Wegener, independent operations panel | Pass for synthetic-only; production blocked | `docs/removal-appeal.md` and `.github/ISSUE_TEMPLATE/data-removal.yml`; no production contact implied | 2026-07-16 |
| Threat model and abuse cases | Kepler, independent security panel | Pass for synthetic-only after controls; production blocked | HF target allowlists, pinned publication dependencies, recursive privacy gate; production threat-model sign-off pending | 2026-07-16 |
| Human owner approval | Accountable owner narrative record | Approved in principle only; no production release | Decisions 1-9 are owner direction; gate remains `synthetic-only` until a signed production release record exists | 2026-07-16 |

## Release rule

Approval requires all seven rows to be complete and the gate file to be updated
by the accountable owner. A partial approval must leave production publication
blocked and may only authorize explicitly bounded synthetic or redacted outputs.
