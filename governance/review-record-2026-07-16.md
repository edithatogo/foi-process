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
