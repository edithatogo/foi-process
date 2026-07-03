# Swarm Orchestration Models

Status captured: 2026-06-15.

The Legal NZ root swarm uses multiple implementation lanes so work can be assigned by strength while preserving repository boundaries and gates.

## Required swarm lanes

| Lane | Engine | Model | Primary use |
| --- | --- | --- | --- |
| `General_Coder` | Cline | `deepseek-v4-flash` | Fast local implementation and routine repo tasks. |
| `Codex_GPT55_Engineer` | Codex | `gpt-5.5` | Cross-repo integration, architecture-sensitive implementation, and final reconciliation. |
| `Xiaomi_MiMo_Code` | Xiaomi MiMo Code | `xiaomi-mimo-code` | Additional code-generation and implementation lane for bounded local tasks, refactors, and CLI/docs migrations. |
| `Architect_Oracle` | Cline-compatible reasoning lane | `deepseek-v4-pro` | Architecture, schema, dependency, and migration review. |
| `Chrome_Operator` | Codex/Chrome-gated lane | `gpt-5.5` | Browser-authenticated or Chrome-only work. |
| `Quality_Validator` | Validator lane | `deepseek-v4-flash` | Lint, tests, docs checks, command-surface checks, and gate verification. |

## Assignment rules

- Use `General_Coder` for straightforward local changes inside one repo.
- Use `Xiaomi_MiMo_Code` for bounded implementation tasks that can run in parallel with `General_Coder`.
- Use `Codex_GPT55_Engineer` when the task crosses repo boundaries, affects root orchestration, or needs careful sequencing.
- Use `Architect_Oracle` before dependency, schema, documentation-platform, or registry decisions become implementation tasks.
- Use `Chrome_Operator` only when Chrome, OAuth, authenticated browser sessions, or browser-rendered verification is explicitly needed.
- Use `Quality_Validator` after each task/phase/track before commit/push claims.

## Shared constraints

- Respect the root/subrepo ownership model.
- Use existing CLIs, package scripts, and maintained repo scripts before custom code.
- Use Astro for documentation site work.
- Keep external writes, Chrome access, account changes, uploads, and `.env` changes behind explicit gates.
- Record blockers instead of bypassing credentials, locks, or account state.

## Presets

The `all_conductor` and `track_swarm` presets include Cline, Codex, Xiaomi MiMo Code, Chrome, architecture, and validation lanes. Use these presets for full track execution unless a narrower preset is explicitly selected.

## Implemented dispatch behavior

- The orchestrator parses swarm presets from `swarm-config.yaml`.
- Task mailbox metadata includes the assigned agent model and mode.
- Dry-run output displays the model assigned to each lane.
- Bounded CLI, Astro, documentation, migration, template, refactor, script, package, and command tasks route to `Xiaomi_MiMo_Code` when available.
- Cross-repo, architecture, validation, Chrome, and external-write-gated tasks remain assigned to their specialist lanes.
