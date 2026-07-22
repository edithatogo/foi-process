# Repository Agent Instructions

## Co-Researcher System

This repository uses the Co-Researcher skills. At the beginning of a task, run:

```powershell
~/.codex/co-researcher/.codex/co-researcher-codex bootstrap
```

## Repository Ownership And External Actions

The additional approval and rendered-diff review gates below apply to upstream,
third-party, or otherwise externally owned repositories. They do not apply to
repositories owned by the user, including `edithatogo/foi-process`,
`edithatogo/fyi-archive`, and `edithatogo/fyi-cli`. In those repositories,
normal autonomous implementation, branch updates, issue maintenance, pull
request creation, and merging are permitted when requested by the user.

For upstream or third-party repositories:

- Treat each pull request, issue, comment, review, tag, branch merge, and other
  externally visible action as a separate approval gate.
- Require approval of the exact repository and exact action after the final
  payload has been shown.
- Require review of the rendered final diff after the last push before merge or
  publication.
- Confirm base repository, head repository, base ref, head ref, commit list,
  merge commits, and final changed-file list before requesting approval.
- Warn and stop when a contribution contains workflow, release, packaging,
  permission, credential, or other security-sensitive changes outside scope.

`openfisca/*` repositories remain denylisted. Do not create or update anything
there without a one-time override naming the repository and action.

## Publication Boundaries

Repository ownership does not remove data-rights, privacy, licensing, or
publication gates. Keep source-derived rights separate from the Apache-2.0
code licence, preserve fail-closed production-data controls, and do not claim
publication until hosted evidence verifies it.
