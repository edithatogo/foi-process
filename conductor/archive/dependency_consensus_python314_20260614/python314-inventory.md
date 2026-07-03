# Python 3.14 Dependency Inventory — All 7 Core Subrepos

> **Track:** 12 — dependency_consensus_python314_20260614  
> **Date:** 2026-06-22  
> **Status:** Updated inventory snapshot with fresh agent inventory  

---

## Summary Table

| Subrepo | Language | Current Python (`requires-python`) | Package Manager | `ruff target-version` | CI Python Version(s) | Docker Python | Python 3.14 Blockers | Migration Priority |
|---|---|---|---|---|---|---|---|---|---|
| **cli-legislation-nz** | TypeScript/Node.js | N/A (not Python) | pnpm | N/A | N/A (Node 18/20/22 matrix) | N/A (typescript-node devcontainer) | N/A — not a Python project | N/A |
| **corpus-law-nz** | Python | `>=3.11` | uv | `py311` | **3.12** (all workflows, 19 files) | None | `requires-python` + `target-version` at 3.11; needs pyarrow, polars, torch compat | **High** — core corpus pipeline |
| **corpus-nz-hansard** | Python | **`>=3.14`** ✅ | pixi + pip | **`py314`** ✅ | **3.14** (all workflows, 8 of 11 files) | None | **None** — already fully migrated to 3.14 | **Done** ✅ |
| **corpus-cases-medilegal-nz** | Python | `>=3.11` | pixi | `py311` | pixi default (>=3.11) | None | Pinned 3.11; sibling dep on `nlp_policy_nz` | **Low** — blocked by nlp-policy-nz |
| **nlp-policy-nz** | Python | `>=3.11` | pixi + uv | `py311` | pixi default (>=3.11) | None | **Heavy ML deps**: torch, transformers, bitsandbytes, spacy, faiss-cpu | **Critical** — shared NLP dep for others |
| **sm-govt-nz** | Python | `>=3.11` | pip + uv | `py311` | **3.11** (12 workflows pin 3.11; 6+ unpinned) | None | All CI pins 3.11; simplest dep tree | **Low** — easiest to migrate |
| **hathi-nz** | Python | `>=3.11` | pixi | `py311` | **3.14** (ci.yml + hf_sync.yml env var, unused) | None | `requires-python`/`target-version` at 3.11 despite CI env var 3.14 | **Lead** — CI targets 3.14 but config says 3.11 |

---

## Per-Subrepo Detailed Findings

### 1. cli-legislation-nz

### 2. corpus-law-nz

**`requires-python`:** `>=3.11` (pyproject.toml line 6)  
**`target-version`:** `py311` (pyproject.toml line 42)  
**Package manager:** uv (astral-sh/setup-uv).  
**CI Python version:** **3.12** consistently across all workflows:
- `tests.yml` — `python-version: "3.12"`
- `code_quality.yml` — `python-version: "3.12"`
- `doctor.yml` — `python-version: "3.12"`
- `hf_sync.yml` — `python-version: "3.12"`
- `full_corpus_bootstrap.yml` — `python-version: "3.12"`

**Pixi:** No `pixi.toml` — pure uv/pip workflow.  
**Docker:** No Dockerfile.  
**Key dependencies:** `pyarrow>=21.0.0`, `polars>=1.0.0`, `pydantic>=2.0.0`, `huggingface_hub>=0.34.0`, `hf-xet>=1.1.0`, `zstandard>=0.23.0`.  
**Optional deps:** `torch>=2.0.0`, `transformers>=5.10.2` (embeddings).  
**Migration blockers:**
- `requires-python` must be bumped to `>=3.13` or `>=3.14`

### 3. corpus-nz-hansard

**`requires-python`:** `>=3.11` (pyproject.toml line 5)  
**`target-version`:** `py311` (pyproject.toml line 50)  
**Package manager:** pip + uv (`uv==0.11.8` in dev deps). Uses `requirements.txt`.  
**CI Python version:** Mixed — **3.11** for tests (`tests.yml`), **3.13** for quality (`quality.yml`).  
**CI Runner:** `windows-2025-vs2026` (Windows — notable for wheel availability).  
**Pixi:** No `pixi.toml`.  
**Docker:** No Dockerfile.  
**Key dependencies:** `duckdb==1.5.3` (pinned!), `polars>=1.41.2`, `pyarrow>=21.0.0`, `pdfplumber>=0.11.0`.  
**Optional deps:** `torch>=2.0.0`, `transformers>=5.10.2`, `scikit-learn>=1.8.0`.  
**Migration blockers:**
- `duckdb==1.5.3` **pinned** — must confirm Python 3.14 wheel
- `requires-python`/`target-version` both at 3.11

### 4. corpus-cases-medilegal-nz

**`requires-python`:** `>=3.11` (pyproject.toml line 10)  
**`target-version`:** `py311` (pyproject.toml line 47)  
**Package manager:** pixi (has `pixi.toml`, conda-forge channel).  
**CI Python version:** Not explicitly set — pixi resolves from `pixi.toml` (`python = ">=3.11"`).  
**Pixi platforms:** `win-64`, `linux-64`, `osx-64`, `osx-arm64`.  
**Docker:** No Dockerfile.  
**Key dependencies:** `polars>=1.0.0`, `pyarrow>=16.0.0`, `beautifulsoup4>=4.12.0`.  
**Sibling dependency:** `nlp_policy_nz = { path = "../nlp-policy-nz", editable = true }` — **blocked by nlp-policy-nz**.  
**Migration blockers:**
- `requires-python`/`target-version` at 3.11

### 5. nlp-policy-nz

**`requires-python`:** `>=3.11` (pyproject.toml line 10)  
**`target-version`:** `py311` (pyproject.toml line 57)  
**Package manager:** pixi (has `pixi.toml`, conda-forge channel).  
**CI Python version:** Not explicitly set — pixi resolves from `pixi.toml` (`python = ">=3.11"`).  
**Pixi platforms:** `win-64`, `linux-64`, `osx-64`, `osx-arm64`.  
**Docker:** No Dockerfile.  
**Key dependencies (HEAVY ML):**
- `torch>=2.2.0`, `transformers>=4.40.0`, `spacy>=3.7.0` — **critical**
- `bitsandbytes>=0.42.0` — **often lags on new Python versions**
- `faiss-cpu>=1.8.0`, `lancedb>=0.6.0` (Rust ext), `networkx>=3.0`
- `gradio>=4.0.0`, `fastapi>=0.110.0`, `maturin>=1.5.0`
**Migration blockers (SEVERE):**
- **Heaviest ML dep tree** — torch, transformers, bitsandbytes, spacy, faiss
- `bitsandbytes` historically slowest to adopt new Python
- Conda-forge 3.14 builds may lag

### 6. sm-govt-nz

**`requires-python`:** `>=3.11` (pyproject.toml line 5)  
**`target-version`:** `py311` (pyproject.toml line 12)  
**Package manager:** pip (requirements.txt, requirements-dev.txt).  
**CI Python version:** Not explicitly set — uses runner default.  
**Docker:** No Dockerfile.  
**Key dependencies:** `feedparser`, `atproto`, `tweepy`, `yt-dlp`, `huggingface_hub`, `pyarrow`.  
**Migration blockers:**
- `requires-python`/`target-version` at 3.11

### 7. hathi-nz

**`requires-python`:** `>=3.11` (pyproject.toml line 5)  
**`target-version`:** `py311` (pyproject.toml line 36)  
**Package manager:** pixi (has `pixi.toml`).  
**CI Python version:** **3.14** — both `ci.yml` and `hf_sync.yml` set `PYTHON_VERSION: "3.14"`.  
**Pixi platforms:** `win-64`, `linux-64`, `osx-64`, `osx-arm64`.  
**Docker:** No Dockerfile.  
**Key dependencies:** `duckdb>=1.5.3`, `polars>=1.41.2`, `pyarrow>=21.0.0`, `huggingface_hub>=1.18.0`.  
**Migration blockers:**
- `requires-python`/`target-version` still at 3.11 despite CI on 3.14 (paradox)
- CI env var `PYTHON_VERSION: "3.14"` set but pixi.toml has no python dep section

---

## Cross-Cutting Issues

### 1. Universal `requires-python >=3.11`
All 6 Python subrepos currently specify `requires-python = ">=3.11"`. This requires a coordinated bump to `>=3.13` (intermediate) or `>=3.14` (direct).

### 2. Universal `ruff target-version = "py311"`
All 6 Python subrepos use `target-version = "py311"` in their Ruff configuration. Must be bumped to `py314` in a coordinated fashion.

### 3. Package Manager Fragmentation
Three different package managers across 6 Python subrepos:
- **uv** (corpus-law-nz) — easiest to specify Python version constraint
- **pixi** (corpus-cases-medilegal-nz, nlp-policy-nz, hathi-nz) — conda-forge channels may have delayed 3.14 builds
- **pip** (corpus-nz-hansard, sm-govt-nz) — depends on PyPI wheel availability

### 4. ML/NLP Stack is the Critical Path
`nlp-policy-nz` has the heaviest dependency tree. Historically:
- PyTorch supports new Python within 2-4 months of CPython release
- `bitsandbytes` often takes 6+ months for new Python support
- Conda-forge packages may add further delay after PyPI releases

### 5. Windows Runner Compatibility
`corpus-nz-hansard` runs CI on `windows-2025-vs2026`. Windows prebuilt wheels for 3.14 may lag Linux, especially for scientific packages.

### 6. Pinned Dependencies at Risk
- `corpus-nz-hansard` pins `duckdb==1.5.3` — must verify 3.14 wheel availability
- Several subrepos pin tooling: `ruff==0.15.16`, `uv==0.11.8`, etc.

### 7. CI Python Version Heterogeneity
| Subrepo | CI Python Version |
|---|---|
| corpus-law-nz | 3.12 |
| corpus-nz-hansard | 3.11 (tests), 3.13 (quality) |
| corpus-cases-medilegal-nz | pixi default (>=3.11) |
| nlp-policy-nz | pixi default (>=3.11) |
| sm-govt-nz | Runner default (no pin) |
| hathi-nz | **3.14** |

---

## Recommended Migration Order

### Phase 0 — Lead (already on 3.14)
1. **hathi-nz** — Already running CI on 3.14. Needs `requires-python` and `target-version` bump to formalize. Fix the `PYTHON_VERSION` env var inconsistency with pixi.toml.

### Phase 1 — Quick Wins (simple dep trees)
2. **sm-govt-nz** — Simplest dependency tree. Add explicit `python-version: "3.14"` to CI, bump `requires-python` and `target-version`. Validate with `pyarrow`, `atproto`, `tweepy`, `yt-dlp`.

### Phase 2 — Core Pipeline (uv-based)
3. **corpus-law-nz** — Already on 3.12 in CI. Step to 3.13 first, then 3.14. Key deps `pyarrow`, `polars`, `huggingface_hub` should have 3.14 wheels early.

### Phase 3 — Mixed CI (Windows + Linux)
4. **corpus-nz-hansard** — Already testing on 3.13 in quality.yml. Need to verify `duckdb==1.5.3` 3.14 wheel. Watch for Windows-specific delays. Consider unpinning `duckdb`.

### Phase 4 — Dependent Subrepos
5. **corpus-cases-medilegal-nz** — Blocked by `nlp-policy-nz` sibling dependency. Must wait for Phase 5.

### Phase 5 — Critical ML Path
6. **nlp-policy-nz** — **Last to migrate** due to ML stack complexity. Wait for:
   - PyTorch 3.14 wheels (stable)
   - `bitsandbytes` 3.14 support (historically the bottleneck)
   - `spacy`, `faiss-cpu` 3.14 compatibility
   - Conda-forge 3.14 package availability
   - Rust extension rebuilds (lancedb, maturin -> PyO3 3.14)

### Not Applicable
- **cli-legislation-nz** — TypeScript/Node.js project, no Python migration needed.

---

## Action Items

### Immediate (Track 23.1)
- [ ] Bump `requires-python` in all 6 Python subrepos from `>=3.11` to `>=3.13` (intermediate) or `>=3.14` (direct)
- [ ] Bump `ruff target-version` from `py311` to `py314` across all 6 subrepos
- [ ] Standardize CI Python version references in workflow files
- [ ] Align `hathi-nz` `PYTHON_VERSION` env var with pixi.toml and pyproject.toml

### Short-term
- [ ] Verify `duckdb` Python 3.14 wheel availability (corpus-nz-hansard, hathi-nz)
- [ ] Verify `pyarrow` Python 3.14 wheel availability (all subrepos)
- [ ] Verify `polars` Python 3.14 wheel availability (all subrepos)
- [ ] Add explicit `python-version: "3.14"` to sm-govt-nz CI

### Medium-term (ML stack)
- [ ] Monitor PyTorch 3.14 wheel release
- [ ] Monitor `bitsandbytes` 3.14 support (historically the bottleneck)
- [ ] Monitor `spacy` 3.14 compatibility
- [ ] Monitor `faiss-cpu` 3.14 wheel availability
- [ ] Monitor conda-forge Python 3.14 package availability for pixi-managed subrepos

---

*Generated 2026-06-14 for Track 23.1 — dependency_consensus_python314_20260614*

- Must bump `requires-python` and `target-version` to match CI reality
- **Already the lead subrepo** — running 3.14 in production CI

- No explicit CI Python version
- **Simplest dependency tree** — easiest subrepo to migrate

- Rust crates need PyO3 3.14 bindings
- Shared dependency for `corpus-cases-medilegal-nz`

- Sibling dependency on `nlp-policy-nz` must be migrated first
- CI uses pixi without explicit Python version pin

- Already **testing on 3.13** — good forward momentum
- Windows runner may have slower 3.14 wheel distribution

- `ruff target-version` must be updated to `py314`
- `pyarrow`, `polars`, `torch` need Python 3.14 wheels (likely available by 2026)
- Already running CI on **3.12** — one intermediate step before 3.14


**Nature:** TypeScript/Node.js CLI application — not a Python project.  
**Package manager:** pnpm.  
**Build system:** tsup, vitest, TypeScript 5.9.3.  
**CI:** Node.js v18/20/22 matrix. No Python involved.  
**Docker:** `.devcontainer/Dockerfile` uses `mcr.microsoft.com/devcontainers/typescript-node:1-20-bookworm`.  
**Python 3.14 impact:** None — this subrepo is language-independent from the Python stack.  
**Note:** If any cross-repo CI workflows invoke this CLI with a Python runner, those invocations are unaffected by Python version.
