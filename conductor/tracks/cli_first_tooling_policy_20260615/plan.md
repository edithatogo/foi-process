# Track 21: CLI-First Tooling Policy and Command-Surface Consolidation

## Objective

Ensure agents use existing repo CLIs, package scripts, and maintained command surfaces instead of writing custom one-off code for repeatable work.

## Phase 1: Root policy and registry

- [x] Add human-readable CLI-first operating policy.
- [x] Add machine-readable CLI tool registry.
- [x] Map root, current submodules, `fyi-cli`, and `dnz`.
- [x] Add swarm prompt guidance requiring CLI-first execution.

## Phase 2: Per-repo maturity audit

- [x] Audit exact CLI/package-script entrypoints in `fyi-cli`. Confirmed PyPI-published Typer CLI.
- [x] Classify `dnz` repository boundary. Confirmed Rust crate workspace with dnz-cli, MCP server, Python bindings.
- [x] Confirm `corpus-cases-medilegal-nz` repeat operations. Weakest CLI (2 commands only), no Makefile, no README CLI docs.
- [x] Confirm `hathi-nz` repeat operations and decide package CLI name. Medium maturity — Makefile + scripts.
- [x] Inventory high-value `corpus-nz-hansard` scripts for CLI consolidation. 12-command CLI dispatcher exists but README bypasses it.
- [x] Inventory `sm-govt-nz` scripts/modules for CLI consolidation. Dedicated `docs/cli-first.md` policy but no root README.

Audit results in `cli-maturity-audit.md`.

## Phase 3: Command-surface consolidation

- [ ] Add or extend first-class CLI commands in owning subrepos where repeated workflows currently require script invocation.
- [ ] Preserve repo boundaries: root creates policy, subrepos implement commands.
- [ ] Add CLI smoke tests or command help tests per owning repo.
- [x] Document preferred commands in each subrepo README/conductor status.

## Phase 4: Enforcement

- [ ] Add a root lint/check that fails when new one-off root scripts duplicate registered CLI surfaces.
- [x] Add conductor task checklist item: "Which CLI/package script was used?"
- [ ] Add subrepo CI checks where CLI help/smoke commands are stable.
- [ ] Require exceptions to be documented in the active conductor track.

### 2026-06-23 Enforcement Evidence

- Updated `conductor/templates/track-improvement-template.md` to require
  `CLI/package script used` and `Custom code exception, if any` fields.
- Updated `conductor/templates/cli-tool-registry.json` so `fyi-cli` and `dnz`
  match their current promoted workspace roles.

## Current CLI-first registry

- Human policy: `docs/cli-first-policy.md`.
- Machine registry: `conductor/templates/cli-tool-registry.json`.

## Guardrails

- Do not write custom root code to replace `nzlegislation`, `nzlc`, `nlp-policy-nz`, or maintained subrepo scripts.
- If a CLI does not exist, add the command to the owning repo rather than the root.
- If temporary code is unavoidable, document the reason and create a follow-up CLI consolidation task.
- Do not use `dnz` until it has a clean repository boundary and remote.

## Review and release gates

- Root policy changes are committed and pushed in the root orchestration repo.
- CLI implementation changes are committed and pushed inside the owning subrepo.
- Every CLI command addition needs help/smoke evidence and GitHub Actions checks.
