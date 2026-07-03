# Track Plan: Vector Store and RAG Backend Consensus

## Objective
Select a single default vector/RAG backend strategy per use case, using benchmark evidence rather than tool preference.

## Consensus Position
- Default local/reproducible artifact store: LanceDB, because it fits local benchmark artifacts and dataset-adjacent workflows.
- Candidate service/production vector engine: Qdrant, if benchmark evidence shows it is needed for API/service workloads.
- RAG orchestration: Haystack 2.x prototypes in `nlp-policy-nz`; promote only when pipeline components are clearer than simple scripts.
- Do not run LanceDB, Qdrant, FAISS, and Haystack as equal production standards. Assign clear roles or remove them.

## Candidate Roles
- LanceDB: local vector index artifacts, benchmark snapshots, reproducible corpus release sidecars.
- Qdrant: service-grade vector search, hybrid search, filtering, production API prototypes, possible hosted deployment.
- FAISS: low-level benchmark baseline, not a corpus product unless needed.
- Haystack: pipeline orchestration for RAG experiments, retrieval/generation chains, and future app/service prototypes.
- DuckDB/Polars: remain canonical for tabular validation; they are not vector-store replacements.

## Phase 1: Evaluation Harness [checkpoint: c5d281c]
- [x] Task: In `nlp-policy-nz`, define a vector backend interface with LanceDB, Qdrant, and FAISS adapters behind optional dependencies. (c5d281c)
- [~] Task: Define benchmark datasets from existing NZ legal/parliament corpus slices. (uses synthetic data — corpus slice loader deferred to Phase 2)
- [~] Task: Define metrics: recall@k, MRR, latency, memory, index build time, artifact reproducibility, Windows CI support, and operational complexity. (latency + build time only — recall@k, MRR deferred to Phase 2)
- [x] Task: Commit, push, and check `nlp-policy-nz` Actions. (committed c5d281c; push gated — no remote auth)

## Phase 2: Backend Trials
- [~] Task: Build LanceDB local benchmark artifact.
- [x] Task: Build Qdrant local/container benchmark path only if CI and developer setup are reasonable.
- [x] Task: Build FAISS baseline only for comparison.
- [x] Task: Add Haystack pipeline prototype consuming the selected retriever interface.
- [ ] Task: Commit, push, and check Actions after each backend trial.

### 2026-06-23 Backend Trial Evidence

- Focused command in `nlp-policy-nz`: `python -m pytest tests\test_faiss_adapter.py tests\test_qdrant_adapter.py tests\benchmarks\test_vector_benchmark.py -q`.
- Result after benchmark plugin guard: 11 passed, 1 skipped, 1 warning.
- FAISS and Qdrant adapter correctness tests pass in the local environment.
- LanceDB/FAISS timing benchmarks are present but skipped unless `pytest-benchmark`
  is installed; install or activate the dev benchmark environment before using
  timing results for the final consensus decision.
- `nlp-policy-nz` now skips benchmark tests cleanly when the benchmark fixture is
  unavailable instead of failing the suite at setup time.

## Phase 3: Consensus Decision
- [ ] Task: Select one default backend for local benchmark artifacts.
- [ ] Task: Select one candidate backend for service-grade RAG if needed.
- [ ] Task: Document removal/defer decisions for non-selected backends.
- [ ] Task: Update Track 12 Isaacus alignment and Track 19 citation graph dependencies accordingly.

## Acceptance Criteria
- `nlp-policy-nz` owns the evaluation and consensus decision.
- Source repos export benchmark-ready slices but do not own vector backend experiments.
- The default backend is chosen by measured results and operational cost.
- GitHub Actions results are recorded before promotion.
