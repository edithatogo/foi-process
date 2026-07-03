# Open New Zealand Regulatory Guidance Corpus

## Purpose

The Open New Zealand Regulatory Guidance Corpus is a bounded source-inventory and ingestion-concept track for regulatory guidance, policy statements, interpretative notes, codes of practice, and enforcement-response guidelines published by New Zealand regulators, government departments, and statutory bodies.

It is a distinct corpus slice because regulatory guidance has different publication patterns, rights characteristics, update cadences, and cross-reference structures from primary legislation, case law, parliamentary debates, or social-media communications. It is also the primary evidence surface for Track 12 policy-to-authority retrieval benchmarks and Track 16 citation graph / retrieval evaluation.

## Numbering conflict note

The Sourceright product `conductor/tracks.md` assigns **Conductor Track 16** to *"Journal workflow integrations"* (completed). The root Legal NZ `task_plan.md` and `swarm-orchestration-plan.md` assign **root Task Plan Track 16** to *"Citation Graph, Benchmarks, Retrieval Evaluation"* (not started; assigned to `nlp-policy-nz`). This document is written as **root Task Plan Track 16.1** — a sub-track of the root Task Plan Track 16 that inventories the regulatory-guidance source base required for citation-graph and benchmark work. It also overlaps with **root Task Plan Track 18** (*Regulatory & Government Publications Corpus*, assigned to `sm-govt-nz`) and should feed its source inventory into that track when Track 18 begins implementation.

## Owning repositories

- **Root `legal-nz`**: corpus identity, source-to-repo map, release-path coordination, evidence recording, and this source inventory.
- **`sm-govt-nz`**: primary implementation repo for regulatory-guidance ingestion, normalisation, rights handling, and publication workflows.
- **`nlp-policy-nz`**: benchmark slices, policy-to-authority retrieval tasks, citation-graph prototypes, and evaluation contracts that consume regulatory-guidance text.
- **`corpus-law-nz`**: legislation cross-reference enrichment where regulatory guidance cites Acts, regulations, or secondary legislation.
- Do not implement corpus builders, scrapers, benchmark runners, or publication workflows in the root repo.

## Source inventory

The following table records every priority regulator identified for this corpus. All URL patterns are illustrative based on known NZ government web-publishing conventions; no scraping or URL fetching was performed.

| Regulator | Document Types | URL Pattern | Update Cadence | Rights Notes | Expected Metadata Fields |
|---|---|---|---|---|---|
| **Commerce Commission** (comcom.govt.nz) | Regulatory decisions, market studies, guidelines, consumer fact sheets, competition enforcement responses, pricing determinations | `comcom.govt.nz/__data/assets/pdf_file/...`, `comcom.govt.nz/regulated-industries/...` | Rolling; decisions published as made; guidelines reviewed periodically (1–3 yr) | Crown copyright; content typically reusable under NZGOAL; check individual PDF for licence mark | Regulator, document_type, title, date_issued, date_updated, URL, file_format, subject_topics, legislation_cited, decision_number, status, provenance_checksum |
| **Financial Markets Authority** (fma.govt.nz) | Regulatory guides, interpretation guidelines, monitoring reports, enforcement outcomes, investor warnings, class exemptions, consultation papers, policy decisions | `fma.govt.nz/library/...`, `fma.govt.nz/regulatory-guides/...` | Rolling; regulatory guides updated as market practices change; enforcement outcomes as published | Crown copyright; most documents published under FMA Information Release Policy; verify per-document licence | Regulator, document_type, title, date_published, date_effective, URL, file_format, reference_number, subject_matter, legislation_cited, status, provenance_checksum |
| **Privacy Commissioner** (privacy.org.nz) | Guidance notes, case notes, codes of practice, opinions, decisions, investigation reports, compliance advice, good-practice guides | `privacy.org.nz/publications/...`, `privacy.org.nz/assets/...` | Rolling; codes reviewed statutorily; guidance updated as technology evolves | Crown copyright; Privacy Act 2020 materials generally reusable under NZGOAL; case notes may be de-identified | Regulator, document_type, title, date_issued, date_reviewed, URL, file_format, ipc_reference, legislation_cited, subject_topic, status, provenance_checksum |
| **Ombudsman** (ombudsman.parliament.nz) | Investigation opinions, good-governance guides, official information practice guides, complaint-handling resources, thematic reports | `ombudsman.parliament.nz/resources/...`, `ombudsman.parliament.nz/assets/...` | Rolling; opinions published as concluded; guides updated periodically (2–4 yr) | Crown copyright; OIA/Ombudsman Act materials published for public use; opinions contain de-identified complaint details | Regulator, document_type, title, date_issued, URL, file_format, opinion_reference, legislation_cited, subject_topic, case_id, status, provenance_checksum |
| **Office of the Privacy Commissioner** (privacy.org.nz) | (Same website as Privacy Commissioner; entity distinction noted per user request.) | — | — | — | — |
| **Department of Internal Affairs** (dia.govt.nz) | Policy guidance, regulatory stewardship statements, gambling/gaming materials, AML/CFT guidance, civil-registration guidance, information-management standards | `dia.govt.nz/...`, `register.realservice.govt.nz/...` | Rolling; statutory guidance updated with legislative changes; stewardship cycle 3–5 yr | Crown copyright; NZGOAL default; verify AML/CFT and gambling-sector materials for redistribution restrictions | Regulator, document_type, title, date_published, date_reviewed, URL, file_format, portfolio, legislation_cited, subject_topic, status, provenance_checksum |
| **MBIE** (mbie.govt.nz) | Sector guidance, policy papers, regulatory impact statements, fair-trading guidance, employment relations guidance, building/housing guidance, energy policy docs | `mbie.govt.nz/assets/...`, `mbie.govt.nz/...` | Rolling; sector guidance updated as policy develops; RIS published per legislative cycle | Crown copyright; NZGOAL default; most reusable with attribution; verify per-document licence | Regulator, document_type, title, date_published, URL, file_format, portfolio_sector, legislation_cited, policy_number, target_audience, status, provenance_checksum |
| **Ministry for the Environment** (mfe.govt.nz) | Policy guidance, environmental standards, emission-reduction plans, waste minimisation guidance, climate-change guidance, fresh-water policy, RMA guidance, consultation docs | `environment.govt.nz/publications/...`, `mfe.govt.nz/data/assets/pdf_file/...` | Rolling; policy guidance updated with legislative changes; state-of-environment reporting 3–5 yr | Crown copyright; NZGOAL default; RMA/CMA materials generally open-government; verify third-party content | Regulator, document_type, title, date_published, date_updated, URL, file_format, portfolio, legislation_cited, subject_topic, status, provenance_checksum |
| **Ministry of Health** (health.govt.nz) | Clinical guidance, service guidelines, operational-policy frameworks, public-health guidance, pharmaceutical policy, disability-sector guidance, Maaori/Pacific health strategy | `health.govt.nz/publications/...`, `health.govt.nz/assets/...` | Rolling; clinical guidance updated as evidence evolves; policy frameworks reviewed 3–5 yr | Crown copyright; NZGOAL default; some clinical guidance includes third-party copyrighted content | Regulator, document_type, title, date_published, date_reviewed, URL, file_format, portfolio, legislation_cited, subject_topic, clinical_domain, status, provenance_checksum |
| **Ministry of Justice** (justice.govt.nz) | Policy guidance, court/tribunal practice guides, civil-justice policy, sentencing/corrections guidance, criminal-justice sector guidance, RIS, public legal-education resources | `justice.govt.nz/about/publications/...`, `justice.govt.nz/assets/...` | Rolling; practice guides updated as rules/procedure change; policy per work programme | Crown copyright; NZGOAL default; court practice guides may have specific redistribution notes | Regulator, document_type, title, date_published, date_effective, URL, file_format, portfolio, legislation_cited, practice_note_reference, subject_topic, status, provenance_checksum |
| **NZ Transport Agency — Waka Kotahi** (nzta.govt.nz) | Regulatory policies, rules, standards, guidelines, codes of compliance, vehicle-certification guidance, road-safety policy, investment guidance, land-transport guidance, consultation docs | `nzta.govt.nz/resources/...`, `nzta.govt.nz/assets/...` | Rolling; rules/standards reviewed on statutory cycle (3–5 yr); operational guidance as needed | Crown copyright; NZGOAL default; verify specific third-party technical standards | Regulator, document_type, title, date_published, date_reviewed, URL, file_format, portfolio, legislation_cited, subject_topic, standard_reference, status, provenance_checksum |
| **Transport Accident Investigation Commission** (taic.org.nz) | Investigation reports, safety recommendations, safety studies, submission responses, research publications, annual safety reports | `taic.org.nz/investigation/...`, `taic.org.nz/reports/...` | Investigation reports published as completed (1–3 per year by sector); safety studies periodic | Crown copyright; TAIC reports published under TAIC Act 1990; generally reusable with attribution | Regulator, document_type, title, date_published, URL, file_format, investigation_number, transport_mode, safety_recommendations, status, provenance_checksum |

## Rights classification per source

All twelve listed regulators publish under Crown copyright. The default reuse posture is **NZGOAL (New Zealand Government Open Access and Licensing framework)** — version 2.0 or earlier — which permits reproduction, distribution, and adaptation with attribution, unless a specific document carries a third-party copyright or a different licence statement.

| Classification | Count | Sources |
|---|---|---|
| **NZGOAL (presumed)** | 11 | Commerce Commission, FMA, Privacy Commissioner, Ombudsman, DIA, MBIE, MfE, MoH, MoJ, NZTA, TAIC |
| **NZGOAL per-document verification required** | 1 | Office of the Privacy Commissioner (same site as Privacy Commissioner) |
| **NZGOAL with third-party content caveat** | 3 | MoH (clinical guidelines), NZTA (technical standards), Commerce Commission (commercially sensitive data) |
| **De-identification required before redistribution** | 2 | Privacy Commissioner (case notes), Ombudsman (investigation opinions) |
| **Practice-note or procedure-specific caveat** | 1 | Ministry of Justice (court practice guides) |

**Overarching rule:** Never assume blanket licence from the NZGOAL default. Every ingested document must carry a per-document rights note populated from the source page, PDF metadata, or explicit licence statement. Where no licence is visible, classify as `rights_review_required`.

## Schema recommendations

The Regulatory Guidance Corpus should share a base record contract with the other Legal NZ corpus tracks, then add guidance-specific fields.

### Base fields (inherited from Open New Zealand Legal Corpus — Track 13)

| Field | Purpose |
|---|---|
| `version_id` | Corpus release or schema version |
| `document_id` | Stable source-derived document identifier |
| `type` | Document category (use `"regulatory_guidance"` for this corpus slice) |
| `jurisdiction` | New Zealand jurisdiction marker (use `"nz"`) |
| `source` | Source system or repository identifier |
| `collection` | Source collection or corpus slice name |
| `mime` | Original or normalized content media type |
| `date` | Source document publication or effective date |
| `title` | Human-readable title |
| `url` | Canonical public URL |
| `when_collected` | Collection timestamp |
| `text` | Normalized text approved for the export visibility class |
| `rights` | Source-specific rights note (never inherited) |
| `provenance` | Machine-readable acquisition and transform lineage |
| `source_checksum` | Checksum of source or normalized input |
| `redaction_status` | Public, gated, redacted, excluded, or review-required |

### Guidance-specific extension fields

| Field | Purpose | Example values |
|---|---|---|
| `regulator` | Publishing regulator or agency name | `"Commerce Commission"`, `"Ministry for the Environment"` |
| `guidance_type` | Specific guidance document class | `"Interpretation_guideline"`, `"Code_of_practice"`, `"Enforcement_response"`, `"Regulatory_decision"`, `"Policy_statement"`, `"Practice_guide"`, `"Investigation_report"`, `"Case_note"`, `"Fact_sheet"`, `"Consultation"` |
| `guidance_reference` | Regulator-specific reference number | FMA guide number, TAIC investigation number, Ombudsman opinion reference |
| `legislation_cited` | Array of Act/regulation short titles cited | `["Privacy Act 2020", "Health Information Privacy Code 2020"]` |
| `subject_topics` | Array of policy or domain topics | `["fair_trading", "credit_contracts", "privacy_breach"]` |
| `target_audience` | Intended reader audience | `["business", "consumer", "practitioner", "regulated_entity", "public"]` |
| `status` | Regulatory currency status | `"current"`, `"superseded"`, `"draft"`, `"withdrawn"`, `"under_review"` |
| `supersedes` | Document ID or title of earlier version | Reference to previous guidance document |
| `superseded_by` | Document ID or title of superseding version | Reference to replacement guidance document |
| `date_effective` | Date the guidance takes effect | ISO 8601 date |
| `date_reviewed` | Date of scheduled or last review | ISO 8601 date |
| `portfolio` | Ministerial portfolio or regulatory domain | `"environment"`, `"health"`, `"justice"`, `"transport"`, `"commerce"`, `"employment"` |

### Publication and archive fields (shared with Track 13)

| Field | Purpose |
|---|---|
| `hf_dataset_id` | Hugging Face dataset identifier |
| `zenodo_deposition_id` | Zenodo staging or release record |
| `osf_project_id` | OSF project or component |
| `doi` | Released DOI when available |
| `release_tag` | Git or dataset release tag |
| `dataset_card_version` | Dataset card version used for publication |
| `source_archive_visibility` | Public, private, gated, or not-published archive state |

## Relationship to other tracks

| Track | Relationship |
|---|---|
| **Track 11** (Hugging Face Namespace) | Controls HF dataset naming, dataset cards, token hygiene, private/gated source-archive visibility, and DOI/archive continuity for this corpus when published. |
| **Track 12** (Isaacus Legal AI Alignment) | Consumes regulatory-guidance text for policy-to-authority retrieval benchmarks, embedding evaluation, and RAG prototypes. The `regulator`, `guidance_type`, `legislation_cited`, and `subject_topics` fields are primary entry points for benchmark task definition. |
| **Track 13** (Open NZ Legal Corpus) | This corpus is a source slice feeding the umbrella Legal Corpus. The base field contract is inherited from Track 13. Umbrella release orchestration must incorporate regulatory-guidance records alongside legislation, parliamentary, and case-law records. |
| **Track 14** (Open NZ Parliament Corpus) | Parliament may debate or amend the regulatory framework agencies administer. Regulatory-guidance records may link to Hansard debates through `legislation_cited` and portfolio mapping. |
| **Track 15** (Legislative History) | Regulatory guidance often interprets specific Acts or regulations. Bills and legislative-history context enriches `legislation_cited` cross-references. |
| **Track 18** (Regulatory & Government Publications — root Task Plan track) | This source inventory is the primary input for Track 18 when it begins implementation in `sm-govt-nz`. Track 16.1 identifies and describes the sources; Track 18 owns ingestion, normalisation, and publication code. |
| **Track 21** (DigitalNZ Discovery Layer) | DigitalNZ/National Library discovery can help identify regulatory publications (e.g., NZ Gazette notices, Parliamentary Papers containing regulatory stewardship submissions) for source triage and rights review. |

## Release phases

| Phase | Description | Owning repo(s) | Depends on |
|---|---|---|---|
| **Phase 1** | Document corpus identity, source authority, source-update cadence, rights notes, and source inventory (this document). | Root `legal-nz` | — |
| **Phase 2** | Produce small local sample of regulatory-guidance metadata (titles, URLs, regulator, dates) without full-text ingestion or scraping. Validate schema coverage and rights classification. | `sm-govt-nz` | Phase 1 |
| **Phase 3** | Add normalised full-text for priority regulators beginning with highest-Track-12-relevance sources (Commerce Commission, FMA, MBIE, MfE). Preserve provenance, source checksums, and per-document rights notes. | `sm-govt-nz` | Phase 2, Track 11 HF gates |
| **Phase 4** | Publish benchmark-ready slices for policy-to-authority retrieval, regulator-guidance retrieval, and legislation-to-guidance linking through `nlp-policy-nz`. | `nlp-policy-nz` | Phase 3, Track 12 alignment |
| **Phase 5** | Stage private Hugging Face dataset for the regulatory-guidance corpus slice after Track 11 naming, token, dataset-card, visibility, viewer/parquet/Croissant, and source-archive gates are cleared. | `sm-govt-nz`, root coordination | Phase 4, Track 11 |
| **Phase 6** | Promote public or gated release only after rights/provenance review, per-document licence verification, source-specific blockers, and archival mapping (Zenodo, OSF, DOI) are complete. | `sm-govt-nz`, root coordination | Phase 5, Track 13 umbrella release |
| **Phase 7** | (Future) Create `open-new-zealand-regulatory-guidance-corpus` only if regulatory-guidance release orchestration becomes independent product code with its own tests, release cycle, and API or package surface. | New repo (if warranted) | Phase 6 |

## Guardrails

- Do not scrape, fetch, or download content from regulator websites during root coordination. All ingestion belongs in `sm-govt-nz` and must follow that repo's CLI-first tooling and source-update policies.
- Do not assume NZGOAL applies to every document. Per-document rights verification is required before any public redistribution.
- Treat documents with de-identified personal information (Ombudsman opinions, Privacy Commissioner case notes) as review-required: verify that de-identification is adequate for corpus-level redistribution.
- Preserve regulator-assigned reference numbers and status fields (`current`, `superseded`, `withdrawn`) so downstream citation graphs and benchmarks reflect the correct regulatory point-in-time.
- Keep private source archives (raw PDFs, internal metadata) separate from public normalized text exports.
- Feed this source inventory into Track 18 when that track begins active implementation in `sm-govt-nz`.
- Do not commit, push, upload, use Chrome, edit `.env`, or access external services from this root coordination artifact.

## Local-only status

This document is a root coordination artifact created 2026-06-15. It does not create a dataset, publish a release, scrape regulator websites, access Chrome, edit `.env` files, commit, push, upload, or mutate external services.

Open external gates:
- Hugging Face staging or publication (Track 11).
- Zenodo or OSF archive mutation (Track 11).
- GitHub push, release, or Actions verification (Track 10).
- Credentialed or rate-limited regulator website access.
- Browser-profile or Chrome-gated acquisition.
- Per-document rights review for documents with third-party content or de-identified material.
- Phase transitions beyond Phase 1 require owning-repo task assignment and Track 10/11 gate clearance.
