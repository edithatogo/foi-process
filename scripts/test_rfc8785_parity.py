#!/usr/bin/env python3
"""Compare Rust content IDs with an independent RFC 8785 implementation."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import rfc8785


VECTORS = [
    {"b": 2, "a": 1},
    {"unicode": "Ångström", "escaped": "line\nfeed", "integer": 9007199254740991},
    {"nested": [{"z": True, "a": None}, {"value": -0.0}], "empty": {}},
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    args = parser.parse_args()
    namespace = "foi-process:rfc8785-parity"
    with tempfile.TemporaryDirectory(prefix="foi-process-jcs-") as directory:
        root = Path(directory)
        for index, value in enumerate(VECTORS):
            path = root / f"vector-{index}.json"
            path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
            canonical = bytes(rfc8785.dumps(value))
            expected = f"urn:{namespace}:sha256:{hashlib.sha256(canonical).hexdigest()}"
            actual = subprocess.check_output(
                [str(args.binary), "content-id", namespace, str(path)],
                text=True,
            ).strip()
            if actual != expected:
                raise SystemExit(
                    f"RFC 8785 parity failed for vector {index}: expected {expected}, got {actual}"
                )
    print(f"RFC 8785 parity passed: {len(VECTORS)} vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
