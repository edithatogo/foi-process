# Hugging Face dataset publication

The dashboard is backed by separate Hugging Face Dataset repositories. The synthetic benchmark
surface is `edithatogo/foi-process-event-logs`; the accepted bounded NZ release is
`edithatogo/foi-process-event-logs-bounded`. Both are projections rather than a duplicate raw
archive. Case-level source material belongs in the canonical `edithatogo/fyi-archive-nz` source
layer and is linked by verified locator and digest.

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
After upload, the workflow downloads the public revision, compares its manifest with the locally
built manifest, rechecks every declared byte length, row count and SHA-256 digest, and records the
remote revision in a `hf-dataset-publication-attestation` workflow artifact. Upload success alone is
not treated as publication proof.

## NZ production gate

The bounded NZ package is classified `public-derived-bounded`; it is not a full-corpus claim. The
synthetic dataset remains `synthetic-fixture`. A complete NZ process projection must not be sent to
the Hub until exact manifest/case/event/attachment/source-record parity, a pinned takedown revision,
and release-specific privacy, rights, retention, removal/appeal, threat-model, and operational
evidence all pass. The exporter and dashboard must fail closed when those checks are absent.
