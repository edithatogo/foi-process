#!/usr/bin/env python3
"""Verify the Hugging Face dataset bundle and build deterministic Space data."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def table(bundle: Path, name: str) -> list[dict[str, Any]]:
    paths = sorted((bundle / "data" / name).glob("*.jsonl"))
    if not paths:
        raise ValueError(f"missing dataset table: {name}")
    return [row for path in paths for row in read_jsonl(path)]


def verify_manifest(bundle: Path) -> dict[str, Any]:
    manifest_path = bundle / "manifest.json"
    manifest = read_json(manifest_path)
    for entry in manifest["files"]:
        path = bundle / entry["path"]
        if not path.is_file():
            raise ValueError(f"manifest file is missing: {entry['path']}")
        actual = sha256(path)
        if actual != entry["sha256"]:
            raise ValueError(f"checksum mismatch for {entry['path']}: {actual}")
    return manifest


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build(bundle: Path, output: Path) -> None:
    manifest = verify_manifest(bundle)
    events = table(bundle, "event_log")
    revisions = table(bundle, "event_revisions")
    deltas = table(bundle, "evidence_deltas")
    edges = table(bundle, "process_edges")
    variants = table(bundle, "process_variants")
    findings = table(bundle, "conformance_findings")
    ocel_events = table(bundle, "ocel_events")
    ocel_objects = table(bundle, "ocel_objects")
    ocel_links = table(bundle, "ocel_event_object_links")

    events_by_case: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        events_by_case.setdefault(event["case_id"], []).append(event)

    cases = []
    edge_waits: dict[tuple[str, str], list[float]] = {}
    for case_id, case_events in sorted(events_by_case.items()):
        ordered = sorted(case_events, key=lambda row: (row["timestamp"], row["event_id"]))
        start = parse_time(ordered[0]["timestamp"])
        end = parse_time(ordered[-1]["timestamp"])
        for previous, current in zip(ordered, ordered[1:]):
            key = (previous["activity"], current["activity"])
            wait = (parse_time(current["timestamp"]) - parse_time(previous["timestamp"])).total_seconds()
            edge_waits.setdefault(key, []).append(wait)
        cases.append(
            {
                "case_id": case_id,
                "authority_id": ordered[0].get("authority_id"),
                "jurisdiction": ordered[0]["jurisdiction"],
                "site": ordered[0]["site"],
                "started_at": ordered[0]["timestamp"],
                "ended_at": ordered[-1]["timestamp"],
                "duration_seconds": (end - start).total_seconds(),
                "event_ids": [row["event_id"] for row in ordered],
                "activities": [row["activity"] for row in ordered],
            }
        )

    enriched_edges = []
    for edge in edges:
        waits = edge_waits.get((edge["source"], edge["target"]), [])
        enriched_edges.append(
            {
                **edge,
                "mean_wait_seconds": sum(waits) / len(waits) if waits else None,
            }
        )

    activity_counts = Counter(event["activity"] for event in events)
    output_value = {
        "meta": {
            "dataset_id": manifest["dataset_id"],
            "classification": manifest["classification"],
            "source_release": manifest["source_release"],
            "generated_at": manifest["generated_at"],
            "manifest_sha256": sha256(bundle / "manifest.json"),
        },
        "metrics": {
            "case_count": len(cases),
            "active_event_count": len(events),
            "activity_count": len(activity_counts),
            "variant_count": len(variants),
            "finding_count": len(findings),
        },
        "quality": {
            "manifest_file_count": len(manifest["files"]),
            "checksums_verified": True,
            "timestamp_coverage": sum(bool(event.get("timestamp")) for event in events) / len(events) if events else 0,
            "evidence_coverage": sum(event.get("evidence_count", 0) > 0 for event in events) / len(events) if events else 0,
            "reviewed_revision_count": sum(
                revision.get("privacy", {}).get("human_reviewed") is True for revision in revisions
            ),
            "revision_count": len(revisions),
            "delta_count": len(deltas),
            "ocel_object_count": len(ocel_objects),
            "ocel_link_count": len(ocel_links),
        },
        "activities": [
            {"activity": activity, "count": count}
            for activity, count in sorted(activity_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "events": events,
        "edges": enriched_edges,
        "variants": variants,
        "cases": cases,
        "findings": findings,
        "ocel": {"events": ocel_events, "objects": ocel_objects, "links": ocel_links},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes((json.dumps(output_value, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"built verified Space data at {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.bundle.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
