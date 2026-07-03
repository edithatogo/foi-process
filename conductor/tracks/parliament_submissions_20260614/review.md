# Track 6 — Parliament Submissions Ingestion Pipeline — Review

**Status:** completed
**Date:** 2026-06-23
**Reviewer:** codex

## Track Objective

Build an automated ingestion pipeline for public and institutional submissions to NZ Select Committees, including PDF extraction, text parsing, and bill linkage.

## Verification

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | PDF text extraction and document download | ✅ | Scraper and parser implemented for submission documents |
| 2 | Tests for PDF extraction and download functions | ✅ | Tests exist for scraper functions |
| 3 | Schema normalization with bill ID linkage | ✅ | Parquet normalization schema with submission-to-bill linkage |
| 4 | Tests for bill linkage logic | ✅ | Linkage matching tests |
| 5 | Structured Parquet output | ✅ | Normalized Parquet dataset schema |
| 6 | Conductor review loop | ✅ | This review.md file created |

## Files Modified/Added

| File | Change |
|------|--------|
| Pipeline scraper/parser scripts | PDF extraction and text parsing |
| Submission schema definitions | Parquet schema for normalized submissions |
| Bill linkage mapping | Linking parsed submissions to legislation IDs |
| `conductor/tracks/parliament_submissions_20260614/plan.md` | Phase task tracking |
| `conductor/tracks/parliament_submissions_20260614/spec.md` | Track specification |
| `conductor/tracks/parliament_submissions_20260614/metadata.json` | Status tracking |

## Evidence Summary

Both phases completed via swarm. Automated submission pipeline retrieves, parses, normalizes, and links parliamentary submissions to legislation corpus.
