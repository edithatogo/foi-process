# Security, quality, and fuzzing

## Goal

Continuously exercise untrusted Rust contract and archive-package intake surfaces with deterministic property tests and bounded coverage-guided fuzzing.

## Requirements

- Existing replay properties are an explicit CI gate with a fixed minimum case count.
- libFuzzer targets cover contract JSON and archive manifest/event intake.
- Every campaign has input, memory, per-input time, and overall runner bounds.
- Actions use immutable revisions, read-only permissions, and no persisted credentials.
- Failure inputs are retained as short-lived diagnostic artifacts.
- Fuzz harnesses must not perform network access or publish data.

## Exit criteria

Focused local tests, formatting, lint, and workflow-contract checks pass; hosted PR smoke and scheduled/manual campaigns remain separately evidenced.
