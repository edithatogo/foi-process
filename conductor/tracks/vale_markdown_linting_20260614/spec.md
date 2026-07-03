# Specification: Markdown & Prose Style Quality Gates

## Overview
This track elevates the Vale prose linter and Markdown styling rules to a workspace-wide standard. Currently, only `cli-legislation-nz` has a `.vale.ini` configuration. We will establish a global Vale configuration at the workspace root, include spelling dictionaries for legal NZ terms, and hook this linter into the local checks and CI pipeline to ensure documentation remains pristine.

## Scope & Features
1. **Global Vale Configuration:** Create a `.vale.ini` at the workspace root.
2. **Legal & NZ Vocabulary:** Establish a shared `Vocab` for terms like "Māori", "NZMJ", "Hansard", etc., to prevent false positive lint warnings.
3. **Markdown Format Standardization:** Implement markdownlint rules to check code block syntax, line endings, and heading structures.
4. **CI Integration:** Provide commands/scripts to run these checks in watch-mode and single-run CI modes.
