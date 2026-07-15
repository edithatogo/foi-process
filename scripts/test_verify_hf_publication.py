#!/usr/bin/env python3
"""Focused tests for Hugging Face publication verification."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from verify_hf_publication import require_same_file, verify_manifest


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

    print("Hugging Face publication verification: checksum and row-count failure paths verified")


if __name__ == "__main__":
    main()
