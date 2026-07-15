# [T08] Scale, release, and governance

## Goal

Benchmark and publish reproducible signed releases.

## Owning/consumer repos

foi-process, fyi-archive

## Evidence update (2026-07-15)

- One bounded public FYI request was captured read-only and validated as a
  derived store plus WARC/WACZ package. See
  `docs/evidence/real-fyi-archive-capture-2026-07-15.json`.
- Publication remains synthetic-only under
  `governance/publication_gate.json` until the human governance gates are approved.
- Zenodo preservation and native DuckDB tests now have manual workflows, but no
  DOI or runtime pass is claimed yet.

## Acceptance gates

- [ ] Named consumer and owner
- [ ] Fixtures and automated validation
- [ ] Privacy/safety boundary documented
- [ ] Performance evidence where relevant
- [ ] Conductor status and promotion ledger updated
- [ ] Duplicate incubator definition removed after promotion

## Source

`conductor/tracks/t08-*` and `conductor/quality-gates.yaml`.
