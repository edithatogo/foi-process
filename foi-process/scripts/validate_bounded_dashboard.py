#!/usr/bin/env python3
"""Build and validate a dashboard projection from a bounded real release."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def build(release: Path, output: Path) -> None:
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in (release / "event_log.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    cases: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        cases[event["logical_request_id"]].append(event)
    activities = Counter(event["activity"] for event in events)
    edges = Counter()
    for case_events in cases.values():
        ordered = sorted(case_events, key=lambda e: (e["timestamp"], e["event_id"]))
        edges.update((a["activity"], b["activity"]) for a, b in zip(ordered, ordered[1:]))
    dashboard = {
        "meta": {
            "dataset_id": manifest["dataset_id"],
            "classification": manifest["classification"],
            "source_release": manifest["source_release"],
            "scope": manifest["scope"],
            "manifest_sha256": sha256(release / "manifest.json"),
            "event_log_sha256": sha256(release / "event_log.jsonl"),
        },
        "metrics": {
            "case_count": len(cases),
            "active_event_count": len(events),
            "activity_count": len(activities),
            "attachment_count": manifest["attachment_count"],
            "batch_count": manifest["batch_count"],
        },
        "activities": [{"activity": k, "count": v} for k, v in sorted(activities.items())],
        "edges": [{"source": a, "target": b, "count": n} for (a, b), n in sorted(edges.items())],
        "cases": [{"case_id": key, "event_count": len(value)} for key, value in sorted(cases.items())],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dashboard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert dashboard["meta"]["classification"] == "public-derived-bounded"
    assert dashboard["meta"]["scope"] != "full corpus"
    assert dashboard["metrics"]["case_count"] == manifest["request_count"]
    assert dashboard["metrics"]["active_event_count"] == manifest["event_count"]
    assert dashboard["metrics"]["attachment_count"] == manifest["attachment_count"]
    assert len(dashboard["meta"]["manifest_sha256"]) == 64
    print(f"validated bounded dashboard: {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.release.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
