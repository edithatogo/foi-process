#!/usr/bin/env python3
"""Regression tests for source-derived registry rights metadata."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import build_registry_metadata


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def make_bundle(root: Path, classification: str, review_status: str) -> Path:
    bundle = root / "bundle"
    rights_path = bundle / build_registry_metadata.SOURCE_RIGHTS_PATH
    write_json(
        rights_path,
        {
            "schema": "foi-process/source-rights/v1",
            "records": [
                {
                    "source_id": "urn:test:source",
                    "rights_basis": "public-source-access",
                    "redistribution_scope": "derived-only",
                    "review_status": review_status,
                }
            ],
        },
    )
    digest = hashlib.sha256(rights_path.read_bytes()).hexdigest()
    write_json(
        bundle / "manifest.json",
        {
            "dataset_id": "edithatogo/foi-process-event-logs",
            "classification": classification,
            "source_release": "v0.1.0",
            "generated_at": "2026-08-14T00:00:00Z",
            "files": [{"path": build_registry_metadata.SOURCE_RIGHTS_PATH, "sha256": digest}],
        },
    )
    return bundle


def test_synthetic_metadata_separates_code_and_data_rights(root: Path) -> None:
    bundle = make_bundle(root, "synthetic-fixture", "production_review_required")
    output = root / "registry"
    build_registry_metadata.build(bundle, output)
    croissant = json.loads((output / "croissant.json").read_text(encoding="utf-8"))
    datacite = json.loads((output / "datacite-draft.json").read_text(encoding="utf-8"))
    assert croissant["license"] == build_registry_metadata.SOURCE_RIGHTS_URI
    rights = datacite["data"]["attributes"]["rightsList"][0]
    assert rights["rightsUri"] == build_registry_metadata.SOURCE_RIGHTS_URI
    assert "only to repository code" in rights["rights"]


def test_production_metadata_fails_closed_without_review(root: Path) -> None:
    bundle = make_bundle(root, "public-derived-bounded", "production_review_required")
    try:
        build_registry_metadata.build(bundle, root / "registry")
    except ValueError as error:
        assert "requires reviewed source rights" in str(error)
    else:
        raise AssertionError("production-derived metadata accepted unreviewed source rights")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="foi-process-registry-rights-") as temporary:
        test_synthetic_metadata_separates_code_and_data_rights(Path(temporary) / "synthetic")
        test_production_metadata_fails_closed_without_review(Path(temporary) / "production")
    print("Registry rights metadata regression tests passed.")


if __name__ == "__main__":
    main()
