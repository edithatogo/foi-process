# Specification: Workspace Doctor Diagnostic Tool

## Overview
As the workspace contains multiple independent subprojects written in different languages (TypeScript, Python), developers and pipelines need a quick and reliable way to verify that their local environment is correctly configured. The `workspace-doctor` tool will scan the workspace, check dependencies, verify critical environment variables, and perform basic connectivity checks to external APIs.

## Scope & Features

### 1. Diagnostic Checks
- **Subproject Scans:** Check if dependency manifests (`package.json`, `requirements.txt`, etc.) are present and if dependencies are installed.
- **Environment Variables:** Verify presence of required keys:
  - `NZ_LEGISLATION_API_KEY` (NZ Legislation API)
  - `HF_TOKEN` (Hugging Face API)
  - `ZENODO_TOKEN` (Zenodo API)
- **API Connectivity:** Perform quick, lightweight checks to verify API credentials work and endpoints are reachable.
- **Language Runtimes:** Check if Node.js (and `npm` or `pnpm`) and Python 3.10+ (and `uv`) are installed and meet version requirements.

### 2. Output Formatting
- Provide a clean console output with clear green checkmarks for success and red crosses for failure.
- Print advice or resolution steps for any failed checks.
- Support exit code `0` for success and `1` if any check fails (critical for CI environments).

## Technical Architecture
- The tool will be implemented as a lightweight Python script or Node.js tool at the workspace root.
- Since Python is widely used in the data pipelines, a simple, typed Python script `scripts/workspace_doctor.py` using standard libraries and standard tools (like `ruff` and strict typing) is proposed.
