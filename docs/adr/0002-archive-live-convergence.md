# ADR 0002: Archive and live convergence

Status: accepted.

Represent archive snapshot observations as `EvidenceDelta` and feed them through the same normaliser/replay engine as live `fyi-cli` output. This makes backfill, replay, correction, and live monitoring comparable and reproducible.
