# Product Guidelines - NZ Legislation and Policy Workspace

## 1. Architectural Principles

### 1.1 API-First and CLI-First Design
- Every tool, parser, and pipeline in the workspace must be executable via a clean command-line interface (CLI) or exposed as a Model Context Protocol (MCP) tool.
- CLIs must support help flags (`--help`), standard exit codes (0 for success, non-zero for failures), and structured outputs (such as JSON or CSV) for easy automation.
- All primary functions should be modular and importable as a library, ensuring that the CLI is simply a thin wrapper over the core business logic.

### 1.2 Strict Separation of Code and Data
- The Git repository must remain lightweight, containing only code, tests, schemas, configuration files, and small test fixtures.
- Raw and compiled datasets (Parquet, JSON Lines, SQLite databases) must not be checked into Git. Instead, they should be stored on remote storage (such as Hugging Face Datasets or Zenodo) and referenced via metadata manifests and checksums (`content_sha256`).

### 1.3 Idempotency and Reproducibility
- All data ingestion, synchronization, and cleaning workflows must be completely idempotent. Re-running a pipeline must not duplicate records or cause unnecessary writes if the source data has not changed.
- Use cryptographic checksums (`content_sha256`) to compare remote and local states to avoid redundant uploads or compute cycles.

## 2. Coding & Quality Standards

### 2.1 Comprehensive Testing
- Every subproject must maintain a robust test suite. Use `vitest` for TypeScript/JavaScript codebases and `pytest` for Python data pipelines.
- Code changes must include unit tests for new logic and integration tests for CLI tools and end-to-end data flows.

### 2.2 Configuration and Environment Variables
- Hardcoded credentials or environment-specific values are strictly prohibited.
- Configuration must be managed through standard environment variables (e.g., `NZ_LEGISLATION_API_KEY`, `HF_TOKEN`, `ZENODO_TOKEN`) or local configuration files (`.env`).
- Provide `.env.example` templates for all configurable subprojects.

## 3. Tooling, Linting & Typing

### 3.1 Python Linting, Formatting, and Typing
- **Ruff:** Use Ruff for as much as possible (linting, code formatting, and import sorting). Enable strict, bleeding-edge configurations (e.g., enabling `ALL` rules, strict complexity thresholds, and aggressive autofix).
- **Static Typing:** Enforce strict, bleeding-edge static type checking for all Python code. Leverage modern Python typing features (PEP 585, PEP 604) and run type checkers (like `pyright` or `mypy`) under their strictest settings (no implicit `Any`, strict optional, etc.) to guarantee type safety.

### 3.2 TypeScript/JavaScript Tooling
- Use ESLint and Prettier with strict TypeScript compiler options (`strict: true`, no implicit `any`) to maintain type-safe development across the JS/TS codebases.

## 4. Documentation Standards

### 4.1 Self-Documenting Repositories
- Each subproject directory must contain a comprehensive `README.md` explaining installation, local development, test execution, and deployment instructions.
- Document all CLI commands, arguments, and environment variables.
