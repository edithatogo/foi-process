# Specification: Monorepo Dependency & Typing Modernization

## Overview
To achieve SOTA and bleeding-edge quality across this monorepo, we must modernize dependencies and enforce the strictest coding standards. This track involves updating all subprojects' Python dependencies to leverage advanced data manipulation features (such as modern PyArrow datasets), setting up aggressive Ruff rules (`ALL` by default, strict lint fixes), and implementing strict TypeScript configuration options in `cli-legislation-nz`.

## Scope & Features
1. **Python Dependency Modernization:** Audit Python requirements and transition to modern libraries. Utilize `pyarrow` datasets for partitioned Parquet writes, and `pydantic` v2 for type validation.
2. **Strict Ruff Integration:** Configure a top-level `pyproject.toml` or individual project settings with strict Ruff guidelines (enforcing code formatting, type annotations, and import ordering).
3. **Strict Static Typing Verification:** Implement strict static checking via Pyright/mypy for Python and configure `tsconfig.json` in JS/TS folders with the strictest type rules.
