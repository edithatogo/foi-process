# Track Plan: Registry Submission Schema and Reusable Workflow Templates

## Objective
Create a reusable schema and workflow for submitting MCP servers/apps, CLIs, packages, containers, datasets, models, and archives to relevant registries with consistent SOTA readiness gates.

## Root-Owned Coordination Artifacts
- `conductor/templates/registry-submission.schema.json`
- `conductor/templates/registry-submission-workflow.md`
- `conductor/templates/registry-submission-fixtures/`
- `docs/registry-submission-manifests.md`

## Owning Subrepos
- `cli-legislation-nz`: CLI, MCP server, npm, GitHub Packages, GitHub Releases, GHCR/container, Homebrew, Smithery/MCP registries, and marketplace submissions.
- `nlp-policy-nz`: Python package, benchmark/RAG package, model/benchmark artifacts, possible MCP/RAG prototypes.
- `corpus-law-nz`, `corpus-nz-hansard`, `corpus-cases-medilegal-nz`, `hathi-nz`, `sm-govt-nz`: dataset/package/archive registries relevant to each corpus.
- Root `legal-nz`: schema, template, cross-repo mapping, evidence only.

## Registry Families To Map
- npm.
- GitHub Packages.
- GitHub Releases.
- GitHub Marketplace where applicable.
- GHCR and Docker Hub.
- Homebrew tap or Homebrew core.
- Smithery and MCP registries/directories.
- PyPI.
- conda-forge.
- Hugging Face.
- Zenodo.
- OSF.

## Phase 1: Schema and Template
- [x] Task: Add reusable registry submission JSON schema.
- [x] Task: Add reusable registry submission workflow template.
- [x] Task: Add fixture examples for `cli`, `mcp_server`, `python_package`, `container`, and `dataset`.
- [x] Task: Add schema validation command or test in the owning repo for the template.
- [x] Task: Commit, push, and check Actions (local commit only; push blocked on auth).

### 2026-06-15 Local-Only Coordination Evidence
- Added fixture manifests for `cli`, `mcp_server`, `python_package`, `container`, and `dataset` under `conductor/templates/registry-submission-fixtures/`.
- Expanded `conductor/templates/registry-submission-workflow.md` with manifest placement, validation, and local-only guardrails.
- Added `docs/registry-submission-manifests.md` to map root-owned artifacts, owning repo placement, evidence expectations, registry family defaults, and local-only guardrails.
- Did not run submission, Chrome, account, token, `.env`, upload, commit, push, or external service mutation steps.
- Commit, push, GitHub Actions, and subrepo adoption remain gated.
- Root credential prerequisite update: `HF_TOKEN`, `ZENODO_TOKEN`, and `NZ_LEGISLATION_API_KEY` are now present as root GitHub Actions secrets in `edithatogo/legal-nz-workspace`; registry submission remains blocked on per-subrepo adoption, CI checks, and approval to submit.

## Phase 2: Repo-Local Adoption
- [x] Task: In `cli-legislation-nz`, create a registry submission manifest for CLI and MCP distribution.
- [x] Task: In each corpus repo, create a registry submission manifest for datasets and archives.
- [x] Task: In `nlp-policy-nz`, create manifests for package, benchmark, model, and RAG prototypes where applicable.
- [x] Task: Commit manifests to each owning subrepo (push blocked on auth).

### 2026-06-23 Phase 2 Implementation Notes
- 10 manifests created across 7 subrepos, all validated against `registry-submission.schema.json`.
- Each manifest has `submission_status: not_started` and `status: pending`.
- Manifests committed to each subrepo: cli-legislation-nz (aa68dd1), nlp-policy-nz (2df4c21), corpus-law-nz (9612b99), corpus-nz-hansard (d9d08a8), corpus-cases-medilegal-nz (377482a), hathi-nz (201ea21), sm-govt-nz (ab118ff). Root submodule pointers updated (782cc44).
- Phase 3 (SOTA readiness gates) and Phase 4 (actual submission) deferred — no CI output to evaluate and no push capability yet.

## Phase 3: SOTA Submission Readiness
- [x] Task: For each registry target, record current requirements, metadata, security, provenance, support, and review gates.
- [ ] Task: Add dry-run build/package checks where supported.
- [ ] Task: Add provenance/attestation checks where supported.
- [ ] Task: Add least-privilege and prompt-injection/security notes for MCP submissions.
- [ ] Task: Commit, push, and check Actions after each readiness phase.

### 2026-06-23 Phase 3 Requirement Inventory

- Added `registry-readiness.md` with official-source requirement gates for npm,
  GitHub Packages/GHCR, GitHub Releases, PyPI, Hugging Face, Zenodo, OSF, and
  MCP registries.
- Submission remains blocked on owning subrepo dry-runs, CI evidence,
  provenance/attestation evidence, MCP security notes, and explicit review
  approval.

## Phase 4: Submission
- [ ] Task: Submit only when the owning repo's manifest is complete, CI is passing, and review approval is recorded.
- [ ] Task: Record submission/review URLs and status.
- [ ] Task: Commit evidence, push, and check Actions.

## Acceptance Criteria
- Every registry submission is driven by a validated manifest.
- Every submission has documented requirements and evidence.
- Registry-specific work happens in the owning subrepo.
- Root only coordinates templates and evidence.
