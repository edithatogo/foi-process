# Threat model: non-publication production path

Status: `technical_controls_reviewed; publication_blocked`

| Threat | Control | Residual decision |
| --- | --- | --- |
| Raw attachment or WARC leakage | Raw stores remain external; adapter verifies bytes without writing them to public outputs. | Production publication remains disabled. |
| Path traversal through attachment metadata | Canonical root check and fail-closed retriever. | Keep derived roots approved per run. |
| Requester or third-party re-identification | Recursive privacy projection, metadata-only defaults, small-cell suppression policy, no raw text/embeddings. | No real-data public projection. |
| Differencing across revisions | Revision-aware replay, state hashes, source ordering, and removal/takedown revision records. | Do not publish successive real snapshots. |
| Token or destination exfiltration | HF target allowlists, pinned token-bearing dependencies, no token values in logs. | Credentials remain external and no publication is performed. |
| Supply-chain compromise | Locked dependencies, CI clippy/test/audit policy, hosted CI as authoritative build. | Review dependency changes before release. |
| Statutory overclaim | Indicative activity labels and statutory-source mapping; no legal conformance label. | Legal certification remains external. |
| Removal failure | Private security advisory and data-removal issue channels, acknowledgement target, replacement-revision record. | Assign production incident owner before any publication. |

The threat model closes the technical non-publication review. It is not a
production release authorization and does not make source-derived data public.
