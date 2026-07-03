# Deferred Root Coordination Items

## root uv workspace pyproject

Moved the provisional root `pyproject.toml` to `conductor/deferred/root-uv-workspace.pyproject.toml` instead of committing it at repository root. Reason: the workspace member list is incomplete and can leak into nested subrepo `uv lock` operations, as seen with `corpus-nz-hansard` resolving unrelated parent workspace members.

Next action: reintroduce a root workspace file only after all intended Python subrepos have explicit `tool.uv.sources` coverage or the root workspace is split from subrepo-local lock operations.

## corpus-nz-hansard root pin

Deferred the root gitlink update for `corpus-nz-hansard` because the subrepo still has uncommitted quality/test fixes and generated documentation artifacts. Root should pin it only after the subrepo is committed, pushed, and clean.

## dnz nested worktree dirt

Deferred any additional nested `dnz` cleanup because after the subrepo commit/push, `dnz/crates/dnz-core/src/autopilot.rs` appeared modified again. Root still pins the pushed `dnz` commit `ad907c0`; the nested worktree change requires separate classification before another subrepo commit.

## sm-govt-nz nested worktree dirt

Deferred additional nested `sm-govt-nz` cleanup because `sm-govt-nz/config/courts_nz_email_ingress.json` appeared modified after the root pin was staged. Root still pins the pushed `sm-govt-nz` commit `e8bfba4`; the config change requires separate classification before another subrepo commit.

## open_social_data nested worktree dirt

Deferred additional nested `open_social_data` cleanup because `src/catalog_sync.rs` and `src/main.rs` appeared modified after the subrepo commit/push and root pin. Root pins the pushed `open_social_data` commit `f836e34`; these changes require separate classification before another subrepo commit.

## sourceright nested worktree dirt

Deferred additional nested `sourceright` cleanup because `src/journal.rs`, `src/workspace.rs`, and two untracked journal fixtures appeared modified/untracked after the root pin. Root pins the existing `sourceright` commit `cb442f2`; these changes require separate classification before another subrepo commit.
