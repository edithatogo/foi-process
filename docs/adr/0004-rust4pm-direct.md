# ADR 0004: Direct Rust4PM integration

Status: accepted.

Depend directly on `process_mining` with default features disabled. Use its existing `AppendableOCEL` and mining algorithms. Maintain only FOI-specific adapters and live dashboard roll-ups locally; upstream generic improvements.
