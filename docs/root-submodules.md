# Root Submodule Workspace

The root `legal-nz` repository is an orchestration workspace. It coordinates conductor tracks, swarm setup, external platform mapping, and cross-repo evidence. Implementation code remains in the owning subrepositories.

## Clone

```sh
git clone --recurse-submodules https://github.com/edithatogo/legal-nz-workspace.git
cd legal-nz-workspace
```

If the root has already been cloned without submodules:

```sh
git submodule update --init --recursive
```

## Update submodules

```sh
git submodule update --remote --recursive
```

Use this only when intentionally advancing submodule pins. Subrepo implementation changes must be committed and pushed inside the owning subrepo before the root pin is updated.

## Inspect status

```sh
git status --short
git submodule status --recursive
git submodule foreach git status --short
```

Dirty submodule status means the nested repo has local changes. Commit those changes inside the owning subrepo, not in the root.

## Included subrepos

| Path | Remote | Purpose |
| --- | --- | --- |
| `cli-legislation-nz` | `https://github.com/edithatogo/nz-legislation.git` | CLI and user-facing commands |
| `corpus-cases-medilegal-nz` | `https://github.com/edithatogo/corpus-cases-medilegal-nz.git` | Medilegal case corpus |
| `corpus-law-nz` | `https://github.com/edithatogo/corpus-legislation-nz.git` | Legislation corpus |
| `corpus-nz-hansard` | `https://github.com/edithatogo/corpus-nz-hansard.git` | Hansard corpus |
| `hathi-nz` | `https://github.com/edithatogo/hathi-nz.git` | HathiTrust and historical material |
| `nlp-policy-nz` | `https://github.com/edithatogo/nlp-policy-nz.git` | NLP, benchmark, RAG, and DigitalNZ prototypes |
| `sm-govt-nz` | `https://github.com/edithatogo/sm-govt-nz.git` | Government social media corpus |
| `open_social_data` | `https://github.com/edithatogo/open_social_data.git` | Open social data workflows and datasets |
| `openfisca-aotearoa` | `https://github.com/edithatogo/openfisca-aotearoa.git` | Aotearoa OpenFisca policy/modeling repo |
| `sourceright` | `https://github.com/edithatogo/sourceright.git` | SourceRight tooling and conductor workspace |
| `dnz` | `https://github.com/edithatogo/dnz.git` | DigitalNZ Rust integration hub, CLI, MCP, and Python FFI workspace |

## Additional mapped repositories/workspaces

| Path | Mapping status | Decision needed |
| --- | --- | --- |
| `fyi-cli` | Real nested Git repo at `https://github.com/edithatogo/fyi-cli`, branch `master`; dirty local changes are present. | Decide whether it belongs in the Legal NZ orchestration workspace as a submodule or remains a separate CLI workspace. |
| `Friction` | Real nested Git repo at `https://github.com/edithatogo/Friction`, branch `master`. | Classified as comparative UK open-law service-design reference material. Do not promote to a Legal NZ implementation submodule unless a later track explicitly depends on it. |
