# Open New Zealand Treaty and Māori Law Corpus

## Governance-first concept status

This root note opens the Track 20 concept as a bounded local-only coordination artifact. It does not authorize scraping, ingestion, redistribution, publication, repo creation, external-service mutation, Chrome access, or subrepo implementation.

## Purpose

The concept is to assess whether a Treaty, Waitangi Tribunal, Māori Land Court, bilingual, and te reo Māori legal/policy corpus can be defined responsibly for the Legal NZ workspace.

The first deliverable is not a dataset. It is a governance and feasibility record that identifies source authority, tikanga and cultural-governance requirements, rights constraints, consultation needs, provenance standards, and safe owning-repo boundaries.

## Candidate source categories

- Treaty and Te Tiriti materials.
- Waitangi Tribunal reports and related public records where permitted.
- Māori Land Court and Māori Appellate Court materials where permitted.
- Bilingual legal, parliamentary, tribunal, policy, and government texts.
- Te reo Māori and English aligned legal/policy materials where alignment is source-supported and culturally appropriate.
- Historical Treaty, land, policy, and public-administration records discovered through rights-reviewed source inventories.

## Non-goals for the opening phase

- No scraping or harvesting.
- No dataset publication or staging upload.
- No public or private Hugging Face, Zenodo, OSF, GitHub, or registry mutation.
- No Chrome, account, credential, OAuth, or browser-profile work.
- No `.env` edits or secret discovery.
- No new repository.
- No subrepo implementation changes.

## Governance questions before implementation

- Which sources are authoritative enough for legal, historical, and cultural use?
- Which materials require tikanga, iwi/hapū, community, tribunal, court, or institutional consultation before use?
- Which materials are public to read but not appropriate or licensed for redistribution?
- Which materials need gated, metadata-only, citation-only, or exclusion treatment?
- How should te reo Māori, bilingual, and translation/alignment records preserve source context, language status, and provenance?
- What redaction, sensitivity, suppression, or withdrawal process is required?
- Which future tasks belong in `nlp-policy-nz`, source corpus repos, or root coordination only?

## Initial ownership model

Root `legal-nz` owns umbrella coordination, risk framing, cross-track mapping, and evidence notes.

`nlp-policy-nz` should own any future governance schema prototypes, rights classification experiments, benchmark-policy implications, and cross-corpus policy analysis once explicitly assigned.

Source-specific ingestion, if ever approved, must stay with the source-owning corpus repo and must be opened as a separate bounded task with source-specific rights evidence.

## Initial phase gates

- Phase 0: Keep Track 20 as governance-first and local-only.
- Phase 1: Build a candidate-source and governance-requirements inventory without scraping.
- Phase 2: Create a rights and cultural-governance classification draft.
- Phase 3: Decide whether any source-specific read-only probes are appropriate.
- Phase 4: Only after explicit approval, open owning-subrepo tasks for prototypes.
- Phase 5: Do not mark implementation-ready until governance approval, rights basis, consultation expectations, and exclusion rules are documented.

## Evidence from opening pass

- Source of truth consulted: root `task_plan.md` Track 20 and root `conductor/tracks.md`.
- Track 20 exists in the root swarm plan as a governance-first concept track.
- Root Conductor registry currently uses its own numbering where Conductor Track 20 is root remote/submodules; this note follows the root swarm Track 20 requested by the user.
- No external services, browser tools, environment files, commits, pushes, uploads, or subrepo files were touched.
