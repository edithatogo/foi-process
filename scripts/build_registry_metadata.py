"""Build deterministic registry metadata from a generated dataset bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(bundle: Path, output: Path) -> None:
    manifest_path = bundle / "manifest.json"
    manifest = read_json(manifest_path)
    manifest_digest = sha256(manifest_path)
    files = manifest["files"]
    data_files = [item for item in files if item["path"].startswith("data/")]

    croissant = {
        "@context": {
            "@vocab": "https://schema.org/",
            "cr": "http://mlcommons.org/croissant/",
        },
        "@type": "Dataset",
        "name": manifest["dataset_id"],
        "description": "Public-safe FOI process event logs and reproducibility artefacts.",
        "version": manifest["source_release"],
        "license": "https://spdx.org/licenses/Apache-2.0.html",
        "distribution": [
            {
                "@type": "DataDownload",
                "contentUrl": f"data/{item['path'].split('/', 2)[1]}/{item['path'].split('/', 2)[2]}",
                "encodingFormat": "application/jsonl",
                "contentSize": item["byte_length"],
                "sha256": item["sha256"],
            }
            for item in data_files
        ],
        "cr:manifestSha256": manifest_digest,
        "cr:recordSet": [
            {
                "@type": "cr:RecordSet",
                "name": item["path"].removeprefix("data/").removesuffix("/demo-00000-of-00001.jsonl"),
                "cr:source": {"fileObject": item["path"]},
            }
            for item in data_files
        ],
    }
    datacite = {
        "data": {
            "type": "dois",
            "attributes": {
                "doi": "",
                "event": "draft",
                "titles": [{"title": "FOI Process Event Logs"}],
                "publisher": "foi-process",
                "publicationYear": int(manifest["generated_at"][:4]),
                "types": {"resourceTypeGeneral": "Dataset"},
                "descriptions": [
                    {
                        "description": "Versioned public-safe event logs with provenance, schemas, and checksums.",
                        "descriptionType": "Abstract",
                    }
                ],
                "url": "https://huggingface.co/datasets/edithatogo/foi-process-event-logs",
                "relatedIdentifiers": [
                    {
                        "relatedIdentifier": "https://github.com/edithatogo/foi-process",
                        "relationType": "IsIdenticalTo",
                        "relatedIdentifierType": "URL",
                    }
                ],
                "sizes": [f"{len(files)} files"],
                "formats": ["application/jsonl", "application/json"],
                "version": manifest["source_release"],
                "rightsList": [{"rights": "Apache-2.0 (code); source-declared rights apply to data"}],
                "subjects": [{"subject": "process mining"}, {"subject": "freedom of information"}],
                "fundingReferences": [],
                "isReferencedBy": [{"value": f"manifest-sha256:{manifest_digest}", "valueType": "ARK"}],
            },
        }
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "croissant.json").write_text(json.dumps(croissant, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "datacite-draft.json").write_text(json.dumps(datacite, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.bundle.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
