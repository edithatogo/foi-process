# Track 22: Astro Documentation Standard

## Objective

Standardize all Legal NZ system repositories on Astro for documentation sites and documentation preview/build workflows going forward.

## Phase 1: Root policy

- [x] Add Astro documentation platform policy.
- [x] Add reusable Astro docs standard checklist.
- [x] Add root conductor/task-plan coordination track.
- [x] Add Astro plugin and style assessment.
- [x] Add machine-readable Astro plugin baseline.

## Phase 2: Inventory

- [x] Audit every mapped repo for documentation tooling and scripts.
- [x] Record existing documentation usage. All 7 subrepos use Astro Starlight; root uses raw markdown.
- [x] Classify each repo: 7 subrepos = `astro-native`; root = `legacy-migration-needed`.
- [x] Record plugin needs. Plugin baseline already covers all repos; no gaps found.

Inventory results in `docs-inventory.md`.

## Phase 3: Migration plans

- [ ] Create per-repo migration tasks for any non-Astro docs site.
- [ ] Preserve API-reference generators only as inputs to Astro.
- [ ] Add `docs:dev`, `docs:build`, and `docs:check` commands where the repo owns docs.
- [ ] Add CI checks for Astro docs builds.

## Phase 4: Enforcement

- [x] Add a root docs-tooling lint that flags new non-Astro docs-site frameworks.
- [ ] Add repo-local CI checks after each repo has a stable docs command.
- [x] Update the CLI-first registry if docs commands are added as package scripts.

### 2026-06-23 Enforcement Evidence

- Added `scripts/check_docs_tooling.py` to flag disallowed docs-site frameworks
  from the Astro baseline in mapped repo config locations.
- Local check passed: `python scripts\check_docs_tooling.py`.
- Updated `conductor/templates/astro-plugin-baseline.json` to classify `dnz`
  as a required Astro documentation surface now that it is promoted.

## Guardrails

- Do not expand Docusaurus, MkDocs, Sphinx, VitePress, Nextra, VuePress, Docsify, or Mintlify as a docs-site platform.
- TypeDoc and similar tools may generate reference content, but Astro owns the published documentation shell.
- Use Starlight, MDX, Sitemap, and shared Legal NZ style tokens as the default plugin/style baseline.
- Add Tailwind, UI framework integrations, RSS, extra search, or Partytown only after a repo-specific need is recorded.
- Root coordinates policy; implementation and CI changes happen in the owning subrepo.
- Do not migrate `dnz` until its repository boundary is classified.

## Review and release gates

- Root policy changes are committed and pushed in the root orchestration repo.
- Per-repo Astro implementation changes are committed and pushed inside the owning repo.
- GitHub Actions must pass for every repo after docs build enforcement is added.
