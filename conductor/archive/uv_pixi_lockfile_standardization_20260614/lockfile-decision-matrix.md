# Lockfile & Environment Manager Decision Matrix

This document establishes the canonical package and environment management tool for each repository/subproject in the NZ Legislation and Policy workspace.

---

## 1. Classification Matrix

| Subrepo | Classification | Environment Manager | Rationale |
|---|---|---|---|
| **cli-legislation-nz** | `pnpm-primary` | `pnpm` | TypeScript CLI and Node.js-native MCP server. Standard JS/TS ecosystem toolchain. |
| **corpus-law-nz** | `uv-primary` | `uv` | Pure Python legislative data ingestion. No heavy GPU/native dependencies. Fast sync and lock behaviors. |
| **corpus-nz-hansard** | `uv-primary` | `uv` | Pure Python parser and processing. Standardizes on `uv.lock` for Windows and Linux CI speed. |
| **corpus-cases-medilegal-nz** | `uv-primary` | `uv` (transitional) | Originally used Pixi but contains only standard web-scraping and text-extraction libraries. Bumping to `uv` simplifies local caching. |
| **hathi-nz** | `pixi-primary` | `pixi` | Ingests data from HathiTrust; requires robust Conda-forge binary packaging environment for historical text tools. |
| **nlp-policy-nz** | `pixi-primary` | `pixi` | The core machine-learning, model-fine-tuning, and vector-database engine. Requires complex native binary compilation, CUDA toolkits, PyTorch GPU configurations, and C++ extensions (`bitsandbytes`, `faiss-cpu`, `spaCy`) which are optimally resolved and sandboxed by Pixi. |
| **sm-govt-nz** | `uv-primary` | `uv` | Simple Python social media archiver with web and API scrapers. No native binaries. |

---

## 2. Manager Comparison & Selection Guiding Principles

### 2.1 Why `uv` for Python Ingestion & Pipelines?
- **Speed:** Locks and installs dependencies up to 10–100x faster than standard pip/poetry, reducing CI bottlenecks.
- **Simplicity:** Integrates natively with `actions/setup-python` and GitHub Actions environments.
- **Single-file lock:** `uv.lock` is cross-platform and highly legible.

### 2.2 Why `pixi` for ML and Research Environments?
- **Multi-language and Native Binaries:** Manages CUDA toolkits, system libraries, and compiled dependencies without relying on hosts' pre-installed headers.
- **Robustness:** Resolves binary package conflicts before running pip-dependency installations.
- **Isolation:** Conda-forge packages run cleanly in isolated user spaces, avoiding DLL conflict errors on Windows runner environments.

---

## 3. Implementation Rules

1. **Lockfile Enforcement:** All `*-primary` repositories must commit their respective lockfiles (`uv.lock`, `pixi.lock`, or `pnpm-lock.yaml`) and verify lock consistency in CI.
2. **No Manager Drift:** Do not mix `uv sync` and `pixi run` inside the same submodule context as primary installers unless explicitly transitioning.
