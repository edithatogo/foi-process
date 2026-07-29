#!/usr/bin/env python3
"""Assemble verified real batches into a clearly bounded release bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build(batch_roots: list[Path], output: Path) -> None:
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    event_lines: list[str] = []
    attachment_lines: list[str] = []
    batch_evidence: list[dict[str, Any]] = []
    request_count = event_count = attachment_count = 0
    for root in batch_roots:
        evidence = next(root.glob("dist/nz-real-backfill-evidence.json"), None)
        coverage = next(root.glob("dist/process-events/projection/coverage.json"), None)
        events = next(root.glob("dist/process-events/events.jsonl"), None)
        attachments = next(root.glob("dist/process-events/attachments.jsonl"), None)
        if not all((evidence, coverage, events, attachments)):
            raise ValueError(f"incomplete batch artifact: {root}")
        c = read_json(coverage)
        if not (c["require_live_manifest"] and c["request_count_reconciles"] and c["attachment_count_reconciles"]):
            raise ValueError(f"parity gate failed: {root}")
        if read_json(evidence)["dry_run"]:
            raise ValueError(f"dry-run batch rejected: {root}")
        event_lines.extend(events.read_text(encoding="utf-8").splitlines())
        attachment_lines.extend(attachments.read_text(encoding="utf-8").splitlines())
        request_count += c["case_count"]
        event_count += c["event_count"]
        attachment_count += c["attachment_count"]
        batch_evidence.append({"coverage": c, "evidence": read_json(evidence)})

    (output / "event_log.jsonl").write_text("\n".join(event_lines) + "\n", encoding="utf-8")
    (output / "attachments.jsonl").write_text("\n".join(attachment_lines) + "\n", encoding="utf-8")
    release = {
        "schema": "foi-process.bounded-real-release.v1",
        "dataset_id": "edithatogo/foi-process-event-logs",
        "classification": "public-derived-bounded",
        "source_release": "nz-real-batches-150-200",
        "scope": "verified real batches only; not full corpus",
        "event_log_complete": False,
        "publication": "not-submitted",
        "code_license": "Apache-2.0",
        "source_rights": "retain source-declared rights; review before external deposit",
        "batch_count": len(batch_roots),
        "request_count": request_count,
        "event_count": event_count,
        "attachment_count": attachment_count,
        "batches": batch_evidence,
    }
    (output / "manifest.json").write_text(json.dumps(release, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = []
    for path in sorted(output.glob("*.json*")):
        if path.name == "manifest.json":
            continue
        files.append({"path": path.name, "sha256": digest(path), "byte_length": path.stat().st_size})
    release["files"] = files
    (output / "manifest.json").write_text(json.dumps(release, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "SHA256SUMS").write_text(
        "\n".join(f"{digest(p)}  {p.name}" for p in sorted(output.glob("*")) if p.is_file() and p.name != "SHA256SUMS") + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build([p.resolve() for p in args.batch], args.output.resolve())


if __name__ == "__main__":
    main()
