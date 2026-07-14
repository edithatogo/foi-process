# Migration from v2

- Replace the seven-crate workspace with this single package.
- Rename `ProcessEventEnvelope` to `ProcessEvent`; full evidence becomes `EvidenceRef`.
- Replace string times/digests/confidence with validated types.
- Convert archived records to `EvidenceDelta` before normalisation.
- Replace `NoopLiveNormalizer` with `DeterministicNormalizer` + `ReplayEngine`.
- Replace hand-sorted complete-log dashboard generation with `RevisableProcessSummary`.
- Replace the proposed appendable-OCEL upstream issue with integration/durability issues.
- Add privacy assessment before any OCR/search/dashboard publication.
- Use each target repository's existing Conductor location and workflow.
