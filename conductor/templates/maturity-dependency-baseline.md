# Maturity Dependency Baseline Checklist

## Purpose
Use this checklist in each owning subrepo before adding, removing, or standardizing dependencies. Classify every category as `required`, `optional`, `deferred`, or `not_applicable`, then record the reason.

## Classification Values
- `required`: should be installed and enforced in this repo.
- `optional`: useful behind extras, optional workflow, or non-default track.
- `deferred`: likely useful but blocked by compatibility, CI, maturity, or priority.
- `not_applicable`: not relevant to this repo's purpose.

## Checklist

| Category | Candidate | Classification | Reason | Evidence/issue |
|---|---|---:|---|---|
| Python environment manager | `uv` |  |  |  |
| Multi-language/native environment | `pixi` |  |  |  |
| Python lint/format | `ruff` |  |  |  |
| Python type checking | `ty` or `pyright` |  |  |  |
| Python logging | `loguru` |  |  |  |
| Python CLI UX | `typer` and `rich` |  |  |  |
| Config/env loading | `pydantic-settings` |  |  |  |
| Boundary validation | `pydantic v2` |  |  |  |
| Hot record serialization | `msgspec` |  |  |  |
| Dataframes | `polars` |  |  |  |
| Query validation | `duckdb` |  |  |  |
| Columnar data | `pyarrow`/Parquet |  |  |  |
| JSON schema | `jsonschema` |  |  |  |
| HTTP clients | `httpx` / `requests` |  |  |  |
| Retry/backoff | `tenacity` |  |  |  |
| HTML parsing | `beautifulsoup4` / `selectolax` |  |  |  |
| Terminal UI | `rich` |  |  |  |
| Checksums/manifests | repo-local utilities |  |  |  |
| Local vector store | `lancedb` |  |  |  |
| Service vector DB | `qdrant` |  |  |  |
| RAG orchestration | `haystack` |  |  |  |
| HF publication | `huggingface_hub`, `datasets` |  |  |  |
| Archive/DOI | Zenodo/OSF adapters |  |  |  |
| JS/TS release | Changesets |  |  |  |
| JS/TS logging | `winston` |  |  |  |
| JS/TS validation | `zod` |  |  |  |
| JS/TS fast tooling | Biome/Oxlint |  |  |  |

## Guardrails
- Do not add heavy ML dependencies to corpus repos unless a repo-local track proves the need.
- Keep RAG orchestration in `nlp-policy-nz` or a future RAG app repo.
- Keep vector-store experiments centralized in `nlp-policy-nz`.
- Prefer repo-local utilities over imports from the root aggregation repo.
- Update this checklist in the same PR/commit as dependency changes.
