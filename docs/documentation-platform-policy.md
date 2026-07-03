# Documentation Platform Policy

Status captured: 2026-06-15.

Astro is the standard documentation platform for every repository in the Legal NZ system going forward.

## Policy

All new documentation sites, published documentation portals, generated documentation shells, and docs-preview workflows must use Astro.

Existing documentation generators may still be used only as source or API-reference generators when they feed Astro-owned documentation output. They must not become the published documentation platform for a repo unless a conductor exception explicitly approves it.

## Required default

| Documentation need | Required platform |
| --- | --- |
| Public docs site | Astro |
| Internal docs portal | Astro |
| Static documentation preview | Astro |
| Versioned docs site | Astro |
| API reference publishing | Generate source reference, then publish through Astro |
| CLI docs publishing | Generate command reference, then publish through Astro |
| Dataset documentation site | Astro, with dataset cards linked or embedded |

## Allowed supporting tools

| Tool class | Allowed use | Limitation |
| --- | --- | --- |
| TypeDoc | Generate TypeScript API/reference content | Must feed Astro or be linked from an Astro docs site |
| Sphinx, MkDocs, Docusaurus, VitePress, Nextra, VuePress, Docsify, Mintlify | Legacy source only during migration | Not approved for new published docs sites |
| Markdown linting and Vale | Prose quality gates | Remain required and independent of Astro |
| Storybook | Component development/reference if needed | Not a replacement for the docs site |

## Repo requirements

Each repo must converge on:

1. An Astro docs app or a documented reason why it delegates docs to the root Astro workspace.
2. `docs/` or `site/` content that can be rendered through Astro.
3. A documented `docs:dev`, `docs:build`, and `docs:check` command where the repo owns a docs site.
4. CI that builds the Astro docs site or verifies that docs are delegated.
5. Migration notes for any existing non-Astro docs library.

## Root orchestration rule

The root `legal-nz` repo coordinates the Astro standard and cross-repo docs map. Implementation belongs in the owning repo.

## Agent instruction

Before adding documentation tooling, agents must check this policy. If a task asks for a docs site or docs build, use Astro. If an existing repo uses another docs framework, create a migration task rather than expanding that framework.

## Plugin and style baseline

Use `docs/astro-plugin-assessment.md` and `conductor/templates/astro-plugin-baseline.json` for repo-specific plugin decisions.

Default docs sites must use Astro with Starlight, MDX, Sitemap, and the shared Legal NZ style tokens. Add Tailwind, UI framework integrations, RSS, extra search, or analytics/performance integrations only when the owning repo has a documented need and a conductor task records the exception.
