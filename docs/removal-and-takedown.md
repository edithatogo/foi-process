# Removal and takedown workflow

This repository treats a removal request as a data-governance input, not as a
silent history rewrite. The request must be recorded, evaluated, and applied
to every derived output that can expose the affected stable identifier.

## Contact

Send a request to `edithatogo@users.noreply.github.com` or open a private
security/contact channel through the repository owner. Do not put personal
documents or private correspondence in a public GitHub issue.

Include the source instance, public URL or stable request identifier, the
requested scope, the basis for removal, and a safe reply address. A source
operator may also contact the archive through the descriptive User-Agent used
by the capture tooling.

## Processing

1. Record an internal case containing the request, received time, scope,
   decision, reviewer, and evidence. Keep the record access-controlled when it
   contains personal information.
2. Add the stable case or event identifier to the takedown JSONL input used by
   `fyi-archive process project --takedown`. The projection excludes matching
   events and attachments and records the exclusion in `coverage.json`.
3. Rebuild the derived Parquet, event-log, OCEL, dashboard, and search/index
   projections. Takedown propagation must remove descendants, not only the
   directly named row.
4. Verify checksums and confirm that the removed identifier is absent from all
   public-output files before replacing any mirror revision.
5. Record the decision, output revision, verification digest, and any mirror
   replacement or cache-expiry action in the governance ledger.

The immutable raw archive is not overwritten by this workflow. Raw retention,
source removal, legal preservation, and mirror replacement are separate
decisions recorded with their applicable rights and governance basis.
