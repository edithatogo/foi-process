# Event-log registry readiness

Issue: `edithatogo/foi-process#63`
Subissues: `#64` (Zenodo/DataCite), `#65` (Hugging Face metadata/Croissant)

## Objective

Prepare authoritative, reproducible registry evidence for the versioned event
log release. Repository metadata preparation is complete. External submission,
acceptance, DOI resolution, and publication remain evidence-gated in #63-#65.

## Plan

- [x] Link the parent issue and native subissues to this Conductor track.
- [x] Define the event-log release manifest, checksums, schema, provenance,
  rights, and source-order requirements in repository documentation.
- [x] Validate the generated release bundle and derive registry metadata from
  its manifest.
- [x] Generate Hugging Face dataset metadata and Croissant evidence for the
  exact bundle files.
- [x] Prepare a draft Zenodo/DataCite metadata payload tied to the manifest
  digest; external deposit and identifier resolution remain pending.
- [ ] Record authoritative external submission, acceptance, and identifier
  evidence when available; leave #63-#65 open until then.
- [x] Record the 2026-07-29 bounded-release scope decision; full-corpus
  evidence is explicitly deferred rather than inferred from archive discovery.

## Evidence rules

The Apache-2.0 licence applies to repository code only. Event-log and source
materials retain their source-declared rights. No registry acceptance or DOI
publication is claimed from local preparation alone.
