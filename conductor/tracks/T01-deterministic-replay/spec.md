# Deterministic replay

## Goal

Make archive/live replay idempotent under duplicates, corrections, gaps, conflicts, and retractions.

## Non-goals

Do not duplicate capabilities owned by another repository or promote an untested contract.

## Exit criteria

- Test fixtures and property cases
- Persist checkpoint/dead-letter state
- Map real FYI archive sample
