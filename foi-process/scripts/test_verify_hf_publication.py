#!/usr/bin/env python3
"""Focused tests for Hugging Face publication verification."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from verify_hf_publication import (
    hf_download,
    require_same_file,
    verify_manifest,
    wait_for_space,
)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        bundle = Path(temp)
        content = b'{"event_id":"one"}\n'
        event_path = bundle / "data/event_log/demo.jsonl"
        event_path.parent.mkdir(parents=True)
        event_path.write_bytes(content)
        manifest = {
            "classification": "synthetic-fixture",
            "files": [
                {
                    "path": "data/event_log/demo.jsonl",
                    "byte_length": len(content),
                    "row_count": 1,
                    "sha256": digest(content),
                }
            ],
        }
        (bundle / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        assert verify_manifest(bundle) == manifest
        assert require_same_file(event_path, event_path, "fixture") == digest(content)

        event_path.write_bytes(content + b"{}\n")
        try:
            verify_manifest(bundle)
        except ValueError as error:
            assert "byte length differs" in str(error)
        else:
            raise AssertionError("modified publication unexpectedly passed verification")

        with patch("verify_hf_publication.subprocess.run") as run:
            hf_download("edithatogo/example", "dataset", bundle / "download")
        command = run.call_args.args[0]
        assert command[:4] == ["hf", "download", "edithatogo/example", "--repo-type"]
        assert command[4] == "dataset"

        with patch(
            "verify_hf_publication.hf_json",
            return_value={
                "runtime": {
                    "stage": "CONFIG_ERROR",
                    "errorMessage": "remote build requires credits",
                }
            },
        ):
            try:
                wait_for_space("edithatogo/example", 600)
            except ValueError as error:
                assert "CONFIG_ERROR" in str(error)
                assert "requires credits" in str(error)
            else:
                raise AssertionError("terminal Space stage did not fail immediately")

    print("Hugging Face publication verification: checksum and row-count failure paths verified")


if __name__ == "__main__":
    main()
