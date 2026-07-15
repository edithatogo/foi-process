#!/usr/bin/env python3
"""Create a Zenodo deposition for a GitHub release and verify its DOI metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import urllib.request
from pathlib import Path


def request_json(url: str, token: str, *, method: str = "GET", payload: bytes | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=payload, method=method, headers=headers)
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=os.environ.get("ZENODO_TOKEN"), required=False)
    parser.add_argument("--release-tag", default="v0.1.0")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--api", default="https://zenodo.org/api")
    args = parser.parse_args()
    if not args.token:
        raise SystemExit("--token or ZENODO_TOKEN is required")

    with tempfile.TemporaryDirectory() as temp:
        archive = Path(temp) / f"foi-process-{args.release_tag}.tar.gz"
        url = f"https://github.com/edithatogo/foi-process/archive/refs/tags/{args.release_tag}.tar.gz"
        urllib.request.urlretrieve(url, archive)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        metadata = {
            "metadata": {
                "title": "FOI Process Workpack",
                "upload_type": "software",
                "description": "Release preservation for the FOI Process Workpack.",
                "creators": [{"name": "Mordaunt, Dylan A", "orcid": "0000-0002-9775-0603"}],
                "license": "Apache-2.0",
                "related_identifiers": [{"identifier": f"https://github.com/edithatogo/foi-process/releases/tag/{args.release_tag}", "relation": "isIdenticalTo", "scheme": "url"}],
            }
        }
        deposition = request_json(f"{args.api}/deposit/depositions", args.token, method="POST", payload=json.dumps(metadata).encode())
        deposition_id = str(deposition["id"])
        bucket = deposition["links"]["bucket"]
        upload = urllib.request.Request(f"{bucket}/foi-process-{args.release_tag}.tar.gz", data=archive.read_bytes(), method="PUT", headers={"Authorization": f"Bearer {args.token}", "Content-Type": "application/gzip"})
        with urllib.request.urlopen(upload) as response:
            uploaded = json.load(response)
        published = request_json(
            f"{args.api}/deposit/depositions/{deposition_id}/actions/publish",
            args.token,
            method="POST",
        )
        doi = published.get("doi")
        if not doi:
            raise RuntimeError("Zenodo publish response did not contain a DOI")
        evidence = {
            "release_tag": args.release_tag,
            "release_url": f"https://github.com/edithatogo/foi-process/releases/tag/{args.release_tag}",
            "deposition_id": deposition_id,
            "sha256": digest,
            "uploaded": uploaded,
            "doi": doi,
            "doi_url": published.get("links", {}).get("doi") or f"https://doi.org/{doi}",
            "status": "published",
        }
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
