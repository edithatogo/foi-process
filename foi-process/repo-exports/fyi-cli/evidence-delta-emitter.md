# Experimental EvidenceDelta emitter for live/archive convergence

## Why

Allow `fyi-cli` capture/sync/watch operations to feed `foi-process` dynamically without embedding process mining or NLP in the CLI.

## Scope

- Place the canonical capture-owned type in `crates/fyi-core` after fixture agreement.
- Emit NDJSON and/or bounded-channel records behind an experimental flag.
- Include logical record ID, revision, source/partition/sequence, observed/captured times, content hashes, WARC/WACZ locator, correlation/causation IDs, and request hint.
- Persist watermarks and make duplicate delivery safe.
- Add `.conductor` track/subtasks and connect them to the existing GitHub Project sync.

## Acceptance

- Replaying an emitted fixture twice is idempotent.
- A changed source emits revision 2 with prior digest and supersedes ID.
- A gap/conflict fixture is detected by `foi-process`.
- No OCR, NLP, or mining algorithm is added to `fyi-cli`.
