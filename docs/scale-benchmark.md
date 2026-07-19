# Rust scale benchmark

The committed report at `benchmarks/rust-scale-windows-gnu.json` exercises the release-mode
revision-aware summary in isolated processes. Each baseline and correction/retraction profile has
three order-alternated repetitions; the report records every timing sample, median throughput,
maximum peak resident memory, output size, and canonical output SHA-256.

## 2026-07-15 local evidence

Host: Windows 11 AMD64, 22 logical CPUs, Rust 1.97 GNU toolchain. Each case has five events. The
stress profile adds a correction every 20 logical events and a retraction every 1,000.

| Profile | Baseline median | Baseline throughput | Peak memory | Stress/baseline |
| --- | ---: | ---: | ---: | ---: |
| 1,000 cases | 0.039 s | 127,144 revisions/s | 9.3 MB | 0.92x |
| 10,000 cases | 0.390 s | 128,069 revisions/s | 41.1 MB | 1.01x |
| 200,000 cases | 8.451 s | 118,332 revisions/s | 814.4 MB | 1.29x |

The 200,000-case baseline materialises 1,000,000 active events. Its canonical summary digest is
`b8ff0ca3ca84b342dde4bdaf57dbdbfad0b78333b0c71aec1837d3555f4c64f8`. The stress profile applies
50,000 corrections and 1,000 retractions and retains a deterministic digest across repetitions.

This is a synthetic full-scale shape, not a claim about the timing distribution or attachment/OCR
weight of the live FYI archive. A separate production-shaped sample benchmark now covers four real
requests and fourteen attachments in `docs/evidence/scaled-live-archive-benchmark-2026-07-19.json`.
It is integration evidence, not a full-corpus throughput claim, and does not authorize publication.

Run locally:

```powershell
python scripts/run_rust_scale_suite.py `
  --profiles 1000,10000,200000 `
  --repetitions 3 `
  --output benchmarks/rust-scale-local.json
python scripts/validate_scale_report.py benchmarks/rust-scale-local.json --require-standard
```
