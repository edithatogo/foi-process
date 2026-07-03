# Python 3.14 Wheel Blockers

**Generated:** 2026-06-23  
**Track:** `dependency_consensus_python314`  
**Python 3.14 release date:** 2025-10-07 (PEP 745)

## Summary

| # | Package | Latest Version | PyPI 3.14 Wheel? | Conda-Forge 3.14? | Dependents | Risk | Notes |
|---|---------|---------------|-----------------|-------------------|------------|------|-------|
| 1 | **torch** | 2.11.0 (stable) | ✅ Yes (cp314) | ✅ Yes | corpus-law-nz, corpus-nz-hansard, nlp-policy-nz | **Medium** | CUDA wheels exist for cu130/cu128/cu126 on cp314. CPU-only fallback if pinned to old CUDA index. Free-threaded (cp314t) nightly wheels experimental. |
| 2 | **transformers** | 5.12.1 | ✅ Yes (py3 none-any) | ✅ Yes | corpus-law-nz, corpus-nz-hansard, nlp-policy-nz | **Low** | Pure Python wheel — works on any Python 3.10+. `setup.py` declares `SUPPORTED_PYTHON_VERSIONS = (10, 14)`. Minor bug with tensorflow_text backend on 3.14 reported/resolved. |
| 3 | **bitsandbytes** | 1.33.7-preview | ✅ Yes (py3 none-any) | ⬜ Unknown | nlp-policy-nz | **Medium** | PyPI wheel is `py3-none-any` (pure Python interface). Actual CUDA/C++ extensions distributed as pre-built binaries from GitHub releases. `pyproject.toml` declares Python 3.14 classifier. Release notes explicitly mention "Python 3.14 compatibility with PyTorch 2.9". |
| 4 | **spacy** | 3.8.14 | ❌ **Missing cp314 on PyPI** | ✅ Yes (cp314) | nlp-policy-nz | **High** | GitHub release `v3.8.14` lists cp314 wheels but they were **not uploaded to PyPI** (see [explosion/spaCy#13949](https://github.com/explosion/spaCy/issues/13949)). v3.8.13 had them. Conda-forge has cp314 builds for all platforms. **Blocker: use conda-forge or pin to spacy<3.8.14.** |
| 5 | **faiss-cpu** | 1.14.3 | ✅ Yes (cp314 via abi3) | ✅ Yes | nlp-policy-nz | **Low** | Uses `cp310-abi3` (stable ABI) — single wheel works for all Python 3.10+. CI builds for 3.10-3.14 confirmed in faiss PR #4862. |
| 6 | **duckdb** | 1.5.3 | ✅ Yes (nightly); **Stable 1.5.3 has cp314** | ✅ Yes | corpus-nz-hansard, hathi-nz | **Low** | Python 3.14 support merged Oct 2025 (PR #116). Stable releases from 1.5.0+ include cp314 wheels on PyPI. |
| 7 | **pyarrow** | 24.0.0 | ✅ Yes (cp314) | ✅ Yes (cp314) | ALL subrepos | **Low** | Python 3.14 support added in Arrow 22.0.0 (Oct 2025). Full cp314 wheels for all platforms on PyPI. |
| 8 | **polars** | 1.41.2 | ✅ Yes (cp314) | ✅ Yes | ALL subrepos except sm-govt-nz | **Low** | Python 3.14 support confirmed working in polars 1.38+ (closed issue #25035). CI runs on 3.14. Free-threaded (cp314t) wheels not yet on PyPI — tracked in issue #27955. |
| 9 | **lancedb** | 0.33.0 | ⬜ **Unknown — platform-dependent** | ⬜ Unknown | nlp-policy-nz | **Medium** | Issue [#2902](https://github.com/lancedb/lancedb/issues/2902) reports it works on some platforms but not others. Some users confirm working on Linux Python 3.14, others report "no matching wheel". **Needs manual verification on target platform.** |
| 10 | **FlagEmbedding** | 1.4.0 | ✅ Yes (py3 none-any) | ⬜ Unknown | corpus-law-nz, corpus-nz-hansard | **Low** | Pure Python wheel (`py3-none-any`). No compiled extensions. Works on any Python 3+. |
| 11 | **tweepy** | 4.16.0 | ✅ Yes (py3 none-any) | ✅ Yes | sm-govt-nz | **Low** | Pure Python wheel (`py3-none-any`). Requires Python >=3.9. No compiled extensions — works on any Python 3. |
| 12 | **atproto** | 0.0.67 | ✅ Yes (py3 none-any) | ⬜ Unknown | sm-govt-nz | **Low** | Python 3.14 support explicitly added in PR #629 (Oct 2025). `pyproject.toml` declares `requires-python = ">=3.9,<3.15"` and includes 3.14 classifier. |
| 13 | **yt-dlp** | 2026.6.9 | ✅ Yes (py3 none-any) | ✅ Yes | sm-govt-nz | **Low** | CI tests on Python 3.14 since Sep 2025 (commit 83b8409). PyPI classifier includes 3.14. Pure Python wheel with some bundled C extensions — works on 3.14. |
| 14 | **pdfplumber** | 0.11.10 | ✅ Yes (py3 none-any) | ⬜ Unknown | corpus-nz-hansard | **Low** | CI tests on Python 3.10–3.14 explicitly. Pure Python + pdfminer.six dependency works on 3.14. |
| 15 | **huggingface_hub** | 1.20.0 | ✅ Yes (py3 none-any) | ✅ Yes | all corpus subrepos | **Low** | Pure Python wheel. Requires Python >=3.10. The `hf-xet` dependency had a free-threaded build issue (resolved). |
| 16 | **pydantic v2** | 2.13.4 | ✅ Yes (cp314) | ✅ Yes | most subrepos | **Low** | Python 3.14 initial support added in v2.12.0 (Oct 2025). Full support in v2.13.0 (Apr 2026) including `pydantic.v1` namespace. cp314 wheels available for all platforms. |

## Risk Ratings

| Risk | Count | Packages |
|------|-------|----------|
| **High** | 1 | spacy (3.8.14 cp314 wheels missing on PyPI) |
| **Medium** | 3 | torch (CUDA index pinning), bitsandbytes (platform-dependent binaries), lancedb (platform-dependent wheels) |
| **Low** | 12 | All others |

## Blocker Details

### 🔴 High — spacy (v3.8.14)

**Issue:** The 3.8.14 release on GitHub produced cp314 wheels, but they were not uploaded to PyPI. This is a known issue documented at [explosion/spaCy#13949](https://github.com/explosion/spaCy/issues/13949).

**Workarounds:**
1. Use `conda install -c conda-forge spacy` (conda-forge has cp314 builds for all platforms)
2. Pin to `spacy==3.8.13` (that version has cp314 wheels on PyPI)
3. Install from source
4. Wait for a spacy 3.8.15+ release that fixes the PyPI upload

**Impact on nlp-policy-nz:** This is the only subrepo that depends on spacy. If the project uses pip-only dependencies (no conda), this is a blocker.

### 🟡 Medium — torch (v2.11.0)

**Issue:** PyTorch provides cp314 wheels on the official download index (`download.pytorch.org`) for CUDA 13.0, 12.8, and 12.6. However, the default PyPI does not host all CUDA variant wheels. If `requirements.txt` pins to a specific CUDA index (e.g., `cu121` or `cu124`), cp314 wheels won't be found.

**Details:**
- CUDA 13.0 wheels for cp314: Available on PyPI (default) and `download.pytorch.org/whl/cu130`
- CUDA 12.8 wheels for cp314: Available on `download.pytorch.org/whl/cu128`
- CUDA 12.6 wheels for cp314: Available on `download.pytorch.org/whl/cu126`
- Older CUDA (12.1, 12.4): **No cp314 wheels** → CPU-only fallback
- `torch.compile()` fully works on Python 3.14 (v2.11 release notes)
- `torch.jit` is not guaranteed on 3.14 (deprecation warnings added)
- Free-threaded (cp314t) experimental — nightly wheels only

**Action:** Audit all torch dependency specifications across corpus-law-nz, corpus-nz-hansard, and nlp-policy-nz to ensure CUDA index URLs point to a version with cp314 support.

### 🟡 Medium — bitsandbytes (v1.33.7-preview)

**Issue:** The PyPI package is `py3-none-any` (pure Python wrapper). The actual compiled CUDA binaries are distributed as separate wheels from GitHub releases. Python 3.14 compatibility was explicitly fixed in PR [#1831](https://github.com/bitsandbytes-foundation/bitsandbytes/pull/1831) (Fix: Python 3.14 compatibility with PyTorch 2.9).

**Details:**
- `pyproject.toml` includes Python 3.14 classifier
- GitHub CI produces `py3-none-*` wheels (stable ABI), which should work on 3.14
- The preview wheels on GitHub Releases claim 3.14 compatibility
- However, the CUDA extension compilation at install time may fail on Windows with Python 3.14 if MSVC build tools aren't configured

**Action:** Test `pip install bitsandbytes` on a Python 3.14 environment with CUDA toolkit before cutting the release.

### 🟡 Medium — lancedb (v0.33.0)

**Issue:** Mixed reports about Python 3.14 support (issue [#2902](https://github.com/lancedb/lancedb/issues/2902)). Some users report successful installation on Linux Python 3.14, while others see "no matching distribution" errors. As of v0.33.0, the `pyproject.toml` may still limit wheel tags.

**Action:** Test `pip install lancedb` on the target platform (OS + arch) before declaring success. May need to pin to a specific version or use preview releases.

## Cross-Cutting Concerns

1. **CUDA/PyTorch version alignment:** Both `bitsandbytes` and `lancedb` (when using GPU) depend on specific PyTorch+CUDA versions. Ensure the CUDA index URLs are consistent across all subrepos.

2. **Conda-forge fallback:** For spacy (the only confirmed blocker), conda-forge provides working cp314 builds. Consider using conda for nlp-policy-nz if pip-only fails.

3. **Free-threaded Python (cp314t):** None of the packages in our stack officially publish cp314t wheels. If someone runs with `PYTHON_GIL=0`, they will need to build from source for torch, bitsandbytes, and lancedb.

4. **spaCy training data:** Even if spacy installs, the language model downloads (`python -m spacy download ...`) may have their own compatibility — verify after installation.

## Verification Checklist

Before declaring the track complete, manually verify:

- [ ] `pip install spacy==3.8.14` on Python 3.14 — confirm the "no cp314 wheel" error
- [ ] `pip install lancedb` on target platform with Python 3.14
- [ ] `pip install torch --index-url https://download.pytorch.org/whl/cu130` with Python 3.14
- [ ] `pip install bitsandbytes` on Python 3.14 with CUDA available
- [ ] Full `pip install -r requirements.txt` for each subrepo on Python 3.14
- [ ] `python -c "import torch; print(torch.cuda.is_available())"` — must be `True`
