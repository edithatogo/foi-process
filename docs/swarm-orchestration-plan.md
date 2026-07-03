# Swarm Orchestration Plan — Legal NZ Antigravity Swarm

**Generated:** 2026-06-15  
**Source:** `task_plan.md` (root), `conductor/tracks.md` (root + subrepos), `subagents.yaml`, `swarm-config.yaml`  
**Control plane:** Root `legal-nz` with 7 core subrepos + 4 auxiliary workspaces

---

## Agent Role Summary

| Agent | Engine/Model | Role | Best For |
|---|---|---|---|
| **Architect_Oracle** | Cline, deepseek-v4-pro | Schema design, architecture review, cross-repo risk analysis | Tracks needing design validation, dependency ordering |
| **General_Coder** | Cline, deepseek-v4-flash | General implementation, file changes, tests, refactoring | Single-repo implementation tasks |
| **Codex_GPT55_Engineer** | Codex, gpt-5.5 | Cross-repo coordination, dependency reconciliation | Tracks spanning multiple subrepos (11, 12, 13, 23) |
| **Xiaomi_MiMo_Code** | Xiaomi MiMo Code | Bounded local tasks — CLI, docs, migration, templates | Tracks 24, 27, 28, 29 |
| **Quality_Validator** | Cline, deepseek-v4-flash | Lint, typecheck, test execution, DoD enforcement | Every track after implementation |
| **Chrome_Operator** | Codex, gpt-5.5 | Browser-authenticated checks, web consoles, OAuth | Only when Track 10 external gates approved |

**Team rule:** 1 Orchestrator + up to 2 Implementers + 1 Reviewer per track.

---

## Dependency Graph Overview

```
Track 10 (External Gates) ──blocks──► Track 11 (HF) ──blocks──► Track 13,14,15,16
     │
     ├──blocks──► Track 22, Track 24, Track 27 (commit/push gates)
     ├──informs──► Track 12, Track 23
     └──soft-dep──► Track 25

Track 23 ──informs──► Track 12, Track 13, Track 24
Track 27 ──enables──► All tracks needing git push
Track 28 ──informs──► Track 23.5, Track 29
```

---

## Track-by-Track Orchestration Plan

### Track 10: External Gates Queue
**Status:** `[x]` Complete (local) | **Root `legal-nz`**
- **Orchestrator:** `Architect_Oracle` | **Implementers:** None | **Reviewer:** `Quality_Validator`

**Done:** Schema unification, feature extraction, 188/193 tests pass, 7 schemas SHA256-identical.

**Remains:** Phase 3 fully gated (commit/push/`.env`/HF/Zenodo/account).

**Blockers:** 🔴 external-write gate, 🔴 Chrome gate, 🟡 npm not found, 🟡 3 API keys, 🟡 tempfile PermissionError.

**Next:** Queue all gated items; no local dispatch.

---

### Track 11: Hugging Face Namespace Organization
**Status:** `[~]` In progress | **Root coordination** + all corpus subrepos
- **Orchestrator:** `Codex_GPT55_Engineer` | **Implementers:** `General_Coder` (workflows), `Xiaomi_MiMo_Code` (dataset cards) | **Reviewer:** `Quality_Validator`

**Done:** HF datasets for Hansard, legislation, legacy DOI; private shells for medilegal and hathi; per-repo HF tokens.

**Remains:** Fix `corpus-nz-hansard` source-archive token; fix `hathi-nz` Pixi cache; fix `corpus-cases-medilegal-nz` workflow_dispatch; standardize dataset IDs.

**Blockers:** 🔴 `corpus-nz-hansard` CI fails (shared_utils import); 🔴 `hathi-nz` Pixi cache-key; 🔴 medilegal workflow_dispatch.

**First task:** Fix `corpus-nz-hansard` `shared_utils` CI import.

---

### Track 12: Isaacus Legal AI Alignment
**Status:** `[x]` Complete (planning) | **`nlp-policy-nz`**
- **Orchestrator:** `Architect_Oracle` | **Implementers:** `General_Coder` (inventory), `Codex_GPT55_Engineer` (benchmark contract) | **Reviewer:** `Quality_Validator`

**Done:** Upstream reviewed; placement decided; 7 integration phases with NZ-specific tasks.

**Blockers:** 🟡 Phase 2+ depends on Track 13; Phase 4+ needs credential gates.

**First task:** Create `nlp-policy-nz/docs/isaacus-inventory.md`.

---

### Track 13: Open New Zealand Legal Corpus
**Status:** `[~]` In progress | **Root coordination** + all corpus repos
- **Orchestrator:** `Codex_GPT55_Engineer` | **Implementers:** `General_Coder` (card), `Xiaomi_MiMo_Code` (sample) | **Reviewer:** `Architect_Oracle` + `Quality_Validator`

**Done:** Concept drafted; source repos mapped; dataset contract defined.

**Blockers:** 🔴 Track 11 HF gates needed for Phases 3-5.

**First task:** Draft corpus card at `docs/corpus-card-open-nz-legal.md`.

---

### Track 14: Open New Zealand Parliament Corpus
**Status:** `[x]` Complete (planning) | **`corpus-nz-hansard`**
- **Orchestrator:** `Architect_Oracle` | **Implementer:** `General_Coder` | **Reviewer:** `Quality_Validator`

**Done:** Concept/release path documented; scope and field contract defined.

**Blockers:** 🟡 Phase 2+ depends on Track 10; Phase 3+ depends on `corpus-law-nz` fields.

**First task:** Create `corpus-nz-hansard/docs/parliament-corpus-identity.md`.

---

### Track 15: Open New Zealand Legislative History Corpus
**Status:** `[~]` In progress | **`corpus-law-nz`**
- **Orchestrator:** `Codex_GPT55_Engineer` | **Implementers:** `General_Coder` + `Xiaomi_MiMo_Code` | **Reviewer:** `Quality_Validator`

**Done:** Concept documented; scope defined.

**Blockers:** 🟡 Phase 3+ depends on Track 10; Phase 4+ depends on `corpus-nz-hansard` bill mapping.

**First task:** Complete the local-only update, finalize scope.

### Track 16: Citation Graph, Benchmarks, Retrieval Evaluation
**Status:** `[ ]` Not started | **`nlp-policy-nz`**
- **Orchestrator:** `Architect_Oracle` | **Implementers:** `General_Coder` (inventory), `Codex_GPT55_Engineer` (prototype) | **Reviewer:** `Quality_Validator`

**First task:** Inventory citation fields across all corpus schemas.

**Blockers:** 🔴 No deliverables assigned; 🟡 Depends on Track 13 exports.

---

### Track 17: Open Historical NZ Legal Corpus
**Status:** `[ ]` Not started | **`hathi-nz`**
- **Orchestrator:** `Architect_Oracle` | **Implementer:** `General_Coder` | **Reviewer:** `Quality_Validator`

**First task:** Define scope — what historical materials are in-scope.

**Blockers:** 🔴 No deliverables assigned; 🟡 `hathi-nz` already has 143/143 tests.

---

### Track 18: Regulatory & Government Publications Corpus
**Status:** `[ ]` Not started | **`sm-govt-nz`**
- **Orchestrator:** `Architect_Oracle` | **Implementers:** `General_Coder` + `Xiaomi_MiMo_Code` | **Reviewer:** `Quality_Validator`

**First task:** Define scope — identify NZ regulator sources.

**Blockers:** 🔴 No deliverables assigned; 🟡 Depends on Track 21 DigitalNZ discovery.

---

### Track 19: Treaty, Māori, Te Reo Māori Legal Corpus
**Status:** `[ ]` Not started (governance-gated) | **Root coordination**
- **Orchestrator:** `Architect_Oracle` | **Implementer:** `General_Coder` (doc-only) | **Reviewer:** `Quality_Validator`

**Done:** Opening note created; 5 tasks defined; guardrails documented.

**Blockers:** 🔴 Governance approval required; 🔴 No scraping/public release without approval.

**First task:** Task 19.1 — Inventory candidate source categories (documentation-only).

---

### Track 20: Treaty/Māori Governance Artifacts
**Status:** `[ ]` Not started | **Root coordination**
- **Orchestrator:** `Architect_Oracle` | **Implementer:** `General_Coder` | **Reviewer:** `Quality_Validator`

**First task:** Draft governance decision memo (Task 19.5).

**Blockers:** 🔴 Governance approval required; 🟡 May overlap with Track 19.

---

### Track 21: DigitalNZ Discovery Layer
**Status:** `[ ]` Not started | **`nlp-policy-nz`**
- **Orchestrator:** `Codex_GPT55_Engineer` | **Implementers:** `General_Coder` (probe), `Xiaomi_MiMo_Code` (crosswalk) | **Reviewer:** `Quality_Validator`

**Done (research):** API docs reviewed; 6 probe queries performed; 10 tasks defined.

**First task:** Task 21.5 — Add DigitalNZ probe script in `nlp-policy-nz`.

**Blockers:** 🟡 Rights review required; 🟡 High-volume harvesting needs API key.

---

### Track 22: Root Ownership Audit & Migration
**Status:** `[~]` In progress | **Root `legal-nz`**
- **Orchestrator:** `Architect_Oracle` | **Implementers:** `General_Coder` (root), `Xiaomi_MiMo_Code` (subrepo) | **Reviewer:** `Quality_Validator`

**Done:** `shared_utils.py` removed; hash helpers moved; `corpus-law-nz/utils.py` self-contained.

**Remains:** Commit root + `corpus-law-nz` changes; push; check Actions.

**Blockers:** 🔴 External-write gate.



---

### Track 23: Dependency Consensus & Toolchain Standardization
**Status:** `[ ]` Not started | **Root coordination** + all subrepos
- **Orchestrator:** `Codex_GPT55_Engineer` | **Implementers:** `General_Coder` (Python), `Xiaomi_MiMo_Code` (TS) | **Reviewer:** `Architect_Oracle` + `Quality_Validator`

**Sub-tracks:**
- **23.1 (Py3.14):** Inventory `pyproject.toml`, lockfiles, CI Python versions per subrepo
- **23.2 (uv/Pixi):** Decision matrix; 🔴 `hathi-nz` Pixi cache-key must be fixed first
- **23.3 (Rust Hot-Path):** Profile ingestion in `corpus-law-nz`
- **23.4 (Vector/RAG):** Define LanceDB/Qdrant/FAISS interface in `nlp-policy-nz`
- **23.5 (TS Toolchain):** Baseline timings in `cli-legislation-nz`

---

### Track 24: Registry Submission Manifests
**Status:** `[~]` In progress | **Root (templates)** + all subrepos (manifests)
- **Orchestrator:** `Xiaomi_MiMo_Code` | **Implementer:** `General_Coder` | **Reviewer:** `Architect_Oracle` + `Quality_Validator`

**Done:** Schema, workflow template, fixture manifests (cli, mcp_server, python_package, container, dataset).

**Remains:** Create manifests in each owning subrepo.

**Blockers:** 🔴 External-write gate; 🟡 Phase 3-4 needs tokens/credentials.

**First task:** Create manifest in `cli-legislation-nz`.

---

### Track 25: Conductor Self-Learning Loops
**Status:** `[~]` In progress | **Root** + all subrepos
- **Orchestrator:** `Xiaomi_MiMo_Code` | **Implementer:** `General_Coder` | **Reviewer:** `Quality_Validator`

**Done:** `conductor/templates/self-improvement-loop.md` and schema added; learning logs and backlogs seeded.

**First task:** Add CI-safe learning candidates summarizer and promote reviewed lessons to shared templates.

**Blockers:** 🟡 Low priority; needs active tracks for learning material.

---

### Track 26: Quality & Maintenance Tooling Baseline
**Status:** `[x]` Complete (coordination) | **Root** + all subrepos
- **Orchestrator:** `Xiaomi_MiMo_Code` | **Implementer:** `General_Coder` | **Reviewer:** `Quality_Validator`

**Done:** Audit of Vale, markdown style, Codecov, Renovate, Scalene; baseline decisions.

**First task:** Create per-repo quality checklists.

**Blockers:** 🟡 Needs commit/push for completion.

---

### Track 27: Root Remote & Submodule Workspace
**Status:** `[~]` In progress | **Root `legal-nz`**
- **Orchestrator:** `Codex_GPT55_Engineer` | **Implementers:** `General_Coder` (git), `Xiaomi_MiMo_Code` (docs) | **Reviewer:** `Quality_Validator`

**Done:** `.gitmodules` created; GitHub repo created; root pushed (`af9f015`); docs created.

**Remains:** Confirm submodule rendering; reattach worktree; resolve `index.lock` blockers; push subrepo changes.

**Blockers:** 🔴 OneDrive `.git` write denial; 🔴 `.git/index.lock` blockers; 🔴 external-write gate.

**First task:** Resolve `.git/index.lock` blockers.

---

### Track 28: CLI-First Tooling Policy
**Status:** `[~]` In progress | **Root (policy)** + all subrepos (impl)
- **Orchestrator:** `Xiaomi_MiMo_Code` | **Implementer:** `General_Coder` | **Reviewer:** `Quality_Validator`

**Done:** Policy doc, tool registry, root CLI surfaces mapped, swarm prompts updated.



---

## Per-Subrepo Orchestration Cells

### `cli-legislation-nz` (Remote: `edithatogo/nz-legislation`)
| Root Track | Orchestrator | Implementers | Status |
|---|---|---|---|
| Track 23.5 (TS Toolchain) | `Xiaomi_MiMo_Code` | `General_Coder` | Not started |
| Track 24 (Registry) | `Xiaomi_MiMo_Code` | `General_Coder` | Phase 1 done |
| Track 26 (Quality) | `Xiaomi_MiMo_Code` | `General_Coder` | Not started |
| Track 28 (CLI-First) | `Architect_Oracle` | `Xiaomi_MiMo_Code` | Phase 1 done |
| Track 29 (Astro) | `Xiaomi_MiMo_Code` | `General_Coder` | Not started |

### `corpus-law-nz` (Remote: `edithatogo/corpus-legislation-nz`)
| Root Track | Orchestrator | Implementers | Status |
|---|---|---|---|
| Track 11 (HF) | `Codex_GPT55_Engineer` | `General_Coder` | Tokens set |
| Track 13 (Legal Corpus) | `Codex_GPT55_Engineer` | `General_Coder` | Phase 1 |
| Track 15 (Leg History) | `Codex_GPT55_Engineer` | `General_Coder` + `Xiaomi_MiMo_Code` | In progress |
| Track 22 (Migration) | `Architect_Oracle` | `Xiaomi_MiMo_Code` | Ready for commit |
| Track 23.1 (Py3.14) | `General_Coder` | — | Not started |
| Track 26 (Quality) | `Xiaomi_MiMo_Code` | `General_Coder` | Not started |

### `corpus-nz-hansard` (Remote: `edithatogo/corpus-nz-hansard`)
| Root Track | Orchestrator | Implementers | Status |
|---|---|---|---|
| Track 11 (HF) | `Codex_GPT55_Engineer` | `General_Coder` | ⚠️ Token scope |
| Track 13 (Legal Corpus) | `Codex_GPT55_Engineer` | `General_Coder` | Phase 1 |
| Track 14 (Parliament) | `Architect_Oracle` | `General_Coder` | Phase 1 |
| Track 28 (CLI-First) | `Xiaomi_MiMo_Code` | `General_Coder` | 130+ scripts |

**Critical:** Fix `shared_utils` CI import — highest-priority blocker.

### `corpus-cases-medilegal-nz` (Private; 98/98 tests)
| Root Track | Orchestrator | Implementers | Status |
|---|---|---|---|
| Track 11 (HF) | `Codex_GPT55_Engineer` | `General_Coder` | ⚠️ workflow_dispatch |
| Track 13 (Legal) | `Codex_GPT55_Engineer` | `General_Coder` | Governance-gated |

### `hathi-nz` (143/143 tests; Phases 1-4 complete)
| Root Track | Orchestrator | Implementers | Status |
|---|---|---|---|
| Track 11 (HF) | `Codex_GPT55_Engineer` | `General_Coder` | ⚠️ Pixi cache |
| Track 17 (Historical) | `Architect_Oracle` | `General_Coder` | Scope TBD |
| Track 23.2 (uv/Pixi) | `General_Coder` | — | 🔴 Cache-key |

### `nlp-policy-nz` (23 local tracks)
| Root Track | Orchestrator | Implementers | Status |
|---|---|---|---|
| Track 10 (Schema) | `Architect_Oracle` | `General_Coder` | Complete |
| Track 12 (Isaacus) | `Architect_Oracle` | `General_Coder` + `Codex_GPT55_Engineer` | Planning done |
| Track 16 (Citation) | `Architect_Oracle` | `General_Coder` + `Codex_GPT55_Engineer` | Not started |
| Track 21 (DigitalNZ) | `Codex_GPT55_Engineer` | `General_Coder` + `Xiaomi_MiMo_Code` | Not started |
| Track 23.4 (Vector/RAG) | `Architect_Oracle` | `General_Coder` | Not started |

### `sm-govt-nz` (Vale fix applied)
| Root Track | Orchestrator | Implementers | Status |
|---|---|---|---|
| Track 13 (Legal) | `Codex_GPT55_Engineer` | `General_Coder` | Governance-gated |
| Track 18 (Regulatory) | `Architect_Oracle` | `General_Coder` | Not started |
| Track 28 (CLI-First) | `Xiaomi_MiMo_Code` | `General_Coder` | Script inventory needed |
**Remains:** Audit `fyi-cli`, classify `dnz`, inventory `corpus-nz-hansard` (130+ scripts), `sm-govt-nz` scripts.

**First task:** Inventory `corpus-nz-hansard` scripts for CLI consolidation.

---

### Track 29: Astro Documentation Standard
**Status:** `[~]` In progress | **Root (policy)** + all subrepos (impl)
- **Orchestrator:** `Xiaomi_MiMo_Code` | **Implementer:** `General_Coder` | **Reviewer:** `Quality_Validator`

**Done:** Policy doc, Astro checklist, plugin assessment, baseline JSON.

**Remains:** Audit docs tooling across all subrepos; classify each repo.

**First task:** Audit documentation tooling across 7 core subrepos.

**Blockers:** 🟡 Low priority.

---

### Track 30: Multi-Model Swarm Orchestration
**Status:** `[~]` In progress | **Root `legal-nz`**
- **Orchestrator:** `Codex_GPT55_Engineer` | **Implementers:** `General_Coder` (scripts), `Xiaomi_MiMo_Code` (presets) | **Reviewer:** `Quality_Validator`

**Done:** Orchestration models doc; presets updated; parser supports metadata.

**Remains:** Continue refining agent assignment; track lane conflicts.

**Blockers:** 🟡 Ongoing maintenance.
**First task:** Review diff, prepare commit scope.


---

## Priority Execution Order

**Tier 1 — Unblock Pipeline:**
1. Track 10 — Queue gated items for user approval
2. Track 22 — Commit/push ownership migration
3. Track 27 — Resolve git infrastructure

**Tier 2 — Fix Active Blockers:**
4. Track 11 — Fix CI imports, Pixi cache, workflow_dispatch
5. Track 23.2 — Fix `hathi-nz` Pixi cache-key

**Tier 3 — Corpus Foundation:**
6. Track 23.1 — Dependency inventory / Python 3.14
7. Track 13 — Open NZ Legal Corpus
8. Track 14 — Open NZ Parliament Corpus
9. Track 15 — Legislative History Corpus

**Tier 4 — Exploration:**
10. Track 12 — Isaacus benchmarks
11. Track 21 — DigitalNZ discovery
12. Track 16 — Citation graph prototype

**Tier 5 — Tooling:**
13. Track 24 — Registry manifests
14. Track 26 — Quality baseline
15. Track 28 — CLI-first enforcement
16. Track 29 — Astro docs
17. Track 25 — Self-learning loops
18. Track 23.5 — TS toolchain

**Tier 6 — Governance-Gated:**
19. Track 19/20 — Treaty/Māori/Te Reo
20. Track 17 — Historical corpus (scope)
21. Track 18 — Regulatory corpus (scope)

---

## Blocker Classification

### 🔴 Critical (Resolve — Block Multiple Tracks)
| Blocker | Tracks | Resolution |
|---|---|---|
| External-write gate | 10, 11, 13-15, 22, 24, 27 | User approval per action |
| Chrome gate | 10, 11 | User approval + browser session |
| `corpus-nz-hansard` source-archive token | 11, 14 | Re-check HF token permissions |
| `hathi-nz` Pixi cache-key | 11, 23.2 | Fix GHA pixi cache workflow |
| Medilegal workflow_dispatch | 11 | Restructure workflow YAML |
| `corpus-nz-hansard` CI shared_utils import | 11, 14 | Fix CI workflow reference |
| OneDrive `.git` write denial | 27 | Restore local git metadata |
| `.git/index.lock` blockers | 27 | Manual cleanup |
| Tracks 16/17/18 — undefined scope | 16, 17, 18 | Assign deliverables in task_plan.md |
| Tracks 19/20 — governance | 19, 20 | Document approval path |

### 🟡 Safe-to-Skip (Deferrable)
| Blocker | Tracks | Notes |
|---|---|---|
| npm not found | 10, 23.5 | TS dev blocked; Python unaffected |
| 3 API keys unset | 10, 11 | Needed only for live API/sync |
| Windows tempfile PermissionError | 10 | OneDrive issue; workaround exists |
| `fyi-cli` / `dnz` classification | 27, 28, 29 | Not on critical path |
| `selectolax` benchmarks | 23.3 | Experimental; no blocker |

---

## Agent Lane Principles

1. **Codex_GPT55_Engineer** — Tracks spanning ≥2 subrepos (11, 12, 13, 15, 21, 23, 27, 30).
2. **Xiaomi_MiMo_Code** — Bounded tasks: CLI, Astro, templates, manifests, migration (22, 24-26, 28, 29, 23.5).
3. **General_Coder** — Single-repo implementation: inventory, profiling, CI fixes, config changes.
4. **Architect_Oracle** — Pre/post review for schema-heavy (12, 13), governance-gated (19, 20), cross-repo ordering.
5. **Quality_Validator** — After every implementation phase, before any commit claim.
6. **Chrome_Operator** — Serial and gated; only when Track 10 gates explicitly approved.

---

## Next Immediate Actions

1. **Track 22** — `Architect_Oracle` review diff → `General_Coder` prepare commit → `Quality_Validator` verify
2. **Track 11** — `Codex_GPT55_Engineer` diagnose → `General_Coder` fix `corpus-nz-hansard` CI → `Quality_Validator` test
3. **Track 27** — Manual/`General_Coder` resolve `.git/index.lock` → `Codex_GPT55_Engineer` verify submodules
4. **Track 12** — `General_Coder` create `isaacus-inventory.md` → `Architect_Oracle` review
5. **Track 21** — `General_Coder` implement DigitalNZ probe → `Xiaomi_MiMo_Code` crosswalk → `Quality_Validator` test
