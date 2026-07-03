# Track 21 Phase 2: Per-Repo CLI Maturity Audit

**Date:** 2026-06-23
**Scope:** All 9 subrepos under `legal-nz/` root orchestration repo
**Policy mandate:** CLI-First Tooling — agents must use existing CLIs before writing custom one-off code

---

## cli-legislation-nz

| Category | Status | Details |
|----------|--------|---------|
| package.json scripts | ✅ | `dev`, `dev:mcp`, `build`, `start`, `start:mcp`, `test`, `test:run`, `test:coverage`, `bench`, `lint`, `lint:fix`, `typecheck`, `format`, `format:check`, `gate:*` (9 gate scripts), `docs:*` |
| package.json bin | ✅ | `nzlegislation`, `nzlegislation-mcp`, `anzlegislation`, `anzlegislation-mcp` (all → `dist/cli.js` / `dist/mcp-cli.js`) |
| pyproject.toml CLI entrypoints | ❌ | TypeScript/Node project — no pyproject.toml |
| Makefile targets | ❌ | No Makefile |
| scripts/ directory | ✅ | 16 files — TypeScript (`bundle-analyze.ts`, check scripts, `smoke-install-snippets.ts`, `load-test.ts`) + `.ps1`/`.sh` release scripts |
| Existing CLI packages | ✅ | `src/commands/`, `src/cli.ts`, `src/mcp-cli.ts` — full Commander.js CLI with search, retrieve, export, cite commands |
| README CLI docs | ✅ | Excellent — CLI install, usage, MCP server setup, feature list documented |
| **Overall CLI maturity** | **high** | Published npm package with 4 binary entrypoints, full Commander.js CLI, MCP server, extensive test/quality gates |

---

## nlp-policy-nz

| Category | Status | Details |
|----------|--------|---------|
| package.json scripts | ❌ | Only `docs:dev`, `docs:build`, `docs:check` |
| pyproject.toml CLI entrypoints | ✅ | `nlp-policy-nz = "nlp_policy_nz.cli.main:main"` |
| Makefile targets | ❌ | No Makefile |
| scripts/ directory | ✅ | 24 files — benchmark, evaluation, finetune scripts (`.py` + `.sh`), `profile_pipeline*.py`, `record_learning_candidate.py` |
| Existing CLI packages | ✅ | `src/nlp_policy_nz/cli/main.py` + `cli/graph.py` — argparse CLI with 6+ subcommands: `process`, `search`, `upload-dataset`, `deploy-space`, `archive-to-zenodo`, `release`, `export-kg` |
| README CLI docs | ✅ | Well-documented with process, search, upload, deploy, archive, release examples |
| **Overall CLI maturity** | **high** | Published Python PyPI package with full argparse CLI, multiple subcommands, HuggingFace + Zenodo integration |

---

## corpus-law-nz

| Category | Status | Details |
|----------|--------|---------|
| package.json scripts | ❌ | Only `docs:dev`, `docs:build`, `docs:check` |
| pyproject.toml CLI entrypoints | ✅ | `nzlc = "nz_legislation_corpus.cli:app"` |
| Makefile targets | ✅ | `.PHONY: install test smoke validate manifest archive quality format-check type-check bootstrap-github first-run` — 10+ documented targets |
| scripts/ directory | ✅ | 19 files — bash bootstrap scripts (`.sh`), Python check scripts (`check_*.py`), `profile_ingestion.py` |
| Existing CLI packages | ✅ | `src/nz_legislation_corpus/cli.py` — Typer CLI app with commands: `sync`, `validate`, `manifest`, `archive`, `feed`, `discovery`, `bootstrap-review`, `zenodo-upload`, `normalize`, `metadata-packages` |
| README CLI docs | ✅ | Mermaid flowchart documents `nzlc sync` pipeline, CLI-first design mentioned |
| **Overall CLI maturity** | **high** | Published Python CLI with Typer/rich, complete Makefile, full pipeline automation through `nzlc` command |

---

## corpus-nz-hansard

| Category | Status | Details |
|----------|--------|---------|
| package.json scripts | ❌ | Only `docs:dev`, `docs:build`, `docs:check` |
| pyproject.toml CLI entrypoints | ✅ | `corpus-nz-hansard` and `nz-hansard-corpus` both → `scripts.cli:main` |
| Makefile targets | ✅ | 50+ .PHONY targets — comprehensive: `quality`, `lint`, `format-check`, `typecheck`, `test`, `test-offline`, `benchmark`, `profile-search-index`, `security-audit`, `sbom`, `mutation-smoke`, plus 40+ build/check targets |
| scripts/ directory | ✅ | 134 files — extremely deep collection: `build_*.py`, `check_*.py`, `fetch_*.py`, `generate_*.py`, `upload_*.py`, `validate_*.py`, plus `cli.py` dispatcher, committee reports, select committee scripts |
| Existing CLI packages | ✅ | `scripts/cli.py` — argparse dispatcher routing to 12 commands: `duckdb`, `hf-stage`, `hf-upload`, `inventory`, `normalize`, `quality-gate`, `release-package`, `schema`, `search-index`, `validate-records`, `zenodo-build`, `zenodo-upload` |
| README CLI docs | ⚠️ | Shows direct `python scripts/*.py` invocations; does NOT document the `corpus-nz-hansard` CLI command or `--list` flag |
| **Overall CLI maturity** | **medium** | CLI dispatcher exists with 12 commands but README is script-invocation oriented; 134 scripts suggest consolidation candidates |

---

## corpus-cases-medilegal-nz

| Category | Status | Details |
|----------|--------|---------|
| package.json scripts | ❌ | Only `docs:dev`, `docs:build`, `docs:check` |
| pyproject.toml CLI entrypoints | ✅ | `corpus-cases-medilegal-nz` and `nz-medilegal-corpus` both → `corpus_cases_medilegal_nz.cli:main` |
| Makefile targets | ❌ | No Makefile |
| scripts/ directory | ❌ | 4 files — `benchmark_selectolax_parser.py`, `check_version_consistency.py`, `profile_pipelines.py`, `record_learning_candidate.py` |
| Existing CLI packages | ✅ | `src/corpus_cases_medilegal_nz/cli.py` — minimal argparse CLI with 2 commands: `sources` (list sources), `sync` (run HF sync pipeline) |
| README CLI docs | ❌ | Shows Python/DuckDB library usage only; no CLI command documentation |
| **Overall CLI maturity** | **low** | CLI entrypoints exist but surface is minimal (2 commands); no Makefile; undocumented in README |

---

## hathi-nz

| Category | Status | Details |
|----------|--------|---------|
| package.json scripts | ❌ | Only `docs:dev`, `docs:build`, `docs:check` |
| pyproject.toml CLI entrypoints | ✅ | `hathi-nz` and `nz-hathi-corpus` both → `scripts.cli:main` |
| Makefile targets | ❌ | No Makefile |
| scripts/ directory | ✅ | 13 files — `fetch_hathitrust.py`, `ocr_extract.py`, `package_release.py`, `publish_zenodo.py`, `stage_hf_dataset.py`, `upload_hf_dataset.py`, `validate_catalog.py`, `cli.py` dispatcher, plus support scripts |
| Existing CLI packages | ✅ | `scripts/cli.py` — argparse dispatcher with 7 commands: `fetch`, `ocr`, `package`, `publish-zenodo`, `stage`, `upload`, `validate` |
| README CLI docs | ⚠️ | Shows direct `python scripts/*.py` invocations in pipeline usage section; does NOT document `hathi-nz` CLI command |
| **Overall CLI maturity** | **medium** | CLI dispatcher exists with 7 pipeline commands but README bypasses it; no Makefile |

---

## sm-govt-nz

| Category | Status | Details |
|----------|--------|---------|
| package.json scripts | ❌ | Only `docs:dev`, `docs:build`, `docs:check` |
| pyproject.toml CLI entrypoints | ✅ | `sm-govt-nz` and `nz-govt-social` both → `scripts.cli:main` |
| Makefile targets | ❌ | No Makefile |
| scripts/ directory | ✅ | 60 files — extensive: archive scripts (`archive_*.py`), check scripts (`check_*.py`), probe scripts (`*_probe.py`, `*_dry_run*.py`), `cli.py` dispatcher, `compile_registry.py`, `publish_*.py`, `render_*.py`, `verify_*.py` |
| Existing CLI packages | ✅ | `scripts/cli.py` — argparse dispatcher with 11 commands: `archive-bluesky`, `archive-current`, `archive-email`, `archive-rss`, `check-blockers`, `check-disk`, `compile-registry`, `profile-discovery`, `publish-archives`, `self-eval`, `validate-secrets` |
| CLI-first policy doc | ✅ | `docs/cli-first.md` documents the CLI-first policy explicitly |
| README CLI docs | ❌ | No root-level README.md; has `docs/cli-first.md` but no central README CLI documentation |
| **Overall CLI maturity** | **medium** | Strong CLI dispatcher with documented policy; lacks root README and could benefit from Typer/rich upgrade |

---

## fyi-cli

| Category | Status | Details |
|----------|--------|---------|
| package.json scripts | ❌ | Only `docs:dev`, `docs:build`, `docs:check` |
| pyproject.toml CLI entrypoints | ✅ | `fyi`, `fyi-cli`, `fyi-system` all → `fyi_system.cli:main` |
| Cargo.toml (Rust) | ✅ | Workspace with `crates/fyi-core`, `crates/fyi-cli` (clap + ratatui), `crates/fyi-mcp` |
| Makefile targets | ❌ | No Makefile |
| scripts/ directory | ❌ | 4 files — `autonomous-tracks.py`, `check_conductor_status.py`, `record_learning_candidate.py`, `run_local_cycle.sh` |
| Existing CLI (Python) | ✅ | `src/fyi_system/cli.py` — published PyPI package: `fyi init-db`, `fyi register-request`, `fyi build-prefilled-url`, `fyi list-requests`, `fyi dashboard`, `fyi monitor`, `fyi audit`, `fyi report`, etc. |
| Existing CLI (Rust) | ✅ | `crates/fyi-cli/` — second CLI surface with clap arg parsing, ratatui TUI |
| README CLI docs | ✅ | Excellent — Quick Start shows `fyi init-db`, `fyi register-request`, `fyi build-prefilled-url`, `fyi list-requests`, `fyi dashboard` |
| **Overall CLI maturity** | **high** | Published PyPI package with dual Python+Rust CLI surface, Typer-based commands, web UI, comprehensive README docs |

**Agent guidance:** fyi-cli has a mature CLI surface. Agents should use `fyi <command>` (Python) or the Rust binary. The `fyi` command is the preferred entrypoint.

---

## dnz

| Category | Status | Details |
|----------|--------|---------|
| package.json scripts | ❌ | Only `docs:dev`, `docs:build`, `docs:check` |
| pyproject.toml CLI entrypoints | ❌ | No Python CLI entrypoints defined |
| Cargo.toml (Rust) | ✅ | Workspace: `crates/dnz-core`, `crates/dnz-cli` (clap), `crates/dnz-mcp`, `crates/dnz-python` |
| pixi.toml tasks | ✅ | `build`, `test`, `fmt`, `clippy`, `coverage`, `mutants`, `audit`, `doctor`, `install-hooks`, `verify`, `dry-run-cargo`, `dry-run-maturin`, `dry-run-python` |
| Makefile targets | ❌ | No Makefile |
| scripts/ directory | ❌ | 8 PowerShell scripts — `coverage.ps1`, `workspace-doctor.ps1`, `validate-*.ps1`, `verify-*.ps1`, `tmdl-*.ps1` |
| Existing CLI packages | ✅ | `crates/dnz-cli/` — Rust CLI with clap; `crates/dnz-mcp/` — MCP server; `crates/dnz-python/` — PyO3 Python bindings |
| README CLI docs | ✅ | Documents pixi commands, workspace layout, mentions `dnz` CLI tool |
| Git remote | ✅ | `origin https://github.com/edithatogo/dnz.git` — valid remote |
| Git state | ✅ | `511527c chore-dnz-track13` — active, recent commit |
| **Overall CLI maturity** | **high** | Real Rust workspace with dedicated CLI crate, MCP server, Python bindings; pixi task runner; clean repo boundary |

**Boundary classification:** `dnz` is an independent Rust crate workspace with its own remote on GitHub (`edithatogo/dnz`). It has a clean repository boundary, active git history, and its own CLI (`dnz`), MCP server, and Python bindings. Agents should use `pixi run` tasks or the compiled `dnz` binary. Do NOT treat dnz as a root-embedded utility.

---

## Summary Matrix

| Repo | package.json scripts | pyproject.toml CLI | Makefile | scripts/ | CLI pkg in src | README CLI docs | Maturity |
|------|---------------------|--------------------|----------|----------|----------------|-----------------|----------|
| cli-legislation-nz | ✅ | ❌ (TS) | ❌ | 16 | ✅ commands/ | ✅ | **high** |
| nlp-policy-nz | ❌ | ✅ | ❌ | 24 | ✅ cli/ | ✅ | **high** |
| corpus-law-nz | ❌ | ✅ (nzlc) | ✅ | 19 | ✅ cli.py | ✅ | **high** |
| corpus-nz-hansard | ❌ | ✅ | ✅ | 134 | ✅ cli.py | ⚠️ | **medium** |
| corpus-cases-medilegal-nz | ❌ | ✅ | ❌ | 4 | ✅ cli.py | ❌ | **low** |
| hathi-nz | ❌ | ✅ | ❌ | 13 | ✅ cli.py | ⚠️ | **medium** |
| sm-govt-nz | ❌ | ✅ | ❌ | 60 | ✅ cli.py | ❌* | **medium** |
| fyi-cli | ❌ | ✅ (fyi) | ❌ | 4 | ✅ cli.py + Rust | ✅ | **high** |
| dnz | ❌ | ❌ (Rust) | ❌ | 8 | ✅ dnz-cli (Rust) | ✅ | **high** |

\* `sm-govt-nz` has `docs/cli-first.md` but no root-level README.md.

---

## Recommendations for Phase 3

1. **corpus-nz-hansard:** Update README to document `corpus-nz-hansard` CLI commands instead of raw `python scripts/*.py` invocations. The dispatcher exists (12 commands) but is invisible to agents reading the README.

2. **hathi-nz:** Same pattern — README shows `python scripts/*.py` but should use `hathi-nz <command>`.

3. **corpus-cases-medilegal-nz:** Expand the CLI surface beyond `sources`/`sync` to cover all repeated workflows (e.g., validate, export, report). Add Makefile. Document in README.

4. **sm-govt-nz:** Create a root-level README.md that documents the `sm-govt-nz` CLI commands and references `docs/cli-first.md`.

5. **fyi-cli:** The Python `fyi` CLI is the primary agent surface. The Rust crate appears to be a different/competing implementation — clarify if the Rust `crates/fyi-cli` should be the target or if `src/fyi_system/cli.py` (PyPI published) takes precedence.

6. **dnz:** Already clean boundary. Add the `dnz` CLI to the root CLI registry after verifying it builds successfully. Lock in `pixi run` as the canonical invocation pattern.
