# Project Tracks

`tracks.yaml` is the canonical machine registry. `status` records lifecycle
(`active`, `deferred`, or `completed`); `maturity` records the implementation or
evidence boundary. An implemented component is not necessarily a completed
track.

## Active

- [ ] **T00** Contract and promotion
  ([plan](./tracks/T00-contract-and-promotion/)) - partial contract acceptance.
- [ ] **T01** Deterministic replay
  ([plan](./tracks/T01-deterministic-replay/)) - replay core implemented; remaining consumer and promotion work is explicit in the plan.
- [ ] **T02** Rust4PM OCEL mining
  ([plan](./tracks/T02-rust4pm-ocel-mining/)) - adapter implemented; round-trip and benchmark acceptance remain.
- [ ] **T05** Conformance rules
  ([plan](./tracks/T05-conformance-rules/)) - indicative trace fixtures implemented; statutory-source promotion remains gated.
- [ ] **T06** Privacy publication
  ([plan](./tracks/T06-privacy-publication/)) - public projection implemented; profile and promotion acceptance remain.
- [ ] **T11** Jurisdiction case and process modelling
  ([plan](./tracks/jurisdiction_case_process_modelling_20260721/)) - foundations implemented; [#39](https://github.com/edithatogo/foi-process/issues/39) retains empirical, adjudication, replay, and legal-promotion gates.
- [ ] **T12** Instance archive-to-process pipeline consolidation
  ([plan](./tracks/instance_pipeline_consolidation_20260812/)) - intake and bounded reconciliation implemented; [#114](https://github.com/edithatogo/foi-process/issues/114) and [fyi-archive #370](https://github.com/edithatogo/fyi-archive/issues/370) retain durable-index, equivalence, publication, and parity work.

## Deferred

- [ ] **T04** Document OCR signals
  ([plan](./tracks/T04-document-ocr-signals/)) - contracts are implemented; full OCR/NLP fixtures remain deferred until production use requires them.

## Completed

- [x] **T08** Scale, release, and governance
  ([plan](./tracks/T08-scale-release-governance/)) - release evidence is hosted and attested; benchmark-only run [31771014519](https://github.com/edithatogo/foi-process/actions/runs/31771014519) verified the pinned 33,217-record live archive manifest without publication or raw-content retention.
- [x] **T03** Archive live adapters
  ([plan](./tracks/T03-archive-live-adapters/)) - acceptance verified.
- [x] **T07** Dashboard and Hugging Face
  ([plan](./tracks/T07-dashboard-propel-hf/)) - reviewed synthetic-fixture Dataset and public no-cost Static Space verified; this is not a real-data or full-corpus claim.
- [x] **T09** Simulation, research, and adoption
  ([plan](./tracks/T09-simulation-research-adoption/)) - repository scope completed; external publication is not part of track completion.
- [x] **T10** Full-corpus process-mining acceptance
  ([plan](./tracks/T10-full-corpus-process-mining/)) - repository-owned acceptance completed against the pinned 33,217-record manifest in closed issues [#36](https://github.com/edithatogo/foi-process/issues/36) and [#37](https://github.com/edithatogo/foi-process/issues/37). Recurring multi-instance operation is T12, not a reopened T10 gate.
- [x] **T13** Security, quality, and fuzzing
  ([plan](./tracks/T13-security-quality-fuzzing/)) - acceptance verified.

## Archived Bounded Track

- [x] **Event-log registry readiness**
  ([plan](./tracks/event_log_registry_readiness_20260721/)) - bounded publication completed at DOI [`10.5281/zenodo.21660296`](https://doi.org/10.5281/zenodo.21660296). Issue [#63](https://github.com/edithatogo/foi-process/issues/63) is a deferred full-corpus expansion placeholder, not unfinished bounded work.
