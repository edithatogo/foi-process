# Dashboard build and free hosting

`space/` contains the reproducible static dashboard source. It consumes a
browser projection generated from the reviewed event-log Dataset bundle; it does not mine raw
correspondence or recalculate legal conclusions in the browser.

## Views

- overview KPIs and activity frequency;
- directly-follows process map with observed waiting times;
- weighted variant flow and path catalogue;
- filterable case queue and request timeline;
- conformance findings, field coverage, OCEL linkage, and publication provenance.

Authority and case-search controls share one scope across the portfolio, process, timeline, and
finding views. The checked-in demonstration projection lets the dashboard build without network
access. The GitHub Pages workflow regenerates it from the same bundle used for the Dataset
repository.

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

## No-cost publication boundary

`deploy_pages.yml` is the only dashboard hosting workflow. It builds the dashboard in GitHub
Actions and deploys the compiled `space/dist` artifact to GitHub Pages, which is the operational
dashboard URL and does not require a Hugging Face runtime, credits, secrets, or paid services.

The Hugging Face Dataset remains an optional public deposit for event logs and reproducibility.
The no-cost Hugging Face Space target is `edithatogo/foi-process-explorer-free`, created by
duplicating the account's already-running free Static Space configuration and then replacing its
pre-built root assets. The repository's manual publication workflow is allowlisted to that target
and verifies its runtime after upload. GitHub Pages remains an independent no-cost fallback.

Production data remains subject to the Dataset privacy and governance gate.
