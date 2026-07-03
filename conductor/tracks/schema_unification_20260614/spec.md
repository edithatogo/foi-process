# Track Specification: Canonical Schema Unification & Multi-Corpus Feature Extraction

## Overview
Unify scattered JSON schemas into a single canonical, additive system hosted within the `nlp-policy-nz` directory. Ensure the NLP pipeline parses and extracts features matching the new additive schemas (Parliament Submissions, Regulations Review, and Select Committee Reports). Automate repository updates, push commits to GitHub, and systematize Hugging Face, Zenodo, and GitHub configurations.

## Functional Requirements
1. **Canonical Schema System**:
   - Establish `nlp-policy-nz/schemas/` as the single canonical schema repository.
   - Unify `shared_nz_corpus_core.schema.json` into an additive core schema containing all fields from both legislation and hansard (e.g., `display_title`, `language`, `coverage_status`, `rights_note`, `record_schema_version` pattern `^v?[0-9]+...`, and full 11-value `document_type` enum).
   - Sync/link canonical schemas down to `corpus-law-nz/schemas/` and `corpus-nz-hansard/schemas/`.
2. **Additive Feature Extraction**:
   - Update `PipelineRecord` msgspec.Struct in `nlp_policy_nz/storage/serialization.py` with additive fields for submissions (e.g., `submitter_name`, `committee`, `bill_reference`, `linkage_confidence`, `challenged_regulation`, `grounds`).
   - Standardize and implement NLP extraction routines to parse these committee features from Hansard and legislative sources.
3. **Repository Sync & Account Systematization**:
   - Check local credentials and environment synchronization (`.env`).
   - Git commit and push all updated nested subprojects to their GitHub origin repositories (`edithatogo`).
   - Verify and test Hugging Face and Zenodo API integrations.

## Acceptance Criteria
- `workspace-doctor` passes validation.
- Centralized schemas are valid JSON schemas.
- `nlp-policy-nz` pipeline runs and outputs Parquet datasets with all unified fields populated.
- Git repositories are clean and pushed to GitHub.
- Hugging Face and Zenodo datasets/depositions are updated/cataloged.
