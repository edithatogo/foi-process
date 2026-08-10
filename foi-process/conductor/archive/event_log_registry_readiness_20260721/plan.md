# Event-log registry readiness

Issue: `edithatogo/foi-process#63`
Subissues: `#64` (Zenodo/DataCite), `#65` (Hugging Face metadata/Croissant)

## Objective

Prepare authoritative, reproducible registry evidence for the bounded versioned
event-log release. The bounded package is publicly preserved; full-corpus
registry expansion remains deferred in #63.

## Plan

- [x] Link the parent issue and native subissues to this Conductor track.
- [x] Define the event-log release manifest, checksums, schema, provenance,
  rights, and source-order requirements in repository documentation.
- [x] Validate the generated release bundle and derive registry metadata from
  its manifest.
- [x] Generate Hugging Face dataset metadata and Croissant evidence for the
  exact bundle files.
- [x] Prepare a Zenodo/DataCite metadata payload tied to the manifest digest.
- [x] Record authoritative external submission, acceptance, DOI, and six-file
  package evidence: Zenodo record `21660296`, DOI
  `10.5281/zenodo.21660296`, published 2026-08-01.
- [x] Record the 2026-07-29 bounded-release scope decision; full-corpus
  evidence is explicitly deferred rather than inferred from archive discovery.

## Evidence rules

The Apache-2.0 licence applies to repository code only. Event-log and source
materials retain their source-declared rights. The published record covers the
bounded package only; it does not claim full-corpus coverage.
