# Rust4PM integration

Rust4PM 0.6 already provides `AppendableOCEL`, so v3 directly implements a generic `append_materialized_snapshot<T: AppendableOCEL>` adapter. It declares types first, then objects, then events, avoiding implementation-defined misordered-input behaviour.

The remaining upstream candidates are narrower:

1. documented duplicate and re-declaration semantics;
2. durable/transactional append targets and checkpoint metadata;
3. delta/retraction conventions for evolving OCEL logs;
4. streaming DFG/OC-DFG and revision-aware incremental conformance;
5. mergeable process summaries and drift windows;
6. benchmarks using FOI-scale, object-rich logs;
7. Propel-compatible typed artefact handles where generic.

Do not upstream FOI vocabulary, legal deadlines, privacy decisions, or Alaveteli mappings.

The current adapter is intentionally reduced to the stable `AppendableOCEL` surface: it emits
latest active events, object declarations, object/event identifiers, timestamps, and relationships.
FOI attributes, object properties, evidence, privacy decisions, and revision/retraction semantics
remain in the normalized/public contracts. They are not silently treated as Rust4PM attributes
until the upstream attribute API is stable.
