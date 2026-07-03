# Technology Stack - NZ Legislation and Policy Workspace

This document defines the approved programming languages, libraries, tools, and runtimes used across all projects in the workspace.

## 1. Programming Languages

### 1.1 TypeScript / JavaScript
- Used for CLI tools, MCP (Model Context Protocol) servers, and developer integrations.
- Target runtime: Node.js (Active LTS versions).
- Packaging & Transpilation: `tsup` for fast bundling, `tsconfig.json` configured for strict type-checking and modern JavaScript output.

### 1.2 Python
- Used for data ingestion pipelines, parser scripts, and natural language processing tasks.
- Target runtime: Python 3.10+ (bleeding-edge type features preferred).
- Typing: Strict static typing using standard `typing` module, PEP 585 (generics in built-in types), and PEP 604 (union operator `|`).

## 2. Dependency & Package Management

### 2.1 Node.js
- Package manager: `npm` / `pnpm` as defined per project subdirectory.
- Dependencies are locked via `package-lock.json` or `pnpm-lock.yaml`.

### 2.2 Python
- Package manager: `uv` for lightning-fast, reproducible dependency installations and virtual environment management.
- Dependency tracking: `requirements.txt` or `pyproject.toml` per project directory.

## 3. Data & Storage Technologies

### 3.1 Storage Formats
- **Parquet:** Used as the primary distribution format for structured legislation and debate corpora. Leverages `pyarrow` and `pandas` for compression and high-performance querying.
- **JSON Lines (.jsonl):** Used for raw/normalized intermediate streams.
- **SQLite:** Used for lightweight relational caching or local query storage when needed.

### 3.2 APIs and Remote Integrations
- **Official NZ Legislation API:** Source for raw legislation data.
- **Hugging Face Datasets:** Remote repository for hosting the live Parquet datasets. Integrates via `huggingface_hub` Python package.
- **Zenodo API:** Target for annual archival snapshots and persistent DOI generation.

## 4. Testing Frameworks

### 4.1 Vitest
- Primary testing tool for JavaScript and TypeScript projects. Supports fast watch modes, ESM-first execution, and native coverage.

### 4.2 Pytest
- Primary testing framework for Python projects. Handles unit tests for data extraction logic, mock API responses, and pipeline schema validation.

## 5. UI & Presentation

### 5.1 Gradio
- Lightweight, Python-based UI framework used for hosting NLP policy classification and analysis tools in Hugging Face Spaces.
