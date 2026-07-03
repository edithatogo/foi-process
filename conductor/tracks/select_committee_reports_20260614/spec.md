# Specification: Parliament Select Committee Reports & Proceedings Ingestion

## Overview
NZ Parliament Select Committees publish reports on bills, conduct briefings, and produce transcripts of proceedings. This track builds a generalized ingestion pipeline to parse, clean, and archive reports and meeting transcripts across all committees, allowing researchers to study select committee work comprehensively.

## Scope & Features
1. **General Scraper & Downloader:** Build a web scraper targeting reports and transcripts of all NZ Parliament Select Committees (e.g., Health, Justice, Finance).
2. **Text Parsing & Structured Extraction:** Parse HTML/PDF reports to extract executive summaries, recommendations, voting records, and transcript dialogues.
3. **Database Schema & Parquet Compactor:** Compact the structured reports and transcripts into a partitioned Parquet dataset.
4. **Keyword & Topic Indexing:** Build indexes matching select committee topics back to related legislation and Hansard debates.
