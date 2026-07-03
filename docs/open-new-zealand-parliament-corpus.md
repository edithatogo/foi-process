# Open New Zealand Parliament Corpus

## Purpose

The Open New Zealand Parliament Corpus is a distinct parliamentary text corpus for debates, sittings, members, bills, Acts, committees, questions, and parliamentary context. It is not just a slice of the broader Open New Zealand Legal Corpus.

The root `legal-nz` workspace owns the concept, release-path coordination, source-to-repo map, and evidence trail. Implementation belongs in the owning subrepos.

## Product boundary

The corpus should answer parliamentary-text questions that are not naturally answered by a legislation-only or general legal corpus:

- What was said in Parliament about a bill, Act, clause, policy, ministerial portfolio, committee, or public issue?
- Which debates, sittings, members, parties, electorates, and parliamentary terms are linked to a legislative or policy event?
- Which parliamentary source records support Hansard-to-bill, Act-to-debate, member-context, and parliamentary-history retrieval tasks?

## Owning repositories

- `corpus-nz-hansard`: Hansard ingestion, sitting metadata, member and speaker metadata, parliamentary terms, source archive manifests, and bill/Act debate linkage.
- `corpus-law-nz`: bill and Act linkage fields where needed.
- `nlp-policy-nz`: benchmark/export contracts, retrieval evaluation slices, DigitalNZ discovery probes, metadata crosswalks, and policy/RAG examples that consume the corpus.
- Root `legal-nz`: product definition, release orchestration notes, cross-repo mapping, and evidence only.

Do not implement corpus builders, scrapers, benchmark runners, publication workflows, or dataset-generation code in the root repo.

## Included source categories

Initial candidate categories:

- Hansard debates.
- Sitting metadata.
- Member and speaker metadata.
- Party, electorate, and parliamentary term context.
- Bill and Act links.
- Debate titles and parliamentary subjects.
- Committee records where available, permitted, and aligned with existing committee source tracks.
- Parliamentary questions where source rights, structure, and provenance are clear.
- Source archive manifests needed to reproduce or audit collection boundaries.

DigitalNZ and National Library discovery can help identify Parliamentary Papers, AJHR, Publications New Zealand records, and related metadata. These discovery records are not automatically corpus-ingestable full text.

## Exclusions and review-required material

Exclude or hold for review:

- Private, restricted, or credentialed source archives.
- Material whose metadata reuse rights do not clearly permit full-text redistribution.
- Images, manuscripts, newspapers, Papers Past material, Turnbull/TAPUHI material, Treaty/Maori governance-sensitive records, or third-party-hosted items until source-specific terms are confirmed.
- Any source requiring Chrome, account access, browser-profile access, OAuth, credentials, or external service mutation.

## Initial dataset contract

Stable fields:

- `version_id`
- `document_id`
- `source`
- `collection`
- `parliament`
- `session`
- `sitting_date`
- `speaker`
- `speaker_role`
- `party`
- `electorate`
- `bill_id`
- `act_id`
- `debate_title`
- `url`
- `when_collected`
- `text`
- `rights`
- `provenance`
- `source_checksum`
- `redaction_status`

Benchmark fields:

- `passage_id`
- `linked_authority_id`
- `question_type`
- `supporting_passage_ids`
- `retrieval_split`
- `evaluation_notes`

Publication and release fields:

- `hf_dataset_id`
- `zenodo_deposition_id`
- `osf_project_id`
- `doi`
- `release_tag`
- `dataset_card_version`
- `source_archive_visibility`

Recommended identifiers:

- `document_id` should remain stable across rebuilds.
- `version_id` should change when extracted text, metadata, rights, or provenance materially changes.
- Source checksums should identify the collected source artifact or normalized source record used for the release.

## Release path

Phase 1: Document corpus identity, source authority, source-update cadence, and rights notes.

Phase 2: Produce a small local sample from current `corpus-nz-hansard` outputs without private source archive leakage.

Phase 3: Add bill, Act, and member linkage fields as enrichment while keeping raw source text reproducible.

Phase 4: Publish benchmark-ready slices for Hansard-to-bill/Act retrieval and parliamentary context retrieval through `nlp-policy-nz`.

Phase 5: Stage a private Hugging Face dataset only after Track 11 naming, token, dataset-card, visibility, viewer/parquet/Croissant, and source-archive gates are cleared.

Phase 6: Promote a public or gated release only after rights/provenance review, source-specific blockers, and archival mapping are complete.

Phase 7: Create `open-new-zealand-parliament-corpus` only if parliamentary release orchestration becomes independent product code with its own tests, release cycle, and API or package surface.

## Track relationships

- Track 11: Controls Hugging Face naming, dataset cards, private/source archive visibility, DOI/archive continuity, and token hygiene.
- Track 12: Consumes parliamentary slices for NZ Legal RAG Bench, embedding benchmark tasks, Hansard-to-bill/Act retrieval, and parliamentary-context retrieval.
- Track 13: Consumes this corpus as the parliamentary component of the broader Open New Zealand Legal Corpus.
- Track 18: Shares bill, Act, legislative-history, and parliamentary-source linkage requirements.
- Track 21: Supplies DigitalNZ/National Library discovery metadata for source triage only unless rights review approves ingestion.

## Local-only status

This document is a root coordination artifact. It does not create a dataset, publish a release, access Chrome, edit `.env` files, commit, push, upload, or mutate external services.

Open external gates:

- Hugging Face staging or publication.
- Zenodo or OSF archive mutation.
- GitHub push, release, or Actions verification.
- Credentialed source archive access.
- Browser-profile or Chrome-gated acquisition.
- Rights review for non-Hansard or third-party records.
