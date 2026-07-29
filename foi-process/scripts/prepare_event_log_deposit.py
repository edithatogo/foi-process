#!/usr/bin/env python3
"""Build a deterministic, non-publishing event-log deposit package.

The command only prepares and verifies a package. It never creates, uploads, or
publishes an external Zenodo or DataCite record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(bundle: Path) -> dict[str, Any]:
    path = bundle / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("classification") not in {
        "synthetic-fixture",
        "public-derived",
        "public-derived-bounded",
    }:
        raise ValueError("manifest classification must be explicit")
    if not manifest.get("source_release"):
        raise ValueError("manifest source_release is required")
    for entry in manifest.get("files", []):
        source = bundle / entry["path"]
        if not source.is_file() or sha256(source) != entry["sha256"]:
            raise ValueError(f"manifest verification failed: {entry['path']}")
    return manifest


def build(bundle: Path, output: Path, *, doi: str | None = None) -> None:
    manifest = load_manifest(bundle)
    if output.exists():
        raise FileExistsError(f"refusing to replace existing package: {output}")
    output.mkdir(parents=True)
    for entry in manifest["files"]:
        source = bundle / entry["path"]
        destination = output / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    package_manifest = {
        "schema": "foi-process.event-log-deposit.v1",
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "publication": "not-submitted",
        "classification": manifest["classification"],
        "dataset_id": manifest.get("dataset_id"),
        "source_release": manifest["source_release"],
        "source_rights": manifest.get("source_rights", "must be reviewed from source records"),
        "code_license": "Apache-2.0",
        "manifest_sha256": sha256(bundle / "manifest.json"),
        "event_log_complete": manifest.get("event_log_complete", False),
        "doi": doi,
    }
    (output / "deposit-manifest.json").write_text(
        json.dumps(package_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    zenodo = {
        "title": manifest.get("title", "FOI process event log"),
        "upload_type": "dataset",
        "description": "Versioned FOI process event log; publication remains externally gated.",
        "creators": [{"name": manifest.get("creator", "Edith Atogo")}],
        "license": manifest.get("data_license", "SEE_SOURCE_RIGHTS"),
        "keywords": ["freedom of information", "process mining", "event log"],
        "version": manifest["source_release"],
        "related_identifiers": ([{"identifier": doi, "relation": "isVersionOf"}] if doi else []),
    }
    datacite = {
        "data": {
            "type": "dois",
            "attributes": {
                "doi": doi,
                "publisher": "Zenodo",
                "publicationYear": datetime.now(timezone.utc).year,
                "types": {"resourceTypeGeneral": "Dataset"},
                "titles": [{"title": zenodo["title"]}],
                "version": manifest["source_release"],
                "descriptions": [{"description": zenodo["description"], "descriptionType": "Abstract"}],
            },
        }
    }
    (output / "zenodo-metadata.json").write_text(json.dumps(zenodo, indent=2) + "\n", encoding="utf-8")
    (output / "datacite-metadata.json").write_text(json.dumps(datacite, indent=2) + "\n", encoding="utf-8")

    checksums = []
    for path in sorted(p for p in output.rglob("*") if p.is_file() and p.name != "SHA256SUMS"):
        checksums.append(f"{sha256(path)}  {path.relative_to(output).as_posix()}")
    (output / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--doi")
    args = parser.parse_args()
    build(args.bundle.resolve(), args.output.resolve(), doi=args.doi)


if __name__ == "__main__":
    main()
