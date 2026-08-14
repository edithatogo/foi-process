# T06 acceptance decision

## Decision

The privacy-aware projection remains owned by `foi-process`. It is accepted as
the canonical integration projection used to produce bounded public event
metadata. It does not transfer legal semantics to `foi-process`, authorize
production publication, or make `foi-process` authoritative for source records.

## Acceptance evidence

- `src/publication.rs` applies a reviewed-public predicate to events, linked
  objects, and evidence.
- `tests/contracts.rs` covers unreviewed events, non-public linked objects,
  unreviewed evidence, metadata-only output, and attribute allowlisting.
- `docs/privacy-classification-profile.md` records the contract values and
  fail-closed behavior.
- `scripts/test_public_privacy.py` recursively validates generated public
  artifacts and rejects prohibited raw fields.

The projection is linear in the number of materialized events plus indexed
objects and evidence. Existing scale-suite evidence covers the shared replay
and projection input path; no separate performance threshold is needed for
this bounded filter.

## Promotion boundary

Propel and FOI-O remain named consumers and semantic collaborators. There is no
duplicate canonical implementation to remove from this repository. External
consumer adoption is tracked separately and is not asserted by this decision.
