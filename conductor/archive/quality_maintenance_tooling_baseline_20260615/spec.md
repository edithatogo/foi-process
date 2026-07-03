# Track 19: Quality and Maintenance Tooling Baseline

## Problem
Different subrepos have inconsistent quality, prose, dependency maintenance, coverage, and profiling tooling. Vale is universal but Codecov, Renovate, Scalene, and markdown style are adopted ad hoc, making cross-repo maintenance harder and leaving silent quality gaps in repos that lack tooling.

## Solution
Standardize tooling by repo role using the `quality-maintenance-tooling-baseline.md` template, classifying each tool as `required`, `conditional`, `optional`, `deferred`, or `not_applicable` per subrepo.

## Scope
- Root `legal-nz`: Vale + markdownlint only (no remote CI to enforce)
- `cli-legislation-nz`: keep Codecov + Renovate; add/confirm markdown style
- `corpus-cases-medilegal-nz`: add markdown style, Renovate, Codecov where relevant
- `corpus-law-nz`: add markdown style + Renovate; confirm Codecov; keep Scalene
- `corpus-nz-hansard`: add markdown style + Renovate; confirm Codecov; keep Scalene
- `hathi-nz`: add markdown style + Renovate; evaluate Codecov + Scalene
- `nlp-policy-nz`: add markdown style + Renovate; confirm Codecov; keep Scalene
- `sm-govt-nz`: add markdown style + Renovate; evaluate Codecov; Scalene optional

## Out of Scope
- Adding Codecov coverage-producing CI jobs (must be separate CI work)
- Adding Scalene profiling targets (separate performance tracks)
- Creating org-level Renovate configs (documented inheritance only)
