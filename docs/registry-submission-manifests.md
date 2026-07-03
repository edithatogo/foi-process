# Registry Submission Manifests

Track 24 coordinates conductor Track 17 from the root `legal-nz` workspace. The root owns reusable schemas, fixtures, workflow guidance, and cross-repo evidence. Owning subrepos own implementation manifests, readiness work, commits, pushes, CI checks, and registry submissions.

## Root-Owned Artifacts

- `conductor/templates/registry-submission.schema.json`
- `conductor/templates/registry-submission-workflow.md`
- `conductor/templates/registry-submission-fixtures/cli.json`
- `conductor/templates/registry-submission-fixtures/mcp_server.json`
- `conductor/templates/registry-submission-fixtures/python_package.json`
- `conductor/templates/registry-submission-fixtures/container.json`
- `conductor/templates/registry-submission-fixtures/dataset.json`

## Owning Repo Placement

Use `conductor/registry-submissions/<artifact-name>.json` in the owning repo unless that repo already has a stronger local convention.

Keep one manifest per artifact and release channel. Do not combine a CLI, MCP server, container, and dataset into a single manifest just because they live in the same repository.

## Required Local Evidence

- Manifest validates against the root schema.
- Registry requirements are inventoried before readiness is claimed.
- Package, build, test, lint, smoke, or dataset validation evidence is recorded before submission.
- Security and provenance gates are recorded, including no-secret checks and source visibility decisions.
- Submission, review, accepted, rejected, or blocked status is recorded with URLs only after the status has been verified.

## Registry Family Defaults

- `cli-legislation-nz`: npm, GitHub Packages, GitHub Releases, GHCR, Homebrew, Smithery, MCP registries, and marketplace targets where applicable.
- `nlp-policy-nz`: PyPI, conda-forge, model or benchmark archives, and MCP/RAG prototypes where applicable.
- Corpus repos: Hugging Face, Zenodo, OSF, GitHub Releases, and package/container registries only where the owning repo has a real artifact.

## Local-Only Guardrails

- Root coordination does not submit artifacts to external registries.
- Root coordination does not edit `.env` files, create tokens, open Chrome, upload artifacts, mutate external services, commit, push, or check authenticated GitHub Actions without explicit approval.
- Placeholder fixture evidence is not readiness evidence.
- External-write blockers stay blocked until explicitly approved.

## Registry rejection and review feedback capture

- When a submission fails, owning repos must record the review/rejection note and publish attempt in
  `conductor/improvement-backlog.md` using `scripts/record_learning_candidate.py`.
- Feedback capture should run on failure paths only and must not auto-commit.
- A reviewed lesson must be marked with explicit owner approval before promoting to shared templates or skills.
