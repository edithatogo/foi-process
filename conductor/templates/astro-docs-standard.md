# Astro Documentation Standard

Use this checklist for every Legal NZ repo that owns documentation.

## Decision

- [ ] Repo owns its own Astro docs site.
- [ ] Repo delegates docs publishing to the root Astro docs workspace.
- [ ] Repo has no docs site requirement yet, with reason documented.

## Required commands

- [ ] `docs:dev`
- [ ] `docs:build`
- [ ] `docs:check`

## Required files

- [ ] Astro config present where repo owns docs.
- [ ] Markdown or MDX source content identified.
- [ ] API or CLI reference generation feeds Astro, not a separate published framework.
- [ ] Vale and Markdown style gates remain active.
- [ ] Plugin choices match `conductor/templates/astro-plugin-baseline.json`.
- [ ] Style choices match the shared Legal NZ Starlight theme.

## Migration inventory

| Existing docs tool | Current use | Migration action | Owner |
| --- | --- | --- | --- |
| TypeDoc | API reference generation if present | Generate reference content and publish through Astro | Owning repo |
| Sphinx/MkDocs/Docusaurus/VitePress/Nextra/VuePress/Docsify/Mintlify | Legacy docs site if present | Replace with Astro docs app | Owning repo |
| Storybook | Component reference if present | Keep as component tool, link from Astro | Owning repo |

## CI gates

- [ ] Build Astro docs in GitHub Actions.
- [ ] Run docs link/prose checks.
- [ ] Fail on introduction of a new non-Astro docs-site framework unless a conductor exception exists.
- [ ] Fail on unapproved Astro integrations that are not in the baseline or documented as conditional.

## Release gates

- [ ] Commit docs migration in the owning repo.
- [ ] Push and check GitHub Actions.
- [ ] Update root repository-status mapping with docs platform status.
