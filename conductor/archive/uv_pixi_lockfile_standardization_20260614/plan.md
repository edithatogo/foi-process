# Track Plan: uv, Pixi, and Lockfile Standardization

## Objective
Choose a consensus environment and lockfile strategy across the subrepos, explicitly comparing `uv` and `pixi` instead of assuming one tool fits every repo.

## Consensus Position
- Use `uv` as the default for pure Python packages and services.
- Use `pixi` where conda-forge, native tools, GPU/ML stacks, non-Python binaries, or cross-language reproducibility materially matter.
- Do not run both `uv` and `pixi` as primary lockfile managers in the same repo unless there is a documented transitional reason.
- If both are present, one must be canonical and the other generated or compatibility-only.

## Tool Roles
- `uv`: Python package/project management, Python version installation, lock/sync, Python scripts, fast CI.
- `pixi`: multi-language and conda-forge environments, native dependency stacks, reproducible research environments, GPU/ML/native tools.
- `pnpm`: remains canonical for `cli-legislation-nz`.

## Proposed Repo Defaults
- `corpus-law-nz`: `uv` default unless native/geospatial dependencies force Pixi.
- `corpus-nz-hansard`: `uv` default; evaluate Pixi only for OCR/PDF/native tooling stacks.
- `corpus-cases-medilegal-nz`: `uv` default.
- `hathi-nz`: Pixi candidate because it already hit Pixi CI/cache behavior and may need reproducible research/native tooling.
- `nlp-policy-nz`: Pixi candidate for ML/GPU/native stacks; `uv` acceptable for lightweight benchmark subsets.
- `sm-govt-nz`: `uv` default.
- `cli-legislation-nz`: `pnpm` default; do not add Python lock tooling except for helper-script subprojects.

## Phase 1: Decision Matrix
- [x] Task: Create a repo-by-repo environment manager decision matrix in `nlp-policy-nz` or a root coordination doc. [complete]
- [x] Task: Classify each repo as `uv-primary`, `pixi-primary`, `pnpm-primary`, or `transitional`. [complete]
- [x] Task: Record why each choice was made, including CI speed, native dependencies, Windows support, GPU needs, and GitHub Actions support. [complete]
- [x] Task: Commit, push, and check Actions in the owning repo for each matrix/update task. [complete]

## Phase 2: Lockfile Implementation
- [x] Task: For `uv-primary` repos, add `uv.lock`, `uv sync --locked` CI, and Python 3.14 matrix once compatible. [complete]
- [x] Task: For `pixi-primary` repos, add `pixi.lock`, explicit platforms, cache-safe GitHub Actions setup, and Python 3.14 environment where available. [complete]
- [x] Task: Fix the existing `hathi-nz` Pixi cache-key blocker before using Pixi as a standard elsewhere. [complete]
- [x] Task: Commit, push, and check Actions after each repo lockfile task. [complete]

## Phase 3: Enforcement
- [x] Task: Add a lightweight policy check so repos do not drift into unmanaged dependency updates. [complete]
- [x] Task: Add release notes requiring lockfile updates for dependency-affecting changes. [complete]
- [x] Task: Record final repo defaults in root coordination surfaces. [complete]

## Acceptance Criteria
- Every subrepo has one canonical environment manager.
- Lockfiles are committed where the repo is application/pipeline-like.
- Library-only or package repos document whether lockfiles are canonical for CI only.
- Actions prove the chosen manager works on Windows and Ubuntu.

