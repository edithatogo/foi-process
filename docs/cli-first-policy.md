# CLI-First Operating Policy

Status captured: 2026-06-15.

This workspace has multiple first-class CLI tools and repo-local command surfaces. Agents must use those tools instead of writing custom one-off code whenever a task can be completed through an existing CLI, package script, or maintained repo script.

## Rule

Use this order of preference:

1. Existing package CLI or binary.
2. Existing npm/pnpm script, Python project script, PowerShell script, or maintained repo script.
3. Existing importable library function exposed by the owning repo.
4. New CLI command or maintained script in the owning repo.
5. Temporary custom code only when no maintained surface exists, and only with a note explaining why it should not become a CLI command.

## Prohibited pattern

Do not create ad hoc custom scripts in the root workspace to bypass an existing subrepo CLI. If a workflow is repeated or operationally important, add it to the owning repo's CLI surface instead.

## Root orchestration commands

| Task | Use | Avoid |
| --- | --- | --- |
| Workspace health checks | `python workspace-doctor.py` | New Python scripts that duplicate environment/API checks |
| Naming lint | `python scripts/check_naming.py` | Manual path scans or one-off naming validators |
| Combined docs/lint checks | `python scripts/check_lint.py` | Separate improvised Vale/markdown/naming glue |
| Swarm dry-run/orchestration | `python scripts/swarm_orchestrator.py` | Hand-written dispatch loops |
| Swarm agent execution | `python scripts/swarm_agent.py` or maintained swarm PowerShell scripts | One-off process launchers |
| Document validation | `node scripts/validate-documents.js` | New Markdown/JSON drift scripts |
| Quality report generation | `node scripts/quality-report.js` | One-off quality summary generators |

## Subrepo CLI and script registry

| Repo | Preferred command surface | Use for | Current maturity |
| --- | --- | --- | --- |
| `cli-legislation-nz` | `nzlegislation`, `anzlegislation`, `nzlegislation-mcp`, `anzlegislation-mcp`, and `pnpm` scripts | Legislation API search/get/export/cite/config/cache/batch/stream/provider/MCP work | First-class CLI |
| `corpus-law-nz` | `nzlc` | Legislation corpus sync, validation, manifests, metadata packages, HF upload, archive, Zenodo upload, coverage reports, RSS feed | First-class CLI |
| `nlp-policy-nz` | `nlp-policy-nz` | Cross-corpus NLP, benchmark, graph, registry, integration, and policy-analysis workflows | First-class CLI plus API |
| `corpus-nz-hansard` | Existing maintained scripts under `scripts/` | Hansard ingestion, validation, release, publication, archive, and derived dataset tasks | Script-heavy; needs CLI consolidation track |
| `sm-govt-nz` | Existing maintained scripts under `scripts/` and importable `src/` modules | Social media archiving, syndication, probes, publishing, and secret validation | Script/module surface; needs CLI consolidation track |
| `hathi-nz` | `python scripts/fetch_hathitrust.py` and maintained scripts | HathiTrust fetching and historical material processing | Script entrypoint; needs package CLI track |
| `corpus-cases-medilegal-nz` | Importable package modules and existing config-driven pipeline surfaces | Medilegal corpus fetching/config processing | Early stage; needs package CLI track before repeat operations |
| `fyi-cli` | Repo-local CLI/package scripts | FYI/OIA CLI workflows | Mapped as auxiliary CLI repo; role and exact entrypoints require follow-up audit |
| `dnz` | None approved | No CLI usage until repo boundary is classified | Not submodule-ready; do not dispatch ad hoc code through it |

## Task gate

Before implementing any task:

1. Identify the owning repo.
2. Check `conductor/templates/cli-tool-registry.json` and this policy for an existing command surface.
3. If a command exists, use it.
4. If the command is insufficient, extend the owning repo's CLI or maintained script surface.
5. If temporary custom code is unavoidable, record the reason and create or update a conductor task to convert it into a maintained CLI command.

## Agent prompt requirement

Swarm agents must say which CLI or maintained command surface they used. If none exists, they must record that absence as a maturity gap in the relevant conductor track.
