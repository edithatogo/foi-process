# Release publication

`foi-process` uses separate publication surfaces for software, derived data, and the dashboard:

- GitHub Releases hold versioned Rust binaries, checksums, release evidence, and build provenance.
- The Hugging Face Dataset holds the public event-log deposit and its manifest.
- GitHub Pages hosts the free dashboard built from the verified public projection.
- The free Hugging Face Space is an additional interactive view of that projection.

The `Release` workflow stages a draft GitHub Release when an annotated semantic-version tag is
pushed or when an existing tag is supplied through manual dispatch. It validates the checked-out
revision, runs the Rust regression suite, builds the three command-line binaries, verifies the
release-evidence package, emits `SHA256SUMS`, and records GitHub build provenance. A manual dispatch
with `publish: true` is required to make the prepared GitHub Release public.

This workflow does not publish a Rust crate, paper, or paid service. `Cargo.toml` remains
`publish = false` until a separate distribution decision is made.

Rights remain split by artifact. Repository code is Apache-2.0. Source-derived records, archive
material, attachments, and derived public data retain the rights, access, removal, and provenance
conditions of their originating source. The publication workflows must not replace those
source-specific conditions with the software licence.
