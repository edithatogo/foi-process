# Specification: Workspace Structure & Dataset Mapping

## Overview
This track focuses on creating a comprehensive catalog and data map of all subprojects in the workspace. Since the workspace consists of multiple disconnected repositories (`cli-legislation-nz`, `corpus-law-nz`, `corpus-nz-hansard`, etc.), we need to establish clean conventions for naming folders, files, and schemas, and map the upload pipelines to Hugging Face and Zenodo.

## Scope & Features
1. **Workspace Audit:** Catalog all project subdirectories, code file locations, entry points, and configurations.
2. **Schema Mapping:** Map and document all database and file schemas (Parquet columns, JSON Lines keys, CLI output formats).
3. **Naming & Folder Structure Plan:** Establish strict conventions for code files, test fixtures, dataset outputs, and documentation.
4. **Integration Map:** Outline Hugging Face datasets and Zenodo depositions used across the subprojects.
