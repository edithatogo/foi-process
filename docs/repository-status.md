# Repository Status Mapping

Status captured: 2026-06-15.

The root `legal-nz` workspace is a coordination repository. Implementation work remains in the owning subrepositories. This mapping records known repository/workspace status for orchestration, submodule hygiene, and follow-up track planning.

## Root orchestration repository

| Workspace | Remote | Branch | Current root status | Notes |
| --- | --- | --- | --- | --- |
| `legal-nz` | `https://github.com/edithatogo/legal-nz-workspace.git` | `main` | Pushed through commit `65523ed` before this classification update | Root `.git` is reattached to durable external Git metadata at `C:/Users/60217257/.gitdirs/legal-nz-root.git`. |

## Current root submodule pins

| Path | Remote | Branch | Pinned commit | Local status | Follow-up |
| --- | --- | --- | --- | --- | --- |
| `cli-legislation-nz` | `https://github.com/edithatogo/nz-legislation.git` | `main` | `b2b270c99a5cdbd7e1ce8e6b59b11af689865f67` | Dirty: `package.json` modified | Commit/push SemVer/logging update inside subrepo, then update root pin. |
| `corpus-cases-medilegal-nz` | `https://github.com/edithatogo/corpus-cases-medilegal-nz.git` | `master` | `b523bd628711d407fbfaf5b48584ee2c161d37b9` | Dirty: `pyproject.toml`, `src/corpus_cases_medilegal_nz/__init__.py` modified | Commit/push SemVer/loguru update inside subrepo, then update root pin. |
| `corpus-law-nz` | `https://github.com/edithatogo/corpus-legislation-nz.git` | `codex/historical-batch-0005-seed` | `0c441bac0695e5862bf5ca15b75b566f5597ab24` | Dirty: `pyproject.toml`, `src/nz_legislation_corpus/utils.py` modified | Commit/push SemVer/loguru and root-ownership migration work inside subrepo, then update root pin. |
| `corpus-nz-hansard` | `https://github.com/edithatogo/corpus-nz-hansard.git` | `main` | `1ec73a14d129f12238e61373248a28248e9cc5a8` | Dirty: `pyproject.toml` modified | Commit/push SemVer/loguru update inside subrepo, then update root pin. |
| `hathi-nz` | `https://github.com/edithatogo/hathi-nz.git` | `master` | `ac19f968a77d911f905b44647a06ca44d5d3164e` | Dirty: `pyproject.toml` modified | Commit/push SemVer/loguru update inside subrepo, then update root pin. |
| `nlp-policy-nz` | `https://github.com/edithatogo/nlp-policy-nz.git` | `master` | `c4f245eca65e7a15dca7879eee152c71904502de` | Dirty: `pyproject.toml`, `src/nlp_policy_nz/__init__.py` modified | Commit/push SemVer/loguru update inside subrepo, then update root pin. |
| `sm-govt-nz` | `https://github.com/edithatogo/sm-govt-nz.git` | `master` | `88530f91701c4fca20c417b10f401eff2252344a` | Dirty: `pyproject.toml` modified | Commit/push SemVer/loguru update inside subrepo, then update root pin. |
| `open_social_data` | `https://github.com/edithatogo/open_social_data.git` | `main` | `c34b510921fe0604bad18f2ef6bc1ebb226e1aac` | Clean at promotion | Approved submodule. |
| `openfisca-aotearoa` | `https://github.com/edithatogo/openfisca-aotearoa.git` | `main` | `9d77ea7ce3c45b6292d4b4eaf3566b2fb00e7ceb` | Clean at promotion | Approved submodule. |
| `sourceright` | `https://github.com/edithatogo/sourceright.git` | `main` | `b259d654bcc13d78a44e41fe755a3fb0aa2b70da` | Clean at promotion | Approved submodule. |
| `dnz` | `https://github.com/edithatogo/dnz.git` | `main` | `58d639c` | Clean at promotion except ignored local swarm artifacts | Approved submodule for DigitalNZ integration hub work. |

## Additional mapped repositories/workspaces

| Path | Detected Git root | Remote | Branch | Local status | Mapping decision |
| --- | --- | --- | --- | --- | --- |
| `fyi-cli` | `C:/Users/60217257/OneDrive - Flinders/repos/legal-nz/fyi-cli` | `https://github.com/edithatogo/fyi-cli` | `master` | Dirty: conductor docs, CI/release workflows, testing strategy, and `tests/test_webapp.py` modified | Real nested repo. Include in workspace mapping as auxiliary CLI repo pending explicit role decision and submodule promotion. |
| `Friction` | `C:/Users/60217257/OneDrive - Flinders/repos/legal-nz/Friction` | `https://github.com/edithatogo/Friction` | `master` | Clean at classification | Comparative UK open-law service-design reference repo. Do not promote to a Legal NZ implementation submodule unless a later track explicitly depends on it. |

## Current blockers

- `open_social_data` and `openfisca-aotearoa` still show submodule dirtiness in the root status and need separate cleanup.
- `fyi-cli` needs an ownership decision before adding it to `.gitmodules`.
- `Friction` is classified as reference-only and should stay outside `.gitmodules` unless a later Legal NZ track adopts it.

## Next phase

1. Resolve local Git lock/resource issues.
2. Commit and push pending subrepo changes inside each owning repo.
3. Decide whether `fyi-cli` is part of the Legal NZ workspace or a separate CLI workspace.
4. Clean up `open_social_data` and `openfisca-aotearoa` submodule dirtiness.
5. Decide whether `fyi-cli` belongs in the Legal NZ workspace or a separate CLI workspace.
6. Update root submodule pins only after the owning repositories are clean and pushed.

## CLI-first status

| Repo | CLI-first status | Required action |
| --- | --- | --- |
| `legal-nz` | Root command surfaces mapped in `docs/cli-first-policy.md` and `conductor/templates/cli-tool-registry.json`. | Use root scripts before writing custom orchestration code. |
| `cli-legislation-nz` | First-class CLI exists. | Use `nzlegislation`, `anzlegislation`, MCP bins, and `pnpm` scripts. |
| `corpus-law-nz` | First-class CLI exists. | Use `nzlc` before writing corpus scripts. |
| `nlp-policy-nz` | First-class CLI exists. | Use `nlp-policy-nz` before writing benchmark/NLP scripts. |
| `corpus-nz-hansard` | First-class CLI dispatcher added: `corpus-nz-hansard` / `nz-hansard-corpus`. | Use the package CLI before invoking `scripts/*.py` directly. |
| `sm-govt-nz` | First-class CLI dispatcher added: `sm-govt-nz` / `nz-govt-social`. | Use the package CLI before invoking social/archive scripts directly. |
| `hathi-nz` | First-class CLI dispatcher added: `hathi-nz` / `nz-hathi-corpus`. | Use the package CLI before invoking HathiTrust/HF/Zenodo scripts directly. |
| `corpus-cases-medilegal-nz` | First-class package CLI added: `corpus-cases-medilegal-nz` / `nz-medilegal-corpus`. | Use `sources` and `sync` subcommands before calling package modules directly. |
| `fyi-cli` | Exact entrypoints audited in `docs/cli-entrypoints-audit.md`: `fyi`, `fyi-cli`, `fyi-system`; Rust CLI/MCP is active migration work. | Prefer Python package entrypoints for stable user workflows; use Rust binaries only for Rust migration tracks. |
| `dnz` | Rust CLI/MCP/Python FFI workspace promoted as a submodule. | Use `dnz` CLI and MCP surfaces before writing custom DigitalNZ integration scripts. |

## Documentation platform status

Astro is the required documentation platform for every repo going forward. See `docs/documentation-platform-policy.md` and `conductor/templates/astro-docs-standard.md`.

| Repo | Current docs status | Required action |
| --- | --- | --- |
| `legal-nz` | Root policy established. | Coordinate Astro standard and cross-repo docs map. |
| `cli-legislation-nz` | Existing package metadata includes docs scripts and TypeDoc-style API documentation. | Treat API generation as input only; migrate published docs shell to Astro. |
| `corpus-law-nz` | Documentation tooling needs audit. | Add Astro docs plan or explicit root-delegation decision. |
| `corpus-nz-hansard` | Documentation tooling needs audit. | Add Astro docs plan or explicit root-delegation decision. |
| `corpus-cases-medilegal-nz` | Documentation tooling needs audit. | Add Astro docs plan or explicit root-delegation decision. |
| `hathi-nz` | Documentation tooling needs audit. | Add Astro docs plan or explicit root-delegation decision. |
| `nlp-policy-nz` | Documentation tooling needs audit. | Add Astro docs plan or explicit root-delegation decision. |
| `sm-govt-nz` | Documentation tooling needs audit. | Add Astro docs plan or explicit root-delegation decision. |
| `fyi-cli` | Documentation tooling needs audit with exact CLI entrypoints. | Include in Astro docs inventory after role decision. |
| `dnz` | Astro docs scaffold exists under `dnz/docs`. | Align with the root Astro style baseline and use as the DigitalNZ integration documentation surface. |

## Astro plugin baseline status

Standard baseline: Astro, Starlight, MDX, Sitemap, shared Legal NZ style tokens, Vale, and markdownlint.

| Repo | Plugin baseline | Extra needs |
| --- | --- | --- |
| `legal-nz` | Required | Aggregate docs portal and shared style source. |
| `cli-legislation-nz` | Required | TypeDoc remains as API generator input only. |
| `corpus-law-nz` | Required | Schema/reference rendering and dataset card embedding. |
| `corpus-nz-hansard` | Required | Large schema/table rendering and possible search tuning. |
| `corpus-cases-medilegal-nz` | Required, private-site mode acceptable | Privacy and rights callouts; sitemap conditional. |
| `hathi-nz` | Required | Rights/source callouts. |
| `nlp-policy-nz` | Required | API reference input and interactive examples only if justified. |
| `sm-govt-nz` | Required | Privacy/platform terms callouts; RSS conditional. |
| `fyi-cli` | Required if promoted | Command-reference generator conditional. |
| `dnz` | Required | Starlight/MDX/Sitemap baseline should be aligned with the root Astro style standard. |
