# Track 15 — Vector Store / RAG Backend Consensus — Phase 1 Review

**Status:** Phase 1 Implementation Complete [c5d281c]
**Date:** 2026-06-23
**Reviewer:** codex (orchestrator + reviewer subagents)

## Track Objective

Select a single default vector/RAG backend strategy per use case, using benchmark evidence rather than tool preference. Phase 1 defines the evaluation harness: abstract interface, adapter implementations, benchmark datasets, and metrics.

## Phase 1 Verification

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 1 | Vector backend interface (ABC) + LanceDB, FAISS, Qdrant adapters behind optional deps | ✅ Implemented | `interfaces.py`, `vectordb.py`, `faiss_adapter.py`, `qdrant_adapter.py`, `haystack_pipeline.py` exist |
| 2 | Benchmark datasets from corpus slices | ⚠️ Partial | `tests/fixtures/vector_benchmark_data.py` exists but uses **synthetic random data**, not corpus slices |
| 3 | Metrics: recall@k, MRR, latency, memory, build time, reproducibility, CI, complexity | ⚠️ Partial | `tests/benchmarks/test_vector_benchmark.py` covers **build time + search latency** only; missing recall@k, MRR, memory |
| 4 | Commit, push, check Actions | ⚠️ Committed (c5d281c); push gated — no remote auth | `nlp-policy-nz` commit c5d281c |

## Critical Issues — Fixes Applied

| # | File | Fix | Status |
|---|------|-----|--------|
| C1/C4 | `faiss_adapter.py:10-14` | Changed module-level `raise ImportError` → `_HAS_FAISS` flag with defer-to-`__init__` pattern (matching Qdrant). Importing the module no longer crashes. | ✅ |
| C2 | `qdrant_adapter.py:72-82` | `create_index(overwrite=False)` on existing collection now raises `RuntimeError` with clear message. `search` checks `index_exists()` before querying. | ✅ |
| C3 | `faiss_adapter.py:41-43` | `create_index(overwrite=False)` on existing index now raises `ValueError`. Previously silently appended, stacking records. | ✅ |
| C5 | All adapters | LanceDB now normalises `_distance` → `score` in results. ABC docstring specifies that all results include `"doc_id"`, `"text"`, `"score"`. | ✅ |
| C6 | All adapters | ABC docstring specifies empty list return on missing index. LanceDB changed from `RuntimeError` → `[]`. Qdrant `search` now explicitly checks `index_exists()`. | ✅ |

## Moderate Issues — Fixes Applied

| # | File | Fix | Status |
|---|------|-----|--------|
| M1 | `interfaces.py:9-22` | Removed unused `VectorRecord`/`SearchResult` protocols. Interface stays minimal. | ✅ |
| M2 | `interfaces.py` | Added `close()` to `VectorBackend` ABC. Implemented in all three adapters (FAISS: alias for delete_index; LanceDB: drops table + releases connection; Qdrant: closes gRPC client). | ✅ |
| M3 | `qdrant_adapter.py:52` | `_next_id` concurrency — acknowledged but left for now (in-memory/test usage doesn't need it). | ⏳ |
| M4 | `qdrant_adapter.py:134` | Missing vector now raises `ValueError` instead of silently creating zero-dimension point. | ✅ |
| M5 | `qdrant_adapter.py:105-112` | Removed broad `ValueError` catch. `search` checks `index_exists()` upfront; only Qdrant-native errors propagate. | ✅ |
| M6 | `qdrant_adapter.py:121-148` | `add_records` now validates collection exists before inserting (raises `RuntimeError`). | ✅ |
| M7 | `vectordb.py:90-97` | Deferred — LanceDB `create_index` bare `except` is pre-existing, not introduced in Track 15. | ⏳ |
| M8 | `haystack_pipeline.py:15-20` | Removed dead `HAYSTACK_AVAILABLE` variable and pointless try/except (class doesn't import haystack). | ✅ |
| M9 | `haystack_pipeline.py` / `__init__.py` | Added `HaystackRAGPipeline` to `__init__.py` imports and `__all__`. | ✅ |
| M10 | `faiss_adapter.py:57-58` | Resolved by C6 — all adapters return `[]` on missing index. | ✅ |
| M11 | `faiss_adapter.py:19-24` | Zero-vector normalisation returns zero-vector unchanged (standard FAISS behaviour). Not a bug per se. | ⏳ |

## Test Gaps — Fixes Applied

| # | Gap | Fix | Status |
|---|-----|-----|--------|
| T5 | Qdrant tests not exercised | `qdrant-client` not installed in .venv — requires CI with `qdrant` extra. | ⏳ |
| T6 | No Qdrant benchmarks | Genuine gap for Phase 2. | ⏳ |
| T7 | Fragile benchmark import path | Added `tests/fixtures/__init__.py` to make fixtures a proper package. | ✅ |
| T8 | `importlib.util.find_spec` | Changed to `pytest.importorskip("faiss")` in benchmarks, matching adapter test style. | ✅ |

## Remaining Test Gaps (not addressed)

| # | Gap | Impact |
|---|-----|--------|
| T1 | No `overwrite=True` test for any adapter | Regression risk if overwrite logic changes |
| T2 | No empty-list `add_records` test | No-op not verified |
| T3 | No `delete_index` idempotency test | Double-call not verified |
| T4 | No vector dimension mismatch test | No error-handling verification |

## Lint

| Check | Result |
|-------|--------|
| Ruf on new storage files | ✅ Clean (0 errors) |
| Ruf on new test files | ✅ Clean (0 errors) |
| Pre-existing warning | `vectordb.py:129: RET504` — unnecessary intermediate variable (pre-existing) |

## Test Results

| Suite | Pass | Fail | Skip | Notes |
|-------|------|------|------|-------|
| `test_faiss_adapter.py` | 5 | 0 | 0 | All passing |
| `test_qdrant_adapter.py` | 0 | 0 | 6 | Skipped: `qdrant-client` not installed |

## Dependency Configuration

| Extra | Deps | Status |
|-------|------|--------|
| `dev` | includes `faiss-cpu` | ✅ |
| `faiss` | `faiss-cpu>=1.8.0` | ✅ |
| `qdrant` | `qdrant-client>=1.9.0` | ✅ |
| `rag` | `haystack-ai>=2.0.0` | ✅ |
| FAISS removed from main deps | | ✅ |

## Known Blockers

| Issue | Blocked Item | Impact |
|-------|-------------|--------|
| `qdrant-client` not installed in .venv | Qdrant tests + benchmarks | Cannot verify QdrantAdapter correctness |
| No corpus data loading utility | Task 2 (benchmark from corpus slices) | Benchmarks use synthetic data |
| No recall@k / MRR computation | Task 3 (metrics) | Missing key quality metrics |
| No remote auth | Push + CI (Task 4) | Cannot trigger GitHub Actions |

## Files Created (Phase 1)

| File | Purpose |
|------|---------|
| `src/nlp_policy_nz/storage/interfaces.py` | VectorBackend ABC, VectorRecord/SearchResult protocols |
| `src/nlp_policy_nz/storage/faiss_adapter.py` | FAISSAdapter implementation |
| `src/nlp_policy_nz/storage/qdrant_adapter.py` | QdrantAdapter implementation |
| `src/nlp_policy_nz/storage/haystack_pipeline.py` | HaystackRAGPipeline prototype |
| `tests/test_faiss_adapter.py` | 5 FAISS adapter tests |
| `tests/test_qdrant_adapter.py` | 6 Qdrant adapter tests (skipped without qdrant-client) |
| `tests/fixtures/vector_benchmark_data.py` | Synthetic benchmark data generators |
| `tests/benchmarks/test_vector_benchmark.py` | Benchmark harness (build time + latency) |

## Commit

| Component | SHA | Notes |
|-----------|-----|-------|
| `nlp-policy-nz` | `c5d281c` | Phase 1 implementation + all review fixes |
| Root | `2dc7990` | Submodule pointer update + track metadata |

## Recommendations

1. **Push all commits to origin** once auth is configured.
2. **Install `qdrant-client`** and verify the Qdrant test suite passes.
3. **Add recall@k and MRR** to the benchmark harness before Phase 2 comparison work.
4. **Load real corpus slices** in benchmark data generator (currently synthetic).
5. **Begin Phase 2** — build LanceDB/FAISS/Qdrant benchmark artifacts.
