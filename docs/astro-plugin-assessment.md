# Astro Plugin and Style Assessment

Status captured: 2026-06-15.

This assessment defines the consistent Astro documentation plugin baseline for the Legal NZ repository system and maps repo-specific documentation needs.

## Source basis

- Astro official integration docs: `https://docs.astro.build/en/guides/integrations/`
- Astro Markdown docs: `https://docs.astro.build/en/guides/markdown-content/`
- Starlight docs framework: `https://starlight.astro.build/`

Key source findings:

- Astro integrations are configured through the `integrations` property in `astro.config.mjs`.
- Official integrations include `@astrojs/mdx` and `@astrojs/sitemap`.
- Astro Markdown supports content collections, Markdown pages, remark/rehype plugins, and optional MDX.
- Starlight is the Astro-native documentation framework and is the right baseline for multi-page technical docs.

## Standard plugin baseline

Every repo that owns a docs site should use this baseline unless a conductor exception is recorded.

| Layer | Required package or integration | Why |
| --- | --- | --- |
| Docs framework | `@astrojs/starlight` | Consistent docs IA, sidebar, search, SEO, code highlighting, and accessibility defaults. |
| Core renderer | `astro` | Required platform. |
| Structured content | Astro content collections | Typed docs metadata, consistent navigation, and validation. |
| Rich Markdown | `@astrojs/mdx` | Needed for reusable callouts, generated API snippets, benchmark cards, and dataset examples. |
| Sitemap | `@astrojs/sitemap` | Required for public docs discoverability. |
| Styling | Starlight theme CSS plus shared Legal NZ tokens | Consistent visual identity across repos. |
| Prose quality | Vale and markdownlint outside Astro | Existing prose gates remain required. |

## Standard style baseline

All Astro docs sites should share a single Legal NZ documentation style.

| Area | Standard |
| --- | --- |
| Site family name | `Legal NZ` |
| Product naming | Use repo-specific product names under the shared `Legal NZ` family. |
| Typography | Use one shared readable documentation font stack through Astro/Starlight theme CSS. |
| Colour | Use a restrained legal/research palette, not per-repo novelty themes. |
| Navigation | Shared top-level sections: `Overview`, `Install`, `Use`, `Data`, `API`, `Release`, `Governance`. Omit irrelevant sections per repo. |
| Callouts | Standardize callouts for `Rights`, `Source`, `Privacy`, `External write`, `Chrome gate`, `Experimental`, and `Deprecated`. |
| Code blocks | Consistent shell examples, PowerShell notes, and CLI-first command examples. |
| Dataset docs | Dataset cards remain canonical for hosting platforms, but Astro pages explain use, provenance, limitations, and release mapping. |
| API/CLI reference | Generated references are embedded or linked from Astro, never published as a separate docs shell. |

## Plugin decisions

| Plugin or integration | Default decision | Notes |
| --- | --- | --- |
| `@astrojs/starlight` | Required for docs sites | Use for all repo-owned docs portals. |
| `@astrojs/mdx` | Required | Enables richer documentation components and generated reference embedding. |
| `@astrojs/sitemap` | Required for public sites | Can be omitted only for private/internal unpublished previews. |
| Tailwind | Not default | Use Starlight theme CSS first. Add Tailwind only if a repo has a real component-heavy docs requirement. |
| React/Preact/Svelte/Vue | Not default | Avoid UI framework integrations unless interactive docs components justify them. |
| `@astrojs/partytown` | Not default | Only for third-party analytics/widgets after privacy review. |
| `@astrojs/rss` or RSS tooling | Conditional | Use only where docs publish changelogs/news feeds. |
| Search plugins beyond Starlight defaults | Conditional | Prefer Starlight default search unless corpus-scale docs require hosted search. |
| Markdown remark/rehype plugins | Conditional shared allowlist | Centralize any heading, link, citation, or table plugins in the shared style package/template. |
| Satteri Markdown processor | Evaluate later | Potential performance improvement, but not the first standard because remark/rehype compatibility is valuable during migration. |

## Repo-by-repo assessment

| Repo | Docs need | Baseline | Extra plugin needs | Migration notes |
| --- | --- | --- | --- | --- |
| `legal-nz` | Root orchestration docs, status, swarm and platform mapping | Starlight, MDX, Sitemap | None initially | Should become the aggregate docs portal and shared style source. |
| `cli-legislation-nz` | CLI, MCP, provider, install, command reference, release/submission docs | Starlight, MDX, Sitemap | TypeDoc as generator input only; possible generated command-reference component | Existing `docs` script uses TypeDoc. Keep TypeDoc for API generation, but publish through Astro/Starlight. |
| `corpus-law-nz` | Corpus pipeline, schema, data release, HF/Zenodo, CLI `nzlc` docs | Starlight, MDX, Sitemap | Schema/reference renderer; dataset card embedding | Use Astro pages for schema and release docs; generated JSON schema references can feed MDX. |
| `corpus-nz-hansard` | Hansard corpus, scripts, schemas, release ledger, source provenance | Starlight, MDX, Sitemap | Large schema/table rendering; possible search tuning | Script-heavy docs should be organized into Starlight sections before CLI consolidation. |
| `corpus-cases-medilegal-nz` | Private/gated corpus docs, config, governance, release posture | Starlight, MDX | Sitemap conditional if private-only | Needs privacy/rights callouts and gated-release templates. |
| `hathi-nz` | Historical source, HathiTrust fetch, rights, archive workflow | Starlight, MDX, Sitemap | Rights/source callouts | Keep docs lightweight until package CLI matures. |
| `nlp-policy-nz` | NLP framework, benchmarks, RAG, DigitalNZ probes, API/server docs | Starlight, MDX, Sitemap | OpenAPI/reference embedding if API docs are generated; possible interactive examples later | Avoid React/other UI integrations initially; add only if demos require islands. |
| `sm-govt-nz` | Social media source docs, platform terms, syndication, privacy/governance | Starlight, MDX, Sitemap | Privacy/platform callouts; changelog feed conditional | Strong governance and platform-terms pages required. |
| `fyi-cli` | Auxiliary CLI docs pending role decision | Starlight, MDX, Sitemap if promoted | Command-reference generator conditional | Audit exact entrypoints before adopting full site. |
| `dnz` | Unknown | None approved | None | Do not assess plugin needs until repo boundary is classified. |

## Shared implementation shape

Each docs-owning repo should converge on:

```text
docs/
  src/
    content/
      docs/
    styles/
      legal-nz.css
  astro.config.mjs
  package.json
```

Alternative for small repos:

```text
site/
  src/content/docs/
  astro.config.mjs
  package.json
```

Use one layout convention per repo; do not mix multiple docs app roots.

## Standard scripts

Every docs-owning repo should expose:

```json
{
  "scripts": {
    "docs:dev": "astro dev --root docs",
    "docs:build": "astro build --root docs",
    "docs:check": "astro check --root docs"
  }
}
```

If the repo uses `site/`, substitute `--root site`.

## Dependency policy

Use the latest stable Astro-compatible versions at implementation time and let Renovate maintain them. Pin only where CI reproducibility requires it.

Required dependency family:

- `astro`
- `@astrojs/starlight`
- `@astrojs/mdx`
- `@astrojs/sitemap`

Optional dependency family:

- `typedoc` for TypeScript API source generation.
- OpenAPI/schema reference generators only when their output is consumed by Astro.
- Remark/rehype plugins only from the shared allowlist once defined.

## Enforcement recommendations

1. Add a root docs-tooling check that flags non-Astro docs-site frameworks in package manifests.
2. Add a shared `astro-docs-standard` checklist to every docs migration PR.
3. Require `docs:build` in CI before claiming docs migration complete.
4. Require all generated API/CLI/schema reference docs to be linked from Starlight navigation.
5. Keep style customization in shared CSS/tokens, not per-repo bespoke themes.
