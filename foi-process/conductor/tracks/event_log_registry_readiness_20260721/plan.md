# Event-log registry readiness

Issue: `edithatogo/foi-process#63`
Subissues: `#64` (Zenodo/DataCite), `#65` (Hugging Face metadata/Croissant)

## Objective

Prepare authoritative, reproducible registry evidence for the versioned event
log release. This track coordinates repository work only; external submission,
acceptance, DOI resolution, and publication remain evidence-gated.

## Plan

- [x] Link the parent issue and native subissues to this Conductor track.
- [x] Define the event-log release manifest, checksums, schema, provenance,
  rights, and source-order requirements in repository documentation.
- [ ] Validate the release bundle against the current fyi-archive snapshot.
- [ ] Complete Hugging Face dataset metadata and Croissant evidence for the
  exact released files.
- [ ] Prepare the Zenodo/DataCite metadata payload and immutable digest record.
- [ ] Record external submission, acceptance, and identifier evidence when
  available; leave the relevant issues open until then.

## Evidence rules

The Apache-2.0 licence applies to repository code only. Event-log and source
materials retain their source-declared rights. No registry acceptance or DOI
publication is claimed from local preparation alone.
