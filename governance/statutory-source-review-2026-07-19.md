# Statutory source review: OIA mapping

Status: `indicative_mapping_complete; legal_conformance_not_certified`

Reviewed 2026-07-19 against the current Official Information Act 1982 text and
current Ombudsman guidance. This review addresses the process-mining mapping
and its limits. It does not certify any agency's legal compliance or infer that
a captured platform state is a statutory decision.

## Sources

- New Zealand Legislation, Official Information Act 1982, current consolidated
  text: <https://www.legislation.govt.nz/act/public/2019/51/en/latest/DLM64784>
- Ombudsman, *The OIA for Ministers and agencies*: <https://www.ombudsman.parliament.nz/resources/oia-ministers-and-agencies-guide-processing-official-information-requests>
- Ombudsman, official information request timing guidance:
  <https://www.ombudsman.parliament.nz/what-ombudsman-can-help/requests-official-information/make-request-official-information>
- Ombudsman, official information calculators:
  <https://www.ombudsman.parliament.nz/agency-assistance/official-information-calculators>

## Mapping and boundary

| Source area | System mapping | Conformance boundary |
| --- | --- | --- |
| OIA ss 4-5 | Availability and purpose are context for reporting | The system must not score openness or legality from event counts. |
| OIA ss 12-13 | Request received and assistance activity candidates | A captured request page is evidence of an observed platform state, not proof that an agency received a valid request. |
| OIA s 14 | Transfer candidate and transfer timing fields | Transfer destination, authority, and statutory effect require source evidence and human review. |
| OIA ss 15-15A | Decision, communication, and extension candidates | Deadlines are indicative calculations unless receipt, working-day calendar, extension reason, and communication evidence are complete. |
| OIA ss 16-18B | Collation, deletion, refusal, consultation candidates | The model reports observed or candidate activities and never determines whether a refusal ground applies. |
| OIA s 19 | Reason-for-refusal evidence candidate | Reasons must be retained as source evidence and reviewed; an inferred activity is not a statutory reason. |
| OIA ss 20-23 | Publication, access, internal-rules, and reasons contexts | These provisions do not authorize republication of captured records or attachments by this project. |
| OIA ss 24-27 | Personal-information access, precautions, correction, refusal candidates | Personal information and corrections require a separate privacy and rights workflow. |
| OIA ss 28-35 | Ombudsman review and complaint context | The system may record a review or complaint event only when supported by evidence; it cannot predict or replace an Ombudsman decision. |

## Controls and decision

- The dashboard may label outputs `indicative`, `observed`, `candidate`, or
  `needs_review`; it must not use `OIA compliant`, `lawful`, or equivalent
  language without an external legal review.
- Working-day calculations require an explicit calendar and source timestamps;
  the default 20-working-day rule is not applied blindly to every record.
- LGOIMA is not silently substituted for OIA. The instance/jurisdiction and
  statutory regime must be recorded before applying any deadline profile.
- This review closes the statutory-source research gate for the current
  non-publication implementation. Production publication remains blocked.
