# Plan

- [x] Identify highest-risk untrusted Rust parsing and intake surfaces.
- [x] Add bounded contract JSON and archive-package libFuzzer targets.
- [x] Add an explicit replay-proptest CI gate.
- [x] Add pinned least-privilege PR and scheduled/manual fuzz jobs.
- [x] Add static workflow regression coverage.
- [x] Run focused library tests, formatting, lint, and workflow-contract checks.
- [x] Compile and execute the libFuzzer harnesses on a supported Unix nightly runner.
- [x] Obtain hosted PR smoke and scheduled campaign evidence.

## Evidence

- Merged implementation: `1f10bfbe406838a17fc990e00a3501b6c60efcea`
- Merged-main CI: https://github.com/edithatogo/foi-process/actions/runs/31682942769
- Manual bounded campaign: https://github.com/edithatogo/foi-process/actions/runs/31682955991
