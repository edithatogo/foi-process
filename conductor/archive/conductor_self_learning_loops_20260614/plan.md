# Track Plan: Hermes-Style Conductor Self-Learning and Skill Improvement Loops

## Objective
Build self-learning and self-improvement loops into conductor repos, tracks, and skills so repeated failures become reusable checks, templates, or skill instructions.

## Root-Owned Coordination Artifacts
- `conductor/templates/self-improvement-loop.md`

## Consensus Loop
- Observe.
- Reflect.
- Distill.
- Improve.
- Evaluate.
- Promote.

## Phase 1: Shared Template
- [x] Task: Add a reusable self-improvement loop template.
- [x] Task: Add a machine-readable learning entry schema if multiple repos need automated learning-log validation.
- [ ] Task: Commit, push, and check Actions.

## Phase 2: Repo-Local Learning Surfaces
- [x] Task: Add `conductor/learning-log.md` to each subrepo where absent.
- [x] Task: Add `conductor/improvement-backlog.md` to each subrepo where absent.
- [x] Task: Add track templates that require `lessons_learned` and `next_check_to_add` sections.
- [ ] Task: Commit, push, and check Actions per subrepo.

## Phase 3: Skill Improvement Path
- [x] Task: Identify skills used by this workspace, including conductor setup/status/newtrack/implement/review/test and swarm orchestration skills.
- [x] Task: Create repo-local proposed skill patches or notes when a lesson should change future agent behavior.
- [x] Task: Do not write directly into global skill directories unless explicitly approved.
- [ ] Task: Commit proposed skill improvements in the owning repo or approved skill repo.

## Phase 4: Automated Feedback
- [x] Task: Add CI failure summarizers that write learning candidates without committing automatically.
- [x] Task: Add registry rejection/review feedback capture to the registry submission workflow.
- [x] Task: Add swarm run retrospectives after each phase.
- [x] Task: Promote only reviewed lessons to shared templates.

All Phase 4 retrospectives and review gates are logged in
`[phase-retrospectives.md](./phase-retrospectives.md)`.

## Acceptance Criteria
- Each conductor repo has a learning log and improvement backlog.
- Lessons are tied to evidence and root cause.
- Reusable lessons become tests, schemas, workflows, or templates.
- Global skills are not mutated without approval.
