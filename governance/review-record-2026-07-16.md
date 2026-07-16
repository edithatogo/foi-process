# Production Governance Review Record

Status: `pending_human_approval`

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

Require a named reviewer with relevant tikanga/data-governance authority and a
written decision covering custodianship, permitted reuse, hosting jurisdiction,
cross-border replication, retention, and withdrawal. Do not treat public source
status or owner approval alone as a substitute for this review.

### 7. Licensing and attribution

Separate the licence for code, schemas, synthetic fixtures, source records, and
derived artefacts. Require a per-source rights and attribution record, replace
all `to-be-recorded` licence values, and publish only when downstream reuse terms
are explicit.

### 8. Removal, correction, and appeal

Create one accountable owner, a public contact channel, response targets,
emergency takedown steps, correction and re-publication rules, revision
quarantine, rollback instructions, and a durable removal log covering GitHub,
Hugging Face, Zenodo, and GitHub Pages.

### 9. Threat model and release authority

Close the high-severity controls identified by the panel: allowlist HF targets,
narrow the HF token scope, pin token-bearing workflow dependencies, validate all
public artifacts recursively, and test re-identification and filter-differencing
risks. The accountable owner should then make the final release decision with a
scope, expiry/review date, and incident-response owner.

## Required decisions

| Gate | Reviewer and role | Decision | Evidence or conditions | Date |
| --- | --- | --- | --- | --- |
| Requester and third-party privacy |  |  | Confirm redaction, minimisation, and exclusion of raw request/attachment content |  |
| OCR and embedding amplification |  |  | Decide whether derived text or vectors are permitted and under what controls |  |
| Tikanga and Māori data governance |  |  | Confirm consultation, custodianship, access conditions, and appropriate use |  |
| Licensing and attribution |  |  | Confirm source terms, archive terms, attribution, and downstream licence |  |
| Removal and appeal |  |  | Confirm a reachable process, response owner, and takedown evidence trail |  |
| Threat model and abuse cases |  |  | Review re-identification, targeting, scraping, poisoning, and misuse scenarios |  |
| Human owner approval |  |  | Name the accountable owner for production publication and incident response |  |

## Release rule

Approval requires all seven rows to be complete and the gate file to be updated
by the accountable owner. A partial approval must leave production publication
blocked and may only authorize explicitly bounded synthetic or redacted outputs.
