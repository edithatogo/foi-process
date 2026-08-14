#!/usr/bin/env python3
"""Build a deterministic, metadata-only NZ case inventory for T11 review."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from validate_bounded_real_release import DEFAULT_PACKAGE, sha256, validate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "conductor"
    / "tracks"
    / "jurisdiction_case_process_modelling_20260721"
    / "nz-bounded-case-inventory.json"
)


def rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build(package: Path = DEFAULT_PACKAGE) -> dict[str, Any]:
    manifest = validate(package)
    cases: dict[str, dict[str, Any]] = {}
    for event in rows(package / "event_log.jsonl"):
        case_id = event["logical_request_id"]
        case = cases.setdefault(
            case_id,
            {
                "case_id": case_id,
                "source_locator": event["provenance"]["capture_uri"],
                "event_count": 0,
                "attachment_count": 0,
                "first_event_at": event["timestamp"],
                "last_event_at": event["timestamp"],
                "activity_path": [],
                "observed_state_labels": [],
                "source_batches": [],
                "request_sequence": event["source_order"]["request_sequence"],
                "annotation_status": "pending_independent_adjudication",
                "promotion_boundary": "engineering_only",
            },
        )
        if case["source_locator"] != event["provenance"]["capture_uri"]:
            raise ValueError(f"case has inconsistent source locator: {case_id}")
        case["event_count"] += 1
        case["last_event_at"] = event["timestamp"]
        case["activity_path"].append(event["activity"])
        if event.get("state") and event["state"] not in case["observed_state_labels"]:
            case["observed_state_labels"].append(event["state"])
        source = event["source_order"]["source"]
        if source not in case["source_batches"]:
            case["source_batches"].append(source)

    attachment_types: dict[str, Counter[str]] = {case_id: Counter() for case_id in cases}
    for attachment in rows(package / "attachments.jsonl"):
        case_id = attachment["logical_request_id"]
        if case_id not in cases:
            raise ValueError(f"attachment references an unknown case: {case_id}")
        cases[case_id]["attachment_count"] += 1
        attachment_types[case_id][attachment["content_type"]] += 1

    ordered_cases = sorted(cases.values(), key=lambda case: (case["request_sequence"], case["case_id"]))
    for case in ordered_cases:
        case["attachment_content_types"] = dict(sorted(attachment_types[case["case_id"]].items()))

    return {
        "schema": "foi-process/jurisdiction-case-inventory/v1",
        "jurisdiction": "jurisdiction:NZ",
        "sampling_frame": {
            "method": "census_of_verified_bounded_release",
            "source_release": manifest["source_release"],
            "bounded_case_count": manifest["request_count"],
            "included_case_count": len(ordered_cases),
            "full_corpus": False,
            "representativeness_claim": "bounded_release_only",
        },
        "provenance": {
            "package_manifest_sha256": sha256(package / "manifest.json"),
            "event_log_sha256": sha256(package / "event_log.jsonl"),
            "attachments_sha256": sha256(package / "attachments.jsonl"),
            "source_run_ids": sorted({batch["evidence"]["source_run_id"] for batch in manifest["batches"]}),
        },
        "coverage": {
            "case_count": len(ordered_cases),
            "event_count": sum(case["event_count"] for case in ordered_cases),
            "attachment_count": sum(case["attachment_count"] for case in ordered_cases),
            "source_order_preserved": True,
        },
        "interpretation": {
            "activity_paths": "observed source metadata only",
            "state_labels": "unadjudicated native source labels; not legal or performance findings",
            "privacy": "metadata-only inventory; no correspondence or attachment bytes",
            "promotion_boundary": "engineering_only",
        },
        "cases": ordered_cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = (json.dumps(build(args.package), indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not args.output.is_file() or args.output.read_bytes().replace(b"\r\n", b"\n") != payload:
            raise SystemExit(f"jurisdiction case inventory is stale: {args.output}")
        print(f"jurisdiction case inventory reproducible: {args.output}")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
