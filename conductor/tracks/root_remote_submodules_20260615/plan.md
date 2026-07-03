# Track 20: Root Remote and Submodule Workspace

## Objective

Make the root `legal-nz` repository a private coordination remote that pins the real implementation repositories
as Git submodules, without migrating implementation code into the root workspace.

## Ownership model

- Root `legal-nz`: orchestration, conductor tracks, swarm configuration, platform mapping, and cross-repo evidence.
- Subrepos: implementation code, tests, release workflows, dataset upload logic, and GitHub Actions evidence.
- Additional mapped workspaces pending classification: `dnz` and `fyi-cli`.

## Submodule set

| Path | Remote | Branch | Role |
| --- | --- | --- | --- |
| `cli-legislation-nz` | `https://github.com/edithatogo/nz-legislation.git` | `main` | CLI and user-facing commands |
| `corpus-cases-medilegal-nz` | `https://github.com/edithatogo/corpus-cases-medilegal-nz.git` | `master` | Private/gated medilegal corpus work |
| `corpus-law-nz` | `https://github.com/edithatogo/corpus-legislation-nz.git` | `codex/historical-batch-0005-seed` | Legislation and legislative history corpus work |
| `corpus-nz-hansard` | `https://github.com/edithatogo/corpus-nz-hansard.git` | `main` | Hansard and Parliament corpus work |
| `hathi-nz` | `https://github.com/edithatogo/hathi-nz.git` | `master` | HathiTrust and historical legal materials |
| `nlp-policy-nz` | `https://github.com/edithatogo/nlp-policy-nz.git` | `master` | Cross-corpus NLP, benchmarks, RAG prototypes, DigitalNZ probes |
| `sm-govt-nz` | `https://github.com/edithatogo/sm-govt-nz.git` | `master` | Government social media corpus work |

## Phase 1: Root-local setup

- [x] Confirm root has no configured remote.
- [x] Confirm the seven core subrepo directories are untracked by root and can be represented as gitlinks.
- [x] Add `.gitmodules` for the seven core subrepos.
- [x] Add root clone/update/operator documentation.
- [x] Record ambiguous folders for later classification instead of adding them prematurely.

## Phase 2: Root remote creation

- [x] Create or connect private GitHub repo `edithatogo/legal-nz-workspace`.
- [x] Push root `main` to the remote.
- [x] Confirm the root remote renders submodules correctly on GitHub.
- [x] Record the root remote URL in the workspace mapping.

### Phase 2 evidence

- Remote URL: `https://github.com/edithatogo/legal-nz-workspace`.
- Root commit pushed: `af9f015` (`Initialize-root-workspace-submodules`).
- Local caveat: OneDrive denied writes inside `legal-nz/.git`, so the root commit and push were performed with external
  Git metadata at `%TEMP%/legal-nz-root-dotgit`.
- Follow-up blocker: create a durable local `.git` file or local Git directory for `legal-nz` once the OneDrive permission/resource issue clears.
- GitHub API check on 2026-06-23 confirmed root contents expose submodule gitlinks for the mapped repos, including `dnz`
  and `fyi-cli`, with `html_url` values pointing to pinned commits in the owning repositories.
- GitHub repository visibility is now verified as `PRIVATE` for `edithatogo/legal-nz-workspace`; the private-remote
  requirement is satisfied.
- Latest checked full root `Docs Lint` audit exposed broad pre-existing markdownlint debt: 1,225 markdown errors across
  archived conductor docs, `task_plan.md`, and other documentation.

## Phase 3: Submodule hygiene

- [x] Resolve outstanding subrepo `.git/index.lock` blockers. None found — all 9 subrepos clean.
- [ ] Commit and push pending SemVer/logging changes inside each owning subrepo. Deferred — multiple repos have changes across active tracks.
- [~] Check GitHub Actions in each changed subrepo. Deferred — no remote auth.
- [ ] Update root submodule pins only after the owning subrepo commits are pushed. Deferred.

Detailed report in `submodule-hygiene-report.md`.

## Phase 4: Classification follow-up

- [x] Decide whether `fyi-cli` belongs in the Legal NZ workspace or a separate aggregation workspace.
- [x] Decide whether `dnz` is a workspace folder, a parent-repo artifact, or a standalone repo to be represented elsewhere.
- [x] Add new submodules only after ownership and remote URLs are explicit.

### Phase 4 evidence

- `fyi-cli` is a real nested Git repo: root `C:/Users/60217257/OneDrive - Flinders/repos/legal-nz/fyi-cli`, remote
  `https://github.com/edithatogo/fyi-cli`, branch `master`, dirty local changes present.
- `dnz` is promoted as a submodule for DigitalNZ integration hub work: remote `https://github.com/edithatogo/dnz.git`, branch `main`, pinned in the root index.
- `fyi-cli` is promoted as an auxiliary CLI submodule: remote `https://github.com/edithatogo/fyi-cli`, branch `master`, pinned in the root index.
- Current mapping added: `docs/repository-status.md`.

## Guardrails

- Do not track subrepo implementation files in the root repository.
- Do not add ambiguous directories as submodules merely because they contain Git metadata.
- Do not delete or move nested repo contents during submodule conversion.
- Treat dirty subrepo state as a hygiene blocker, not a reason to collapse code into root.
- Commit root orchestration changes separately from subrepo implementation changes.

## Review and release gates

- After each root task: review root diff, commit root-only changes, and push root `main`.
- After each subrepo task: review, commit, push, and check GitHub Actions inside the owning subrepo.
- After each phase: update this plan and `task_plan.md` with evidence or blockers.
- After track completion: confirm root remote, submodule rendering, subrepo pins, and GitHub Actions status.
