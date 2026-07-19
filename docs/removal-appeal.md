# Removal and takedown workflow

This repository publishes reviewed synthetic fixtures. The same workflow is
ready for a future restricted or public export, but production publication
remains disabled and no raw source material is currently published here.

## Contact channels

- **Privacy/security or urgent exposure:** open a private GitHub Security Advisory at
  <https://github.com/edithatogo/foi-process/security/advisories/new>. Do not include personal data
  in a public issue.
- **Non-sensitive correction or removal request:** use the repository's
  [data-removal issue form](https://github.com/edithatogo/foi-process/issues/new?template=data-removal.yml).

The repository owner acknowledges requests within five business days. An apparent privacy or
security exposure is treated as urgent: pause the affected export, preserve revision and digest
evidence privately, assess scope, remove or quarantine affected projections, and issue a corrected
or withdrawn revision only after review.

## Operator procedure

1. Record the request identifier, received time, affected platform/path, and
   requested action in a private working record.
2. Freeze the affected export and identify every derived projection, mirror,
   dashboard build, and checksum that contains the affected identifier.
3. Re-run recursive privacy validation and mark the affected source/revision as
   withheld pending decision.
4. Remove or replace the affected public projection, preserve the old digest
   privately, and record the replacement revision/digest.
5. Notify the requester through the channel used for the request where
   appropriate, then record decision, operator, action, and closure time.
6. Reopen publication only for a newly reviewed revision; never silently mutate
   an existing public artifact.

The public operational contact details are the private GitHub Security Advisory channel and the
data-removal issue form above. The accountable owner must designate an incident owner in the
production release record before enabling real-data publication; this repository does not invent a
personal email address.

Record the request identifier, affected public URL or dataset path, received time, decision,
operator, action taken, replacement revision/digest if applicable, and closure time. Do not place
requester personal information or raw correspondence in the public log.
