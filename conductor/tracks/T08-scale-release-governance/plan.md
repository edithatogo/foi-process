# Plan

- [x] 1k/10k/200k synthetic full-scale benchmark with isolated repeated profiles
- [x] Parquet partition decision and tested path contract
- [x] SBOM/checksum/mining manifest release-evidence builder and verifier
- [x] Update promotion/adoption ledger
- [x] Close repository work with benchmark, fixtures, and decision records
- [x] Rerun the full profile on a representative privacy-approved live archive sample:
  benchmark-only hosted run [`31771603638`](https://github.com/edithatogo/foi-process/actions/runs/31771603638)
  verified all 33,217 records at pinned source revision
  `bd119937c0532cc1f03ca60a7d84ca6991dab5c6`; full and incremental replay
  produced the same canonical snapshot, and only aggregate evidence was retained.
- [x] Publish and attest the code release-evidence artifact in hosted CI:
  [`v0.2.0`](https://github.com/edithatogo/foi-process/releases/tag/v0.2.0),
  run [`31766462302`](https://github.com/edithatogo/foi-process/actions/runs/31766462302),
  exact commit `71da1b84ff8d0a50894348f61ad60947906c6359`, and verification receipt
  `conductor/evidence/v0.2.0-release-verification.json`.

- [x] Add license files, dependency policy, Dependabot, deterministic fixture regeneration, and SBOM manifest fields.
- [x] Generate and commit `Cargo.lock` in the Rust export environment.
- [x] Pin the code-release workflow actions and enforce exact tag, metadata, evidence, and attestation checks.
