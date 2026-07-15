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
dashboard, and uploads the build as a GitHub artifact. Only the compiled `dist/` and the Space card
are deposited at the Space root; the source remains auditable in GitHub and the Hub does not run
Node during publication. Hub publication occurs only when the
workflow is explicitly dispatched with `publish: true` and an `HF_TOKEN` secret is available.
After upload, the workflow compares every published root asset with the validated local build,
waits for the public Static Space to report `RUNNING` when the account permits it, requests the
public host, and records the remote revision and source checksums in a
`hf-space-publication-attestation` workflow artifact. If HF rejects activation with its known
credit gate, the workflow records `deposited_unverified` and the exact runtime error instead of
misrepresenting repository upload as a live dashboard.

The Space uses the pre-built Static SDK path. This dashboard does not need GPU inference, so
ZeroGPU is not part of the deployment: HF documents ZeroGPU as a Gradio-only GPU option whose
hosting requires PRO for personal accounts. Keeping build execution in GitHub Actions avoids the
credit-gated Hub static-build path observed for this account.

The same verified `space/dist` artifact can be deployed to GitHub Pages with
`deploy-pages.yml` as a free operational fallback. This does not replace the Hugging Face Space
record or its runtime attestation; it provides a public dashboard URL while the Hub account gate
remains unresolved.

A pre-built Static Space is used here because Docker and Gradio CPU hosting are also PRO-gated for
this account. Production data remains subject to the Dataset privacy and governance gate.
