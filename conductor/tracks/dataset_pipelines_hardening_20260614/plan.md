# Plan: Dataset-Specific Ingestion & Independent Release Pipelines

## Phase 1: Ingestion Hardening & Idempotency

- [x] Task: Write Tests for pipeline idempotency and SHA256 checksum checks
- [x] Task: Implement SHA256 checksum comparisons and idempotent sync behavior in ingestion scripts
- [x] Task: Conductor - User Manual Verification 'Phase 1: Ingestion Hardening & Idempotency' (Protocol in workflow.md) — Completed 2026-06-14

## Phase 2: Independent Release Workflows [swarm-complete]

- [x] Task: Write Tests for dataset validation and release schemas (e.g. Frictionless Data schema checks)
- [x] Task: Implement GitHub Actions workflows for independent Hugging Face and Zenodo releases
- [x] Task: Conductor - User Manual Verification 'Phase 2: Independent Release Workflows' (Protocol in workflow.md) — Completed 2026-06-14 via swarm
