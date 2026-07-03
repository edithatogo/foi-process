# Open New Zealand Government Social Media Corpus

## Root coordination status

- Track: Root swarm Track 15.
- Date recorded: 2026-06-15.
- Root role: concept, cross-repo mapping, release-path coordination, and evidence recording only.
- Owning implementation repo: `sm-govt-nz`.
- Benchmark coordination repo: `nlp-policy-nz`.
- Local-only boundary: no commit, push, upload, browser, `.env`, account, Chrome, or external-service mutation.

## Concept

The Open New Zealand Government Social Media Corpus is a distinct public-sector communications dataset for public posts and permitted metadata from New Zealand government accounts, agencies, ministers, regulators, courts, and public bodies.

It remains separate from the broader Open New Zealand Legal Corpus unless a post is a government legal or policy communication with a clear authority link. The separation is deliberate because platform terms, privacy handling, redistribution permissions, deletion/update status, and public-interest scope are different from legislation, case law, parliamentary, and regulatory-guidance corpora.

## Source-of-truth alignment

- `sm-govt-nz/conductor/tracks/govt_registry_20260614/spec.md` defines the central registry, historical archive, multi-remote sync, and syndication/mirroring roadmap.
- `sm-govt-nz/conductor/tracks/govt_registry_20260614/plan.md` records completed registry schema, compilation, SQLite export, deactivated-account archive seeding, and unified transparency dry-run work, with manual/live-post/mirror verification still open.
- `sm-govt-nz/conductor/tracks.md` keeps LinkedIn source-only and archive-only for now, and requires deferred outbound platform mirrors to be separate conductor tracks.
- Root `task_plan.md` limits the root repo to cross-repo mapping and release evidence.

## Dataset scope

Included material:

- Public posts from New Zealand government accounts where collection and redistribution are permitted.
- Platform-specific metadata, canonical URLs, media references, deletion/update status, collection manifests, and engagement snapshots only where platform terms permit.
- Agency, portfolio, jurisdiction, account type, provenance, source checksum, and rights metadata needed for auditability.
- Benchmark labels for public-sector policy retrieval, topic classification, chronology retrieval, and source-to-guidance linking.

Excluded material:

- Private messages.
- Comments or replies requiring special privacy treatment unless separately approved.
- Deleted, private, or unavailable content unless explicitly justified and legally reviewed.
- Material outside the documented public-interest scope.
- Outbound mirror posting or platform actions without separate approval and track ownership.

## Initial release path

1. Define public-interest scope, account inclusion rules, platform-by-platform terms posture, privacy/redaction policy, and retention/update handling.
2. Publish only a private staging dataset first, using synthetic rows or low-risk public samples to validate schema and release packaging.
3. Add normalized public-post exports and validation reports from `sm-govt-nz` after source-specific gates pass.
4. Build benchmark slices in `nlp-policy-nz` for policy-to-authority retrieval, public-sector topic classification, crisis/comms chronology retrieval, and source-to-guidance linking.
5. Promote to public or gated release only after platform-terms review, privacy review, dataset-card warnings, DOI/archive mapping, and explicit external-write approval.

## Initial dataset contract

Core fields:

- `version_id`
- `post_id`
- `platform`
- `account_id`
- `account_name`
- `account_type`
- `agency`
- `portfolio`
- `jurisdiction`
- `published_at`
- `collected_at`
- `url`
- `text`
- `language`
- `media_refs`
- `engagement_snapshot`
- `topic_tags`
- `rights`
- `platform_terms_note`
- `provenance`
- `source_checksum`
- `deleted_or_unavailable_status`
- `redaction_status`

Benchmark fields:

- `policy_topic`
- `linked_authority_id`
- `linked_legislation_id`
- `linked_guidance_id`
- `retrieval_split`
- `classification_label`
- `evaluation_notes`

## Release blockers

- Platform terms and redistribution posture are not yet signed off.
- Privacy, redaction, and deletion/update handling are not yet signed off.
- Public or gated Hugging Face, Zenodo, OSF, or other archive mutation remains externally gated.
- Live posting, mirror validation, and account-level actions remain externally gated.
- Commit, push, and GitHub Actions confirmation were intentionally not performed in this local-only pass.
