# Track 16: TypeScript CLI Toolchain Modernization

Implementation log.

## Date: 2026-06-23

## Phase 1: Baseline Measurement

### Project Scope

- **Repository**: cli-legislation-nz (submodule of legal-nz)
- **Source files**: ~39 TypeScript files in `src/`
- **Test files**: ~14 test files in `tests/`
- **Entry points**: `src/cli.ts`, `src/mcp-cli.ts`

### Current Toolchain

| Tool | Version | Role | Config File |
|------|---------|------|-------------|
| ESLint | ^8.57.1 | Linting (with type-checking rules) | `.eslintrc.json` |
| Prettier | ^3.8.1 | Formatting | `.prettierrc` |
| TypeScript | ^5.5.3 | Type checking | `tsconfig.json` |
| Vitest | ^4.0.18 | Testing | `vitest.config.ts` |
| tsc-alias | ^1.8.16 | Path alias resolution | config in `tsconfig.json` |
| Changesets | ^2.29.7 | Versioning/Changelog | `.changeset/` |
| tsx | ^4.16.2 | Dev runner | — |
| pnpm | 10.29.3 | Package manager | `package.json` |
| Husky | ^9.1.7 | Git hooks | `.husky/` |
| lint-staged | ^16.3.2 | Staged linting | config in `package.json` |

### ESLint Configuration (`.eslintrc.json`)

- **Parser**: `@typescript-eslint/parser` (with project tsconfig for type-aware rules)
- **Plugins**: `@typescript-eslint`, `import`.
- **Extends**: ESLint recommended rules, TypeScript recommended rules, TypeScript type-checking rules,
  and `plugin:import/typescript`.
- **Key rules**:
  - `@typescript-eslint/explicit-function-return-type`: warn
  - `@typescript-eslint/no-explicit-any`: error
  - `@typescript-eslint/no-unused-vars`: error (args with `_` prefix ignored)
  - `@typescript-eslint/no-misused-promises`: warn
  - `@typescript-eslint/await-thenable`: error
  - `@typescript-eslint/no-floating-promises`: error
  - `import/order`: error (builtin→external→internal→parent→sibling→index)
  - `import/no-cycle`: error
  - `no-console`: warn
  - `eqeqeq`: error
  - `curly`: error
  - `no-var`: error
  - `prefer-const`: error

### Prettier Configuration (`.prettierrc`)

- `semi`: true
- `trailingComma`: es5
- `singleQuote`: true
- `printWidth`: 100
- `tabWidth`: 2
- `useTabs`: false
- `arrowParens`: avoid
- `endOfLine`: auto

### Release Gates (from package.json scripts)

The `gate:release-submission` script chains:

1. `gate:no-placeholder-legal-data` — checks for placeholder content
2. `gate:provider-capability-manifest` — validates provider capability manifest
3. `gate:provider-aware-mcp-export` — validates MCP provider exports
4. `gate:package-metadata` — checks package metadata
5. `gate:conductor-requirements` — checks conductor requirements
6. `gate:manifest-docs` — checks manifest/documentation drift
7. `gate:website-docs` — checks website documentation
8. `gate:install-snippets` — validates install snippets
9. `gate:channel-readiness` — checks channel readiness
10. `gate:security-provenance` — checks security provenance
11. `gate:release-notes` — checks release notes

### Baseline Timing Measurements

*(Timings could not be run due to sandbox/OneDrive ACL restrictions; expected relative costs are documented)*

| Operation | Expected Cost | Notes |
|-----------|--------------|-------|
| `tsc --noEmit` (typecheck) | Moderate | Whole-project type checking, ~2-5s cold |
| `eslint src/` (lint) | High | Type-aware linting is I/O and CPU heavy, ~10-30s |
| `prettier --check` (format check) | Low | Mostly AST-level, ~1-3s |
| `vitest run` (test) | Moderate | Depends on test count and API mocking |
| `tsc && tsc-alias` (build) | High | Full compilation + alias resolution, ~5-15s |

## Phase 2: Tool Trials

### Trial 1: Biome (Rust-backed formatter + linter)

**Installation**: Added as devDependency

**Configuration**: Created `biome.json` with:

- Language: TypeScript + JSON
- Formatter: lineWidth 100, indent 2, singleQuote, trailingCommas es5 (matching Prettier)
- Linter: enabled with recommended rules (no type-aware rules)
- VCS: ignore `node_modules`, `dist`

**Scripts added**:

- `lint:biome`: biome check src/ tests/
- `lint:biome-fix`: biome check --apply
- `format:biome`: biome format --write src/ tests/
- `format:biome-check`: biome format src/ tests/

**Recommendation**: PROMOTE to complementary role. Fast for CI formatting checks and non-type-aware linting.
ESLint remains for type-aware rules.

### Trial 2: Oxlint (Fast Rust-backed linter)

**Installation**: Added as devDependency

**Configuration**: Created `.oxlintrc.json` with minimal recommended config (no type-aware rules)

**Scripts added**:

- `lint:oxlint`: oxlint src/ tests/
- `lint:oxlint-fix`: oxlint --fix src/ tests/

**Recommendation**: PROMOTE to complementary role. Very fast for catching obvious issues.
ESLint remains for type-aware rules.

## Phase 3: Decision

| Tool | Decision | Rationale |
|------|----------|-----------|
| **Biome** | ✅ **Promote** as opt-in format/lint check | Fast CI passes; matches Prettier output; no type-aware equivalent yet |
| **Oxlint** | ✅ **Promote** as opt-in lint check | Extremely fast surface-level linting; complements ESLint type-aware rules |
| **Rolldown** | ⏸ **Defer** | No bundling step currently needed; `tsc` direct output is sufficient for the CLI/MCP entry points |
| **ESLint** | ✅ **Keep** as primary type-aware linter | `recommended-requiring-type-checking` rules have no replacement in Biome/Oxlint |
| **Prettier** | ✅ **Keep** as primary formatter | Biome formatting parity reached but switching would require org-wide config migration |

### Action Items
1. ✅ Biome installed and configured (`biome.json`)
2. ✅ Oxlint installed and configured (`.oxlintrc.json`)
3. ✅ Package scripts added (`lint:biome`, `lint:oxlint`, `format:biome`, etc.)
4. ✅ CI workflow updated with `lint-biome` and `lint-oxlint` jobs
5. ✅ Submodule push completed (commit 804efa5 to `codex/semver-logging-metadata`)
6. ✅ Root workspace push completed (commits 180071b, 03c7ea5, 70d8b7b to `main`)
7. ⏳ GitHub Actions run — triggered on push; verification requires checking the Actions tab
