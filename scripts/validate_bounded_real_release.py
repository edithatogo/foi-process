#!/usr/bin/env python3
"""Validate the checked-in bounded real release without retaining source bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "data" / "bounded-real-release-150-200"


def canonical_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(canonical_bytes(path)).hexdigest()


def ndjson(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def verify_order(rows: list[dict[str, Any]], sequence_field: str) -> None:
    previous: tuple[str, int, int] | None = None
    for row in rows:
        order = row["source_order"]
        current = (str(order["source"]), int(order["request_sequence"]), int(order[sequence_field]))
        if previous is not None and current < previous:
            raise ValueError(f"source order regressed from {previous!r} to {current!r}")
        previous = current


def validate(package: Path = DEFAULT_PACKAGE) -> dict[str, Any]:
    expected: dict[str, str] = {}
    for line in (package / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        expected[name] = digest
    package_files = {path.name for path in package.iterdir() if path.is_file()} - {"SHA256SUMS"}
    if set(expected) != package_files:
        raise ValueError("SHA256SUMS must cover every package file exactly once")
    for name, digest in expected.items():
        if sha256(package / name) != digest:
            raise ValueError(f"SHA256SUMS mismatch for {name}")

    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    if manifest["classification"] != "public-derived-bounded" or manifest["event_log_complete"] is not False:
        raise ValueError("package must remain bounded and must not claim full-corpus completeness")
    descriptors = {entry["path"]: entry for entry in manifest["files"]}
    for name in ("event_log.jsonl", "attachments.jsonl"):
        path = package / name
        descriptor = descriptors[name]
        if descriptor["sha256"] != sha256(path) or descriptor["byte_length"] != len(canonical_bytes(path)):
            raise ValueError(f"manifest descriptor mismatch for {name}")

    events = ndjson(package / "event_log.jsonl")
    attachments = ndjson(package / "attachments.jsonl")
    verify_order(events, "event_sequence")
    verify_order(attachments, "attachment_sequence")
    observed = (len({row["logical_request_id"] for row in events}), len(events), len(attachments))
    declared = (manifest["request_count"], manifest["event_count"], manifest["attachment_count"])
    if observed != declared:
        raise ValueError(f"package counts do not reconcile: observed={observed}, declared={declared}")
    dashboard = json.loads((package / "dashboard.json").read_text(encoding="utf-8"))
    if dashboard["meta"]["manifest_sha256"] != sha256(package / "manifest.json"):
        raise ValueError("dashboard manifest digest does not match canonical manifest bytes")
    if dashboard["meta"]["event_log_sha256"] != sha256(package / "event_log.jsonl"):
        raise ValueError("dashboard event-log digest does not match canonical event bytes")
    dashboard_counts = (
        dashboard["metrics"]["case_count"],
        dashboard["metrics"]["active_event_count"],
        dashboard["metrics"]["attachment_count"],
    )
    if dashboard_counts != declared:
        raise ValueError("dashboard counts do not reconcile with the release manifest")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path, nargs="?", default=DEFAULT_PACKAGE)
    args = parser.parse_args()
    manifest = validate(args.package)
    print(
        "bounded real release valid: "
        f"{manifest['request_count']} cases, {manifest['event_count']} events, "
        f"{manifest['attachment_count']} attachments"
    )


if __name__ == "__main__":
    main()
