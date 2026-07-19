# T09 decision record

## Decision

Adopt a deterministic Python reference generator in foi-process for baseline, demand-surge, concept-drift and correction-stress workloads. Deposit active events, revision history, cases, daily metrics, summaries and OCEL links in the Hugging Face dataset bundle. Expose only summary and daily series in the Static Space.

## Rationale

- Standard-library generation keeps the fixture reproducible in CI and publication workflows.
- Explicit active and revision tables exercise the same latest-revision boundary as replay without claiming production data fidelity.
- Compact browser projections preserve the Space asset/data budget while the dataset remains analytically complete.
- Scenario-specific invariants are stronger than snapshot-only testing because they assert expected behavioural separation.

## Ownership

The generator incubates in foi-process. Kairos is a reference for simulation design, rulesandprocesses for adoption evidence, and Sourceright for review patterns. None becomes a runtime dependency. Promotion requires a named consumer, compatibility fixture, benchmark, privacy review and maintenance commitment.

## Safety

All generated records are synthetic and visibly marked. The scenarios do not certify legal compliance, forecast a real authority, establish causal effects or justify automated decisions. Real-data calibration remains gated by privacy, tikanga/data-governance and threat-model review.

## Verification

- scripts/test_synthetic_scenarios.py
- scripts/build_hf_dataset.py and manifest verification
- scripts/build_hf_space_data.py
- Space TypeScript build and asset budget
- GitHub Actions CI on the implementation branch

## External state

Repository implementation does not imply publication. Uploading the verified dataset requires the
HF_TOKEN repository secret; dashboard hosting uses the free GitHub Pages workflow and does not
require Hugging Face Space activation, credits, or a paid service.
