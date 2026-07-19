#!/usr/bin/env python3
"""Run an fyi-archive backfill followed by a resumable live continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def annotate(source: Path, destination: Path, revision: int, previous: int | None,
             request_ids: set[int] | None, sequence_start: int) -> None:
    manifest = load(source)
    requests = [r for r in manifest["requests"]
                if request_ids is None or int(r["request_id"]) in request_ids]
    manifest["requests"] = requests
    manifest["meta"]["record_count"] = len(requests)
    manifest["meta"]["snapshot_revision"] = revision
    if previous is None:
        manifest["meta"].pop("previous_snapshot_revision", None)
    else:
        manifest["meta"]["previous_snapshot_revision"] = previous
    for offset, request in enumerate(requests):
        request["source_sequence"] = sequence_start + offset
    write(destination, manifest)


def run(binary: Path, *args: str) -> None:
    subprocess.run([str(binary), *args], check=True)


def outcomes(path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            status = str(json.loads(line)["status"])
            counts[status] = counts.get(status, 0) + 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("binary", "backfill-manifest", "backfill-derived-root",
                 "continuation-manifest", "continuation-derived-root", "changes",
                 "output-dir"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    for name in ("backfill-captured-at", "continuation-captured-at",
                 "backfill-processed-at", "continuation-processed-at"):
        parser.add_argument(f"--{name}", required=True)
    args = parser.parse_args()
    root = args.output_dir
    if root.exists() and any(root.iterdir()):
        raise SystemExit("output directory must be fresh")
    inputs, pipeline = root / "inputs", root / "pipeline"
    changes = load(args.changes)
    changed = {int(e["request_id"])
               for bucket in ("added", "updated") for e in changes.get(bucket, [])}
    if not changed:
        raise SystemExit("continuation changes contain no added or updated request rows")
    backfill_manifest, continuation_manifest = inputs / "backfill.json", inputs / "continuation.json"
    annotate(args.backfill_manifest, backfill_manifest, 1, None, None, 1)
    annotate(args.continuation_manifest, continuation_manifest, 2, 1, changed, 2)
    backfill_deltas, continuation_deltas = pipeline / "backfill.ndjson", pipeline / "continuation.ndjson"
    for manifest, derived, output, captured, report in (
        (backfill_manifest, args.backfill_derived_root, backfill_deltas,
         args.backfill_captured_at, pipeline / "backfill-attachments.json"),
        (continuation_manifest, args.continuation_derived_root, continuation_deltas,
         args.continuation_captured_at, pipeline / "continuation-attachments.json"),
    ):
        run(args.binary, "fyi-archive-derived-store-to-deltas", "--input", str(manifest),
            "--derived-root", str(derived), "--output", str(output), "--captured-at", captured,
            "--report", str(report))
    backfill_out, continuation_out = pipeline / "backfill", pipeline / "continuation"
    backfill_state, continuation_state = pipeline / "backfill-state.json", pipeline / "continuation-state.json"
    run(args.binary, "replay-stream", str(backfill_deltas), str(backfill_out),
        "--processed-at", args.backfill_processed_at, "--state-out", str(backfill_state))
    run(args.binary, "replay-stream", str(continuation_deltas), str(continuation_out),
        "--processed-at", args.continuation_processed_at, "--state-in", str(backfill_state),
        "--state-out", str(continuation_state))
    state = load(continuation_state)
    continuation_outcomes = outcomes(continuation_out / "outcomes.ndjson")
    if continuation_outcomes.get("accepted", 0) != len(changed) or continuation_outcomes.get("quarantined", 0):
        raise SystemExit(f"continuation was not fully accepted: {continuation_outcomes}")
    if not state["records"] or state["records"][0]["revision"] != 2:
        raise SystemExit("continuation snapshot did not advance logical record revision")
    if state["partitions"][0]["last_sequence"] != len(changed) + 1:
        raise SystemExit("continuation snapshot did not advance source sequence")
    evidence = {
        "schema": "foi-process/fyi-archive-production-continuation/v1",
        "status": "verified", "changed_request_ids": sorted(changed),
        "backfill": {"delta_sha256": digest(backfill_deltas), "delta_count": len(backfill_deltas.read_text(encoding="utf-8").splitlines()),
                      "attachment_report": load(pipeline / "backfill-attachments.json"), "outcomes": outcomes(backfill_out / "outcomes.ndjson")},
        "continuation": {"delta_sha256": digest(continuation_deltas), "delta_count": len(continuation_deltas.read_text(encoding="utf-8").splitlines()),
                          "attachment_report": load(pipeline / "continuation-attachments.json"), "outcomes": continuation_outcomes,
                          "snapshot_id": state["snapshot_id"], "state_hash": state["state_hash"]},
    }
    write(root / "evidence.json", evidence)
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
