# Privacy classification profile

The public projection uses four independent fields:

- `sensitivity`: `public`, `personal`, `sensitive`, or `unknown`;
- `access_tier`: `public`, `restricted`, or `confidential`;
- `disposition`: `publish`, `publish_metadata_only`, `needs_review`, or `withhold`;
- `human_reviewed` and `reason_codes` for the decision record.

The fail-closed public rule is:

1. only `public` sensitivity and access may produce a published event;
2. `publish_metadata_only` emits no evidence links;
3. `needs_review` and `withhold` emit no event;
4. a published event linked to a non-public object is withheld;
5. evidence links are independently filtered by the same public criteria;
6. event attributes are restricted to the publication-policy allowlist.

Public source availability is evidence of access, not a publication decision.
OCR text, embeddings, extracted names, and attachment bytes remain outside the
public projection unless a separate reviewed projection explicitly permits
them.
