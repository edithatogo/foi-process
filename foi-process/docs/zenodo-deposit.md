# Zenodo deposit package

The Zenodo-ready package is assembled from the verified release-evidence
directory. It contains the public event-log dataset manifest, mining-run
provenance, SBOM, benchmark evidence, sorted SHA-256 checksums, Croissant
metadata, and the draft DataCite payload.

The repository code is Apache-2.0. That licence does not replace the
source-declared rights for archived records, attachments, or derived data.
The deposit description must retain those rights and the removal/takedown
contact recorded in the release governance documentation.

## External gate

Local preparation and checksum verification do not constitute Zenodo
submission, acceptance, DOI assignment, or publication. Those actions require
explicit approval of the exact Zenodo target and action after review of the
final package and metadata.

## Commands (intentionally not executed here)

Prepare the package locally:

```powershell
python scripts/prepare_event_log_deposit.py --bundle .\verified-bundle --output .\deposit-package
```

For an explicitly approved Zenodo draft, upload only the reviewed contents of
`deposit-package` with a token supplied through the documented environment
variable. A generic API sequence is:

```powershell
curl.exe -H "Authorization: Bearer $env:ZENODO_TOKEN" -H "Content-Type: application/json" -d "@deposit-package/zenodo-metadata.json" https://zenodo.org/api/deposit/depositions
curl.exe -H "Authorization: Bearer $env:ZENODO_TOKEN" -F "file=@deposit-package/SHA256SUMS" https://zenodo.org/api/deposit/depositions/<deposit-id>/files
```

The DataCite payload is `datacite-metadata.json`; DOI registration is a
separate external action and must not be inferred from package preparation.
