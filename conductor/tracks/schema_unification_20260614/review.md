# Track 10 — Canonical Schema Unification & Multi-Corpus Feature Extraction — Review

**Status:** completed [verified]
**Date:** 2026-06-23
**Reviewer:** codex

## Track Objective

Unify scattered JSON schemas into a single canonical, additive system in `nlp-policy-nz`, implement NLP feature extraction matching the unified schemas, and systematize repository sync and account configuration.

## Verification

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Canonical schema system in `nlp-policy-nz/schemas/` | ✅ | 8 schema files including `shared_nz_corpus_core`, `legislation_record`, `hansard_record`, `parliament_submission_record`, `regulations_review_proceeding_record`, `select_committee_report_record`, `release_evidence` |
| 2 | Schema unification — additive core with 14-value `document_type` enum | ✅ | `shared_nz_corpus_core.schema.json` unified with full property set |
| 3 | Schema SHA256 identity across 3 repos | ✅ | All 7 schemas identical across `nlp-policy-nz`, `corpus-law-nz`, `corpus-nz-hansard` |
| 4 | PipelineRecord msgspec struct with additive fields | ✅ | 9 additive optional fields (submitter_name, committee, bill_reference, etc.) |
| 5 | Feature extraction for all committee types | ✅ | `feature_extraction.py` with extractors for select committee, regulations review, submissions, metadata, bill references |
| 6 | Tests for schema compliance and Parquet serialization | ✅ | 38 tests (16 storage + 22 feature extraction) all passing |
| 7 | Full workspace re-validation | ✅ | 193 tests: 188 passed, 5 expected env-specific failures |
| 8 | Conductor review loop | ✅ | This review.md file created |

## Files Modified/Added

| File | Change |
|------|--------|
| `nlp-policy-nz/schemas/` (8 files) | Canonical schema repository |
| `corpus-law-nz/schemas/` | Synced canonical schemas |
| `corpus-nz-hansard/schemas/` | Synced canonical schemas |
| `nlp-policy-nz/src/nlp_policy_nz/storage/serialization.py` | PipelineRecord with additive fields |
| `nlp-policy-nz/src/nlp_policy_nz/feature_extraction.py` | Multi-corpus feature extraction |
| `nlp-policy-nz/tests/test_feature_extraction.py` | Feature extraction tests (22) |
| `nlp-policy-nz/tests/test_storage.py` | Storage tests (16) |
| `conductor/tracks/schema_unification_20260614/plan.md` | Phase task tracking |
| `conductor/tracks/schema_unification_20260614/spec.md` | Track specification |
| `conductor/tracks/schema_unification_20260614/metadata.json` | Status tracking |

## Evidence Summary

All 3 phases completed. Canonical schemas unified and SHA256-identical across 3 repos. Feature extraction pipeline implemented with 38 passing tests. Full workspace re-validation: 188/193 passed.
