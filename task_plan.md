# Swarm Mission: All Conductor Workspaces

## Swarm Assignment
- **Primary implementation:** `General_Coder` on Cline with `deepseek-v4-flash`.
- **Cross-repository integration:** `Codex_GPT55_Engineer` on Codex with `gpt-5.5`.
- **Parallel implementation:** `Xiaomi_MiMo_Code` on Xiaomi MiMo Code with `xiaomi-mimo-code`.
- **Schema architecture and compatibility review:** `Architect_Oracle`.
- **Chrome-gated work:** `Chrome_Operator` only when authenticated web UI, browser profile, screenshots, OAuth, Hugging Face web console, Zenodo web console, or similar browser-only surfaces are required.
- **Validation:** `Quality_Validator` after each phase and before any commit/push.

## Source of Truth
- Workspace inventory: `swarm-workspaces.yaml`.
- Root conductor registry: `conductor/tracks.md`.
- Subproject conductor registries:
  - `cli-legislation-nz/conductor/tracks.md`
  - `corpus-cases-medilegal-nz/conductor/tracks.md`
  - `corpus-law-nz/conductor/tracks.md`
  - `corpus-nz-hansard/conductor/tracks.md`
  - `hathi-nz/conductor/tracks.md`
  - `nlp-policy-nz/conductor/tracks.md`
  - `sm-govt-nz/conductor/tracks.md`

## Repository Ownership Model
- The root `legal-nz` workspace is an aggregation, coordination, orchestration, and evidence-mapping base.
- Do not implement corpus builders, scrapers, benchmark runners, API clients, model experiments, publication workflows, or dataset-generation code in the root repo unless the task is explicitly root orchestration.
- Implementation tasks must be assigned to the owning subrepo, committed in that subrepo, pushed from that subrepo, and checked against that subrepo's GitHub Actions.
- Root-only changes are limited to `task_plan.md`, `swarm-workspaces.yaml`, root conductor registry/status, cross-repo mapping documents, and orchestration manifests.
- If a track spans multiple subrepos, create separate subrepo tasks with separate commits and Actions checks; use the root only to coordinate dependencies and record evidence.
- Future standalone repos may be created only when the relevant track says the functionality has outgrown a subrepo and has its own release cycle.

## Subrepo Assignment Map
- `cli-legislation-nz`: user-facing CLI commands, stable public workflows, release/package commands, and any future `legal-nz benchmark`, `legal-nz embed`, or `legal-nz rag` command surface.
- `corpus-law-nz`: NZ legislation, regulations, secondary legislation, historical legislative slices, bills, amendments, versions, and legislative-history source ingestion.
- `corpus-nz-hansard`: Hansard, parliamentary debates, sitting/member metadata, Parliament corpus ingestion, and bill/Act debate linkage.
- `corpus-cases-medilegal-nz`: medilegal case-law subset only, with gated/private release posture unless separately cleared.
- `hathi-nz`: HathiTrust/public-domain/historical legal material and rights-cleared historical legal text.
- `nlp-policy-nz`: cross-corpus NLP, benchmarks, DigitalNZ discovery probes, schema crosswalks, citation graph prototypes, Haystack/RAG prototypes, embedding/reranking experiments, and policy/regulatory guidance prototypes.
- `sm-govt-nz`: government social media ingestion, normalization, validation, privacy/platform-terms handling, and public-sector communications corpus work.

## Execution Gates
- **No Chrome gate:** local schema generation, msgspec updates, tests, linting, documentation, and non-authenticated CLI checks.
- **Chrome gate:** browser-authenticated account checks, manual web-console verification, OAuth renewal, screenshots, and any action requiring the user's existing Chrome session.
- **External-write gate:** GitHub push, Hugging Face dataset mutation, Zenodo deposition mutation, OSF mutation, social-platform posting, `.env` synchronization, or account-setting changes require explicit approval before execution.
- **Granular delivery gate:** each task must be small enough to commit independently with a clear evidence note.
- **Task completion gate:** after each implemented task, review the local diff, commit only the files belonging to that task, push the branch, and check the relevant GitHub Actions run status.
- **Phase completion gate:** after each phase, perform a cross-task review, push any phase-summary/documentation commit, and confirm all relevant GitHub Actions are passing or record a specific blocker.
- **Track completion gate:** after each track, perform a final review, push the track-completion state, confirm GitHub Actions pass, and update the relevant conductor/progress/task-plan surface with evidence.
- **Repo-boundary gate:** commits, pushes, and CI checks must happen inside the owning repo for the task; never bundle unrelated parent-repo or sibling-repo changes.

## Track 1: Root legal-nz Conductor Registry
- [x] Task: Run all outstanding local, non-gated work in `conductor/tracks.md` using root swarm lanes.
  - Blocked items remain blocked when their plan requires manual sign-off, Chrome, account access, `.env`, commit, push, upload, Hugging Face, Zenodo, OSF, or other external-write gates.
  - Evidence: `conductor/tracks.md` records Tracks 1-9 complete and Track 10 in progress with Phase 3 blocked by external-write gates; `conductor/tracks/schema_unification_20260614/plan.md` records Phase 1/2 local completion and leaves manual verification unchecked.

## Track 2: cli-legislation-nz Conductor Registry
- [x] Task: Run all outstanding local, non-gated work in `cli-legislation-nz/conductor/tracks.md` using the root swarm control plane.
  - The subproject has no local swarm files; use `swarm-workspaces.yaml` and the root `all_conductor` preset.
  - Evidence: `cli-legislation-nz/conductor/status.md` separates active preparation tracks from release/submission gates; publishing, deployment, package submission, registry submission, Docker/GHCR, Homebrew, and repository/package rename work remain external gates.

## Track 3: corpus-cases-medilegal-nz Conductor Registry
- [x] Task: Run all outstanding local, non-gated work in `corpus-cases-medilegal-nz/conductor/tracks.md`.
  - External publication, registry, Hugging Face, Zenodo, OSF, GitHub push, or account mutation remains gated.
  - Evidence: `corpus-cases-medilegal-nz/progress.md` records the multi-source local pipeline active with 98/98 tests passing; remaining publication, registry, Hugging Face, Zenodo, OSF, GitHub push, and account mutations stay gated.

## Track 4: corpus-law-nz Conductor Registry
- [x] Task: Run all outstanding local, non-gated work in `corpus-law-nz/conductor/tracks.md`.
  - Full-corpus bootstrap, live sync, publication, GitHub, Hugging Face, Zenodo, and secret-dependent steps remain gated unless explicitly approved.
  - Evidence: `corpus-law-nz/progress.md` records local full-corpus bootstrap research and workflow state; remaining batch execution, live sync, publication, GitHub, Hugging Face, Zenodo, and secret-dependent actions are gated.

## Track 5: corpus-nz-hansard Conductor Registry
- [x] Task: Run all outstanding local, non-gated work in `corpus-nz-hansard/conductor/tracks.md`.
  - Browser-protected acquisition, HathiTrust OAuth, live publication, GitHub, Hugging Face, Zenodo, OSF, and account mutations remain gated.
  - Evidence: `corpus-nz-hansard/progress.md` records member-identity research and blocker status; browser-protected acquisition, HathiTrust OAuth, live publication, GitHub, Hugging Face, Zenodo, OSF, and account mutations remain gated.

## Track 6: hathi-nz Conductor Registry
- [x] Task: Run all outstanding local, non-gated work in `hathi-nz/conductor/tracks.md`.
  - OAuth, HathiTrust downloads requiring credentials, live Hugging Face, Zenodo, GitHub, and archive mutations remain gated.
  - Evidence: `hathi-nz/progress.md` records Phases 1-4 complete with 143/143 tests passing and local validation complete; OAuth, credentialed HathiTrust downloads, live Hugging Face, Zenodo, GitHub, and archive mutations remain gated.

## Track 7: nlp-policy-nz Conductor Registry
- [x] Task: Run all outstanding local, non-gated work in `nlp-policy-nz/conductor/tracks.md` using the root swarm config.
  - The subproject has no local `swarm-config.yaml`; inherit the root `all_conductor` preset.
  - Evidence: root Track 10 validation records 31 focused `nlp-policy-nz` feature/storage tests passing and additive `PipelineRecord` fields verified; model, publication, account, and external-write work remains gated.

## Track 8: sm-govt-nz Conductor Registry
- [x] Task: Run all outstanding local, non-gated work in `sm-govt-nz/conductor/tracks.md` using the root swarm config.
  - Social platform posting, account access, live API writes, browser profile work, and credentials remain gated.
  - Evidence: root Track 10 validation records the `sm-govt-nz/.vale.ini` fix and shared lint validation; social platform posting, account access, live API writes, browser-profile work, and credentials remain gated.

## Track 9: Quality Gate and Evidence Reconciliation
- [x] Task: Run local validation slices for every workspace changed by swarm agents and record evidence in the relevant Conductor plan/progress surface.
  - Evidence: current Codex pass reran `python scripts\swarm_orchestrator.py --dry-run --once`, `python -m pytest tests/test_swarm_orchestrator.py tests/test_release_schemas.py tests/test_swarm_agent.py::TestResolveIdentity::test_subagents_yaml tests/test_swarm_agent.py::TestSystemPrompt tests/test_swarm_agent.py::TestYAML -q -p no:cacheprovider` (45 passed), and `python -m pytest tests/test_workspace_doctor_subprojects.py tests/test_markdown_lint.py -q -p no:cacheprovider` (35 passed).

## Track 10: External Gates Queue
- [x] Task: Queue but do not perform all Chrome, browser-profile, account, `.env`, commit, push, upload, Hugging Face, Zenodo, OSF, and social-platform mutation tasks.
  - Blocked: requires explicit user approval for each external-write or Chrome/account gate.

## Track 11: Hugging Face Namespace Organization and Optimization
- [~] Task: Create and maintain a cross-repo Hugging Face operating model for the `edithatogo` legal-NZ corpus family.
  - Scope: dataset naming, repo visibility, dataset cards, metadata tags, Croissant/parquet viewer health, multi-config layout, Xet/storage use, gated-source handling, secrets, token rotation, DOI continuity, and repo-to-dataset ownership.
  - Required mapping surface: `docs/external-platform-mapping.md`.
  - Required repository actions:
    - Standardize live corpus dataset IDs, legacy DOI dataset redirects/notes, and private source-archive datasets.
    - Keep one explicit `HF_TOKEN` secret per GitHub repo and document the matching token name without recording token values.
    - Ensure each corpus repo has a Hugging Face publication workflow or a documented blocker.
    - Verify dataset shells exist before upload workflows run.
    - Keep source archives private/gated unless a track explicitly approves public redistribution.
    - Validate published dataset cards, configs, splits, first rows, parquet exports, tags, and legal/provenance limitations after each upload.
  - Current status:
    - `edithatogo/nz-hansard-corpus`, `edithatogo/nz-hansard-source-archive`, `edithatogo/corpus-legislation-nz`, `edithatogo/corpus-legislation-nz-historical`, and legacy `edithatogo/nz-legislation-corpus` exist.
    - `edithatogo/corpus-cases-medilegal-nz` and `edithatogo/corpus-nz-hathi` were created as private dataset shells.
    - Fresh per-repo HF tokens were created and written to local env files and GitHub `HF_TOKEN` secrets on 2026-06-14.
  - Open blockers:
    - `corpus-nz-hansard` rerun needs source-archive token scope rechecked after the latest workflow failure at `Download source archive`.
    - `hathi-nz` HF sync is blocked by GitHub Actions Pixi cache-key setup.
    - `corpus-cases-medilegal-nz` manual dispatch is blocked by GitHub workflow-dispatch recognition despite the workflow YAML containing `workflow_dispatch`.

## Track 12: Isaacus Legal AI Alignment, Benchmarks, and Contribution Path
- [x] Task: Adopt the useful Isaacus patterns without prematurely creating another repository.
  - Owning subrepo: `nlp-policy-nz`.
  - Supporting subrepos: corpus repos provide benchmark-ready exports only when explicitly assigned by a phase task.
  - Root role: coordinate cross-repo dependencies and record evidence only.
  - Upstream surfaces reviewed on 2026-06-14:
    - `https://huggingface.co/isaacus`
    - `https://github.com/isaacus-dev/open-australian-legal-corpus-creator`
    - `https://github.com/isaacus-dev/open-australian-legal-embeddings-creator`
    - `https://github.com/isaacus-dev/isaacus-haystack`
    - `https://haystack.deepset.ai/`
  - Placement decision:
    - Keep corpus ingestion, provenance, and publication improvements inside the existing corpus repos (`corpus-law-nz`, `corpus-nz-hansard`, `corpus-cases-medilegal-nz`, `hathi-nz`, and `sm-govt-nz`) rather than creating a generic scraper repo.
    - Put benchmark adapters, model comparison scripts, embedding/reranking experiments, and Haystack pipeline prototypes in `nlp-policy-nz` first, because it is the natural cross-corpus NLP evaluation and policy-analysis workspace.
    - Put CLI-facing user workflows in `cli-legislation-nz` only when they expose stable commands for users, for example `legal-nz benchmark`, `legal-nz embed`, or `legal-nz rag`.
    - Create a new repo only if the Haystack/RAG layer becomes a reusable application or service with its own release cycle, deployment assets, API surface, or dependency graph. Working name: `legal-nz-rag-haystack`.
    - Do not fork Isaacus repos unless there is a specific upstream pull request, patch queue, or long-lived divergence to maintain.
  - Integration phases:
    - Phase 1: Inventory Isaacus schemas, benchmark task formats, document metadata conventions, chunking strategy, embedding defaults, and Haystack component boundaries.
    - Phase 2: Define a New Zealand legal benchmark export contract in `nlp-policy-nz` that can consume existing HF datasets and emit Legal RAG Bench/MLEB-style evaluation slices.
      - Adapt Australian-specific benchmark ideas rather than copying Australian benchmark content: replace Victorian/Australian source material with NZ legislation, NZ judgments, NZ parliamentary material, NZ regulator/policy texts, and NZ citation/procedure tasks.
      - Preserve comparable benchmark shapes where useful, including corpus passages, expert/curated questions, supporting-passage labels, retrieval metrics, long-form answer checks, classification tasks, and cross-model embedding/reranking comparisons.
      - Add NZ-specific task families: legislative provision retrieval, amendment/version retrieval, case-to-statute retrieval, Hansard-to-bill/Act retrieval, policy-to-authority retrieval, regulator guidance retrieval, and NZ citation normalization.
    - Phase 3: Add per-corpus benchmark-ready slices in the existing corpus repos, preserving source provenance, citation fields, jurisdiction, date/version, rights notes, and stable document IDs.
    - Phase 4: Build local embedding and retrieval baselines against `edithatogo` datasets using open embedding models first; compare Isaacus/Kanon API models only behind explicit credential and cost gates.
    - Phase 5: Prototype a Haystack RAG pipeline in `nlp-policy-nz` using a minimal adapter layer, then decide whether it stays as examples/tests or graduates to `legal-nz-rag-haystack`.
    - Phase 6: Identify contribution candidates upstream, such as NZ legal source support, benchmark task additions, metadata harmonisation, documentation corrections, or Haystack integration examples.
    - Phase 7: Evaluate fine-tuning only after benchmark baselines, licensing checks, compute/cost constraints, and dataset leakage controls are documented.
  - Guardrails:
    - Prefer benchmark adaptation and retrieval evaluation before model fine-tuning.
    - Treat paid/proprietary Isaacus API usage as gated until credentials, cost limits, and permitted use are explicit.
    - Keep legal/provenance metadata richer than the Australian corpus minimum so downstream users can filter by jurisdiction, source authority, version, and redistribution limits.
    - Do not mix public corpus exports with private source archives or gated datasets.
    - Keep HF dataset cards, Croissant/parquet viewer health, and DOI/archive mapping aligned with Track 11.

## Track 13: Open New Zealand Legal Corpus
- [~] Task: Create an `Open New Zealand Legal Corpus` concept and implementation path based on the useful parts of the Open Australian Legal Corpus model, adapted to NZ law, rights, provenance, and publication constraints.
  - Local-only update 2026-06-15: root concept and implementation path drafted in `docs/open-new-zealand-legal-corpus.md`.
  - Evidence: the draft preserves the root role as coordination/evidence only, keeps source-specific ingestion in existing repos, separates public/gated/private release states, and records the root source-of-truth conflict where `conductor/tracks.md` currently labels Conductor Track 13 as `uv, Pixi, and Lockfile Standardization`.
  - Owning implementation subrepos: `corpus-law-nz`, `corpus-nz-hansard`, `corpus-cases-medilegal-nz`, `hathi-nz`, and `sm-govt-nz` for their own source slices.
  - Coordination subrepo for benchmark/export contracts: `nlp-policy-nz`.
  - Root role: umbrella product definition, cross-repo mapping, release orchestration notes, and evidence only.
  - Recommendation:
    - Start as an umbrella corpus product coordinated from this root `legal-nz` workspace, not as a new repo immediately.
    - Keep source-specific ingestion in existing repos until the unified schema, dataset card, release contract, and DOI/archive strategy are stable.
    - Publish the first corpus as a Hugging Face dataset under the existing `edithatogo` namespace, with Zenodo/OSF archival mapping from Track 11.
    - Create a new GitHub repo only when the unified corpus builder becomes more than packaging glue. Working name: `open-new-zealand-legal-corpus`.
  - Candidate source repos:
    - `corpus-law-nz`: NZ legislation and historical legislative corpus slices.
    - `corpus-nz-hansard`: parliamentary debates and source archive-derived parliamentary text.
    - `corpus-cases-medilegal-nz`: restricted medilegal case corpus where licensing/privacy permits public or gated release.
    - `hathi-nz`: public-domain or rights-cleared historical NZ legal material.
    - `sm-govt-nz`: government social/policy communications only if provenance, terms, and public-interest scope are clear.
  - Initial dataset contract:
    - Stable fields: `version_id`, `document_id`, `type`, `jurisdiction`, `source`, `collection`, `mime`, `date`, `citation`, `title`, `url`, `when_collected`, `text`, `rights`, `provenance`, `source_checksum`, and `redaction_status`.
    - NZ-specific fields: `nz_source_authority`, `legislation_version`, `bill_id`, `act_id`, `hansard_sitting_date`, `parliament`, `court`, `neutral_citation`, `report_series`, `matter_domain`, and `te_reo_or_bilingual_status`.
    - Publication fields: `hf_dataset_id`, `zenodo_deposition_id`, `osf_project_id`, `doi`, `release_tag`, `dataset_card_version`, and `source_archive_visibility`.
  - Release phases:
    - Phase 1: Draft a corpus card and schema specification using OALC as the conceptual comparator, but with NZ-specific source authority, versioning, and rights language.
    - Phase 2: Generate a small benchmarkable sample from existing corpus outputs, with no private/gated source leakage.
    - Phase 3: Publish a private HF staging dataset and validate viewer, parquet conversion, metadata tags, and Croissant output.
    - Phase 4: Add public/gated split policy and map every source to GitHub, HF, OSF, and Zenodo records.
    - Phase 5: Promote a first public release only after legal/provenance review, source-specific blockers, and Track 11 HF organization gates are cleared.
    - Phase 6: If the release process requires cross-repo orchestration, create `open-new-zealand-legal-corpus` as the unifying builder/release repo and leave source ingestion in the existing source repos.
  - Benchmark relationship:
    - The corpus is the source-of-truth data product.
    - Track 12 consumes this corpus to produce NZ Legal RAG Bench/MLEB-style benchmark slices.
    - Fine-tuning datasets must be derived as separate, documented exports, not silently mixed into the canonical corpus.
  - Guardrails:
    - Do not imply the OALC licence applies to NZ source materials; each source needs its own rights note.
    - Do not publicize medilegal/private/gated text without explicit release review.
    - Keep private source archives separate from public normalized text.
    - Use stable IDs and checksums so benchmarks, embeddings, and DOI releases remain reproducible.

## Track 14: Open New Zealand Parliament Corpus
- [x] Task: Create an `Open New Zealand Parliament Corpus` concept and release path as a distinct parliamentary text corpus, not merely a slice of the broader legal corpus.
  - Owning subrepo: `corpus-nz-hansard`.
  - Supporting subrepo: `corpus-law-nz` for bill/Act linkage fields where needed.
  - Coordination subrepo: `nlp-policy-nz` for benchmark slices and retrieval tasks.
  - Root role: record cross-repo mapping and release evidence only.
  - Local-only coordination status: concept and release path recorded in `docs/open-new-zealand-parliament-corpus.md` on 2026-06-15; no commit, push, upload, browser, `.env`, account, subrepo implementation, or external-service mutation performed.
  - Recommendation:
    - Use `corpus-nz-hansard` as the source-specific ingestion and normalization repo.
    - Coordinate dataset identity, release mapping, HF/Zenodo/OSF records, and benchmark contracts from this root workspace.
    - Create a new repo only if parliamentary release orchestration becomes independent product code. Working name: `open-new-zealand-parliament-corpus`.
  - Scope:
    - Hansard debates, sitting metadata, member/speaker metadata, bill/Act links, parliamentary terms, committees where available and permitted, questions, debates, and source archive manifests.
    - Public normalized text as the main release product.
    - Private or gated source archives kept separate where source terms, size, or provenance require it.
  - Initial dataset contract:
    - Stable fields: `version_id`, `document_id`, `source`, `collection`, `parliament`, `session`, `sitting_date`, `speaker`, `speaker_role`, `party`, `electorate`, `bill_id`, `act_id`, `debate_title`, `url`, `when_collected`, `text`, `rights`, `provenance`, `source_checksum`, and `redaction_status`.
    - Benchmark fields: `passage_id`, `linked_authority_id`, `question_type`, `supporting_passage_ids`, `retrieval_split`, and `evaluation_notes`.
  - Release phases:
    - Phase 1: Document corpus identity, source authority, source-update cadence, and rights notes.
    - Phase 2: Produce a small HF staging dataset from the current Hansard pipeline without leaking private source archives.
    - Phase 3: Add bill/Act/member linkage fields as enrichment, keeping raw source text reproducible.
    - Phase 4: Publish benchmark-ready slices for Hansard-to-bill/Act retrieval and parliamentary context retrieval.
    - Phase 5: Promote public release only after HF viewer/parquet/Croissant checks, source archive mapping, and DOI/archive mapping are complete.
  - Relationship to other tracks:
    - Feeds Track 13 as the parliamentary component of the broader legal corpus.
    - Feeds Track 12 as a source for NZ Legal RAG Bench and embedding benchmark tasks.
    - Aligns with Track 11 for HF naming, cards, visibility, and DOI/archive continuity.
  - Evidence:
    - `docs/open-new-zealand-parliament-corpus.md` records the distinct corpus scope, source inclusion policy, schema contract, release phases, owning-repo boundaries, rights gates, Track 11/12/13/18/21 relationships, and external-write blockers.

## Track 15: Open New Zealand Government Social Media Corpus
- [x] Task: Create an `Open New Zealand Government Social Media Corpus` concept and release path as a distinct public-sector communications dataset.
  - Owning subrepo: `sm-govt-nz`.
  - Coordination subrepo: `nlp-policy-nz` for benchmark/classification/retrieval slices.
  - Root role: record cross-repo mapping and release evidence only.
  - Local-only coordination status: concept and release path recorded in `docs/open-new-zealand-government-social-media-corpus.md` on 2026-06-15; no commit, push, upload, browser, `.env`, account, or external-service mutation performed.
  - Recommendation:
    - Use `sm-govt-nz` as the source-specific ingestion, validation, and normalization repo.
    - Keep this separate from the legal corpus until public-interest scope, platform terms, privacy handling, and redistribution permissions are documented.
    - Create a new repo only if cross-platform release orchestration becomes independent product code. Working name: `open-new-zealand-government-social-media-corpus`.
  - Scope:
    - Public posts from NZ government accounts, agencies, ministers, regulators, and public bodies where collection and redistribution are permitted.
    - Platform-specific metadata, canonical URLs, engagement fields only where terms permit, media metadata, deletion/update status, and collection manifests.
    - Exclude private messages, comments requiring special privacy treatment, deleted/private content unless explicitly approved and legally justified, and any material outside the documented public-interest scope.
  - Initial dataset contract:
    - Stable fields: `version_id`, `post_id`, `platform`, `account_id`, `account_name`, `account_type`, `agency`, `portfolio`, `jurisdiction`, `published_at`, `collected_at`, `url`, `text`, `language`, `media_refs`, `engagement_snapshot`, `topic_tags`, `rights`, `platform_terms_note`, `provenance`, `source_checksum`, `deleted_or_unavailable_status`, and `redaction_status`.
    - Benchmark fields: `policy_topic`, `linked_authority_id`, `linked_legislation_id`, `linked_guidance_id`, `retrieval_split`, `classification_label`, and `evaluation_notes`.
  - Release phases:
    - Phase 1: Define public-interest scope, platform-by-platform terms posture, privacy/redaction policy, and account inclusion rules.
    - Phase 2: Publish a private HF staging dataset with synthetic or low-risk public samples first.
    - Phase 3: Add normalized public-post exports and validation reports from `sm-govt-nz`.
    - Phase 4: Build benchmark slices for policy-to-authority retrieval, public-sector topic classification, crisis/comms chronology retrieval, and source-to-guidance linking.
    - Phase 5: Promote public or gated release only after platform terms review, privacy review, dataset-card warnings, and DOI/archive mapping are complete.
  - Relationship to other tracks:
    - Feeds Track 13 only where posts are government legal/policy communications with clear authority linkage.
    - Feeds Track 12 as benchmark material for policy retrieval, classification, and grounded public-sector RAG.
    - Aligns with Track 11 for HF naming, cards, visibility, token/secrets hygiene, and archive continuity.
  - Evidence:
    - `sm-govt-nz/conductor/tracks/govt_registry_20260614/spec.md` establishes the registry, historical archive, multi-remote sync, and syndication/mirroring roadmap.
    - `sm-govt-nz/conductor/tracks/govt_registry_20260614/plan.md` shows registry schema, compilation, deactivation archive seeding, and unified transparency dry-run work, with manual/live-post/mirror gates still open.
    - `sm-govt-nz/conductor/tracks.md` keeps LinkedIn source-only/archive-only and defers outbound mirrors to separate tracks.

## Track 16: Open New Zealand Regulatory Guidance Corpus
- [ ] Task: Create an `Open New Zealand Regulatory Guidance Corpus` concept and staged implementation path.
  - Owning subrepo for prototype: `nlp-policy-nz`.
  - Future owning repo only if needed: `open-new-zealand-regulatory-guidance-corpus`.
  - Root role: coordination and evidence only.
  - Placement decision:
    - Prototype source inventory, schema, and benchmark adapters in `nlp-policy-nz`.
    - Keep any source-specific scrapers/adapters close to the relevant policy/regulator collection code until a stable cross-regulator package exists.
    - Create a new repo only when multi-regulator ingestion and release orchestration becomes substantial product code. Working name: `open-new-zealand-regulatory-guidance-corpus`.
  - Scope:
    - Regulator guidance, codes, enforcement policies, practice notes, consultation outcomes, policy statements, public determinations, and public compliance guidance.
    - Initial priority sources should be chosen for public access, stable URLs, clear reuse posture, and high legal/policy value.
  - Granular tasks:
    - Task 16.1: Create source inventory with regulator, document type, URL pattern, update cadence, rights note, and expected metadata fields.
    - Task 16.2: Define a normalized schema and dataset-card template.
    - Task 16.3: Build a small local sample from one low-risk regulator source.
    - Task 16.4: Add validation for required fields, stable IDs, provenance, and rights notes.
    - Task 16.5: Publish a private HF staging dataset only after local validation and external-write approval.
    - Task 16.6: Add benchmark slices for policy-to-authority retrieval and regulator-topic classification.
  - Phase gates:
    - After each task: review diff, commit, push, and check GitHub Actions in the owning repo.
    - After each phase: update progress evidence, push phase-summary commit, and confirm Actions pass or record a blocker.
    - After track completion: review, push, confirm Actions pass, and update Track 11/12/13 mapping where this corpus is consumed.

## Track 17: Open New Zealand Case Law Corpus
- [ ] Task: Create an `Open New Zealand Case Law Corpus` concept with rights-first staging.
  - Owning subrepo for broad schema/prototype: `nlp-policy-nz`.
  - Owning subrepo for medilegal subset: `corpus-cases-medilegal-nz`.
  - Future owning repo only if source permissions and release posture justify it: `open-new-zealand-case-law-corpus`.
  - Root role: coordination and evidence only.
  - Placement decision:
    - Keep `corpus-cases-medilegal-nz` focused on the existing medilegal subset and its own release constraints.
    - Prototype broader case-law schema and citation normalization in `nlp-policy-nz`.
    - Create a new repo only after source permissions, suppression/privacy handling, and public/gated release posture are clear. Working name: `open-new-zealand-case-law-corpus`.
  - Scope:
    - Public judgments and tribunal decisions where collection, normalization, and redistribution are permitted.
    - Court, tribunal, neutral citation, parties where safe/permitted, decision date, subject matter, linked legislation, suppression/privacy status, and source authority metadata.
  - Granular tasks:
    - Task 17.1: Inventory candidate sources and classify each as public, gated, blocked, or review-required.
    - Task 17.2: Define suppression, privacy, name-handling, and republication guardrails.
    - Task 17.3: Define canonical case metadata and NZ citation-normalization schema.
    - Task 17.4: Build a tiny local sample from a clearly permitted source.
    - Task 17.5: Add validation for citation, court/tribunal, date, URL, rights, and redaction status.
    - Task 17.6: Add benchmark slices for case-to-statute retrieval and citation normalization.
  - Phase gates:
    - After each task: review diff, commit, push, and check GitHub Actions in the owning repo.
    - After each phase: update progress evidence, push phase-summary commit, and confirm Actions pass or record a blocker.
    - After track completion: review, push, confirm Actions pass, and update Track 12/13 mapping.
  - Guardrails:
    - Do not publicize private, suppressed, sensitive, or uncertain-rights decisions.
    - Treat medilegal material as gated unless separately cleared.
    - Do not merge broad case-law work into `corpus-cases-medilegal-nz` if it would contaminate that repo's purpose or release posture.

## Track 18: Open New Zealand Bills and Legislative History Corpus
- [ ] Task: Create an `Open New Zealand Bills and Legislative History Corpus` that links bills, explanatory notes, SOPs, select committee material, Hansard, and enacted Acts.
  - Owning subrepo: `corpus-law-nz`.
  - Supporting subrepo: `corpus-nz-hansard` for debate linkage.
  - Coordination subrepo: `nlp-policy-nz` for benchmark slices.
  - Root role: coordination and evidence only.
  - Placement decision:
    - Use `corpus-law-nz` for legislation/bill/version ingestion.
    - Use `corpus-nz-hansard` for parliamentary debate linkage.
    - Coordinate the unified corpus product from the root workspace.
    - Create a new repo only if the release builder needs independent orchestration. Working name: `open-new-zealand-legislative-history-corpus`.
  - Scope:
    - Bills, bill versions, explanatory notes, supplementary order papers, select committee reports, Hansard debates, assent/enactment metadata, commencement information, and Act lineage.
  - Granular tasks:
    - Task 18.1: Define bill-to-Act/version lineage fields and stable IDs.
    - Task 18.2: Inventory source coverage and update cadence across legislation and parliamentary sources.
    - Task 18.3: Build a small lineage sample for one Act/bill family.
    - Task 18.4: Add link validation for bill IDs, Act IDs, dates, URLs, and source checksums.
    - Task 18.5: Add benchmark slices for legislative intent retrieval and amendment/version retrieval.
    - Task 18.6: Stage a private HF dataset after local validation and external-write approval.
  - Phase gates:
    - After each task: review diff, commit, push, and check GitHub Actions in the owning repo.
    - After each phase: update progress evidence, push phase-summary commit, and confirm Actions pass or record a blocker.
    - After track completion: review, push, confirm Actions pass, and update Track 12/13/14 mapping.

## Track 19: Open New Zealand Legal Citation Graph
- [ ] Task: Create an `Open New Zealand Legal Citation Graph` as a derived dataset linking authorities across legislation, cases, Hansard, bills, regulator guidance, government publications, and social media where appropriate.
  - Owning subrepo for prototype: `nlp-policy-nz`.
  - Supporting subrepos: source repos provide normalized authority records and citation-bearing exports only via assigned tasks.
  - Future owning repo only if graph releases, schema migrations, and graph export tooling become independent: `open-new-zealand-legal-citation-graph`.
  - Root role: coordination and evidence only.
  - Placement decision:
    - Prototype graph extraction and evaluation in `nlp-policy-nz`.
    - Keep raw source extraction in the existing source repos.
    - Create a new repo only when the graph has its own release process, schema migrations, graph exports, and evaluation suite. Working name: `open-new-zealand-legal-citation-graph`.
  - Scope:
    - Citation normalization, authority linking, source-to-source edges, provenance for each edge, confidence scores, extraction method, and release snapshots.
  - Granular tasks:
    - Task 19.1: Define graph node and edge schema.
    - Task 19.2: Define NZ citation normalization rules for legislation, cases, bills, Hansard references, and regulator materials.
    - Task 19.3: Build a small graph sample from legislation and Hansard links.
    - Task 19.4: Add validation for stable node IDs, edge provenance, confidence, and source checksums.
    - Task 19.5: Add export formats for JSONL and parquet; defer graph-database exports until needed.
    - Task 19.6: Add benchmark slices for authority-linking and citation-grounded retrieval.
  - Phase gates:
    - After each task: review diff, commit, push, and check GitHub Actions in the owning repo.
    - After each phase: update progress evidence, push phase-summary commit, and confirm Actions pass or record a blocker.
    - After track completion: review, push, confirm Actions pass, and update all consuming corpus/benchmark tracks.

## Track 20: Open New Zealand Treaty and Māori Law Corpus Governance Track
- [~] Task: Establish a governance-first concept track for Treaty, Waitangi Tribunal, Māori Land Court, bilingual, and te reo Māori legal/policy materials.
  - Owning subrepo for governance docs/schema prototypes: `nlp-policy-nz`.
  - Supporting subrepo: `corpus-nz-hansard` only for already-cleared Hansard-derived bilingual metadata experiments.
  - Root role: coordination and evidence only.
  - Placement decision:
    - Keep this as a governance and feasibility track first, not an implementation track.
    - Do not create a repo or public dataset until source authority, cultural governance, tikanga, rights, and community/stakeholder consultation requirements are explicit.
    - Prototype only metadata inventories or synthetic schemas unless implementation is separately approved.
  - Scope:
    - Treaty materials, Waitangi Tribunal reports where permitted, Māori Land Court materials where permitted, bilingual legal/government texts, te reo Māori/English alignment, and related public legal-policy documents.
  - Granular tasks:
    - Task 20.1: Inventory candidate source categories and identify governance requirements before source scraping.
    - Task 20.2: Define cultural, legal, and ethical guardrails.
    - Task 20.3: Define a metadata-only schema for feasibility assessment.
    - Task 20.4: Identify potential benchmark use cases without collecting sensitive or culturally restricted content.
    - Task 20.5: Prepare a decision memo on whether, when, and how to proceed.
  - Current local-only opening status:
    - Root coordination note opened at `docs/open-new-zealand-treaty-maori-law-corpus.md`.
    - This pass did not create a new repo, scrape sources, mutate subrepos, access Chrome, edit `.env`, commit, push, upload, or contact external services.
    - Implementation remains blocked until governance approval, source-specific rights, cultural/tikanga requirements, consultation expectations, and owning-subrepo task boundaries are documented.
  - Phase gates:
    - After each task: review diff, commit, push, and check GitHub Actions for documentation/schema-only changes.
    - After each phase: update progress evidence, push phase-summary commit, and record open governance questions.
    - After track completion: do not mark implementation-ready unless governance approval and source rights are documented.
  - Guardrails:
    - No scraping, public release, fine-tuning, or benchmark generation from this material without explicit approval.
    - Preserve te reo Māori and bilingual metadata accurately.
    - Treat cultural licence and community expectations as separate from copyright.

## Track 21: DigitalNZ, National Library, and Supplejack Discovery Layer
- [ ] Task: Explore and integrate DigitalNZ/National Library metadata as a discovery, triangulation, and source-expansion layer for the Open New Zealand corpus family.
  - Owning subrepo for API probes, source inventories, and metadata crosswalks: `nlp-policy-nz`.
  - Supporting subrepos: source-specific ingestion moves to `corpus-law-nz`, `corpus-nz-hansard`, `hathi-nz`, `corpus-cases-medilegal-nz`, or `sm-govt-nz` only after source selection and rights review.
  - Future owning repo only if a reusable DigitalNZ collector package is justified: `open-new-zealand-digitalnz-collector`.
  - Root role: coordination and evidence only.
  - Placement decision:
    - Prototype DigitalNZ API probes, source inventories, and metadata crosswalks in `nlp-policy-nz` first.
    - Add source-specific adapters to the owning corpus repo only after a source is selected for real ingestion.
    - Do not create a new repo initially; create `open-new-zealand-digitalnz-collector` only if DigitalNZ harvesting becomes a reusable cross-corpus package with its own tests, release cycle, and API/client abstractions.
  - Upstream surfaces reviewed:
    - `https://natlib.govt.nz/about-us/open-data/digitalnz-api`
    - `https://digitalnz.org/developers`
    - `https://digitalnz.org/developers/api-docs-v3`
    - `https://digitalnz.org/developers/digitalnz-metadata-dictionary`
    - `https://digitalnz.org/developers/api-examples-in-use`
    - `https://github.com/DigitalNZ`
    - `https://digitalnz.github.io/supplejack/`
    - `https://natlib.govt.nz/about-us/open-data/turnbull-metadata-via-digitalnz-api`
    - `https://natlib.govt.nz/about-us/open-data/publications-nz-metadata`
  - API findings:
    - DigitalNZ is primarily a metadata aggregator and pointer service, not a full-content host.
    - Public API access no longer requires an API key for basic public-content queries, but unauthenticated requests are rate limited and an API key is recommended for regular, high-volume, or application use.
    - Core endpoints are search records and get metadata for a specific record.
    - High-value metadata fields include `category`, `collection`, `content_partner`, `title`, `description`, `landing_url`, `thumbnail_url`, `creator`, `date`, `display_date`, `placename`, `rights`, `rights_url`, `usage`, `subject`, `format`, `identifier`, and `language`.
    - Documented filtering should use DigitalNZ metadata fields, for example `and[collection][]=TAPUHI` for Turnbull metadata; do not rely on unverified `primary_collection` parameters without an API test.
    - Supplejack is the open-source metadata aggregation stack behind DigitalNZ and is useful as an architectural reference for cross-source harvesting, schema mapping, enrichment, and public API surfacing.
  - Initial read-only probe evidence from 2026-06-14:
    - Query `Parliamentary Papers`: API reported 236447 matching records; sample titles included `Native and defence. Parliamentary papers`.
    - Query `AJHR`: API reported 89 matching records; sample titles included `Map showing Kauri-gum reserves, Auckland, N.Z. under "The Kauri-gum Industry Act, 1898" March 31st 1903`.
    - Query `New Zealand Gazette`: API reported 901371 matching records; sample titles included `The New Zealand Government gazette`.
    - Query `Waitangi Tribunal`: API reported 3974 matching records; sample titles included `Orakei report : report of the Waitangi Tribunal on the Orakei claim (Wai-9)`.
    - Query `Papers Past legislation`: API reported 249322 matching records; treat this as noisy discovery evidence, not corpus-ready legal text.
    - Query `New Zealand statutes`: API reported 125377 matching records; sample titles included `[Statutes of New Zealand] [electronic resource].`.
  - Corpus use cases:
    - Triangulate legal/parliamentary/historical records against existing source-specific corpora.
    - Discover missing source collections for the Open New Zealand Legal Corpus, Parliament Corpus, Legislative History Corpus, Treaty/Māori Law governance track, and Historical Legal Corpus work.
    - Harvest metadata-only inventories for source selection, rights review, and provenance mapping.
    - Use `landing_url`, `identifier`, `rights`, `rights_url`, `usage`, `content_partner`, and `collection` fields to route records to the proper source repo and release posture.
    - Use DigitalNZ/Papers Past date facets and metadata to build historical trend and coverage maps before any full-text ingestion.
  - Candidate source categories to investigate:
    - Parliamentary Papers, AJHR, and related parliamentary records.
    - New Zealand Gazette and government notices.
    - Historical statutes and law publications.
    - Turnbull/TAPUHI political, legal, public-administration, and Treaty-related manuscripts and images.
    - Publications New Zealand bibliographic metadata for legal, regulatory, parliamentary, and government publications.
    - Papers Past newspapers and periodicals as triangulation sources for historical legal events, public notices, debates, and legal terminology.
    - Waitangi Tribunal, Treaty, Māori Land, and bilingual public materials as governance-gated discovery only.
  - Rights and licensing tasks:
    - Task 21.1: Replace provisional licensing assumptions with item/source-specific evidence from `rights`, `rights_url`, `usage`, content partner pages, and National Library open-data pages.
    - Task 21.2: Distinguish API metadata reuse from full-text/item reuse for every candidate source.
    - Task 21.3: Record attribution requirements and source-identification requirements for each candidate source.
    - Task 21.4: Treat Papers Past, Turnbull unpublished collections, Treaty/Māori materials, private papers, images, and newspapers as review-required until source-specific terms are confirmed.
  - Granular implementation tasks:
    - Task 21.5: Add a read-only DigitalNZ probe script in `nlp-policy-nz` that accepts query text, field filters, pagination limits, and output path.
    - Task 21.6: Add a metadata crosswalk from DigitalNZ fields to the root Open New Zealand corpus schema.
    - Task 21.7: Add a source triage report generator that classifies results as `triangulation_only`, `metadata_inventory`, `candidate_ingestion`, `rights_review_required`, or `blocked`.
    - Task 21.8: Build small inventories for Parliamentary Papers/AJHR, New Zealand Gazette, Waitangi Tribunal, Publications NZ, Turnbull/TAPUHI, Papers Past legal queries, and historical statutes.
    - Task 21.9: Add tests using recorded fixture responses, not live API calls, for normalisation, rights classification, and pagination handling.
    - Task 21.10: Add a documentation page mapping DigitalNZ query strategies to Tracks 13-20.
  - Phase gates:
    - After each task: review diff, commit only the owning repo files, push, and check GitHub Actions.
    - After each phase: update progress evidence, push a phase-summary commit, and confirm relevant Actions pass or record a blocker.
    - After track completion: review, push, confirm Actions pass, and update Track 11/13/14/18/19/20 mappings where DigitalNZ-discovered sources are consumed.
  - Guardrails:
    - Do not assume DigitalNZ search-result counts equal corpus-ingestable records.
    - Do not treat metadata licence as permission to redistribute full text or images.
    - Do not perform high-volume API harvesting without an API key, rate-limit policy, cache policy, and contact/attribution plan.
    - Keep DigitalNZ as a discovery/triangulation layer unless a source-specific rights review approves ingestion.

## Track 22: Root Ownership Audit and Subrepo Migration
- [~] Task: Use conductor Track 11 to audit whether any implementation code has landed in the root aggregation repo and migrate safe candidates to their owning repos.
  - Conductor link: `conductor/tracks/root_ownership_migration_20260614/`.
  - Owning repo for coordination: root `legal-nz`.
  - Owning repos for implementation migrations: the relevant subrepo named by each migration task.
  - Current migration action:
    - Root `shared_utils.py` was identified as misplaced corpus utility code.
    - Root hash/change-report helpers now live in root orchestration-owned `scripts/sha256_utils.py`.
    - `corpus-law-nz/src/nz_legislation_corpus/utils.py` is self-contained and no longer imports root `shared_utils.py`.
    - Root `shared_utils.py` has been removed.
  - Pending gates:
    - Review and commit root-owned changes.
    - Review and commit `corpus-law-nz` changes inside that subrepo boundary.
    - Push after each commit/phase.
    - Check relevant GitHub Actions and record run URLs or blockers.

## Track 23: Dependency Consensus, Python 3.14, and SOTA Toolchain Standardization
- [ ] Task: Coordinate conductor Tracks 12-16 for dependency standardization, Python 3.14 readiness, uv/pixi decisions, Rust-backed hot-path libraries, vector/RAG backend consensus, and TypeScript CLI tooling.
  - Root role: coordination and evidence only.
  - Conductor links:
    - `conductor/tracks/dependency_consensus_python314_20260614/`
    - `conductor/tracks/uv_pixi_lockfile_standardization_20260614/`
    - `conductor/tracks/rust_backed_tooling_hotpaths_20260614/`
    - `conductor/tracks/vector_rag_backend_consensus_20260614/`
    - `conductor/tracks/typescript_cli_toolchain_modernization_20260614/`
  - Consensus defaults:
    - Python 3.14 is the target for new Python work once each subrepo proves dependency and CI compatibility.
    - `uv` is the default for pure Python repos.
    - `pixi` is preferred where conda-forge, native tools, GPU/ML stacks, or cross-language reproducibility materially matter.
    - LanceDB is the initial default for local/reproducible vector artifacts.
    - Qdrant is the service-grade vector-store candidate and must win benchmark/operations review before becoming a default.
    - Haystack 2.x belongs in `nlp-policy-nz` prototypes first.
    - `cli-legislation-nz` should evaluate Biome/Oxlint/Rolldown as opt-in trials, not immediate replacements.
    - Each subrepo must maintain a maturity dependency checklist using `conductor/templates/maturity-dependency-baseline.md`.
    - Heavy ML dependencies stay optional and mostly centralized in `nlp-policy-nz`.
    - RAG orchestration stays out of source corpus repos unless a future dedicated RAG repo is approved.
  - Delivery gates:
    - Each implementation task is committed inside the owning subrepo.
    - Each phase is pushed and checked against the relevant GitHub Actions.
    - Any repo that cannot move to Python 3.14 must record the exact dependency blocker.

## Track 24: Registry Submission Manifests and Reusable Submission Workflows
- [~] Task: Coordinate conductor Track 17 so MCPs, CLIs, packages, containers, datasets, models, and archives use a standard registry submission schema and reusable workflow.
  - Root coordination artifacts:
    - `conductor/templates/registry-submission.schema.json`
    - `conductor/templates/registry-submission-workflow.md`
    - `conductor/templates/registry-submission-fixtures/`
    - `docs/registry-submission-manifests.md`
  - Owning implementation repo:
    - `cli-legislation-nz` for CLI/MCP/npm/GitHub Packages/GitHub Releases/GHCR/Homebrew/Smithery/MCP registry submission.
    - Corpus repos for dataset/archive submission.
    - `nlp-policy-nz` for benchmark/model/RAG/package submission.
  - Delivery gates:
    - Manifest before submission.
    - Requirements inventory before readiness claims.
    - Local package/build/test evidence before submission.
    - Push and GitHub Actions check after each phase.
  - Current local status:
    - Root Track 17 schema and workflow templates exist.
    - Fixture manifests now cover `cli`, `mcp_server`, `python_package`, `container`, and `dataset`.
    - Root documentation now records manifest placement, evidence expectations, registry family defaults, and local-only guardrails.
    - Subrepo manifest creation, commit, push, Actions checks, Chrome/account work, token/`.env` work, uploads, and registry submissions remain unperformed and gated.

## Track 25: Hermes-Style Conductor Self-Learning and Skill Improvement
- [ ] Task: Coordinate conductor Track 18 so each conductor repo and relevant skill has a repeatable observe/reflect/distill/improve/evaluate/promote loop.
  - Root coordination artifact:
    - `conductor/templates/self-improvement-loop.md`
  - Repo-local required surfaces:
    - `conductor/learning-log.md`
    - `conductor/improvement-backlog.md`
  - Guardrails:
    - Repo-local learning first.
    - Shared templates only for repeated or cross-repo lessons.
    - Global skill updates only with explicit approval.
    - Never record secrets or credential-specific details in learning logs.

## Track 26: Quality and Maintenance Tooling Baseline
- [x] Task: Coordinate conductor Track 19 so Codecov, Renovate, Scalene, Vale, and Markdown style are standardized by repo role.
  - Root coordination artifact:
    - `conductor/templates/quality-maintenance-tooling-baseline.md`
  - Current audit summary:
    - Vale is present in root and all checked subrepos.
    - Markdown style is root-local and should be made repo-local or explicitly inherited by each subrepo.
    - Codecov is present in `cli-legislation-nz` and should be conditional elsewhere.
    - Renovate is present in `cli-legislation-nz` and should be added or documented across all real GitHub repos.
    - Scalene is present in `corpus-law-nz`, `corpus-nz-hansard`, and `nlp-policy-nz`; it should be conditional for other Python data/performance repos.
  - Baseline decisions:
    - Vale required across repos.
    - Markdown style required across repos with Markdown.
    - Renovate required unless org-level inheritance is documented.
    - Codecov conditional on meaningful coverage artifacts.
    - Scalene conditional on Python data/ingestion/NLP/performance-sensitive use.
  - Delivery gates:
    - Create repo-local checklist first.
    - Add config second.
    - Add CI enforcement only after local commands are known.
    - Commit, push, and check GitHub Actions per owning subrepo.

## Track 27: Root Remote and Submodule Workspace
- [~] Task: Coordinate conductor Track 20 so the root `legal-nz` repo becomes a private orchestration remote with implementation repos represented as submodules.
  - Conductor link: `conductor/tracks/root_remote_submodules_20260615/`.
  - Root role:
    - Own `.gitmodules`, conductor/task-plan surfaces, root swarm coordination, and workspace documentation.
    - Do not own implementation code, corpus builders, CLI features, publication workflows, dataset builders, or benchmark runners.
  - Submodule set:
    - `cli-legislation-nz` -> `https://github.com/edithatogo/nz-legislation.git`
    - `corpus-cases-medilegal-nz` -> `https://github.com/edithatogo/corpus-cases-medilegal-nz.git`
    - `corpus-law-nz` -> `https://github.com/edithatogo/corpus-legislation-nz.git`
    - `corpus-nz-hansard` -> `https://github.com/edithatogo/corpus-nz-hansard.git`
    - `hathi-nz` -> `https://github.com/edithatogo/hathi-nz.git`
    - `nlp-policy-nz` -> `https://github.com/edithatogo/nlp-policy-nz.git`
    - `sm-govt-nz` -> `https://github.com/edithatogo/sm-govt-nz.git`
  - Exclusions pending classification:
    - `dnz` is mapped but not submodule-ready because the local Git root resolves to `C:/Users/60217257/OneDrive - Flinders`, outside this workspace, and no `origin` remote was detected.
    - `fyi-cli` is mapped as a real nested repo at `https://github.com/edithatogo/fyi-cli`, branch `master`, with dirty local changes; it awaits an explicit role decision before submodule promotion.
  - Current local setup:
    - `.gitmodules` has been added for the seven core subrepos.
    - `docs/root-submodules.md` documents clone, update, status, inclusion, and exclusion rules.
    - `docs/repository-status.md` records root, submodule, `dnz`, and `fyi-cli` status.
    - Root submodule gitlinks should be committed in the root repo only.
  - Pending gates:
    - Private GitHub repo `edithatogo/legal-nz-workspace` has been created.
    - Root `main` has been pushed at commit `af9f015`.
    - Confirm GitHub renders the seven submodules.
    - Reattach the local `legal-nz` worktree to durable Git metadata after the current OneDrive `.git` permission/resource blocker clears.
    - Resolve subrepo `.git/index.lock` blockers before claiming stable updated pins.
    - Commit and push pending SemVer/logging changes inside each owning subrepo.
    - Check GitHub Actions per changed repo and record run URLs or blockers.

## Track 28: CLI-First Tooling Policy and Command-Surface Consolidation
- [~] Task: Coordinate conductor Track 21 so every agent uses existing CLIs, package scripts, and maintained repo command surfaces before writing custom code.
  - Conductor link: `conductor/tracks/cli_first_tooling_policy_20260615/`.
  - Root coordination artifacts:
    - `docs/cli-first-policy.md`
    - `conductor/templates/cli-tool-registry.json`
  - Required default:
    - Use existing CLI/package script first.
    - Extend the owning repo CLI second.
    - Use temporary custom code only with an explicit exception and follow-up CLI consolidation task.
  - Known first-class command surfaces:
    - `cli-legislation-nz`: `nzlegislation`, `anzlegislation`, `nzlegislation-mcp`, `anzlegislation-mcp`, and `pnpm` scripts.
    - `corpus-law-nz`: `nzlc`.
    - `nlp-policy-nz`: `nlp-policy-nz`.
    - Root: `workspace-doctor.py`, `scripts/check_naming.py`, `scripts/check_lint.py`, `scripts/swarm_orchestrator.py`, `scripts/swarm_agent.py`, `scripts/validate-documents.js`, and `scripts/quality-report.js`.
  - Script-heavy repos requiring consolidation tracks:
    - `corpus-nz-hansard`
    - `sm-govt-nz`
    - `hathi-nz`
    - `corpus-cases-medilegal-nz`
  - Additional mapped repos:
    - `fyi-cli`: mapped as an auxiliary CLI repo pending exact entrypoint audit.
    - `dnz`: no CLI dispatch until repository boundary is classified.
    - `open_social_data`, `openfisca-aotearoa`, and `sourceright`: promoted to approved submodules on 2026-06-15.
    - `Friction`: mapped as an auxiliary repo pending Legal NZ role and submodule decision.
  - Delivery gates:
    - Root policy committed and pushed.
    - Subrepo CLI changes committed and pushed inside owning subrepos.
    - CLI help/smoke tests added before enforcement claims.

## Track 29: Astro Documentation Standard
- [~] Task: Coordinate conductor Track 22 so every repo in the Legal NZ system uses Astro for documentation sites going forward.
  - Conductor link: `conductor/tracks/astro_documentation_standard_20260615/`.
  - Root coordination artifacts:
    - `docs/documentation-platform-policy.md`
    - `conductor/templates/astro-docs-standard.md`
    - `docs/astro-plugin-assessment.md`
    - `conductor/templates/astro-plugin-baseline.json`
  - Required default:
    - Astro is the docs-site and docs-preview platform for every repo.
    - Default plugin baseline is Astro, Starlight, MDX, Sitemap, and shared Legal NZ style tokens.
    - Existing TypeDoc/API-reference generation may feed Astro but must not replace the Astro docs shell.
    - Do not introduce or expand Docusaurus, MkDocs, Sphinx, VitePress, Nextra, VuePress, Docsify, or Mintlify as published docs-site frameworks.
    - Add Tailwind, UI framework integrations, RSS, extra search, or Partytown only with a documented repo-specific need.
  - Delivery gates:
    - Audit every mapped repo for docs tooling.
    - Create per-repo Astro migration or root-delegation task.
    - Commit and push docs implementation changes inside the owning repo.
    - Add `docs:dev`, `docs:build`, and `docs:check` where the repo owns docs.
    - Check GitHub Actions after docs enforcement is added.

## Track 30: Multi-Model Swarm Orchestration
- [~] Task: Coordinate root swarm execution using Cline, Codex, and Xiaomi MiMo Code lanes.
  - Root coordination artifact:
    - `docs/swarm-orchestration-models.md`
  - Active implementation lanes:
    - `General_Coder`: Cline with `deepseek-v4-flash`.
    - `Codex_GPT55_Engineer`: Codex with `gpt-5.5`.
    - `Xiaomi_MiMo_Code`: Xiaomi MiMo Code with `xiaomi-mimo-code`.
  - Presets updated:
    - `all_conductor`
    - `track_swarm`
  - Delivery gates:
    - Use root `swarm-workspaces.yaml` for workspace targeting.
    - Use CLI-first policy before custom code.
    - Use Astro documentation standard for docs-site work.
    - Keep Chrome and external-write tasks explicitly gated.
    - Hand completed tasks to `Quality_Validator` before commit/push claims.
  - Implementation evidence:
    - `scripts/swarm_orchestrator.py` now parses swarm presets and includes assigned model/mode metadata in task dispatch.
    - Xiaomi MiMo Code is preferred for bounded CLI, Astro, docs, migration, template, refactor, script, package, and command tasks.
    - Tests cover preset parsing, MiMo assignment, model metadata in task content, and Xiaomi identity resolution.
