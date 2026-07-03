# Plan: Antigravity Swarm Track Execution

**Generated**: 2026-06-14

## Overview
Set up all Conductor tracks for Antigravity swarm execution using the existing `cline` engine with `deepseek-v4-flash`, plus Codex `gpt-5.5` lanes for cross-repository reasoning and Chrome-gated work where browser features are required.

The completed tracks remain historical artifacts. New or resumed work should run through the `track_swarm` preset in `swarm-config.yaml`, with Track 10 using the narrower `track10_schema` preset.

## Prerequisites
- Antigravity swarm configuration: `swarm-config.yaml`
- Agent roster: `subagents.yaml`
- Track definitions: `conductor/tracks.md` and `conductor/tracks/*/plan.md`
- Local Cline lane: `deepseek-v4-flash`
- Codex lane requested by user: `gpt-5.5`
- Chrome plugin or node_repl browser-control workflow for Chrome-gated tasks

## Dependency Graph

```text
T1 ──┬── T3 ──┬── T5 ──┬── T8 ── T10
T2 ──┘        │        │
              ├── T6 ──┤
T4 ───────────┘        │
                       └── T9
T7 ───────────────────────┘
```

## Tasks

### T1: Normalize Swarm Agent Roster
- **depends_on**: []
- **location**: `subagents.yaml`
- **description**: Ensure Cline `deepseek-v4-flash`, Codex `gpt-5.5`, Chrome-gated, architecture, and validation lanes are represented as explicit agents.
- **validation**: `subagents.yaml` includes `General_Coder`, `Codex_GPT55_Engineer`, `Chrome_Operator`, `Architect_Oracle`, and `Quality_Validator`.
- **status**: Completed
- **log**: Added Codex and Chrome operator lanes while preserving existing Cline agents.
- **files edited/created**: `subagents.yaml`

### T2: Add Track Swarm Presets
- **depends_on**: []
- **location**: `swarm-config.yaml`
- **description**: Add reusable Antigravity swarm presets for all-track execution and Track 10 schema work.
- **validation**: `swarm-config.yaml` contains `track_swarm` and `track10_schema` presets with implementation, Codex, Chrome, architecture, and validator lanes.
- **status**: Completed
- **log**: Added presets without changing the existing default Cline `deepseek-v4-flash` engine.
- **files edited/created**: `swarm-config.yaml`

### T3: Assign Completed Tracks to Audit-Only Swarm Mode
- **depends_on**: [T1, T2]
- **location**: `conductor/tracks.md`, `conductor/tracks/*/plan.md`
- **description**: Treat Tracks 1-9 as completed, swarm-runnable audit lanes. Use Cline for quick inspection, Codex for cross-track reconciliation, and Quality_Validator for evidence checks.
- **validation**: Completed tracks remain marked complete and are not reopened unless a specific regression or missing artifact is found.
- **status**: Completed
- **log**: Codex verified `conductor/tracks.md` keeps Tracks 1-9 complete and Track 10 open. No Track 1-9 implementation changes were made; they remain audit-only unless future evidence shows a concrete gap.
- **files edited/created**: `conductor/tracks/schema_unification_20260614/plan.md`, `progress.md`

### T4: Define Track 10 Implementation Waves
- **depends_on**: []
- **location**: `task_plan.md`, `conductor/tracks/schema_unification_20260614/plan.md`
- **description**: Make Track 10 executable in parallel waves: schema architecture, schema sync, msgspec optional/default-safe record updates, feature extraction, tests, and account/deployment gates.
- **validation**: Track 10 plan states which tasks can run in parallel and which require validation or user approval.
- **status**: Completed
- **log**: Added swarm assignment and gate rules to the active mission plan.
- **files edited/created**: `task_plan.md`

### T5: Run Local Implementation Lanes
- **depends_on**: [T3, T4]
- **location**: `nlp-policy-nz/`, `corpus-law-nz/`, `corpus-nz-hansard/`, `scripts/`, `tests/`
- **description**: Dispatch non-browser local work to Cline `General_Coder` and Codex `Codex_GPT55_Engineer`. Keep schema generation, msgspec changes, local tests, and file synchronization out of Chrome.
- **validation**: Local code changes are captured in the relevant track plan logs and pass phase-specific checks.
- **status**: Completed
- **log**: Local Track 10 implementation artifacts were already present and reconciled by Cline lanes; Codex verified canonical schemas across all three target repos, additive `PipelineRecord` fields, committee/submission/regulations feature extraction helpers, and focused tests.
- **files edited/created**: `subagents.yaml`, `scripts/swarm_orchestrator.py`, `conductor/tracks/schema_unification_20260614/plan.md`, `progress.md`

### T6: Run Architecture and Compatibility Review
- **depends_on**: [T3, T4]
- **location**: `nlp-policy-nz/schemas/`, `corpus-law-nz/schemas/`, `corpus-nz-hansard/schemas/`, `findings.md`
- **description**: Use `Architect_Oracle` and Codex to review schema additivity, field defaults, downstream compatibility, and account/deployment assumptions.
- **validation**: Review findings are recorded and any blocking incompatibilities become explicit follow-up tasks.
- **status**: Completed
- **log**: Codex compatibility review found the current schema set byte-identical across `nlp-policy-nz`, `corpus-law-nz`, and `corpus-nz-hansard`. External-write wording in agent prompts was tightened so pushes/uploads/account mutation remain approval-gated.
- **files edited/created**: `subagents.yaml`, `conductor/tracks/schema_unification_20260614/plan.md`, `progress.md`

### T7: Queue Chrome-Gated Work
- **depends_on**: []
- **location**: `task_plan.md`, browser-authenticated external services
- **description**: Reserve `Chrome_Operator` for work that cannot be completed through local files or authenticated CLI/API checks, such as web-console verification, OAuth renewal, screenshots, or browser-profile-dependent account checks.
- **validation**: Chrome tasks are serial, approval-gated, and do not block local implementation lanes unless the specific phase needs browser-only evidence.
- **status**: Completed
- **log**: Added Chrome and external-write gate rules to the active mission plan.
- **files edited/created**: `task_plan.md`, `subagents.yaml`

### T8: Validate Phase Outputs
- **depends_on**: [T5, T6]
- **location**: `tests/`, `pytest.ini`, `.vale.ini`, `.markdownlint.json`, track plan files
- **description**: Run phase validations through `Quality_Validator`, including schema validation, pipeline serialization tests, linting, and workspace-doctor checks as relevant.
- **validation**: Validation results are recorded in the active track plan before sign-off.
- **status**: Completed with sandbox limitations
- **log**: Focused validation passed: 43 schema/swarm tests, 31 NLP feature/storage struct tests, 35 workspace/markdown tests, and 27 SHA/content-manifest tests. Full temp-file and bytecode-write validations are blocked by Windows ACL/OneDrive cache restrictions in this sandbox.
- **files edited/created**: `conductor/tracks/schema_unification_20260614/plan.md`, `progress.md`

### T9: Handle External Writes
- **depends_on**: [T5, T6, T7]
- **location**: GitHub remotes, Hugging Face datasets, Zenodo depositions
- **description**: Perform commits, pushes, Hugging Face updates, and Zenodo updates only after validation and explicit user approval for external writes.
- **validation**: Remote state is verified after each approved write.
- **status**: Blocked
- **log**: Not performed. Commit, push, Hugging Face mutation, Zenodo mutation, `.env` synchronization, browser-profile access, Chrome work, and account-setting changes require explicit approval.
- **files edited/created**:

### T10: Final Conductor Sign-Off
- **depends_on**: [T8, T9]
- **location**: `conductor/tracks.md`, `conductor/tracks/schema_unification_20260614/plan.md`, `progress.md`, `findings.md`
- **description**: Mark completed phases, update status surfaces, and record any residual blockers.
- **validation**: Track status matches evidence, no unchecked task is marked complete, and blockers are concrete.
- **status**: Blocked
- **log**: Local Track 10 integration is recorded in the Conductor plan and progress log. Full sign-off remains blocked on Phase 3 external-write/account gates and user manual verification.
- **files edited/created**: `conductor/tracks/schema_unification_20260614/plan.md`, `progress.md`

## Parallel Execution Groups

| Wave | Tasks | Can Start When |
|------|-------|----------------|
| 1 | T1, T2, T4, T7 | Immediately |
| 2 | T3 | T1 and T2 complete |
| 3 | T5, T6 | T3 and T4 complete |
| 4 | T8 | T5 and T6 complete |
| 4 | T9 | T5, T6, and T7 complete, plus explicit external-write approval |
| 5 | T10 | T8 and T9 complete |

## Testing Strategy
- Validate YAML shape before dispatch if the swarm runner has a config check command.
- Validate Track 10 schemas before pipeline changes consume them.
- Validate `msgspec.Struct` changes with optional/default-safe fields before Parquet serialization tests.
- Run local tests and linting before any external write.
- Use Chrome only for browser-authenticated evidence or visual/browser verification.

## Risks & Mitigations
- **Model label availability:** `gpt-5.5` is recorded because it was requested. Runtime dispatch should confirm the Codex model alias before starting that lane.
- **Unknown Antigravity schema strictness:** New presets and agents follow the existing YAML style, but the swarm runner should be config-checked before launch.
- **Chrome session sensitivity:** Browser profile, OAuth, and web-console tasks are isolated in the serial `Chrome_Operator` lane.
- **External side effects:** GitHub push, Hugging Face mutation, and Zenodo mutation are explicit external-write gates.
- **Completed-track drift:** Tracks 1-9 are audit-only unless new evidence shows their artifacts are incomplete.

## Planner Review
- Dependencies keep local implementation independent from Chrome-gated work.
- Validation sits after implementation and architecture review, before external writes and sign-off.
- The plan does not assume browser access or account mutation without an explicit gate.
- No separate subagent review tool was exposed in this turn, so this review was performed inline against the swarm-planner checklist.
