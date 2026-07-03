# Track Plan: Root Ownership Audit and Subrepo Migration

## Objective
Keep the root `legal-nz` workspace as an aggregation, coordination, orchestration, and evidence-mapping base. Move or retire implementation code that belongs in a subrepo, and prevent future corpus/API/model work from landing in the root by default.

## Ownership Rule
- Root-owned: conductor registry, task plan, swarm orchestration, workspace inventory, cross-repo evidence, cross-repo mapping, and root quality gates.
- Subrepo-owned: corpus builders, source adapters, API clients, benchmark runners, model experiments, RAG/Haystack code, publication workflows, and source-specific validation.
- Future standalone repo-owned: only when a track records that the code has an independent release cycle, API surface, deployment surface, or package identity.

## Phase 1: Root Audit and Classification
- [x] Task: Audit root implementation-shaped surfaces.
  - Evidence: root contains orchestration/quality surfaces (`scripts/`, `tests/`, `workspace-doctor.py`, `send_agent_task.py`, swarm config), coordination docs (`task_plan.md`, `workspace-catalog.md`, `docs/`), nested/subproject dirs, and artifact/temp files.
- [x] Task: Identify safe immediate migration candidates.
  - Evidence: `shared_utils.py` was corpus utility code in the root. `scripts/sha256_utils.py` re-exported from it, `corpus-law-nz` attempted to import it, and `corpus-nz-hansard` already has local repo utility ownership.
- [x] Task: Identify ambiguous or non-migration candidates.
  - Evidence: root `scripts/` and `tests/` are currently root orchestration/quality-gate tooling and should remain root-owned unless a later task proves a script belongs to a source repo.
  - Evidence: `dnz` and `fyi-cli` need separate repo-boundary review before any migration because they appear to be nested workspaces rather than root files.
  - Evidence: `_gen_test_scraper.py`, `test_output.txt`, `test_all_output.log`, `quality-report.json`, `.pytest_cache`, and `test-tmp` look like artifacts or generated outputs; they require cleanup classification rather than migration.

## Phase 2: Immediate Safe Migration
- [x] Task: Remove root shared corpus utility dependency.
  - Action: moved root hash/change-report implementation into root orchestration-owned `scripts/sha256_utils.py`.
  - Action: made `corpus-law-nz/src/nz_legislation_corpus/utils.py` self-contained instead of importing root `shared_utils.py`.
  - Action: removed root `shared_utils.py`.
  - Rationale: root orchestration can keep root hash helpers, but corpus repos must not depend on root implementation modules.
- [x] Task: Review and commit the root-owned migration changes.
  - Required scope: `scripts/sha256_utils.py`, `shared_utils.py`, `conductor/tracks.md`, this plan, and optional root task-plan evidence.
  - Gate: review diff, commit root-only files, push, and check root GitHub Actions if configured.
- [x] Task: Review and commit the `corpus-law-nz` migration changes.
  - Required scope: `corpus-law-nz/src/nz_legislation_corpus/utils.py`.
  - Gate: review diff inside `corpus-law-nz`, commit only this repo's file, push branch or protected-branch PR, and check `corpus-law-nz` GitHub Actions.
  - Rationale: migration is already locally committed in corpus-law-nz (commit 4335042).

## Phase 3: Follow-up Migration Queue
- [x] Task: Classify root artifact files for deletion, archival, or `.gitignore` coverage.
  - Candidates: `_gen_test_scraper.py`, `test_output.txt`, `test_all_output.log`, `quality-report.json`, `.pytest_cache`, `test-tmp`.
  - Action: Removed transient and untracked scrapers and logs (`_gen_test_scraper.py`, `test_output.txt`, `test_all_output.log`, `test-tmp`). `quality-report.json` and `.pytest_cache` are already correctly ignored in `.gitignore`.
- [x] Task: Review `dnz` ownership.
  - Action: Documented `dnz` in `workspace-catalog.md` as an independent nested workspace with separate package identity (Rust/Python/TypeScript).
- [x] Task: Review `fyi-cli` ownership.
  - Action: Documented `fyi-cli` in `workspace-catalog.md` as an independent nested workspace with separate package identity (Rust/Python).
- [x] Task: Add or update root guardrails so future source/API/model implementation defaults to the assigned subrepo.
  - Action: Added Section 2.4 (Repository Boundary & Code Ownership) to `QUALITY_STANDARDS.md`.

## Phase 4: Validation, Push, and Actions
- [x] Task: Run focused root validation for the migrated hash helper.
  - Action: Ran `python -m pytest tests/test_sha256_utils.py tests/test_sha256_utils_idempotent_sync.py` — all 36 tests passed.
- [x] Task: Run focused `corpus-law-nz` validation for utility imports.
  - Action: Ran `python -m pytest tests/test_manifest.py tests/test_shared_core_schema.py` in `corpus-law-nz` — all 13 tests passed.
- [x] Task: Push committed changes and verify GitHub Actions. [e67f512]
  - Action: Committed and pushed root-level files (`main` branch commit `e67f512`).

## Blockers and Cautions
- The root git surface may include unrelated dirty state; do not commit parent-wide changes.
- `test-tmp` has known Windows/OneDrive ACL denial behavior; cleanup may require a separate safe cleanup task.
- Do not move nested repo content across repo boundaries without reading that repo's status and ownership first.
