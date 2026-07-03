# External platform mapping

Updated: 2026-06-14

This file maps the legal-nz workspace repositories to GitHub, Hugging Face, OSF, and Zenodo setup state. It intentionally records identifiers and URLs only; no tokens or secrets are stored here.

## Authentication status

| Platform | Local status | GitHub status | Notes |
| --- | --- | --- | --- |
| GitHub | Authenticated as `edithatogo` via `gh` | Variables/secrets updated across mapped repos | `OSF_PROJECT_ID`, `OSF_TOKEN`, `ZENODO_TOKEN`, and `ZENODO_SANDBOX_TOKEN` configured where repositories exist. |
| Hugging Face | CLI logged in with `legal-nz-corpus-law-nz-github-actions-20260614`; per-repo tokens created 2026-06-14 | `HF_TOKEN` secrets replaced across mapped repos | Missing dataset shells were created as private datasets; Hansard source archive access now validates. Current workflow failures are repo/tooling issues, not HF auth. |
| OSF | `OSF_TOKEN` present; `osfclient` installed; CLI access validated | `OSF_PROJECT_ID` variables and `OSF_TOKEN` secrets set across mapped repos | OSF projects below were created as private projects. |
| Zenodo production | New production token created in Chrome and validated with HTTP 200 against `/api/deposit/depositions` | `ZENODO_TOKEN` secret updated across mapped repos | Token name: `legal-nz-corpus-actions-20260614-1138`. |
| Zenodo sandbox | Existing env token returned HTTP 403 before replacement work | `ZENODO_SANDBOX_TOKEN` secret set from existing env value | Sandbox token still needs replacement if sandbox deposits are required. |

## Repository mapping

| Workspace | GitHub repo | Hugging Face dataset | OSF project | Zenodo status |
| --- | --- | --- | --- | --- |
| `cli-legislation-nz` | `edithatogo/nz-legislation` | N/A for CLI package | `n7gwd` / https://osf.io/n7gwd/ | Production token configured. |
| `corpus-cases-medilegal-nz` | `edithatogo/corpus-cases-medilegal-nz` | `edithatogo/corpus-cases-medilegal-nz` exists as a private HF dataset shell | `u8ype` / https://osf.io/u8ype/ | Production token configured; Zenodo archive plan exists locally. |
| `corpus-law-nz` | `edithatogo/corpus-legislation-nz` | `edithatogo/corpus-legislation-nz`; `edithatogo/corpus-legislation-nz-historical`; legacy DOI dataset `edithatogo/nz-legislation-corpus` | `s9754` / https://osf.io/s9754/ | Production token configured; existing Zenodo config present. |
| `corpus-nz-hansard` | `edithatogo/corpus-nz-hansard` | `edithatogo/nz-hansard-corpus`; source archive `edithatogo/nz-hansard-source-archive` | `dypvx` / https://osf.io/dypvx/ | Production token configured. HF/Zenodo workflows are blocked until the HF token can access the gated source archive. |
| `hathi-nz` | `edithatogo/hathi-nz` | `edithatogo/corpus-nz-hathi` exists as a private HF dataset shell | `2yaxt` / https://osf.io/2yaxt/ | Production token configured; local Zenodo scripts exist. |
| `nlp-policy-nz` | `edithatogo/nlp-policy-nz` | No primary corpus dataset; integration/upload tooling exists | `472sm` / https://osf.io/472sm/ | Production token configured; integration scripts exist. |
| `sm-govt-nz` | `edithatogo/sm-govt-nz` | Dataset target not confirmed in this pass | `d8zgx` / https://osf.io/d8zgx/ | Production token configured; archive workflow exists. |

## Outstanding blockers

1. Hugging Face per-repo tokens were recreated and stored in local env files and GitHub `HF_TOKEN` secrets.
2. `edithatogo/corpus-cases-medilegal-nz` and `edithatogo/corpus-nz-hathi` now exist as private HF dataset shells.
3. `corpus-nz-hansard` source archive download now succeeds; current HF/Zenodo reruns fail at `Rebuild Parquet` because CI cannot import `shared_utils`.
4. Zenodo sandbox token currently returns HTTP 403 and needs replacement if sandbox deposit testing is required.

