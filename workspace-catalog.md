# Workspace Catalog — NZ Legislation Workspace

> **Generated:** 2026-06-14 | **Role:** Oracle  
> **Scope:** Full topology, schema definitions, dataset mapping, naming conventions

---

## 1. Workspace Topology Map

```text
legal-nz/                                    (Swarm root)
│
├── cli-legislation-nz/                      [TypeScript] CLI + MCP server
├── corpus-law-nz/                            [Python] Legislation corpus pipeline
├── corpus-nz-hansard/                        [Python] Hansard corpus pipeline
├── corpus-cases-medilegal-nz/                [Python] Medical-legal cases pipeline
├── nlp-policy-nz/                            [Python] NLP analysis framework
├── sm-govt-nz/                               [Python] Social media govt archiver
├── hathi-nz/                                 [Python] HathiTrust debates fetcher
├── dnz/                                      [Rust/Python] DigitalNZ API Client & CLI
├── fyi-cli/                                  [Rust/Python] OIA/FYI.org.nz Portal CLI & API
│
├── conductor/                                Orchestration docs, track specs
├── .swarm/                                   Swarm runtime mailboxes/state
├── logs/                                     Shared logs
├── tests/                                    Workspace-level tests
├── .github/
│
├── findings.md, progress.md, task_plan.md
├── swarm-config.yaml, subagents.yaml
├── send_agent_task.py, workspace-doctor.py
└── workspace-catalog.md                      ← THIS FILE
```

---

## 2. Subproject Catalog

### 2.1 `cli-legislation-nz` — NZ Legislation CLI + MCP Server

| Attribute | Value |
|---|---|
| **Language** | TypeScript (ES2022, ESNext modules) |
| **Runtime** | Node.js >= 18.0.0 |
| **Package Manager** | pnpm 10.29.3 |
| **Package** | `nz-legislation-tool` v1.2.0 |
| **Entry Points** | `src/cli.ts` → `dist/cli.js` (bins: `nzlegislation`, `anzlegislation`) |
| | `src/mcp-cli.ts` → `dist/mcp-cli.js` (MCP server bins) |
| **CLI Framework** | `commander` v12 + `chalk` + `cli-table3` |
| **Key Deps** | `got`, `zod`, `winston`, `@modelcontextprotocol/sdk`, `lru-cache`, `conf`, `ora` |
| **Test** | Vitest v4, coverage 60% via v8 |
| **Linting** | ESLint, Prettier, Vale (`write-good` + `NZLegislation` vocab) |
| **Build** | tsc + tsc-alias → `dist/` |
| **CI/CD** | 15 GH Actions workflows |

#### CLI Commands (11)

`search`, `get`, `export`, `cite`, `capabilities`, `config`, `cache`, `batch`, `stream`, `help`, `generate`

#### Architecture

```

src/
├── cli.ts, mcp-cli.ts        # Entry points
├── client.ts                 # HTTP API client (got + LRU cache)
├── config.ts, errors.ts
├── commands/                 # 11 command implementations
├── models/                   # Zod schemas (Work, Version, SearchResults, Citation)
├── output/                   # Table, JSON, CSV, citation formatters
├── providers/                # NZ + Au Commonwealth providers
├── mcp/                      # MCP server
└── utils/                    # Logger, streaming, validation, config

```text

### 2.2 `corpus-law-nz` — Legislation Corpus Pipeline

| Attribute | Value |
|---|---|
| **Language** | Python >= 3.11 |
| **Package Manager** | uv (uv.lock) |
| **Package** | `corpus-legislation-nz` v0.5.0 |
| **Entry Point** | `nzlc` CLI (Typer) — `nz_legislation_corpus.cli:app` |
| **Key Deps** | pyarrow>=21, polars>=1.0, pydantic>=2, huggingface_hub, hf-xet, requests, jsonschema, zstandard |
| **Test** | Pytest + pytest-cov, threshold: **60%** |
| **Linting** | Ruff (target py311, strict), `ty` type checking, Vale |
| **Build** | hatchling |
| **CI/CD** | 16 GH Actions workflows |

#### CLI Commands: `nzlc`

`doctor`, `sync`, `discover-work-ids`, `split-work-id-batches`, `reconcile-work-ids`, `validate`, `manifest`, `metadata-packages`, `validate-metadata-packages`, `hf-upload`, `archive`, `zenodo-upload`, `smoke-fixture`, `coverage-report`, `rss-feed`

#### Modules

```

src/nz_legislation_corpus/
├── cli.py, config.py, types.py, schema.py
├── nz_api.py, normalize.py, extract_text.py, validate.py
├── manifest.py, parquet_writer.py, hf_sync.py, zenodo.py
├── archive.py, discovery.py, embeddings.py, metadata_packages.py
├── rss_feed.py, artifact_provenance.py, osf_optional.py
└── utils.py                   # SHA256 + JSON I/O

```text

#### Data Layout

```

data/                          # Primary data

### 2.3 `corpus-nz-hansard` — Hansard Corpus Pipeline

| Attribute | Value |
|---|---|
| **Language** | Python >= 3.11 |
| **Package Manager** | uv (uv.lock), `tool.uv.package = false` |
| **Package** | `corpus-nz-hansard` v0.2.0 |
| **Entry Point** | N/A — script-based (130+ scripts) |
| **Key Deps** | duckdb==1.5.3, polars>=1.41, pyarrow>=21, huggingface_hub, jsonschema>=4.26, pydantic>=2 |
| **Test** | Pytest + pytest-cov, threshold: **60%** |
| **Linting** | Ruff (py311), ty, taplo, typos, zizmor, Vale |
| **CI/CD** | 9 GH Actions (quality, huggingface_publish, publication_readiness, zenodo_*) |

**⚠️ 130+ flat scripts without module structure — highest duplication risk in workspace.**

#### Data Layout

```text

derived/                       # All derived artifacts
├── bills_api/, corpus_wide_member_identity/, corpus_wide_party_attribution/
├── historical_sitting_official_exports/ (PDF + JSON + indices)
├── historical_sitting_reconciliation/ (Parquet + JSON)
├── parliament_stealth/ (scraped HTML/PNG/TXT)
├── sitting_proceeding_components/, validated_speech_turns/
└── vote_motion_bill_question_extraction/
generated/                     # Build artifacts
fixtures/                      # Gold eval samples, neutral components
manifests/                     # 60+ validation/release manifests
schemas/                       # 43 JSON Schema files
scripts/                       # 130+ scripts (normalize, build, check, fetch, generate)

```text

### 2.4 `corpus-cases-medilegal-nz` — Medical-Legal Cases

| Attribute | Value |
|---|---|
| **Language** | Python >= **3.11** |
| **Package Manager** | pixi + pyproject.toml |
| **Package** | `corpus_cases_medilegal_nz` v0.1.0 |
| **Entry Point** | N/A (early stage) |
| **Key Deps** | polars, pyarrow, pydantic, beautifulsoup4, defusedxml, **nlp_policy_nz** (editable) |
| **Test** | Pytest + pytest-cov, threshold: **80%** |
| **Linting** | Ruff (py311, strict, unified rules), pyright (strict) |
| **CI/CD** | None yet |

```text

src/corpus_cases_medilegal_nz/   → __init__.py, config_models.py, fetcher.py
data/                            → raw/hdc/, processed/{json,jsonl,markdown,parquet,text}/
config/                          → hdc_pipeline.yaml

```text

**⚠️ Python 3.13+ diverges from workspace 3.11 standard. Editable dep on nlp_policy_nz.**

### 2.5 `nlp-policy-nz` — NLP Analysis Framework

| Attribute | Value |
|---|---|
| **Language** | Python >= **3.11** |
| **Package Manager** | uv + **pixi** (dual config) |
| **Package** | `nlp_policy_nz` v0.1.0 |
| **Entry Points** | CLI: `nlp-policy-nz` → `nlp_policy_nz.cli.main:main` |
| | API: `nlp_policy_nz.api.server` (FastAPI) |
| **Key Deps** | spacy>=3.7, transformers>=4.40, torch>=2.2, lancedb, networkx, faiss-cpu, datasets, gradio, fastapi |
| **Test** | Pytest (18 test files) |
| **Linting** | Ruff (py311, unified strict rules), pyright, tach, import-linter, complexipy, mutatest |
| **CI/CD** | 2 workflows (ci, release) |

```text

src/nlp_policy_nz/
├── pipeline_api.py, xml_parser.py, universal_framework.py / v1 / v2 / v3.py
├── api/server.py              # FastAPI
├── cli/main.py, graph.py
├── guard/                     # language_id, normalizer, tokenizer_exceptions
├── integrations/              # dataset_card, data_registry, hf_uploader, zenodo, release
├── semantic/                  # embeddings, finetune, model_loader
├── storage/                   # serialization (msgspec), vectordb (LanceDB)
└── syntactic/                 # chunking, citations, pipeline
data/samples/                  # sample_hansard.txt, sample_legislation.txt
lancedb_data/                  # Vector store (runtime)

```text

**⚠️ Dual uv+pixi config causes ambiguity. Central `data_registry.json` maps all datasets.**

### 2.6 `sm-govt-nz` — Social Media Govt Archiver

| Attribute | Value |
|---|---|
| **Language** | Python >= 3.11 (implicit) |
| **Package Manager** | pip (requirements.txt) |
| **Entry Points** | `src/` modules + `scripts/` (22 scripts) |
| **Key Deps** | feedparser, atproto (Bluesky), tweepy (X), yt-dlp |
| **Test** | Pytest (32 test files) |
| **Linting** | Ruff, Vale |
| **CI/CD** | 9 workflows (ci, syndicate, pages, validate_*) |

```text

src/ → archiver.py, bluesky.py, config.py, syndication.py, threads_pipeline.py ... (16 modules)
scripts/ → 22 scripts (archive_*,*_probe, publish_archives, validate_secrets)

```text

**Active syndication:** Bluesky ✅, Threads ✅ | **Disabled:** X, Instagram, Facebook, Mastodon, Discord, LinkedIn

### 2.7 `hathi-nz` — HathiTrust Debates Fetcher

| Attribute | Value |
|---|---|
| **Language** | Python >= **3.11** |
| **Package Manager** | pixi + pyproject.toml + requirements.txt |
| **Package** | `hathi-nz` v0.1.0 |
| **Entry Point** | `scripts/fetch_hathitrust.py` |
| **Key Deps** | duckdb>=1.5.3, polars>=1.41, pyarrow>=21, huggingface_hub>=1.18, pydantic>=2 |
| **Test** | Pytest (2 test files) |
| **Linting** | Ruff (py311, unified strict rules), ty, taplo, typos, zizmor |
| **CI/CD** | None yet |

```text

scripts/ → fetch_hathitrust.py, __init__.py
data/    → metadata/, processed/, raw/,_state/

```text

**✅ Python requirement now >=3.11 (downgraded from >=3.14 via Track 5).**

├── records.jsonl              # Master JSON Lines store
├── parquet/                   # Hive-partitioned: legislation_type=X/year=N/part-NNNNN.parquet
├── raw_xml/                   # Raw XML/HTML downloads
├── manifests/                 # latest_manifest.json, validation_report.json
└── _state/                    # sync_state.json
seeds/                         # work_ids.txt, reviewed/, batches/
generated/                     # Historical discovery/reconciliation
dist/archive/                  # Annual .tar.zst, .tar.gz, manifest, release-evidence, SHA256SUMS
```

### 2.8 `dnz` — DigitalNZ API Client & CLI

| Attribute | Value |
|---|---|
| **Language** | Rust / Python >= 3.11 / TypeScript |
| **Package Manager** | cargo + pixi + npm |
| **Package** | `digitalnz` (Rust), `pydnz` (Python), `dnz` (JS) |
| **Key Deps** | reqwest, serde, tokio (Rust); requests, urllib3 (Python) |
| **Test** | Cargo test / Pytest |
| **CI/CD** | Yes (GitHub Actions) |

Nested workspace under `dnz/` with separate package identity.

### 2.9 `fyi-cli` — OIA/FYI.org.nz Portal CLI & API

| Attribute | Value |
|---|---|
| **Language** | Rust / Python >= 3.11 |
| **Package Manager** | cargo + pip + conda |
| **Package** | `fyi-cli` (Rust), `fyi` (Python) |
| **Key Deps** | reqwest, serde, tokio (Rust) |
| **Test** | Cargo test / Pytest |
| **CI/CD** | Yes (GitHub Actions) |

Nested workspace under `fyi-cli/` with separate package identity.

## 3. Data Schema Definitions

### 3.1 Shared NZ Corpus Core Schema

**Exists in:** `corpus-law-nz/schemas/` and `corpus-nz-hansard/schemas/`  
**Purpose:** Cross-corpus compatibility fields.

| Field | Type | Req | Notes |
|---|---|---|---|
| `corpus_id` | string (enum) | ✅ | `"corpus-nz-legislation"` or `"corpus-nz-hansard"` |
| `record_id` / `source_id` | string | ✅ | Unique + source-specific IDs |
| `jurisdiction` | const `"New Zealand"` | ✅ | |
| `country` | const `"NZ"` | ✅ | |
| `document_type` | string (enum) | ✅ | `act`, `bill`, `secondary_legislation`, `regulation`, `instrument`, `hansard_document`, `speech_turn`, `sitting`, `proceeding_item`, `other` |
| `display_title` | string | ✅ | |
| `language` | string | ✅ | |
| `record_schema_version` | string | ✅ | Semver pattern |
| `canonical_uri` | string (uri) | ✅ | |
| `content_sha256` | string (SHA256) | ✅ | |
| `manifest_sha256` | string (SHA256) | ✅ | |
| `provenance` | object | ✅ | Pipeline name/version, source, release version/commit, license |

### 3.2 Legislation Record Schema

**File:** `corpus-law-nz/schemas/legislation_record.schema.json` | **Version:** `"1.0"`

| Field | Type | Req | Description |
|---|---|---|---|
| `stable_id` | string | ✅ | Primary key |
| `work_id` / `version_id` | string | ✅ | API identifiers |
| `title` | string | ✅ | |
| `legislation_type` | string | ✅ | act, bill, secondary_legislation, etc. |
| `legislation_status` | string | ✅ | |
| `year` | int/null | ❌ | Extracted from version |
| `text` | string | ✅ | Extracted content |
| `text_sha256` / `source_hash` | string (SHA256) | ✅ | Integrity hashes |
| `scrape_date` / `ingest_timestamp_utc` | string | ✅ | Audit timestamps |
| `administering_agencies` | string[] | ❌ | |
| `is_latest_version` | bool | ❌ | |
| `pipeline_version` | string | ✅ | |

## 4. HF Datasets & Zenodo Integration Map

### 4.1 Hugging Face Datasets

| Dataset | HF Repo ID | Maintained By | Cadence | Format |
|---|---|---|---|---|
| **NZ Legislation Corpus** | `edithatogo/corpus-legislation-nz` | corpus-law-nz | Daily | Hive-partitioned Parquet |
| **NZ Hansard Corpus** | `edithatogo/nz-hansard-corpus` | corpus-nz-hansard | On release | Single `data/hansard.parquet` |

**HF Integration points:**

| Project | Module | Token | Workflow Trigger |
|---|---|---|---|
| `corpus-law-nz` | `hf_sync.py` (`upload_large_folder`) | `HF_TOKEN` | `hf_sync.yml`, `full_corpus_hf_upload.yml` |
| `corpus-nz-hansard` | `scripts/stage_huggingface_dataset.py` | `HF_TOKEN` | `huggingface_publish.yml` |
| `nlp-policy-nz` | `integrations/hf_uploader.py` | `HF_TOKEN` | Manual |
| `hathi-nz` | (planned — `huggingface-hub` in deps) | `HF_TOKEN` | — |

**HF managed paths (corpus-law-nz):** `_state/`, `manifests/`, `parquet/`, `raw_xml/`, root: `README.md`, `records.jsonl`

**HF viewer config (corpus-nz-hansard):**

```yaml
configs:
  - config_name: default

## 5. Naming Conventions & Standards

> **Enforced by:** [`scripts/check_naming.py`](scripts/check_naming.py) — run
> via `python scripts/check_naming.py` or `python scripts/check_lint.py`.

### 5.1 Workspace-Wide Rules

These rules apply to **all files and directories** across every subproject.
The naming lint script (`check_naming.py`) enforces all rules automatically.

| # | Rule | Applies To | Standard | Example ✅ | Violation ❌ |
|---|---|---|---|---|---|
| 1 | **No spaces** in paths | All files + dirs | Use hyphens or underscores | `my_file.py` | `my file.py` |
| 2 | **Python files** snake_case | `*.py` | `lowercase_with_underscores.py` | `nz_api.py` | `NZ_API.py` |
| 3 | **Config/doc files** kebab-case | `.yaml`, `.yml`, `.md`, `.json`, `.toml`, `.ini`, `.cfg`, `.jsonl` | `lowercase-with-hyphens.ext` | `swarm-config.yaml` | `swarm_config.yaml` |
| 4 | **Fixture dirs** standardised | Directories | Always named `fixtures/` | `fixtures/` | `test_fixtures/` |
| 5 | **Test files** named `test_*.py` | `*.py` inside `tests/` | `test_MYTHING.py` | `test_fetcher.py` | `fetcher_test.py` |
| 6 | **Directory names** | All directories | `snake_case` or `kebab-case` | `my_dir/`, `my-dir/` | `MyDir/`, `my dir/` |
| 7 | **Subproject dirs** kebab-case | Top-level project dirs | `lowercase-with-hyphens` | `corpus-law-nz/` | `corpus_law_nz/` |

**Exempt files** (never flagged): `__init__.py`, `__main__.py`, `conftest.py`,
`.gitignore`, `.gitattributes`, `.env.*`, `.markdownlint.json`,
`.prettierrc`, `.prettierignore`, `.eslintrc.json`, `.lintstagedrc.json`,
`.gitkeep`, `.dockerignore`, `Dockerfile`, `Makefile`, `LICENSE`,
`CACHEDIR.TAG`, plus any file starting with `-` or `_`.

### 5.2 Python Package Naming

| Convention | Standard | Example |
|---|---|---|
| Package name | `snake_case` | `nz_legislation_corpus` |
| Source dir | `src/<package>/` | `src/nz_legislation_corpus/` |
| Test dir | `tests/` at project root | `tests/test_*.py` |
| Scripts dir | `scripts/` (+ `__init__.py`) | |
| CLI binary | `[project.scripts]` in pyproject.toml | `nzlc` |

### 5.3 TypeScript Naming

| Convention | Standard | Example |
|---|---|---|
| Source files | `camelCase.ts` | `client.ts`, `config.ts` |
| Dir names | `snake_case/` | `commands/`, `providers/` |
| Entry point | `src/cli.ts` | |

### 5.4 Data Directory Standards

| Directory | Usage | Example projects |
|---|---|---|
| `data/` | Primary data store | corpus-law-nz |
| `derived/` | Derived artifacts | corpus-nz-hansard |
| `generated/` | Build artifacts | corpus-law-nz, corpus-nz-hansard |
| `fixtures/` | Test fixtures (always plural) | corpus-nz-hansard |
| `seeds/` | Seed work IDs | corpus-law-nz |
| `schemas/` | JSON Schema files | corpus-law-nz, corpus-nz-hansard |
| `config/` | Config files | corpus-cases-medilegal-nz, sm-govt-nz |
| `manifests/` | Manifests + validation | corpus-law-nz |
| `scripts/` | Auxiliary scripts (with `__init__.py`) | All projects |

### 5.5 Environment Variable Naming

| Prefix | Examples |
|---|---|
| `NZLC_*` | `NZLC_OUTPUT_DIR`, `NZLC_SEARCH_TERMS` |
| `NZ_LEGISLATION_*` | `NZ_LEGISLATION_API_KEY` |
| `HF_*` | `HF_TOKEN`, `HF_REPO_ID` |
| `ZENODO_*` | `ZENODO_TOKEN`, `ZENODO_API_URL` |
| `ARCHIVE_*` | `ARCHIVE_TITLE`, `ARCHIVE_CREATORS_JSON` |

### 5.6 Naming Lint Tool

A dedicated naming lint script enforces all of the above rules:

```bash
# Run all naming checks (human-readable)
python scripts/check_naming.py

# Verbose — shows fix suggestions for each violation
python scripts/check_naming.py --verbose

# Machine-readable JSON (for CI integrations)
python scripts/check_naming.py --json
```

The naming check is integrated into the combined lint runner:

```bash
python scripts/check_lint.py          # runs Vale + markdownlint + naming
```

**Exit codes:** `0` = all passed, `1` = violations found.

**Key design decisions:**

- Uses `os.walk()` with directory pruning to skip large data dirs, scanning
  50K+ files in ~3 seconds.
- Ignores `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `data/`,
  `derived/`, `generated/`, and all hidden directories.
- Detects violations but does **not** auto-fix — reports guide manual
  remediation or bulk rename planning.

---

## 6. Cross-Cutting Patterns

### 6.1 Shared Toolchain

| Tool | Projects |
|---|---|
| **Ruff** (lint+format) | All 6 Python projects |
| **ty** (type checking) | corpus-law-nz, corpus-nz-hansard, hathi-nz |
| **Vale** (docs lint) | 6 projects (all except hathi-nz) |
| **Pre-commit** (hooks) | 4 Python projects |
| **GitHub Actions** (CI/CD) | 6 projects (except corpus-cases-medilegal-nz) |
| **Conductor** (track planning) | Root + subprojects |

### 6.2 SHA256 Checksumming Pattern

- `corpus-law-nz/utils.py`: `sha256_bytes()`, `sha256_text()`, `sha256_file()`
- `corpus-nz-hansard`: Duplicated in `canonical_ids.py` and `validate_hansard_records.py`
- `corpus-law-nz/manifest.py`: Dual `content_sha256` + `manifest_sha256` system

### 6.3 Python Version — Now Unified ✅

| Project | Python | Manager | Status |
|---|---|---|---|
| corpus-law-nz | >=3.11 | uv ✅ | ✅ Consistent |
| corpus-nz-hansard | >=3.11 | uv ✅ | ✅ Consistent |
| corpus-cases-medilegal-nz | >=3.11 | pixi ✅ | ✅ Downgraded from >=3.13 |
| nlp-policy-nz | >=3.11 | uv + pixi ✅ | ✅ Downgraded from >=3.13 |
| sm-govt-nz | >=3.11 | pip ✅ | ✅ Explicit in new pyproject.toml |
| hathi-nz | >=3.11 | pixi ✅ | ✅ Downgraded from >=3.14 |

All 6 subprojects now target `py311` with identical unified Ruff rule set.

### 6.4 Coverage Targets

| Project | Target |
|---|---|
| cli-legislation-nz | 60% |
| corpus-law-nz | 60% |
| corpus-nz-hansard | 60% |
| corpus-cases-medilegal-nz | **80%** |
| nlp-policy-nz | Not set |
| sm-govt-nz | Not set |
| hathi-nz | 60% |

---

## 7. Critical Findings Summary

| Sev | Finding | Impact | Status |
|---|---|---|---|---|
| 🔴 | 130+ flat scripts in corpus-nz-hansard | No modularity; high duplication | 🟡 Partially addressed |
| 🟡 | SHA256 utilities duplicated across 3 files | Maintenance burden | 🟡 Partially addressed |
| 🟡 | 6 different `.vale.ini` configs | Inconsistent docs linting | 🟡 Partially addressed |
| 🟡 | nlp-policy-nz has dual uv+pixi config | Ambiguous package mgmt | ⚠️ Not addressed |
| 🟡 | corpus-cases-medilegal-nz depends on nlp_policy_nz via editable path | No version pinning | ⚠️ Not addressed |
| 🟡 | No shared Python library across projects | Code duplication | 🟡 Partially addressed |
| 🟢 | sm-govt-nz uses pip (no uv/pixi) | Inconsistent with workspace | ⚠️ Not addressed |
| 🟢 | Coverage targets range 60-90% | No workspace standard | 🟡 Partially addressed |
| ✅ | Python version fragmentation (3.11/3.13/3.14) | Dual runtime; no shared venv | **RESOLVED — all >=3.11** |
| ✅ | hathi-nz requires Python 3.14 (pre-release) | May break on stable builds | **RESOLVED — downgraded to >=3.11** |
| ✅ | sm-govt-nz missing pyproject.toml & ruff config | No linting or type safety | **RESOLVED — created with unified ruff** |
| ✅ | Ruff config inconsistency (3 patterns across 6 projects) | Hard to maintain | **RESOLVED — unified select rules** |

```yaml
data_files:
  - split: train
    path: data/hansard.parquet
```

### 4.2 Zenodo Deposition Map

| Deposition | Project | DOI | Sandbox/Prod |
|---|---|---|---|
| **NZ Legislation Corpus** | corpus-law-nz | `10.5281/zenodo.20592540` | Production |
| **NZ Hansard Corpus** | corpus-nz-hansard | `10.5281/zenodo.20595194` | Production |
| **NZ Hansard Corpus (sibling)** | corpus-nz-hansard | `10.5281/zenodo.20591996` | Production |

**Zenodo integration:**

| Project | Module | Token | Workflow |
|---|---|---|---|
| `corpus-law-nz` | `zenodo.py` (`ZenodoClient`) | `ZENODO_TOKEN` | `annual_zenodo_archive.yml` |
| `corpus-nz-hansard` | 5 scripts (build/publish/upload/update) | `ZENODO_TOKEN` | `zenodo_archive.yml`, `zenodo_publish.yml` |
| `nlp-policy-nz` | `integrations/zenodo.py` | `ZENODO_TOKEN` | Manual |

### 4.3 Resource Index

| Resource | URL / DOI |
|---|---|
| **CLI Tool** (GitHub) | `https://github.com/edithatogo/nz-legislation` |
| **Legislation Corpus** (HF) | `https://huggingface.co/datasets/edithatogo/corpus-legislation-nz` |
| **Legislation Corpus** (Zenodo) | `https://doi.org/10.5281/zenodo.20592540` |
| **Hansard Corpus** (HF) | `https://huggingface.co/datasets/edithatogo/nz-hansard-corpus` |
| **Hansard Corpus** (Zenodo) | `https://doi.org/10.5281/zenodo.20595194` |
| **Hansard Corpus** (Git) | `https://github.com/edithatogo/corpus-nz-hansard` |
| **NZ Legislation API** | `https://api.legislation.govt.nz/v0` |
| **Zenodo Sandbox API** | `https://sandbox.zenodo.org/api` |

**Parquet:** Hive-partitioned `legislation_type=X/year=N/part-NNNNN.parquet`, zstd + CDC.

### 3.3 Hansard Record Schema

**File:** `corpus-nz-hansard/schemas/hansard_record.schema.json`

| Field | Type | Req | Description |
|---|---|---|---|
| `stable_id` | string | ✅ | |
| `source_archive` / `source_file` / `source_row_number` | string/int | ✅ | CSV lineage |
| `parliament_number` | int | ✅ | 47-54 |
| `document_type` / `title` | string | ✅ | |
| `content` | string | ✅ | Document text |
| `member_of_parliament_raw` | string/null | ❌ | Raw MP names |
| `text_sha256` / `source_hash` | string (SHA256) | ✅ | |

**Parquet:** Single `data/hansard.parquet` (193,922 rows, not partitioned).

### 3.4 Release Evidence Schema

**File:** `corpus-law-nz/schemas/release_evidence.schema.json`

Key fields: `artifact_class`, `corpus_family_label` (`corpus-nz-legislation`),
`sibling_corpus` (`corpus-nz-hansard`), `workflow` (GH run metadata),
`dataset` (HF repo + Zenodo DOIs), `manifest` (sha256 hashes + record count),
`subjects` (file inventory), `attestation_policy`.

### 3.5 Hansard Derived Schemas (43 total)

Key schemas in `corpus-nz-hansard/schemas/`:

- `canonical_id_uri_policy.schema.json`
- `release_evidence_ledger.schema.json`
- `historical_coverage_audit.schema.json`
- `validated_speech_turn_component.schema.json`
- `vote_motion_bill_question_extraction_validation.schema.json`
- `semantic_search_embeddings_record.schema.json`
- `corpus_wide_member_identity.schema.json`
- `corpus_wide_party_attribution.schema.json`
- - 35 endpoint/component-specific validation schemas

### 3.6 CLI Output Formats

**TypeScript CLI** (cli-legislation-nz):

- **Table:** cli-table3 with colored type/status indicators
- **JSON:** `JSON.stringify(data, null, 2)`
- **CSV:** Custom serializer with quoted fields
- **Citations:** NZMJ, BibTeX, RIS, ENW, APA

**Python CLI** (corpus-law-nz `nzlc`): Rich `console.print_json()` for JSON, `console.print()` for text/status.
