# Hugging Face Space dashboard

`space/` contains the Static Space profile for `edithatogo/foi-process-explorer`. It consumes a
browser projection generated from the reviewed event-log Dataset bundle; it does not mine raw
correspondence or recalculate legal conclusions in the browser.

## Views

- overview KPIs and activity frequency;
- directly-follows process map with observed waiting times;
- weighted variant flow and path catalogue;
- filterable case queue and request timeline;
- conformance findings, field coverage, OCEL linkage, and publication provenance.

Authority and case-search controls share one scope across the portfolio, process, timeline, and
finding views. The checked-in demonstration projection lets the Space build without network access.
The publication workflow regenerates it from the same bundle uploaded to the Dataset repository.

## Reproduce locally

```powershell
python scripts/build_hf_dataset.py --output target/huggingface/foi-process-event-logs
python scripts/build_hf_space_data.py `
  --bundle target/huggingface/foi-process-event-logs `
  --output space/public/data/dashboard-data.json
cd space
npm ci
npm run build
cd ..
python scripts/check_hf_space_budget.py `
  --dist space/dist `
  --dashboard-data space/public/data/dashboard-data.json
cd space
npm run preview
```

`build_hf_space_data.py` verifies every SHA-256 entry in the bundle manifest before writing the
dashboard projection. Missing tables, missing files, or checksum differences fail the build.
The asset-budget check also prevents accidental unbounded growth of the client bundle or embedded
demonstration data; the accepted limits are recorded in ADR 0005.

## Publication boundary

The `publish-hf-space` workflow always regenerates the Dataset and dashboard data, compiles the
Static Space, and uploads the build as a GitHub artifact. The compiled `dist/` is overlaid at the
Space repository root while the auditable source is retained alongside it, so Hugging Face can
serve the application without running Node on the Hub. Hub publication occurs only when the
workflow is explicitly dispatched with `publish: true` and an `HF_TOKEN` secret is available.
After upload, the workflow compares the published dashboard source and generated data with the
validated local build, waits for the public Static Space to report `RUNNING`, requests the public
host, and records the remote revision and source checksums in a
`hf-space-publication-attestation` workflow artifact.

Runtime activation remains subject to Hugging Face account policy. If the Hub reports a terminal
stage such as `CONFIG_ERROR` because credits are required, verification fails immediately and the
Space remains deposited-but-unverified until that account-level gate is resolved.

The same verified `space/dist` artifact can be deployed to GitHub Pages with
`deploy-pages.yml` as a free operational fallback. This does not replace the Hugging Face Space
record or its runtime attestation; it provides a public dashboard URL while the Hub account gate
remains unresolved.

A Static Space is intentional. The dashboard is client-side and does not require a persistent
Python or Docker runtime, which reduces infrastructure and avoids treating compute-tier access as a
functional dependency. Production data remains subject to the Dataset privacy and governance gate.
