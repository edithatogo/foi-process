# Specification: Workspace Environment Variables Synchronization

## Overview
This chore sets up a centralized environment variables management system for the workspace. Since the workspace consists of multiple subprojects, a master `.env` file at the root acts as the single source of truth for shared credentials (such as Hugging Face, Zenodo, and legislation API keys). A synchronization script propagates these shared keys down to individual subprojects.

## Scope & Features
1. **Master Root Env File:** Create a central `.env` file at the root containing shared keys and active environment values.
2. **Synchronization Script:** Implement a Python script ([`sync_env.py`](file:///C:/Users/60217257/.gemini/antigravity-cli/brain/21575cc5-41eb-413e-9fc3-3c3c4c781262/scratch/sync_env.py)) to copy shared keys from the root `.env` down to all subprojects while preserving local project-specific variables.
3. **Environment Setup for All Repos:** Enforce that all subprojects have a local `.env` (or `.env.local`) file containing the shared credentials.

## Acceptance Criteria
- A root `.env` file exists at the root of the workspace.
- All 6 subprojects have their own local `.env` (or `.env.local`) files populated with the shared credentials.

## Out of Scope
- Automated drift checks integrated into CI/CD pipelines.
