# Simulation, research and adoption evidence

## Implemented evidence

T09 adds a deterministic, standard-library-only workload generator for four public-safe synthetic scenarios:

| Scenario | Controlled change | Intended observation |
|---|---|---|
| Baseline | Stable arrivals and service time | Reference backlog and cycle-time distribution |
| Demand surge | Concentrated arrivals plus slower processing during the surge | Peak backlog exceeds baseline |
| Concept drift | Later cases add clarification activity and processing delay | Additional variant and higher tail cycle time |
| Correction stress | Elevated decision-event revision probability | Latest-revision replay and correction-rate pressure |

The generator deposits eight Hugging Face dataset tables: active event log, full event revision history, cases, daily metrics, summaries, OCEL events, OCEL objects, and OCEL event-object links. All identifiers, timestamps and pseudo-random choices are deterministic for the recorded seed. No real requester, authority or correspondence data is used.

Executable invariants verify deterministic regeneration, unique identifiers, latest-revision materialisation, non-negative backlog, terminal backlog closure, expected separation between scenarios, and referential integrity for OCEL links. The Space projection includes only scenario summaries and daily metrics; raw event-level tables remain in the dataset bundle.

## Adoption ledger

| Candidate consumer | Evidence available now | Promotion gate | State |
|---|---|---|---|
| Kairos simulation workflows | Deterministic JSONL cases, events and daily operating metrics | Consumer fixture proving import and scenario selection | Reference-ready, not promoted |
| rulesandprocesses research | Scenario definitions, hypotheses and reproducible summary measures | Independent review of construct validity and limitations | Evidence packet ready |
| Sourceright review workflow | Manifested artefacts, invariant tests and comparative dashboard | Recorded review outcome against a named release | Review-ready |
| Propel / public dashboard | Compact comparative projection and responsive charts | Free GitHub Pages deployment from a verified dataset commit | Operational; Hugging Face Space runtime is not required |
| FOI operational pilot | Synthetic workload and acceptance measures | Privacy assessment, tikanga/data-governance review and approved de-identified pilot data | Not started |

No ownership is transferred by this track. Kairos, rulesandprocesses and Sourceright remain reference patterns or candidate consumers, not runtime dependencies.

## Funding evidence work packages

### WP1: Independent simulation validation

- Deliverable: reviewed scenario catalogue, construct-validity assessment and reproducibility report.
- Acceptance: an external reviewer can regenerate all tables and explain each expected scenario separation.
- Evidence supplied: generator, invariant suite, dataset manifest and comparative dashboard.

### WP2: De-identified pilot calibration

- Deliverable: approved calibration protocol comparing synthetic distributions with aggregate operational measures.
- Acceptance: governance approval precedes data access; no requester-level material enters the public dataset.
- Dependency: participating authority, privacy impact assessment and tikanga/data-governance decision.

### WP3: Operational decision-support evaluation

- Deliverable: prospective evaluation of backlog and correction indicators in a read-only workflow.
- Acceptance: pre-registered measures, human decision authority retained, false-confidence and subgroup-impact review completed.
- Dependency: WP2 approval and a named operational sponsor.

These work packages are funding-ready evidence structure, not evidence that funding has been awarded or that an operational deployment exists.

## Decision and limitations

The synthetic generator remains owned by foi-process until a real consumer, compatibility fixture, benchmark, privacy review and maintenance commitment satisfy the promotion gate. Synthetic scenario separation demonstrates engineering behaviour, not legal compliance, causal effect, institutional performance or production readiness. Publication of the generated bundle remains separately gated by Hugging Face write credentials and the existing publication workflows.
