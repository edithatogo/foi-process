# Submodule Hygiene Report

**Date:** 2026-06-23  
**Track:** root_remote_submodules_20260615, Phase 3  
**Tooling:** opencode / conductor

---

## 1. Index Lock Check

All 9 subrepos checked — **no `.git/index.lock` files found**.

| Subrepo | index.lock |
|---|---|
| cli-legislation-nz | ✗ absent |
| nlp-policy-nz | ✗ absent |
| corpus-law-nz | ✗ absent |
| corpus-nz-hansard | ✗ absent |
| corpus-cases-medilegal-nz | ✗ absent |
| hathi-nz | ✗ absent |
| sm-govt-nz | ✗ absent |
| fyi-cli | ✗ absent |
| dnz | ✗ absent |

---

## 2. Dirty / Unstaged State

### cli-legislation-nz
- `??` `.github/workflows/ci-learning-candidates.yml`
- `??` `conductor/improvement-backlog.md`
- `??` `conductor/learning-entry.schema.json`
- `??` `conductor/learning-log.md`
- `??` `conductor/templates/`
- `??` `scripts/record_learning_candidate.py`

All untracked — learning-system scaffolding, no tracked-file modifications.

### nlp-policy-nz
- `??` `.github/workflows/ci-learning-candidates.yml`
- `??` `conductor/improvement-backlog.md`
- `??` `conductor/learning-entry.schema.json`
- `??` `conductor/learning-log.md`
- `??` `conductor/templates/`
- `??` `conductor/tracks/13_argument_structure_annotation_20260611/`
- `??` `scripts/benchmark_msgspec_orjson.py`
- `??` `scripts/benchmark_tokenizers_chunking.py`
- `??` `scripts/record_learning_candidate.py`
- `??` `test_out.traces.jsonl`
- `??` `tests/test_track13_external_gate_manifest.py`
- `??` `tests/test_track14_benchmarks.py`
- `??` `track17-test-output/` (multiple cache and output dirs)
- `??` `uv.lock`

Heavy untracked state from benchmark/test runs and learning system.

### corpus-law-nz
- ` M` `pyproject.toml` — tracked file modified
- `??` `.github/workflows/ci-learning-candidates.yml`
- `??` `conductor/improvement-backlog.md`
- `??` `conductor/learning-entry.schema.json`
- `??` `conductor/learning-log.md`
- `??` `conductor/templates/`
- `??` `scripts/record_learning_candidate.py`

One modified tracked file (`pyproject.toml`) plus learning-system untracked.

### corpus-nz-hansard
- `MM` `.github/workflows/quality.yml` — staged + unstaged modifications
- `MM` `Makefile`
- `MM` `conductor/tracks.md`
- ` M` `conductor/tracks/bills_api_integration_20260612/metadata.json`
- ` M` `conductor/tracks/bills_api_integration_20260612/plan.md`
- ` M` `conductor/tracks/cross_repo_dataset_architecture_20260612/plan.md`
- `M ` `conductor/tracks/member_identity_triangulation_20260612/evidence.md` — staged
- `M ` `conductor/tracks/member_identity_triangulation_20260612/index.md` — staged
- `M ` `conductor/tracks/member_identity_triangulation_20260612/metadata.json` — staged
- `M ` `conductor/tracks/member_identity_triangulation_20260612/plan.md` — staged
- ` M` `conductor/tracks/parliament_website_stealth_access_20260612/evidence.md`
- ` M` `conductor/tracks/parliament_website_stealth_access_20260612/plan.md`
- ` M` `conductor/tracks/wikipedia_mp_lists_acquisition_20260612/evidence.md`
- ` M` `conductor/tracks/wikipedia_mp_lists_acquisition_20260612/metadata.json`
- ` M` `conductor/tracks/wikipedia_mp_lists_acquisition_20260612/plan.md`
- ` M` `derived/historical_sitting_official_exports/`
- ` M` `derived/wikipedia_mp_lists.json`
- `MM` `docs/quality-gate.md`
- ` M` `docs/static-documentation-portal/index.html`
- ` M` `manifests/static_documentation_portal_manifest.json`
- ` M` `pixi.lock`
- `MM` `pixi.toml`
- ` M` `pyproject.toml`
- ` M` `schemas/static_documentation_portal.schema.json`
- ` M` `scripts/build_static_documentation_portal.py`
- ` M` `scripts/check_bills_api_integration.py`
- `A ` `scripts/check_member_identity_triangulation.py` — staged new file
- `MM` `scripts/check_quality_gate.py`
- ` M` `scripts/check_static_documentation_portal.py`
- ` M` `scripts/fetch_wikipedia_mps.py`
- `A ` `tests/test_member_identity_triangulation.py` — staged new file
- Many `??` untracked (learning-system, HathiTrust, parliament, wiki tests/fixtures)

**Most active subrepo** — multiple active tracks with both staged and unstaged changes.

### corpus-cases-medilegal-nz
- ` M` `pyproject.toml` — tracked file modified
- `??` `conductor/improvement-backlog.md`
- `??` `conductor/learning-log.md`
- `??` `conductor/templates/`
- `??` `scripts/benchmark_selectolax_parser.py`
- `??` `tests/test_track14_selectolax_benchmark.py`

Light dirty state: one modified tracked file plus benchmark/learning artifacts.

### hathi-nz
- ` M` `pyproject.toml` — tracked file modified
- `??` `.github/workflows/ci-learning-candidates.yml`
- `??` `conductor/improvement-backlog.md`
- `??` `conductor/learning-entry.schema.json`
- `??` `conductor/learning-log.md`
- `??` `conductor/templates/`
- `??` `scripts/record_learning_candidate.py`

Light dirty state: one modified tracked file plus learning-system scaffolding.

### sm-govt-nz
- ` M` `.github/workflows/ci.yml` — tracked file modified

Minimal dirty state: single workflow file modification. **Note:** `git submodule status` shows `+` prefix (not at superproject-indexed commit).

### fyi-cli
- `??` `.github/workflows/ci-learning-candidates.yml`
- `??` `conductor/improvement-backlog.md`
- `??` `conductor/learning-entry.schema.json`
- `??` `conductor/learning-log.md`
- `??` `conductor/templates/`
- `??` `scripts/record_learning_candidate.py`

All untracked learning-system scaffolding.

### dnz
- `??` `.github/workflows/ci-learning-candidates.yml`
- `??` `conductor/improvement-backlog.md`
- `??` `conductor/learning-entry.schema.json`
- `??` `conductor/learning-log.md`
- `??` `conductor/templates/`
- `??` `scripts/record_learning_candidate.py`

All untracked learning-system scaffolding.

---

## 3. HEAD Commits

| Subrepo | HEAD |
|---|---|
| cli-legislation-nz | `562f932` feat(qa): Track 19 Phase 1-2 — markdownlint + checklist |
| nlp-policy-nz | `1b841c6` fix(track19): add [tool.scalene] section to pyproject.toml |
| corpus-law-nz | `e7b7cfd` feat(qa): Track 19 Phase 1-2 — markdownlint + checklist |
| corpus-nz-hansard | `b9b9551` fix(track19): add YAML coverage to vale.ini |
| corpus-cases-medilegal-nz | `aa28ac9` feat(qa): Track 19 Phase 1-2 — markdownlint, renovate, checklist |
| hathi-nz | `300617f` fix(track19): update checklist for present markdownlint/renovate |
| sm-govt-nz | `743f4b9` "conductor_learning_dirty_worktree_guardrail" |
| fyi-cli | `af3bf99` chore: add fyi cli quality and rust tracks |
| dnz | `511527c` chore-dnz-track13 |

All are recent commits. Most subrepos are on Track 19 (QA) work.

---

## 4. fyi-cli Classification (Phase 4)

| Attribute | Value |
|---|---|
| **Remote** | `https://github.com/edithatogo/fyi-cli` |
| **Repo type** | Python (`pyproject.toml`) |
| **Registered submodule?** | Yes (`.gitmodules` entry, `git submodule status` shows it) |
| **Is it a real repo with clean boundary?** | Yes — dedicated remote, own tooling, clean boundary |
| **Should agents know about and use?** | **Yes** — it is a tool (CLI) that could provide FYI/OIA request functionality. Document for agent discovery. |

**Verdict:** fyi-cli is a Python CLI tool registered as a submodule. Agents should be aware of it.

---

## 5. dnz Classification (Phase 4)

| Attribute | Value |
|---|---|
| **Remote** | `https://github.com/edithatogo/dnz.git` |
| **Repo type** | Node.js (`package.json`) |
| **Registered submodule?** | Yes (`.gitmodules` entry, `git submodule status` shows it) |
| **Is it a real repo with clean boundary?** | Yes — standalone remote, standard Node project layout, clear purpose. |
| **Should it be a submodule?** | Already **is** a submodule. This is appropriate. |

**Verdict:** dnz is a Node.js project, already properly registered as a submodule. No action needed.

---

## 6. Additional Submodules (not in scope but noted)

The `.gitmodules` file also tracks these subrepos not in the task scope:

| Submodule | Remote |
|---|---|
| `open_social_data` | `https://github.com/edithatogo/open_social_data.git` |
| `openfisca-aotearoa` | `https://github.com/edithatogo/openfisca-aotearoa.git` |
| `sourceright` | `https://github.com/edithatogo/sourceright.git` |

`sourceright` shows a `+` prefix in `git submodule status`, meaning its checked-out commit differs from the superproject's index.

---

## Summary

- **index.lock:** None found in any subrepo — all clean.
- **Dirtiest subrepo:** `corpus-nz-hansard` — extensive staged and unstaged changes across multiple active tracks (bills API, member identity, parliament website, Wikipedia MP lists).
- **Dirty tracked files (staged-only):** `corpus-nz-hansard` — member_identity_triangulation track files staged plus two `A` (added) scripts.
- **Sm-govt-nz:** Needs `git submodule update` — tracked commit differs from superproject index (`+` prefix).
- **Common untracked pattern:** All subrepos except `sm-govt-nz` and `corpus-cases-medilegal-nz` have learning-system files (`.github/workflows/ci-learning-candidates.yml`, `conductor/`, `scripts/record_learning_candidate.py`).
- **fyi-cli:** Python CLI, registered submodule, agents should document it.
- **dnz:** Node.js project, correctly registered submodule, no action needed.
