# Incremental jurisdiction FOI case and process modelling

Issue: [foi-process #39](https://github.com/edithatogo/foi-process/issues/39). Programme: [foi-o #81](https://github.com/edithatogo/foi-o/issues/81).

For every roadmap target, incrementally model representative FOI cases and process paths from immutable archive inputs and reviewed legislation/Gazette/case candidates. Bind every event, rule and outcome to jurisdiction/profile, source, temporal scope, extractor/ontology version, annotation status and uncertainty. Maintain Markdown/Mermaid and BPMN 2.0 representations for each workflow contract.

Observed platform behavior is not law. Case samples cannot certify completeness or legal outcomes, and profile promotion and publication remain human gates.

Issue [#96](https://github.com/edithatogo/foi-process/issues/96) adds a
jurisdiction-neutral Australian state template. It is synthetic-only and
requires exact profile, source, effective-date, transformation, and ontology
pins. Its strict semantic contract separates observed events, deterministic
calculations, interpretive mappings, and human-only decisions; preserves
unresolved and unsupported states; and requires graph-equivalent Mermaid and
BPMN 2.0 representations with rejection and remediation paths.

## Acceptance

- Each target has a documented sampling frame, positive/negative examples and representative process/case model, or an explicit evidence blocker.
- Models pass schema, deterministic replay, cross-profile isolation and independent annotation/oracle checks.
- Markdown/Mermaid and BPMN representations remain paired and validated.
- Strict template profiles pass node, semantic-kind, sequence-flow, gateway,
  branch-label, reachability, rejection, remediation-loop, pin, temporal, and
  non-equivalence validation.
