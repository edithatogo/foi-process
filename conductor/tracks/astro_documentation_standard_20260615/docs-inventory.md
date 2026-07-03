# Track 22 Phase 2 — Documentation Tooling Inventory

**Date:** 2026-06-15
**Scope:** All 8 target repos under legal-nz monorepo
**Method:** Manual filesystem inspection of each repo root, `docs/`, and `docs-site/`

---

## cli-legislation-nz

| Category | Status | Details |
|----------|--------|---------|
| docs/ directory | ✅ | `adr/`, `developer-guide/`, `maintainers/`, `user-guide/`, `capabilities.md`, `documentation-site-config.md`, `documentation-site-setup.md`, `LAUNCH_MAINTENANCE.md`, `PERFORMANCE_DASHBOARD.md`, `PERFORMANCE_METRICS_GUIDE.md`, `PERFORMANCE_SCORECARDS.md`, `provider-runtime.md`, `testing-validation-guide.md` |
| README.md | ✅ | 627 lines, substantial |
| Astro config | ✅ | `docs-site/astro.config.mjs` |
| Other SSG config | ✅ | `typedoc.json` (API reference docs) |
| package.json docs deps | ✅ | `typedoc` (root); `@astrojs/starlight`, `@astrojs/mdx`, `@astrojs/sitemap`, `astro` (docs-site) |
| docs scripts | ✅ | `docs` (typedoc), `docs:serve`, `docs:dev` (--prefix docs-site), `docs:build`, `docs:check` |
| Makefile docs targets | ❌ | No Makefile |
| website/site directory | ❌ | Neither |
| **Classification** | **astro-native** | Has both Astro Starlight docs-site and typedoc API docs; full docs pipeline in place |

---

## nlp-policy-nz

| Category | Status | Details |
|----------|--------|---------|
| docs/ directory | ✅ | `architecture_comparison.md`, `build_backend.md`, `isaacus_integration.md`, `isaacus-inventory.md`, `multi_archive_strategy.md`, `perf.md`, `profiling.md`, `pydantic_vs_msgspec.md` |
| README.md | ✅ | 92 lines, moderate |
| Astro config | ✅ | `docs-site/astro.config.mjs` |
| Other SSG config | ❌ | None |
| package.json docs deps | ✅ | `@astrojs/starlight`, `@astrojs/mdx`, `@astrojs/sitemap`, `astro` (docs-site) |
| docs scripts | ✅ | `docs:dev`, `docs:build`, `docs:check` (all via `--prefix docs-site`) |
| Makefile docs targets | ❌ | No Makefile |
| website/site directory | ❌ | Neither |
| **Classification** | **astro-native** | Has Astro Starlight docs-site with content pipeline |

---

## corpus-law-nz

| Category | Status | Details |
|----------|--------|---------|
| docs/ directory | ✅ | `ADR/`, `zenodo/`, and 50+ markdown files covering design docs, runbooks, policies, contracts, release notes |
| README.md | ✅ | 242 lines, substantial |
| Astro config | ✅ | `docs-site/astro.config.mjs` |
| Other SSG config | ❌ | None |
| package.json docs deps | ✅ | `@astrojs/starlight`, `@astrojs/mdx`, `@astrojs/sitemap`, `astro` (docs-site) |
| docs scripts | ✅ | `docs:dev`, `docs:build`, `docs:check` (all via `--prefix docs-site`) |
| Makefile docs targets | ❌ | Makefile exists but has no docs-related targets |
| website/site directory | ❌ | Neither |
| **Classification** | **astro-native** | Has Astro Starlight docs-site; Makefile for build/test only |

---

## corpus-nz-hansard

| Category | Status | Details |
|----------|--------|---------|
| docs/ directory | ✅ | `static-documentation-portal/` and 75+ markdown files covering contracts, design docs, runbooks, release decisions |
| README.md | ✅ | 154 lines, substantial |
| Astro config | ✅ | `docs-site/astro.config.mjs` |
| Other SSG config | ❌ | None |
| package.json docs deps | ✅ | `@astrojs/starlight`, `@astrojs/mdx`, `@astrojs/sitemap`, `astro` (docs-site) |
| docs scripts | ✅ | `docs:dev`, `docs:build`, `docs:check` (all via `--prefix docs-site`) |
| Makefile docs targets | ❌ | Makefile exists (extensive) but has no docs-related targets |
| website/site directory | ❌ | Neither |
| **Classification** | **astro-native** | Has Astro Starlight docs-site; large docs/ archive of design records |

---

## corpus-cases-medilegal-nz

| Category | Status | Details |
|----------|--------|---------|
| docs/ directory | ✅ | `cli-first.md` |
| README.md | ✅ | 232 lines, substantial |
| Astro config | ✅ | `docs-site/astro.config.mjs` |
| Other SSG config | ❌ | None |
| package.json docs deps | ✅ | `@astrojs/starlight`, `@astrojs/mdx`, `@astrojs/sitemap`, `astro`, `astro-expressive-code` (docs-site) |
| docs scripts | ✅ | `docs:dev`, `docs:build`, `docs:check` (all via `--prefix docs-site`) |
| Makefile docs targets | ❌ | No Makefile |
| website/site directory | ❌ | Neither |
| **Classification** | **astro-native** | Has Astro Starlight docs-site |

---

## hathi-nz

| Category | Status | Details |
|----------|--------|---------|
| docs/ directory | ✅ | `cli-first.md` |
| README.md | ✅ | 257 lines, substantial |
| Astro config | ✅ | `docs-site/astro.config.mjs` |
| Other SSG config | ❌ | None |
| package.json docs deps | ✅ | `@astrojs/starlight`, `@astrojs/mdx`, `@astrojs/sitemap`, `astro`, `astro-expressive-code` (docs-site) |
| docs scripts | ✅ | `docs:dev`, `docs:build`, `docs:check` (all via `--prefix docs-site`) |
| Makefile docs targets | ❌ | No Makefile |
| website/site directory | ❌ | Neither |
| **Classification** | **astro-native** | Has Astro Starlight docs-site |

---

## sm-govt-nz

| Category | Status | Details |
|----------|--------|---------|
| docs/ directory | ✅ | `bluesky-mirror-runbook.md`, `cli-first.md`, `courts-nz-adapter-contracts.md`, `courts-nz-dataset-publication.md`, `courts-nz-email-ingress-fallbacks.md`, `courts-nz-email-ingress.md`, `courts-nz-linkedin-access.md`, `courts-nz-x-archive-access.md`, `source-health-statuses.md`, `source-tools.md`, `upstream-contributions.md`, `x-poc.md`, `zernio.md` |
| README.md | ❌ | Missing (has `SETUP_GUIDE.md` instead) |
| Astro config | ✅ | `docs-site/astro.config.mjs` |
| Other SSG config | ❌ | None |
| package.json docs deps | ✅ | `@astrojs/starlight`, `@astrojs/mdx`, `@astrojs/sitemap`, `astro`, `astro-expressive-code` (docs-site) |
| docs scripts | ✅ | `docs:dev`, `docs:build`, `docs:check` (all via `--prefix docs-site`) |
| Makefile docs targets | ❌ | No Makefile |
| website/site directory | ❌ | Neither |
| **Classification** | **astro-native** | Has Astro Starlight docs-site but missing root README.md |

---

## legal-nz (root)

| Category | Status | Details |
|----------|--------|---------|
| docs/ directory | ✅ | `astro-plugin-assessment.md`, `cli-first-policy.md`, `documentation-platform-policy.md`, `external-platform-mapping.md`, `open-new-zealand-government-social-media-corpus.md`, `open-new-zealand-legal-corpus.md`, `open-new-zealand-parliament-corpus.md`, `open-new-zealand-regulatory-guidance-corpus.md`, `open-new-zealand-treaty-maori-law-corpus.md`, `registry-submission-manifests.md`, `repository-status.md`, `root-submodules.md`, `swarm-orchestration-models.md`, `swarm-orchestration-plan.md` |
| README.md | ✅ | 14 lines, minimal |
| Astro config | ❌ | None at root or in docs/ |
| Other SSG config | ❌ | None |
| package.json docs deps | ❌ | No root package.json |
| docs scripts | ❌ | No package.json |
| Makefile docs targets | ❌ | No Makefile |
| website/site directory | ❌ | Neither |
| **Classification** | **legacy-migration** | Has markdown docs/ with no SSG; acts as monorepo orchestrator; subrepos own their Astro sites independently |

---

## Summary Table

| Repo | Classification | docs/ | README | Astro | Docs Scripts | Notes |
|------|---------------|-------|--------|-------|-------------|-------|
| cli-legislation-nz | **astro-native** | ✅ 13 items | ✅ 627 lines | ✅ docs-site/ | ✅ docs, docs:dev, docs:build, docs:check, docs:serve | Also has typedoc API docs |
| nlp-policy-nz | **astro-native** | ✅ 8 items | ✅ 92 lines | ✅ docs-site/ | ✅ docs:dev, docs:build, docs:check | |
| corpus-law-nz | **astro-native** | ✅ 50+ items | ✅ 242 lines | ✅ docs-site/ | ✅ docs:dev, docs:build, docs:check | Largest docs/ archive |
| corpus-nz-hansard | **astro-native** | ✅ 75+ items | ✅ 154 lines | ✅ docs-site/ | ✅ docs:dev, docs:build, docs:check | Largest docs/ archive |
| corpus-cases-medilegal-nz | **astro-native** | ✅ 1 item | ✅ 232 lines | ✅ docs-site/ | ✅ docs:dev, docs:build, docs:check | |
| hathi-nz | **astro-native** | ✅ 1 item | ✅ 257 lines | ✅ docs-site/ | ✅ docs:dev, docs:build, docs:check | |
| sm-govt-nz | **astro-native** | ✅ 13 items | ❌ (missing) | ✅ docs-site/ | ✅ docs:dev, docs:build, docs:check | Missing README.md |
| legal-nz (root) | **legacy-migration** | ✅ 14 items | ✅ 14 lines (minimal) | ❌ | ❌ | No SSG; monorepo policy docs |

**Key findings:**
1. **All 7 subrepos** already have Astro Starlight configured at `docs-site/astro.config.mjs` — unanimous **astro-native**.
2. **cli-legislation-nz** is most mature: has Typedoc API docs + Astro Starlight + full docs pipeline (`docs:dev`, `docs:build`, `docs:check`, `docs:serve`, plus `lint:docs` for vale).
3. All 7 subrepos share the same docs-site pattern: `@astrojs/starlight`, `@astrojs/mdx`, `@astrojs/sitemap`, `astro` with dev/start/build/check/preview scripts.
4. **sm-govt-nz** is the only subrepo missing a root README.md — gap to fix.
5. **Root legal-nz** is **legacy-migration**: has `docs/` with 14 policy/architecture `.md` files but no SSG, no package.json, no build pipeline. Its subrepos each own their docs independently.
