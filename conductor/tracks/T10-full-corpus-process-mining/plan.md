# Plan: Full-corpus ingestion, mining, and static dashboard

Status: acceptance verified; publication and jurisdiction modelling remain
separate gates.

## Phase 1: Cross-repository contract acceptance

- [ ] Task: Pin the `fyi-cli` and `fyi-archive` contract versions and golden fixtures.
- [ ] Task: Write failing schema, checksum, coverage, and privacy-boundary tests.
- [ ] Task: Extend T03 adapter contracts for partitioned process projections.
- [ ] Task: Phase verification and checkpoint against repository quality gates.

## Phase 2: Full replay and incremental equivalence

- [ ] Task: Write failing bounded-ingestion and source-order regression tests.
- [ ] Task: Implement partitioned full-corpus ingestion and replay.
- [ ] Task: Implement incremental continuation, correction, retraction, and takedown handling.
- [ ] Task: Prove full/incremental equivalence with deterministic hashes.
- [ ] Task: Phase verification and checkpoint against repository quality gates.

## Phase 3: Mining and aggregate contract

- [ ] Task: Write failing tests for activities, edges, variants, waits, durations, and authority cubes.
- [ ] Task: Generate process, OCEL, quality, freshness, and qualified conformance aggregates.
- [ ] Task: Reconcile aggregate totals to source coverage and checksums.
- [ ] Task: Run representative and full-corpus benchmarks under T08.
- [ ] Task: Phase verification and checkpoint against repository quality gates.

## Phase 4: Static Space visualization

- [ ] Task: Extend T07 dashboard data contract with full-corpus aggregate and coverage views.
- [ ] Task: Add process map, authority comparison, timeline, variant, duration, outcome, and quality views.
- [ ] Task: Add Dataset Viewer pagination for case/event detail and resilient unavailable states.
- [ ] Task: Enforce accessibility, mobile/desktop layout, and static payload budgets.
- [ ] Task: Phase verification and checkpoint against repository quality gates.

## Phase 5: Operational continuation and closeout

- [ ] Task: Add scheduled build verification without enabling publication.
- [ ] Task: Add freshness, revision, coverage, and pipeline-health evidence.
- [ ] Task: Complete privacy, removal, threat-model, rights, and statutory qualification checks.
- [ ] Task: Record acceptance evidence in issue #37 and parent epic #36.
- [ ] Task: Leave actual Hugging Face publication behind the separate explicit gate in issue #9.
