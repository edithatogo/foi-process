# Release Notes: Lockfile & Environment manager Standardization

As part of the Track 13 standardization initiative, all workspace repositories are now classified under one of the three primary lockfile managers: `uv`, `pixi`, or `pnpm`.

## Policy Highlights

1. **Enforced standard:**
   - Any dependency-affecting changes in the Python repositories must be verified using the canonical tool (`uv` for `uv-primary` repos, `pixi` for `pixi-primary` repos).
   - Committing raw updates without updating the canonical lockfiles (`uv.lock`, `pixi.lock`, or `pnpm-lock.yaml`) is disallowed.
2. **Quality Gates:**
   - The workspace diagnostic tool (`workspace-doctor.py`) has been upgraded to automatically detect missing canonical lockfiles or disallowed mixing of managers.
3. **Subproject Classifications:**
   - Refer to [lockfile-decision-matrix.md](./lockfile-decision-matrix.md) for individual subrepo statuses and rationale.
