# Quality Standards — legal-nz

> **Validator**: Quality_Validator (Antigravity Swarm — Root)
> **Last Review**: 2026-06-14
> **Status**: Active

---

## 1. Purpose

This document defines the quality framework for the **legal-nz** knowledge base and document management system. All contributions — code, content, and data — must adhere to these standards.

---

## 2. Quality Domains

### 2.1 Document Quality

| Criterion | Standard | Validation Method |
|-----------|----------|-------------------|
| Format | NZ law conventions (NZLC, NZLR, etc.) | Automated check |
| Citations | Must follow NZ legal citation style | Reference validator |
| Terminology | Aligned with Te Ture ā-Rohe / NZ Legal Glossary | Term linter |
| Metadata | All documents must have title, source, date, jurisdiction | Schema validation |
| Anonymisation | No PII or confidential info (unless authorised) | Regex scanner |

### 2.2 Code Quality

| Criterion | Standard | Validation Method |
|-----------|----------|-------------------|
| Linting | Pass ESLint / Ruff (whichever is configured) | CI pipeline |
| Formatting | Consistent with `.editorconfig` / project formatter | Pre-commit hook |
| Type Safety | TypeScript strict mode OR Python type annotations | Type checker |
| Test Coverage | ≥ 80% for core logic, ≥ 60% overall | Coverage reporter |
| API Contracts | OpenAPI / Zod schemas validated | Contract tests |

### 2.3 Data Quality

| Criterion | Standard | Validation Method |
|-----------|----------|-------------------|
| Schema | Adheres to defined JSON Schema / Avro schemas | Schema validation |
| Completeness | Required fields non-null, no missing refs | Integrity checks |
| Consistency | Values conform to controlled vocabularies | Lookup validation |
| Freshness | Data sources timestamped and within SLA | Staleness checks |

### 2.4 Repository Boundary & Code Ownership

To maintain a clean modular architecture, all code must respect repository boundaries:
- **Root Repository (legal-nz)**: Limited to orchestration, workflow templates, cross-repo mapping, workspace diagnostics, and global quality checks. No corpus processing, model training, scraping, or API implementation code is permitted at the root.
- **Subrepositories (Subprojects)**: All corpus collection, data normalization, database connections, API clients, and modeling experiments must reside within their respective subprojects (e.g., `corpus-law-nz`, `nlp-policy-nz`, `dnz`, `fyi-cli`). Subprojects must not import root-level files.

---

## 3. Quality Gates

### Gate 1 — Pre-Commit (Local)

- [ ] Files linted with no errors
- [ ] No secrets/credentials committed
- [ ] Document metadata is valid
- [ ] Unit tests pass for changed modules

### Gate 2 — Pull Request

- [ ] All pre-commit checks pass
- [ ] New code has ≥ 80% test coverage
- [ ] Legal citations verified against NZ citation DB
- [ ] No regression in existing tests
- [ ] At least one reviewer has approved

### Gate 3 — Release

- [ ] All PR gates pass
- [ ] Full test suite passes
- [ ] Coverage thresholds met
- [ ] Schema validation passes for all data artifacts
- [ ] All documents validated against legal standards

---

## 4. Validation Tooling

| Tool / Script | Purpose | Location |
|---------------|---------|----------|
| `lint` | Run linters across codebase | `npx eslint .` / `ruff check .` |
| `test` | Run test suite | Project-specific |
| `validate-docs` | Check document formatting/citations | `scripts/validate-documents.js` |
| `check-metadata` | Validate document metadata | `scripts/check-metadata.js` |
| `quality-report` | Generate quality summary | `scripts/quality-report.js` |

---

## 5. Enforcement

- **Automated**: CI pipeline runs all quality gates on push and PR
- **Manual**: Quality_Validator may flag issues and block PRs/RFEs
- **Audit**: Quarterly quality audit with full report

---

## 6. Exceptions

Exceptions to these standards must be documented in `QUALITY_EXCEPTIONS.md` and approved by Quality_Validator.

---

*This quality framework is part of the Antigravity Swarm governance model for legal-nz.*
