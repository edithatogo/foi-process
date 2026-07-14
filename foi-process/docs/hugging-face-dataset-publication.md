# Hugging Face dataset publication

The dashboard is backed by a separate Hugging Face Dataset repository,
`edithatogo/foi-process-event-logs`. The repository is built from reviewed projections rather than
from raw requester correspondence.

## Published surfaces

- active public event log for process discovery and duration analysis;
- complete synthetic event-revision and EvidenceDelta logs for replay demonstrations;
- process-map edges and variants;
- OCEL events, objects, and event-object links;
- synthetic conformance findings;
- dashboard, public-projection, OCEL, conformance, and mining-run artefacts;
- portable schemas and a deterministic SHA-256 manifest.

Run locally:

```powershell
python scripts/build_hf_dataset.py --output target/huggingface/foi-process-event-logs
```

The `publish-hf-dataset` workflow always builds and validates the bundle. It uploads only when its
`publish` input is true and the GitHub repository has an `HF_TOKEN` secret with write access.

## Production gate

The current dataset is classified `synthetic-fixture`. Production data must not be sent to the Hub
until every record has passed the public projection and the privacy, tikanga/data-governance,
licensing, removal/appeal, and threat-model reviews. The exporter fails closed when fixture records
are not explicitly marked human-reviewed and public or metadata-only.
