# Open New Zealand Legal Corpus concept and implementation path

Date: 2026-06-15

Scope: root coordination only. Source-specific ingestion, validation, and release code stays in the owning corpus repositories.

## Product concept

The Open New Zealand Legal Corpus is an umbrella data product that brings together rights-reviewed New Zealand legal and legal-adjacent text from existing Legal NZ corpus repositories. It should start as a coordinated release contract from the root `legal-nz` workspace, not as a new implementation repository.

The useful comparator from the Open Australian Legal Corpus model is the public, multi-source legal corpus idea: one dataset identity, normalized records, source provenance, and platform-facing release metadata. The New Zealand implementation must differ where local law, source authority, publication rights, privacy, and cultural governance require stricter handling.

## Root source-of-truth reconciliation

Root `task_plan.md` defines Track 13 as `Open New Zealand Legal Corpus`.

Root `conductor/tracks.md` currently defines Conductor Track 13 as `uv, Pixi, and Lockfile Standardization`. This document therefore treats the requested Track 13 as the task-plan product track and does not renumber or rewrite the existing Conductor registry.

## Owning repositories

| Slice | Owning repo | Release posture |
|---|---|---|
| Legislation and legislative history | `corpus-law-nz` | Public where source terms and version provenance permit |
| Hansard and parliamentary text | `corpus-nz-hansard` | Public normalized text, with source archives separated where required |
| Medilegal or sensitive case material | `corpus-cases-medilegal-nz` | Private, gated, redacted, or excluded unless explicitly reviewed |
| Historical legal material | `hathi-nz` | Public-domain or rights-cleared only |
| Government social or policy communications | `sm-govt-nz` | Include only where authority, public-interest scope, platform terms, and privacy handling are documented |
| Benchmark and export contracts | `nlp-policy-nz` | Consumes corpus outputs for benchmark slices; does not own source ingestion |

## Dataset identity

Working dataset name: `open-new-zealand-legal-corpus`

Initial hosting target: Hugging Face dataset under the existing `edithatogo` namespace, staged privately first.

Archive mapping: Zenodo, OSF, and DOI records should be mapped through the existing Track 11 publication and archive gates before public promotion.

New GitHub repository: defer until the unified builder becomes more than packaging glue. Until then, root `legal-nz` owns product coordination and evidence only.

## Minimum record contract

Every public or gated export row should provide:

| Field | Purpose |
|---|---|
| `version_id` | Corpus release or schema version |
| `document_id` | Stable source-derived document identifier |
| `type` | Document category, aligned to the shared NZ corpus schema where possible |
| `jurisdiction` | New Zealand jurisdiction marker or more specific authority |
| `source` | Source system or source repository |
| `collection` | Source collection or corpus slice |
| `mime` | Original or normalized content media type |
| `date` | Source document date, version date, sitting date, or publication date |
| `citation` | Legal citation or canonical source citation where available |
| `title` | Human-readable title |
| `url` | Canonical public URL where available |
| `when_collected` | Collection timestamp |
| `text` | Normalized text approved for the export visibility class |
| `rights` | Source-specific rights note; never inherited from comparator corpora |
| `provenance` | Machine-readable source, transform, and release lineage |
| `source_checksum` | Checksum of source or normalized input used for reproducibility |
| `redaction_status` | Public, gated, redacted, excluded, or review-required status |

## New Zealand-specific extensions

Use these fields when applicable:

| Field | Applies to |
|---|---|
| `nz_source_authority` | Agency, court, Parliament, regulator, library, archive, or publisher |
| `legislation_version` | Legislation and legislative history |
| `bill_id` | Bills, debates, submissions, committee reports, and legislative links |
| `act_id` | Acts and linked parliamentary material |
| `hansard_sitting_date` | Hansard and parliamentary debates |
| `parliament` | Parliamentary term or parliament number |
| `court` | Court or tribunal decisions |
| `neutral_citation` | Case law |
| `report_series` | Reported or archival case collections |
| `matter_domain` | Domain classification for sensitive or gated material |
| `te_reo_or_bilingual_status` | Te reo Maori, bilingual, or language-governance marker |

## Publication metadata

Release orchestration should track:

| Field | Purpose |
|---|---|
| `hf_dataset_id` | Hugging Face dataset identifier |
| `zenodo_deposition_id` | Zenodo staging or release record |
| `osf_project_id` | OSF project or component |
| `doi` | Released DOI when available |
| `release_tag` | Git or dataset release tag |
| `dataset_card_version` | Dataset card version used for publication |
| `source_archive_visibility` | Public, private, gated, or not-published archive state |

## Implementation path

1. Draft the corpus card and schema specification in root coordination docs, using the Open Australian Legal Corpus only as a conceptual comparator.
2. Map source slices to existing owning repos and record rights, provenance, and release posture per slice before any unified export.
3. Produce a small local sample from existing corpus outputs only after each owning repo has a safe public or gated export artifact.
4. Stage a private Hugging Face dataset and validate viewer, parquet, metadata tags, Croissant output, and dataset-card clarity.
5. Split public, gated, redacted, and excluded material explicitly. Do not let private source archives leak into public normalized text.
6. Map release records to GitHub, Hugging Face, Zenodo, OSF, and DOI surfaces after Track 11 archive gates are clear.
7. Promote the first public release only after source-specific rights review, legal/provenance review, and platform publication checks.
8. Create a new `open-new-zealand-legal-corpus` repo only if cross-repo builder code becomes a maintained implementation surface.

## Guardrails

- Do not assume the Open Australian Legal Corpus licence or redistribution posture applies to New Zealand sources.
- Do not publicize medilegal, private, suppressed, sensitive, or uncertain-rights material without explicit review.
- Keep private source archives separate from public normalized exports.
- Keep source-specific ingestion in source-specific repos.
- Preserve stable IDs and checksums so benchmarks, embeddings, and DOI releases remain reproducible.
- Treat te reo Maori, tikanga, Treaty, and cultural-governance considerations as distinct from ordinary copyright review where source scope requires it.

## Current local-only status

This concept path is ready for review as a root coordination artifact. No implementation repository was modified, no publication surface was accessed, and no external service was mutated.
