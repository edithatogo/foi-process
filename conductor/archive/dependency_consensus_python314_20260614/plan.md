# Track Plan: Dependency Consensus Baseline and Python 3.14 Runtime Policy

## Objective
Create a consensus dependency baseline for all subrepos while keeping implementation inside the owning subrepo. Python 3.14 is the target runtime for new Python work, with compatibility gates for native, ML, and platform-specific dependencies.

## Current Reference Facts
- Python 3.14 is in bugfix/stable maintenance, first released on 2025-10-07, with bugfix support into 2027 and security support to approximately October 2030.
- Python 3.15 is prerelease as of 2026-06-14 and is not the repo-wide target.
- Some ML/native packages may lag Python 3.14 wheels; migration must be evidence-based.

## Consensus Position
- Default target: Python 3.14 for new Python tracks, CI, and local development.
- Minimum compatibility: retain a lower bound only where a repo has documented dependency blockers.
- Do not change `requires-python` to `>=3.14` in a subrepo until CI proves install, lint/type, and focused tests pass on Python 3.14.
- Use SemVer for all package/application versions.
- Use Loguru for Python runtime logging unless a repo has a documented equivalent.
- Keep TypeScript logging on Winston unless a benchmarked replacement is approved.

## Maturity Dependency Baseline
Each subrepo must classify every baseline category as `required`, `optional`, `deferred`, or `not_applicable` before adopting or rejecting it.

| Category | Consensus candidate | Default scope | Maturity purpose |
|---|---|---|---|
| Python environment manager | `uv` | Most Python repos | Fast lock/sync, Python version management, CI reproducibility |
| Multi-language/native environment | `pixi` | `hathi-nz`, `nlp-policy-nz`, native/GPU/OCR/PDF-heavy repos | Conda-forge/native/GPU reproducibility |
| Python lint/format | `ruff` | All Python repos | Fast formatter/linter and rule convergence |
| Python type checking | `ty` or `pyright` | All Python repos | Static correctness and CI maturity |
| Python logging | `loguru` | All Python repos | Consistent runtime logging |
| Python CLI UX | `typer` and `rich` | Python CLIs and scripts | Consistent help, progress, and error UX |
| Config/env loading | `pydantic-settings` | Repos with env/config | Typed config and secret boundary handling |
| Boundary validation | `pydantic v2` | APIs, config, manifest models | Mature validation with Rust-backed core |
| Hot record serialization | `msgspec` | Corpus and benchmark hot paths | Fast typed records and JSON/MessagePack |
| Dataframes | `polars` | Corpus/data repos | Fast lazy/streaming transformations |
| Query validation | `duckdb` | Corpus/data repos | Local SQL/Parquet validation |
| Columnar data | `pyarrow`/Parquet | Corpus/data repos | Dataset interoperability and HF/DuckDB compatibility |
| JSON schema | `jsonschema` | Public schemas/manifests | Registry and dataset contract validation |
| HTTP clients | `httpx` for new code; `requests` where stable | API/source ingestion repos | Modern sync/async API clients |
| Retry/backoff | `tenacity` | API/source ingestion repos | Resilient source acquisition |
| HTML parsing | `beautifulsoup4`; `selectolax` for hot paths | Scraper-heavy repos | Compatibility first, speed where benchmarked |
| Terminal UI | `rich` | Python scripts/CLIs | Consistent operator UX |
| Checksums/manifests | Repo-local checksum utilities | Corpus repos | Stable release and rebuild evidence |
| Local vector store | `lancedb` | `nlp-policy-nz` first | Reproducible local vector artifacts |
| Service vector DB | `qdrant` candidate | `nlp-policy-nz` only initially | Service-grade vector/RAG backend if benchmarks justify |
| RAG orchestration | `haystack` | `nlp-policy-nz` prototypes | Modular RAG experiments |
| HF publication | `huggingface_hub`, `datasets` | Corpus/model repos | Dataset/model publishing |
| Archive/DOI | Zenodo/OSF clients or thin adapters | Corpus repos | Citable release/archive flow |
| JS/TS release | Changesets | `cli-legislation-nz` | SemVer release discipline |
| JS/TS logging | `winston` | `cli-legislation-nz` | Node equivalent to Loguru |
| JS/TS validation | `zod` | `cli-legislation-nz` | Runtime schema validation |
| JS/TS fast tooling | Biome/Oxlint candidates | `cli-legislation-nz` trial only | Faster lint/format without weakening gates |

## Non-Default / Optional Dependency Guardrails
- Keep `torch`, `transformers`, `bitsandbytes`, and `faiss-cpu` mainly in `nlp-policy-nz` or optional extras unless a corpus repo has a specific benchmark/export need.
- Do not standardize `qdrant` across repos; evaluate centrally in `nlp-policy-nz`.
- Do not standardize `pixi` across repos; use it where native, conda-forge, GPU, OCR, or multi-language reproducibility justifies it.
- Do not add `haystack` to source corpus repos; keep RAG orchestration in `nlp-policy-nz` or a future RAG app repo.
- Use `selectolax` only after parser parity and speed benchmarks prove it beats BeautifulSoup for the target source.

## Subrepo Ownership
- `corpus-law-nz`: legislation pipeline dependency baseline and Python 3.14 readiness.
- `corpus-nz-hansard`: Hansard pipeline dependency baseline and Python 3.14 readiness.
- `corpus-cases-medilegal-nz`: medilegal source adapters and Python 3.14 readiness.
- `hathi-nz`: Hathi/Hansard historical pipeline and Python 3.14 readiness.
- `nlp-policy-nz`: cross-corpus dependency policy, benchmark harness, ML/RAG dependency readiness.
- `sm-govt-nz`: government social-media archive dependency baseline and Python 3.14 readiness.
- `cli-legislation-nz`: TypeScript package baseline; Python policy does not apply except to helper scripts.
- Root `legal-nz`: coordination and evidence only.

## Phase 1: Inventory and Baseline
- [x] Task: In each Python subrepo, inventory current `pyproject.toml`, lockfiles, CI Python versions, and runtime import surface. [61a6597]
- [x] Task: In `nlp-policy-nz`, create a dependency policy matrix covering Python, dataframes, validation, logging, serialization, vector/RAG, and test tooling. [61a6597]
- [x] Task: In each subrepo, create a maturity dependency checklist classifying each baseline category as `required`, `optional`, `deferred`, or `not_applicable`. [46b96d4] (subrepo commits: corpus-law-nz@7748cea, corpus-nz-hansard@58eecaa, corpus-cases-medilegal-nz@ec9092e, nlp-policy-nz@dbc70ac, sm-govt-nz@462c877, hathi-nz@e168d0a)
- [x] Task: Record blockers for Python 3.14 wheels, especially `torch`, `bitsandbytes`, `faiss-cpu`, `spacy`, `duckdb`, `pyarrow`, `polars`, and `lancedb`. [61a6597]
- [x] Task: Commit, push, and check Actions in each owning subrepo after its inventory task. [46b96d4]

## Phase 2: Python 3.14 Trial Gates
- [x] Task: Add Python 3.14 CI jobs as non-blocking or matrix-allowed failures where dependency risk is high. [c4e4fc4, c653cfa]
- [ ] Task: Promote Python 3.14 jobs to required only after install, lint/type, and focused tests pass consistently.
- [ ] Task: Update `requires-python` per subrepo only after the CI evidence is green.
- [ ] Task: Commit, push, and check Actions after each subrepo promotion.

## Phase 3: Version and Logging Consistency
- [ ] Task: Add version consistency tests where absent.
- [ ] Task: Ensure every Python package exposes `__version__` or a documented package-metadata equivalent.
- [ ] Task: Add repo-local Loguru adapters only after dependency install is proven.
- [ ] Task: Commit, push, and check Actions after each repo-local logging/version task.

## Acceptance Criteria
- Each subrepo has a documented Python version target and blocker list.
- Python 3.14 is either active and green, or explicitly blocked with package evidence.
- No subrepo depends on root implementation code for runtime behavior.
- GitHub Actions status is recorded for every subrepo phase.
