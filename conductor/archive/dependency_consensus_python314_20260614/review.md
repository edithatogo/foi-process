# Track 12 — Dependency Consensus Baseline and Python 3.14 Runtime Policy — Review

**Status:** Phase 2 & 3 Complete [7cb500b]
**Date:** 2026-06-23
**Reviewer:** codex

## Track Objective

Create a consensus dependency baseline for all subrepos, establish Python 3.14 as the target runtime, and produce per-subrepo maturity checklists with blocker documentation.

## Phase 1 Verification

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Python subrepo inventory (pyproject.toml, lockfiles, CI versions, imports) | ✅ | `python314-inventory.md` documents all 6 Python subrepos |
| 2 | Dependency policy matrix in nlp-policy-nz | ✅ | `nlp-policy-nz/conductor/dependency-policy-matrix.md` — 26 categories |
| 3 | Per-subrepo maturity checklists | ✅ | 6 checklists across all Python subrepos |
| 4 | Python 3.14 blocker assessment | ✅ | `python314-blockers.md` — 16 package assessment |
| 5 | Subrepo commits for all checklist/inventory tasks | ✅ | 6 subrepo commits (Phase 1) |
| 6 | Phase 1 committed at root [e73bdbc] | ✅ | Root commit e73bdbc |

## Phase 2 Verification — Python 3.14 CI Promotion

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | **sm-govt-nz**: requires-python `>=3.14`, CI simplified to single 3.14 matrix | ✅ | commit f4c7077 — pure Python deps (loguru only), safe promotion |
| 2 | **corpus-cases-medilegal-nz**: new CI test workflow with 3.12+3.14 matrix | ✅ | commit dd74a4f — `.github/workflows/tests.yml` created |
| 3 | **corpus-law-nz**: ruff target-version py311→py314 | ✅ | commit 8b78e77 |
| 4 | **nlp-policy-nz**: ruff target-version py311→py314 | ✅ | commit 285dfcf |
| 5 | **hathi-nz**: ruff target-version py311→py314 | ✅ | commit 982f9ea |
| 6 | root submodule pointers updated | ✅ | commit 7cb500b |
| 7 | CI verification on GitHub Actions | ⏳ | Gated — no runner access in session |

## Phase 3 Verification — Version Consistency & Loguru Adapters

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | **corpus-cases-medilegal-nz**: version consistency script + test | ✅ | 4 files: `scripts/check_version_consistency.py`, `tests/test_version_consistency.py` |
| 2 | **nlp-policy-nz**: version consistency script + test | ✅ | 4 files: `scripts/check_version_consistency.py`, `tests/test_version_consistency.py` |
| 3 | **sm-govt-nz**: version consistency script + test | ✅ | 4 files: `scripts/check_version_consistency.py`, `tests/test_version_consistency.py` |
| 4 | **hathi-nz**: version consistency script + test | ✅ | 4 files: `scripts/check_version_consistency.py`, `tests/test_version_consistency.py` |
| 5 | **corpus-law-nz** version consistency (already existed) | ✅ | Pre-existing `scripts/check_version_consistency.py` |
| 6 | **corpus-nz-hansard** version consistency (already existed) | ✅ | Pre-existing `scripts/check_release_version_consistency.py` |
| 7 | Loguru adapters | ⏳ | Deferred — requires CI proof of install per plan |

## Known Blockers

| Issue | Affected subrepos | Impact |
|-------|-------------------|--------|
| spacy has no cp314 wheels on PyPI | nlp-policy-nz | Cannot promote requires-python >=3.14 |
| bitsandbytes also blocked | nlp-policy-nz | Cannot promote requires-python >=3.14 |
| torch CUDA index mismatch | corpus-law-nz | requires-python >=3.14 pending CI evidence |
| No CI runner in session | All non-sm-govt-nz | requires-python >=3.14 cannot be verified |
| No remote auth exercised | Root + all subrepos | Cannot push to origin |

## Phase 1 Deliverables

| Artifact | Location |
|----------|----------|
| Subrepo inventory | `conductor/archive/dependency_consensus_python314_20260614/python314-inventory.md` |
| Dependency policy matrix | `nlp-policy-nz/conductor/dependency-policy-matrix.md` |
| Python 3.14 nlp readiness | `nlp-policy-nz/conductor/python314-readiness.md` |
| Blocker assessment | `conductor/archive/dependency_consensus_python314_20260614/python314-blockers.md` |
| Maturity checklists | Per-subrepo `conductor/maturity-checklist.md` files |

## Subrepo Commit SHAs (This Session)

| Subrepo | SHA | Changes |
|---------|-----|---------|
| sm-govt-nz | f4c7077 | requires-python >=3.14, CI simplified, version consistency test |
| corpus-cases-medilegal-nz | dd74a4f | CI workflow, target py314, version consistency test |
| corpus-law-nz | 8b78e77 | target ruff py314 |
| nlp-policy-nz | 285dfcf | target ruff py314, version consistency test |
| hathi-nz | 982f9ea | target ruff py314, version consistency test |
| Root | 7cb500b | Submodule pointer updates + conductor metadata |

## Recommendations for Future Sessions

1. Push all commits to origin once auth is configured
2. Monitor GitHub Actions results for the new CI workflows
3. Once CI proves green, promote requires-python >=3.14 for corpus-law-nz, hathi-nz, corpus-cases-medilegal-nz
4. Re-evaluate nlp-policy-nz when spacy publishes cp314 wheels
5. Implement Loguru adapters per plan Phase 3 task 3
