# ADR 0001: One integration crate

Status: accepted for export candidate.

Use one `foi-process` library/binary with modules and features. Do not publish microcrates until a module has a second independent consumer and a stable ownership boundary. This reduces maintenance while retaining clear module boundaries.
