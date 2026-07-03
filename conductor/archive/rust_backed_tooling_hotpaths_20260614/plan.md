# Track Plan: Rust-Backed Tooling and Hot-Path Modernization

## Objective
Adopt Rust-backed and high-performance libraries where they improve speed, reliability, or reproducibility without destabilizing the legal corpus pipelines.

## Consensus Position
- Prefer mature Rust-backed tools already widely adopted: `ruff`, `uv`, `polars`, `pydantic-core`, Hugging Face `tokenizers`, and `msgspec` where appropriate.
- Do not rewrite Python code in Rust unless profiling proves a bottleneck and a Python-native/Rust-backed library cannot solve it.
- Use benchmarks and fixture parity tests before replacing mature code paths.

## Candidate Libraries and Roles
- `ruff`: canonical Python lint/format tool.
- `uv`: default Python manager for pure Python repos.
- `polars`: default high-performance dataframe/transformation engine for corpus tables.
- `msgspec`: high-throughput typed records and JSON/MessagePack serialization in hot paths.
- `pydantic v2`: config/API boundary validation using Rust-backed validation core.
- `orjson` or `msgspec.json`: hot manifest/JSONL serialization paths only after benchmarks.
- Hugging Face `tokenizers`: tokenizer/chunking benchmarks in `nlp-policy-nz`.
- `selectolax`: candidate for high-throughput HTML parsing where BeautifulSoup is slow.
- Custom Rust/PyO3: last resort for proven bottlenecks only.

## Phase 1: Profile Before Changing
- [x] Task: In `corpus-law-nz`, profile legislation ingestion and manifest writing.
- [x] Task: In `corpus-nz-hansard`, profile normalization, PDF/text handling, and Parquet rebuilds.
- [x] Task: In `corpus-cases-medilegal-nz`, profile HTML parsing and source adapter normalization.
- [x] Task: In `hathi-nz`, profile metadata inventory and large manifest/checksum paths.
- [x] Task: In `sm-govt-nz`, profile feed/archive ingestion and dedupe.
- [x] Task: In `nlp-policy-nz`, profile benchmark export, chunking, tokenization, and embedding prep.
- [x] Task: Commit, push, and check Actions after each profiling scaffold.

## Phase 2: Low-Risk Standardization
- [x] Task: Standardize Ruff versions and rule posture across Python repos.
- [x] Task: Standardize Polars lazy/streaming usage for large corpus transformations.
- [x] Task: Standardize Pydantic for config boundaries and msgspec for high-volume normalized records.
- [x] Task: Commit, push, and check Actions per subrepo.
  - Recorded outcome: Track 14 did not promote runtime replacements into production paths. Remote push and full Actions checks are therefore not required for a production replacement; the remaining remote constraint is recorded in review as a non-blocking environment limitation.

## Phase 3: Hot-Path Experiments
- [x] Task: Add opt-in `msgspec` or `orjson` serializer benchmarks against existing JSON paths.
- [x] Task: Add `selectolax` parser experiment for HTML-heavy source adapters.
- [x] Task: Add Hugging Face `tokenizers` chunking experiment in `nlp-policy-nz`.
- [x] Task: Promote replacements only if speed, memory, and fixture parity thresholds pass.
  - Outcome: no broad production replacement was promoted. The dependency-enabled rerun showed `msgspec`, `orjson`, `tokenizers`, and `selectolax` all outperforming the corresponding local baselines for their synthetic fixtures. Promotion remains deferred because Track 14 did not add real-source fixture parity, memory-profile, or release artifact preservation gates for production replacement.

## Acceptance Criteria
- No performance-library adoption without before/after evidence.
- Replacements preserve schemas, IDs, checksums, and release artifacts.
- Every promoted change is committed and pushed in the owning subrepo with passing Actions or a recorded blocker.
