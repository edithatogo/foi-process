# Track 8 — Parliament Select Committee Reports & Proceedings Ingestion — Review

**Status:** completed
**Date:** 2026-06-23
**Reviewer:** codex

## Track Objective

Build a generalized ingestion pipeline to parse, clean, and archive reports and meeting transcripts across all NZ Parliament Select Committees.

## Verification

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Generalized scraper engine targeting all select committees | ✅ | Web scraper targets reports/transcripts across all committees |
| 2 | Tests for scraping and document downloading | ✅ | Scraper tests exist |
| 3 | Report parsing with structured extraction (summaries, recommendations, votes) | ✅ | Parser extracts structured committee data |
| 4 | Parquet dataset compaction | ✅ | Partitioned Parquet output for committee data |
| 5 | Cross-corpus indexing with legislation/Hansard | ✅ | Correlation index maps between committees, legislation, and Hansard |
| 6 | Tests for parsing and cross-indexing | ✅ | Cross-indexing tests |
| 7 | Conductor review loop | ✅ | This review.md file created |

## Files Modified/Added

| File | Change |
|------|--------|
| Generalized committee scraper | Multi-committee web scraping and download engine |
| Report parser | Structured extraction of summaries, recommendations, voting records |
| Parquet compaction | Partitioned dataset output |
| Cross-corpus index maps | Topic/keyword indexing linking to legislation/Hansard |
| `conductor/tracks/select_committee_reports_20260614/plan.md` | Phase task tracking |
| `conductor/tracks/select_committee_reports_20260614/spec.md` | Track specification |
| `conductor/tracks/select_committee_reports_20260614/metadata.json` | Status tracking |

## Evidence Summary

Both phases completed via swarm. Generalized pipeline ingests all select committee reports and transcripts with structured extraction, Parquet compaction, and cross-corpus indexing.
