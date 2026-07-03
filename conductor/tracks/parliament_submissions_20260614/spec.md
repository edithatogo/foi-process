# Specification: Parliament Submissions Ingestion Pipeline

## Overview
This track builds an automated ingestion pipeline for public and institutional submissions made to NZ Select Committees regarding active or historical bills. Submissions represent a rich text corpus containing expert legal analysis, advocacy viewpoints, and policy debates.

## Scope & Features
1. **API / Scraper Connector:** Create an interface to query and download submission documents (typically PDFs or HTML transcripts) from the official NZ Parliament portal.
2. **PDF Text Extraction & OCR:** Implement a parser to extract clean raw text and metadata (author, date, related bill, committee name) from submissions.
3. **Data Normalization:** Clean and structure the extracted content into a standard Parquet format.
4. **Linkage to Legislation:** Model relationships between submissions and the unique bill IDs in the legislation corpus.
