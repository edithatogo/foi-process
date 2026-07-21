"""Validate jurisdiction fixture contracts without promoting them to evidence."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    path = ROOT / "examples" / "input" / "au-commonwealth-cases.ndjson"
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    labels = {case["sampling_label"] for case in cases}
    if labels != {"positive-path", "negative-path"}:
        raise SystemExit(f"expected positive and negative sampling paths, got {labels}")
    required = {
        "case_id", "jurisdiction", "source_manifest_sha256", "source_locator",
        "observed_at", "temporal_scope", "annotation_status", "uncertainty",
        "promotion_boundary", "activities",
    }
    for case in cases:
        missing = required - case.keys()
        if missing:
            raise SystemExit(f"{case.get('case_id')}: missing {sorted(missing)}")
        if case["annotation_status"] != "unreviewed" or case["promotion_boundary"] != "engineering_only":
            raise SystemExit(f"{case['case_id']}: fixture escaped its engineering-only boundary")
    print(f"validated {len(cases)} Australian Commonwealth engineering fixtures")


if __name__ == "__main__":
    main()
