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

## Dependency repair, 2026-11-20

- [x] Reconcile PR #144's direct serde_json requirements, preserving the root lock's 1.0.151 selection.
- [x] Compile and run both existing bounded fuzz targets locally with the qualification below.
- [ ] Verify hosted security-fuzz on the corrected PR head; prior successful runs are historical evidence only.

The Renovate branch at `84a4e09a36c02f3398f78887477db4ec6d8a0d99` selected 1.0.151 in the root manifest but 1.0.154 in the fuzz manifest. Both direct requirements belong to the same semver-compatible package graph. Aligning the fuzz requirement with the root lock restores a satisfiable graph without changing any production dependency version.

Local execution evidence:

- `cargo +nightly-2026-08-01 check --manifest-path fuzz/Cargo.toml --bins`: passed.
- `python scripts/test_security_fuzz_workflow.py` and `git diff --check`: passed.
- Both `contract_json` and `archive_package_intake` completed 1,000 runs with
  cargo-fuzz 0.13.2, `-max_len=65536 -rss_limit_mb=1024 -timeout=5` and local
  `ASAN_OPTIONS=detect_leaks=0`. AddressSanitizer instrumentation remained enabled.
- The initial default-sanitizer `contract_json` campaign completed its 1,000
  inputs, then LeakSanitizer exited with its explicit ptrace-environment error.
  Local leak detection is therefore unqualified. No sanitizer setting or gate
  was weakened in the repository; hosted default-sanitizer execution remains
  required on this repair.
