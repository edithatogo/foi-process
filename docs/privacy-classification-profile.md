# Privacy classification profile

The public projection uses four independent fields:

- `sensitivity`: `public`, `personal`, `sensitive_personal`, `restricted`, or `unknown`;
- `access_tier`: `public`, `research`, `restricted`, or `embargoed`;
- `disposition`: `publish`, `publish_metadata_only`, `needs_review`, or `withhold`;
- `human_reviewed` and `reason_codes` for the decision record.

The fail-closed public rule is:

1. only human-reviewed `public` sensitivity and access with a `publish` disposition may produce a full published event;
2. human-reviewed `publish_metadata_only` emits event metadata but no evidence links;
3. `needs_review` and `withhold` emit no event;
4. a full published event linked to an object that is not reviewed and public is withheld;
5. evidence links are independently filtered by the same reviewed-public criteria;
6. event attributes are restricted to the publication-policy allowlist.

Public source availability is evidence of access, not a publication decision.
OCR text, embeddings, extracted names, and attachment bytes remain outside the
public projection unless a separate reviewed projection explicitly permits
them.
