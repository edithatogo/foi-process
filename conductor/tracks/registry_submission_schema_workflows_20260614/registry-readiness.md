# Track 17 Registry Readiness Matrix

Status captured: 2026-06-23.

This matrix records the current pre-submission gates for registry targets used by
Legal NZ manifests. It does not authorize publication. Owning subrepos must
complete local build checks, CI, provenance, and review approval before any
submission.

## Official Sources

| Registry family | Source |
| --- | --- |
| npm packages | <https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry/> |
| npm provenance | <https://docs.npmjs.com/generating-provenance-statements/> |
| GitHub Container Registry | <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry> |
| GitHub artifact attestations | <https://docs.github.com/en/actions/security-for-github-actions/security-guides/use-artifact-attestations> |
| PyPI trusted publishing | <https://docs.pypi.org/trusted-publishers/> |
| PyPI attestations | <https://docs.pypi.org/attestations/> |
| Zenodo deposits | <https://help.zenodo.org/docs/deposit/create-new-upload/> |
| GitHub release citation | <https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content> |

## Registry Gates

| Target | Applies to | Required before submission | Local status |
| --- | --- | --- | --- |
| npm | `cli-legislation-nz` packages and CLIs | Valid `package.json`, README, version, license, access/visibility decision, `npm pack --dry-run`, publish workflow with OIDC/provenance where supported | Pending subrepo CI and package dry-run evidence |
| GitHub Packages / GHCR | containers and package artifacts | Package owner mapping, repository package permissions, image labels, immutable tag policy, SBOM/provenance, container build dry-run | Pending owner-repo build evidence |
| GitHub Releases | CLI binaries and source archives | Version tag, release notes, generated artifacts, checksums, artifact attestation, changelog/support links | Pending release artifact dry-run evidence |
| PyPI | Python packages in corpus/NLP repos | Package metadata, README render, license, version, `python -m build`, trusted publisher configuration, attestation policy | Pending per-subrepo build evidence |
| Hugging Face | datasets, models, benchmark artifacts | Dataset/model card, license, source/provenance statement, privacy/rights notes, upload dry-run where available | Pending dataset-specific review |
| Zenodo | DOI archives for datasets/software | Metadata, creators, license, related identifiers, files, communities/funders if applicable, deposition review before publish | Pending deposition draft evidence |
| OSF | source/archive evidence bundles | Project/component structure, metadata, license, contributor/rights notes, file checksum manifest | Pending account/project decision |
| Smithery / MCP registry | MCP server distributions | Tool manifest, install command, least-privilege token model, prompt-injection notes, no secrets in examples, review approval | Pending MCP security review |

## Security and Provenance Gates

| Gate | Required evidence | Status |
| --- | --- | --- |
| Least-privilege credentials | Registry token or trusted-publisher scope documented without storing secrets in repo | Pending per registry |
| Build provenance | npm provenance, PyPI attestations, GitHub artifact attestations, or explicit not-applicable rationale | Pending per artifact |
| SBOM/checksums | Package or archive checksum manifest; SBOM where package/container tooling supports it | Pending per artifact |
| MCP prompt-injection review | Manifest notes covering tool inputs, remote content handling, credential boundaries, and user approval points | Pending for MCP artifacts |
| Rights/privacy review | Dataset card or manifest field documenting source rights, takedown route, and privacy exclusions | Pending per dataset |
| CI evidence | Passing Actions run for the owning subrepo after manifest and packaging changes | Blocked by push/Actions state |

## Dry-Run Commands

| Artifact family | Preferred dry-run |
| --- | --- |
| Node package | `npm pack --dry-run` or package-manager equivalent in owning repo |
| Python package | `python -m build` plus metadata/readme validation in owning repo |
| Container | Build image locally or in CI without pushing; record digest if produced |
| Dataset archive | Generate manifest/checksums and validate card metadata without uploading |
| GitHub release | Build artifacts and checksums without creating a release |
| Zenodo/OSF | Prepare deposition/project metadata draft without publishing |

## Current Track 17 Outcome

- Phase 3 requirement inventory is now captured.
- No registry is ready for submission until owning subrepo dry-runs, CI evidence,
  provenance gates, and review approval are complete.
- Phase 4 remains blocked until submission/review URLs can be recorded after
  explicit approval.
