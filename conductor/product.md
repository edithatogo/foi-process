# Product Guide - NZ Legislation and Policy Workspace

## Overarching Vision
This workspace is a comprehensive repository containing command-line tools, Model Context Protocol (MCP) servers, datasets, and pipelines designed to retrieve, clean, structure, and analyze New Zealand legislation, parliamentary debates (Hansard), and policy documents.

## Target Audience
The tools, datasets, and pipelines in this workspace are built for:
- **Legal Researchers and Academics:** Users analyzing legislative trends, tracing the evolution of acts, and examining case law.
- **Software Developers and AI Builders:** Engineers integrating legislative search via MCP or utilizing normalized datasets (Parquet format) for training, fine-tuning, or retrieving legal context.
- **Government, Policy, and Compliance Analysts:** Professionals tracking health/AI policies, regulatory shifts, and public sector developments.
- **General Public:** Anyone else interested in transparent, accessible, and structured New Zealand legal data.

## Workspace Subprojects
The workspace consists of several key subprojects:
- **cli-legislation-nz:** A command-line tool and MCP server for searching, retrieving, and citing NZ legislation.
- **corpus-law-nz:** A Python-based data pipeline that pulls official NZ legislation, normalizes it into Parquet shards, and uploads it to Hugging Face Datasets.
- **corpus-nz-hansard:** A parser and ingestion pipeline for NZ parliamentary debate transcripts.
- **nlp-policy-nz:** Natural Language Processing tools and models for policy analysis.
- **sm-govt-nz:** Agents and parsers for official and social media government channels.

## Core Features
1. **Accurate Retrieval & Citation:** Instantly search official NZ legislation and export bibliographic citations (NZMJ, APA, BibTeX).
2. **Normalized Data Pipelines:** Convert raw API outputs and XML formats into structured Parquet and JSON Lines datasets.
3. **Idempotence & Provenance:** Safe-to-run pipelines that compare checksums to minimize upload churn and ensure full data provenance.
4. **AI-Ready Interfaces:** Native Model Context Protocol (MCP) servers enabling LLM agents to call tools and query local data.
