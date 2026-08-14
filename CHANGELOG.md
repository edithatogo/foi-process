# Changelog

## Unreleased

### Hugging Face publication

- Added a deterministic, public-safe Dataset bundle containing active event logs, revision logs,
  EvidenceDelta streams, process edges and variants, OCEL tables, conformance findings, schemas,
  dashboard artefacts, and SHA-256 manifests.
- Added a fail-closed GitHub workflow that validates the dataset on every run and uploads only
  when explicitly dispatched with an `HF_TOKEN` secret.
- Marked the initial deposit as synthetic reviewed fixture data; real FOI data remains gated by
  privacy, tikanga/data-governance, licensing, removal/appeal, and threat-model review.
- Added a Static Hugging Face Space with process-map, variant, request-timeline, conformance, data
  quality, and provenance views backed by a checksum-verified browser projection.
- Added a fail-closed Space workflow that builds and archives the application on every dispatch but
  publishes only with an explicit input and Hugging Face token.
- Upgraded the chart runtime to ECharts 6.1.0 to include the upstream XSS fix.
- Added a CI-enforced client/data asset budget and ADR for the no-runtime Static Space boundary.

### Scale and release evidence

- Added isolated repeated Rust scale profiles with correction/retraction overhead, deterministic
  hashes, peak resident memory, output size, and a committed 1k/10k/200k evidence report.
- Accepted and tested the path-safe Hive-style Parquet partition contract in ADR 0006.
- Added an SPDX 2.3 SBOM, mining provenance, release manifest, SHA-256 package builder/verifier, and
  a build-only release-evidence workflow.

## [0.2.0](https://github.com/edithatogo/foi-process/compare/v0.1.0...v0.2.0) (2026-08-14)


### Features

* add Alaveteli metadata event adapter ([#60](https://github.com/edithatogo/foi-process/issues/60)) ([9878a01](https://github.com/edithatogo/foi-process/commit/9878a01c982529b3a88067f886e6ae3b4a6124f2))
* add deterministic FOI simulation scenarios ([#11](https://github.com/edithatogo/foi-process/issues/11)) ([3353075](https://github.com/edithatogo/foi-process/commit/33530752acb2f706b81f19c967c7812b205c36df))
* add fail-closed jurisdiction intake validation ([#110](https://github.com/edithatogo/foi-process/issues/110)) ([5be0e55](https://github.com/edithatogo/foi-process/commit/5be0e55745cab0535f2932abc34be2602f44cdf5))
* add free GitHub Pages dashboard fallback ([#16](https://github.com/edithatogo/foi-process/issues/16)) ([83a3dbb](https://github.com/edithatogo/foi-process/commit/83a3dbb6fe3733e8c67b6feee8e1d3a05f1c8bc8))
* add Hugging Face process explorer ([0a53094](https://github.com/edithatogo/foi-process/commit/0a530948c5d9a3049de357432c99ae720180b01f))
* add scale and release evidence gates ([81af68b](https://github.com/edithatogo/foi-process/commit/81af68b860291c37157d715a0ffd8dea5ca4bfb1))
* add synthetic jurisdiction process-model template ([#103](https://github.com/edithatogo/foi-process/issues/103)) ([ae2a825](https://github.com/edithatogo/foi-process/commit/ae2a825128cccfbf8566d48531b9e5dbf5213dc8))
* package Hugging Face event-log dataset ([5a6c728](https://github.com/edithatogo/foi-process/commit/5a6c7280c153b8fd20992a06fbaf7c3f9cf568f2))
* reconcile immutable archive packages ([f85bb75](https://github.com/edithatogo/foi-process/commit/f85bb75a2dba7c5442aa436d1ba5a2a69df196ac))
* reconcile immutable archive packages ([#121](https://github.com/edithatogo/foi-process/issues/121)) ([015502e](https://github.com/edithatogo/foi-process/commit/015502e0ce4a0a3534b7da153a56bea62b9f8df7))
* validate immutable archive packages ([#116](https://github.com/edithatogo/foi-process/issues/116)) ([e902804](https://github.com/edithatogo/foi-process/commit/e90280460f1f430116562b28eded25fd45d59887))
* verify Hugging Face publication revisions ([#12](https://github.com/edithatogo/foi-process/issues/12)) ([31f67ce](https://github.com/edithatogo/foi-process/commit/31f67cee0f60f5aa91785aa42d2446675fb7ee4d))
* visualize scenario process mining ([#14](https://github.com/edithatogo/foi-process/issues/14)) ([2ee7fa3](https://github.com/edithatogo/foi-process/commit/2ee7fa326238f7b67a214e25d61efe7b0d17456f))


### Bug Fixes

* emit complete Alaveteli ProcessEvent fields ([#61](https://github.com/edithatogo/foi-process/issues/61)) ([c8d06da](https://github.com/edithatogo/foi-process/commit/c8d06da1f676a39d80cafebb9749cdfa7c7d32c9))
* format pinned Hugging Face CLI install step ([e8cc250](https://github.com/edithatogo/foi-process/commit/e8cc2505680656dcd3995c458b625b3131a6d248))
* harden live release controller ([#130](https://github.com/edithatogo/foi-process/issues/130)) ([9cd2014](https://github.com/edithatogo/foi-process/commit/9cd2014476cff890b8f693b62dc2786bb9640b25))
* include click for dataset publication verification ([b24364b](https://github.com/edithatogo/foi-process/commit/b24364b3b9089a77fce3fbc092af110b41410387))
* include click for Hugging Face publication attestation ([20ff808](https://github.com/edithatogo/foi-process/commit/20ff808d0293de7ccf21f1ef60f646a34b955432))
* normalize Hugging Face bundle newlines ([eb901b2](https://github.com/edithatogo/foi-process/commit/eb901b2ca0ea53187795157b9527740e339f1204))
* publish bounded dashboard to existing free Space ([#91](https://github.com/edithatogo/foi-process/issues/91)) ([fd3e8f8](https://github.com/edithatogo/foi-process/commit/fd3e8f8bc5f6a603c0146770941273640aa4c0c8))
* secure parquet temporary files ([58c2a9b](https://github.com/edithatogo/foi-process/commit/58c2a9b6552b2a0ffeb091585ccaac86c502bcc8))
* select foi-process adapter binary ([43f0813](https://github.com/edithatogo/foi-process/commit/43f0813cfb390e947ba9664eb62e2fecc84a0b7e))
* send Zenodo JSON content type ([#19](https://github.com/edithatogo/foi-process/issues/19)) ([60e9805](https://github.com/edithatogo/foi-process/commit/60e98059f9fab056e71a420e9d098b10e317c473))
* stabilize dataset manifest ordering ([5d0fab3](https://github.com/edithatogo/foi-process/commit/5d0fab3b5cfeb4c7868db63c9db4b4a3f116c77d))
* support current Hugging Face CLI publication ([#15](https://github.com/edithatogo/foi-process/issues/15)) ([e328a70](https://github.com/edithatogo/foi-process/commit/e328a7055458f2b6bcd6ad0b12ae825b4c79d6c6))
* support external scale evidence paths ([852311c](https://github.com/edithatogo/foi-process/commit/852311c73052e2e612bba2adff3b7e7abdc5d8ab))
* use binary media type for Zenodo upload ([#20](https://github.com/edithatogo/foi-process/issues/20)) ([d9147fd](https://github.com/edithatogo/foi-process/commit/d9147fda1bc1b56948586d045f9d9e7a77cf4036))
* verify published registry metadata ([#83](https://github.com/edithatogo/foi-process/issues/83)) ([f7d61d2](https://github.com/edithatogo/foi-process/commit/f7d61d2d661f41464ebc880d5d871c380c0a901e))
* withhold events linked to withheld objects ([#84](https://github.com/edithatogo/foi-process/issues/84)) ([012454a](https://github.com/edithatogo/foi-process/commit/012454a1d7ec3d33c1bdfb31c5d0ce1bc3d2e9c0))


### Performance Improvements

* optimize BTreeMap lookups ([4508a97](https://github.com/edithatogo/foi-process/commit/4508a97630d1c53cf23924ad283367123ab8e551))
* optimize hex encoding ([38f224a](https://github.com/edithatogo/foi-process/commit/38f224a3452570c8178fa409350fc8399b93909d))
* optimize partition component formatting ([01aad96](https://github.com/edithatogo/foi-process/commit/01aad9649f33a23520e39195157364ae24f9ade6))
* optimize redundant entry allocation ([8befbd1](https://github.com/edithatogo/foi-process/commit/8befbd17b263f1a8a26c29019b7eceb77292f34f))
* validate Hugging Face bundles in one process ([#13](https://github.com/edithatogo/foi-process/issues/13)) ([9df4619](https://github.com/edithatogo/foi-process/commit/9df46196b2fcb0dd6e15fcb10f7e4dca2291b0b2))

## v3 — 2026-07-09

### Architecture

- Collapsed seven proposed crates into one modular Rust package plus binaries.
- Made archive and live ingestion converge on one delta/replay path.
- Replaced proposed custom mining code with a direct Rust4PM adapter.
- Corrected the Rust4PM roadmap because appendable OCEL already exists upstream.

### Contracts and integrity

- Added typed identifiers, terms, digests, timestamps, confidence, privacy, revisions, stream positions, provenance, object links/changes, document bundles, review records, and run manifests.
- Replaced ad-hoc canonical JSON with RFC 8785 JCS for generated identifiers.
- Separated evidence records from references to avoid row duplication at corpus scale.
- Added schema generation and portable compatibility schemas.
- Added a feature-gated `AppendableOCEL` recording-sink integration test that asserts corrected events are appended once.

### Replay and live processing

- Added duplicate, stale, conflict, revision-gap, position-gap, position-regression, correction, and retraction semantics.
- Added restartable replay snapshots, checkpoints, quarantine output, and revision-aware aggregation.
- Verify replay snapshot state hashes before restoration and reject duplicate snapshot records/partitions.
- Added stdin NDJSON support, complete normalized table journals, append-only resume semantics, and refusal to truncate an existing fresh-run journal.
- Added output sync, parent-directory sync on Unix, state-before-checkpoint commit ordering, and out-of-order revision protection in live summaries.

### Safety and publication

- Added explicit privacy/access/publication disposition and safe public projections.
- Added human review records and a candidate-to-certified fixture.
- Kept statutory and legal certification outside autonomous process mining.

### Repository operations

- Added Conductor tracks/quality gates, repo-layout-aware export packets, parent/sub-issue plans, funding work packages, CI, dependency policy, and reproducibility checks.
