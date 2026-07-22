# Verification evidence: 2026-07-22

The Windows MSVC `link.exe` name is shadowed by the Git Unix linker shim in
the local PATH. Verification therefore used the installed GNU Rust toolchain
and MinGW linker explicitly; this does not change the repository's MSRV or
release target.

```powershell
$env:CARGO_TARGET_X86_64_PC_WINDOWS_GNU_LINKER = "C:\Users\60217257\scoop\apps\mingw\current\bin\gcc.exe"
rustup run stable-x86_64-pc-windows-gnu cargo test --target x86_64-pc-windows-gnu --all-targets
rustup run stable-x86_64-pc-windows-gnu cargo clippy --target x86_64-pc-windows-gnu --all-targets -- -D warnings
rustup run stable-x86_64-pc-windows-gnu cargo doc --target x86_64-pc-windows-gnu --no-deps
```

Results:

- `foi-process`: all test binaries passed, including contracts, archive,
  Parquet, replay, and Rust4PM adapter tests.
- `foi-process`: Clippy passed with warnings denied.
- `foi-process`: documentation generation passed.
- `foi-process`: `cargo fmt -- --check` passed.
- `fyi-archive`: `242 passed, 1 skipped` under its repository virtualenv.

This verifies source behavior on the GNU target. A protected release still
needs the CI MSVC/MSRV matrix and hosted acceptance checks.

## Cross-repository archive evidence

- fyi-archive historical-source run
  [29908248734](https://github.com/edithatogo/fyi-archive/actions/runs/29908248734)
  produced 4,997 distinct Internet Archive candidates. Reconciliation classified
  all 4,997 as `archive_only_candidate` against the 33,217-record public HF
  manifest; no Internet Archive candidate was treated as a live capture.
- fyi-archive backfill-controller run
  [29908342309](https://github.com/edithatogo/fyi-archive/actions/runs/29908342309)
  found no pending batches because the persisted NZ horizon is complete through
  request ID 250,000. The retained controller state reports 3,074 merged batches
  and 33,244 captured records.
- These figures are operational provenance only. They do not update the public
  HF dataset and do not authorize publication of production-derived events,
  attachments, OCR, embeddings, or unrestricted NLP outputs.
