# ADR 0005: Publish the dashboard as a static analytical projection

Status: accepted.

## Context

The dashboard must expose process maps, variants, request timelines, conformance findings, and
provenance without creating a second mining engine or requiring a persistent hosted runtime. The
source Dataset is already a reviewed publication projection with deterministic checksums.

## Decision

Publish a React and ECharts Static Hugging Face Space. Generate one browser projection from the
verified Dataset bundle at build time, and keep process discovery, replay, privacy, and conformance
semantics in the existing Rust and publication layers.

The Space build must pass a checked asset budget: at most 800,000 uncompressed JavaScript bytes,
25,000 CSS bytes, and 100,000 bytes for the reviewed demonstration projection. Tooltips use the
canvas rich-text renderer rather than HTML.

## Consequences

- the dashboard works without Docker or Python compute allocation;
- the deposited event logs and the displayed metrics share one checksum-verified source;
- larger production datasets will need paged or pre-aggregated versioned projections rather than
  embedding an unbounded event log in the Space;
- live refresh and authenticated case access remain future, separately governed capabilities.
