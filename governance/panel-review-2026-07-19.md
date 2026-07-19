# Independent technical panel rerun

Review date: 2026-07-19
Commit reviewed: `b957249`
Scope: non-publication implementation and production-shaped archive continuation.

This is an independent technical review record. It is not a substitute for a
statutory lawyer, privacy officer, licensing owner, or tikanga reviewer. No
separate tikanga reviewer was commissioned for this single-person project;
culturally sensitive real data remains escalation-controlled and unpublished.

| Panel role | Result | Evidence |
| --- | --- | --- |
| Privacy and public-output minimisation | Controls present; recursive validation and raw-data exclusion verified | `docs/privacy-publication.md`, `scripts/test_public_privacy.py`, `governance/non-publication-review-2026-07-19.json` |
| Archive provenance and source rights | Four-request continuation and fourteen attachment checks passed; source rights remain separate from Apache-2.0 code rights | `docs/evidence/scaled-live-archive-benchmark-2026-07-19.json`, `docs/source-rights-and-licensing.md` |
| Security and abuse resistance | Path traversal, token-bearing workflow, destination allowlist, differencing, and takedown controls documented | `governance/threat-model-2026-07-19.md` |
| Replay and process semantics | Revision 2 and source sequences 2-5 accepted with zero quarantine rows | `docs/evidence/production-continuation-2026-07-19.json` |
| Operations and removal | Private security advisory, data-removal form, acknowledgement target, and replacement-revision procedure documented | `docs/removal-appeal.md` |
| Statutory mapping | Indicative OIA mapping complete; no legal conformance claim | `governance/statutory-source-review-2026-07-19.md` |

## Formal governance rows

| Gate | Non-publication result | Publication result |
| --- | --- | --- |
| Requester and third-party privacy | Technical controls reviewed | Blocked |
| OCR, embeddings, and NLP amplification | Deferred; raw derivatives prohibited | Blocked |
| Tikanga and data governance | Owner-led assessment; escalation required for culturally sensitive data | Blocked |
| Licensing and attribution | Code/schemas Apache-2.0; source-derived rights not inferred | Blocked |
| Removal and appeal | Workflow operational for synthetic outputs and future controlled review | Blocked |
| Threat model | Technical controls reviewed | Blocked |
| Statutory source review | Indicative mapping complete | Legal conformance not asserted |
| Accountable owner | Non-publication work authorized | Publication not authorized |

The panel therefore supports continued engineering, testing, and private
operational backfill while preserving the fail-closed publication gate.
