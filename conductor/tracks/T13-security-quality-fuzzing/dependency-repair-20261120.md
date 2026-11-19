# Dependency repair follow-up, 2026-11-20

- [x] Reconcile PR #144's direct serde_json requirements, preserving the root lock's 1.0.151 selection.
- [x] Compile and run both existing bounded fuzz targets locally with the qualification below.
- [x] Verify hosted PR security-fuzz on repair head `4367ccb2562c84d3fe6640ef39ccc8fd111f10b4`: replay properties and bounded default-sanitizer smoke passed in [run 44605772750](https://github.com/edithatogo/foi-process/actions/runs/44605772750).
- [ ] Verify required CI on the final follow-up head before merge.

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

The first repair correctly restored fuzz execution, but its appended unchecked
items caused the completed-track validator to reject T13. This follow-up keeps
new maintenance acceptance separate from that completed historical plan and
retains all unexecuted acceptance gates honestly.
