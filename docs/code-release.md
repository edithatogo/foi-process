# Code release automation

Repository code is Apache-2.0. Source-derived datasets and documents retain
their separately recorded rights and are not relicensed by a code release.

Release Please maintains a version PR across `Cargo.toml`, `Cargo.lock`,
`CITATION.cff`, `.zenodo.json`, the changelog, and the release manifest. The
bot is configured not to create a GitHub release itself. A release operation
starts only when an intentionally merged Release Please PR changes the version
on `main`; pull-request and manual workflow tests cannot create a release.

The workflow creates a lightweight `vMAJOR.MINOR.PATCH` tag at the exact merged
commit and stages a draft GitHub release. It then builds and verifies the
checksummed release-evidence package, uploads it as a workflow artifact,
attaches it to the draft, and creates a GitHub artifact provenance attestation.
Publishing the draft is the final step. Any earlier failure leaves the release
unpublished and retryable from the same workflow run.

Release Please PRs created with `GITHUB_TOKEN` do not emit ordinary pull-request
events. The workflow therefore dispatches `ci.yml` explicitly on the release
branch. This keeps release PR validation tokenless while attaching the full CI
result to the exact release head.
