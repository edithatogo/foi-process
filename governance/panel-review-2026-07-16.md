# Historical independent panel rerun

Superseded for current non-publication status by
`governance/panel-review-2026-07-19.md`; retained as an audit record.

The panel was rerun against integrity-hardening commit `ace8320` on 2026-07-16. It was an
independent agent review, not a substitute for a named human statutory, tikanga, privacy, or
licensing approver.

| Reviewer | Focus | Outcome |
| --- | --- | --- |
| Ohm | Privacy and public-output minimisation | Synthetic-only publication remains acceptable; production data remains blocked. |
| Erdos | Data governance, archive provenance and licensing | Snapshot, digest and provenance controls are documented; source-specific production rights remain pending. |
| Kepler | Security and token-bearing workflows | HF destinations are allowlisted, publication client is pinned, and production threat-model sign-off remains pending. |
| Mendel | Technical contracts and replay | Activity-independent logical identity, snapshot revisions, attachment verification, filesystem retriever bridge, and source ordering are covered by tests. |
| Wegener | Operations and takedown | Removal/correction channels and five-business-day acknowledgement target are documented; owner contact remains the release responsibility. |

## Chair reconciliation

The synthetic release can proceed through the existing free GitHub Pages and Hugging Face paths.
The filesystem retriever bridge is implemented, but a live fyi-cli caller still needs to supply the
approved derived-store root and retrieval policy before real attachment publication is considered.
The production gate remains fail-closed because this single-person project has not produced a
separately signed human review record for real FOI-derived content, tikanga/data sovereignty,
source licensing, or final release authority. The formal rows in the review record therefore
document the bounded synthetic decision rather than falsely upgrading the production gate.
