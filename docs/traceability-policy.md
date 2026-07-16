# Traceability and Reporting Granularity Policy

This policy applies to process-mining dashboards and public projections derived
from FOI records. It separates provenance traceability from public disclosure.

## Public source mode

The public dashboard may link to a source record only when the source is already
public, the link adds provenance value, and the link does not expose additional
personal or sensitive information through the process-mining projection.

The dashboard should default to system-level performance views. Exact event
timestamps and stable source identifiers may remain in the auditable data where
required for reproducibility, but should not be the default presentation for
mixed or sensitive populations.

Public outputs must:

- suppress or aggregate groups with fewer than six cases;
- prevent filter combinations from reconstructing suppressed cells;
- avoid requester and third-party identity, contact details, free text, OCR,
  embeddings, and inferred sensitive attributes;
- avoid joins with other datasets that could identify an individual;
- retain enough provenance to reproduce the published result.

The threshold is a conservative starting control and must be reviewed against
the population, geography, time period, and auxiliary information available to
the public. Stats NZ uses suppression for counts below six in sensitive tables.

## Confidential source mode

For non-public requests, the system may retain a separate internal traceability
mechanism. It must use a keyed pseudonymous case identifier, with the mapping
key held outside public repositories and dashboard assets. The pseudonym is not
an anonymisation claim and must not be published as a lookup key.

External views should default to aggregated metrics and process patterns. A
case-level timeline requires an explicit disclosure review and an authorised
access path.

## Governance basis

Public availability of a source does not by itself authorise unrestricted
amplification or cross-linking. The applicable privacy, licensing, tikanga,
data-sovereignty, security, and removal decisions remain separate gates in
`governance/publication_gate.json`.

References:

- [New Zealand Privacy Act Principle 11](https://www.privacy.org.nz/privacy-principles/11/)
- [Stats NZ confidentiality standard](https://www.stats.govt.nz/assets/Methods/2023-Census-methods/Methodological-standard-for-confidentiality-in-the-2023-Census.pdf)
