# Specification: Dataset-Specific Ingestion & Independent Release Pipelines

## Overview
This track focuses on hardening each individual data ingestion pipeline (`corpus-law-nz`, `corpus-nz-hansard`, etc.) and treating their data outputs as independently versioned releases. We will standardise the sync architecture, enforce cryptographic checks (using SHA256 checksums) to prevent redundant computation, and establish separate CI/CD workflows to publish updates to Hugging Face and Zenodo based on dataset-specific triggers.

## Scope & Features
1. **Idempotence & Checksum Guards:** Implement SHA256 hash checks on raw files to ensure the pipeline skips processing when content has not changed.
2. **Independent Dataset Versioning:** Treat each dataset (Legislation, Hansard, Case Law) as an independent release artifact. Establish semantic or date-based version tagging.
3. **GitHub Actions Workflows:** Create workflows that build, validate schemas, and publish updates to Hugging Face Datasets or draft annual Zenodo records.
4. **Error Handling & Resiliency:** Add retry mechanisms and diagnostic logs for external API rate-limiting or network issues.
