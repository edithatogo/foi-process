#!/usr/bin/env python3
"""Check that Rust-generated and portable schema surfaces remain aligned."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


NAMES = (
    "evidence-record",
    "evidence-delta",
    "process-event",
    "document-bundle",
    "document-signal",
    "normalized-bundle",
    "stream-checkpoint",
    "replay-snapshot",
    "conformance-trace",
    "human-review-record",
    "mining-run-manifest",
    "public-projection",
    "dashboard-summary",
    "ocel-projection",
)

INTENTIONAL_REQUIRED_DIFFERENCES = {"schema_version", "privacy"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rust", type=Path, required=True)
    parser.add_argument("--portable", type=Path, default=Path("schemas/portable"))
    args = parser.parse_args()
    differences = []
    for name in NAMES:
        rust = load(args.rust / f"{name}.schema.json")
        portable = load(args.portable / f"{name}.schema.json")
        rust_props = set(rust.get("properties", {}))
        portable_props = set(portable.get("properties", {}))
        missing = sorted(portable_props - rust_props)
        if missing:
            differences.append({"schema": name, "portable_properties_missing_in_rust": missing})
        for field in portable.get("required", []):
            if field not in rust.get("required", []):
                if field not in INTENTIONAL_REQUIRED_DIFFERENCES:
                    differences.append({"schema": name, "portable_required_missing_in_rust": field})
    if differences:
        print(json.dumps({"status": "drift", "differences": differences}, indent=2))
        return 1
    print(json.dumps({
        "status": "aligned_with_intentional_differences",
        "schemas": len(NAMES),
        "intentional_required_differences": sorted(INTENTIONAL_REQUIRED_DIFFERENCES),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
