# Propel and Hugging Face

## Goal

Expose process maps, variants, timelines, evidence, and conformance through typed Rust/WASM artefacts.

## Non-goals

Do not duplicate capabilities owned by another repository or promote an untested contract.

## Exit criteria

- Consume summary/projection
- Add request timeline
- Build and validate a public-safe Hugging Face Dataset bundle containing event logs, revision
  logs, EvidenceDelta streams, OCEL tables, process edges, variants, findings, schemas, and hashes
- Publish the dataset only after the privacy gate passes
- Build a Static Space profile that consumes the checksum-verified, versioned dataset projection
- Publish and verify the Space only after Hub authentication is available
