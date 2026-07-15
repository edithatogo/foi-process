# Release evidence package

`scripts/build_release_evidence.py` creates a bounded release evidence directory containing:

- the committed `Cargo.lock`;
- an SPDX 2.3 JSON SBOM derived from `cargo metadata --locked`;
- the reviewed Dataset manifest;
- the Rust scale report;
- a refreshed mining-run manifest linking the Dataset, benchmark, SBOM, source revision, and commit;
- a release evidence manifest plus sorted `SHA256SUMS`.

The builder refuses a non-empty output directory. `verify_release_evidence.py` rejects malformed or
duplicate checksum entries, path separators, uncovered files, digest differences, byte-length
differences, and disagreement between the evidence manifest and the directory.

```powershell
python scripts/build_release_evidence.py `
  --benchmark benchmarks/rust-scale-windows-gnu.json `
  --output target/release-evidence
python scripts/verify_release_evidence.py target/release-evidence
```

The `release-evidence` workflow regenerates the benchmark and package from a clean checkout and
uploads the verified directory as one GitHub Actions artifact. Cryptographic signing or GitHub
artifact attestation remains a protected-release gate and must not be claimed from checksums alone.
