#!/usr/bin/env python3
"""Validate lifecycle, paths, plans, and metadata in the Conductor registry."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = {"id", "slug", "status", "maturity", "owner", "track"}
ALLOWED_STATUSES = {"active", "deferred", "completed"}
ACTIVE_METADATA = {"active", "in_progress"}
COMPLETED_METADATA = {"completed", "acceptance_verified"}


def parse_registry(path: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line or line == "tracks:":
            continue
        match = re.fullmatch(r"- id: (T[0-9]{2})", line)
        if match:
            current = {"id": match.group(1)}
            records.append(current)
            continue
        match = re.fullmatch(r"  ([a-z_]+): (\S.*)", line)
        if not match or current is None:
            raise ValueError(f"unsupported registry syntax at {path}:{line_number}: {line!r}")
        key, value = match.groups()
        if key in current:
            raise ValueError(f"duplicate field {key!r} for {current['id']}")
        current[key] = value
    return records


def checkbox_counts(path: Path) -> tuple[int, int, int]:
    text = path.read_text(encoding="utf-8")
    completed = len(re.findall(r"(?m)^\s*- \[[xX]\] ", text))
    in_progress = len(re.findall(r"(?m)^\s*- \[~\] ", text))
    pending = len(re.findall(r"(?m)^\s*- \[ \] ", text))
    return completed, in_progress, pending


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    registry_path = root / "conductor" / "tracks.yaml"
    try:
        records = parse_registry(registry_path)
    except ValueError as error:
        return [str(error)]

    ids = [record["id"] for record in records]
    expected_ids = [f"T{number:02d}" for number in range(14)]
    if ids != expected_ids:
        errors.append(f"track IDs must be ordered T00..T13, got {ids}")
    if len(ids) != len(set(ids)):
        errors.append("track IDs must be unique")

    registry_markdown = (root / "conductor" / "tracks.md").read_text(encoding="utf-8")
    markdown_ids = re.findall(r"\*\*(T[0-9]{2})\*\*", registry_markdown)
    if sorted(markdown_ids) != sorted(ids):
        errors.append(f"tracks.md IDs differ from tracks.yaml: {markdown_ids} != {ids}")

    for record in records:
        missing = sorted(REQUIRED_FIELDS - record.keys())
        if missing:
            errors.append(f"{record['id']} is missing fields: {', '.join(missing)}")
            continue
        status = record["status"]
        if status not in ALLOWED_STATUSES:
            errors.append(f"{record['id']} has unsupported lifecycle status {status!r}")

        track_dir = root / "conductor" / "tracks" / record["track"]
        for filename in ("spec.md", "plan.md"):
            if not (track_dir / filename).is_file():
                errors.append(f"{record['id']} is missing {track_dir / filename}")
        expected_link = f"./tracks/{record['track']}/"
        if expected_link not in registry_markdown:
            errors.append(f"tracks.md is missing {record['id']} link {expected_link}")

        marker = "[x]" if status == "completed" else "[ ]"
        if f"- {marker} **{record['id']}**" not in registry_markdown:
            errors.append(f"tracks.md lifecycle marker for {record['id']} must be {marker}")

        plan_path = track_dir / "plan.md"
        if plan_path.is_file():
            _, in_progress, pending = checkbox_counts(plan_path)
            if status == "completed" and (in_progress or pending):
                errors.append(f"completed {record['id']} plan has unfinished checkboxes")
            if status in {"active", "deferred"} and not (in_progress or pending):
                errors.append(f"{status} {record['id']} plan has no unfinished checkbox")

        metadata_path = track_dir / "metadata.json"
        if metadata_path.is_file():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata.get("track_id") not in {record["id"], record["track"]}:
                errors.append(f"{record['id']} metadata track_id does not identify its directory")
            metadata_status = metadata.get("status")
            if status == "completed" and metadata_status not in COMPLETED_METADATA:
                errors.append(f"completed {record['id']} metadata status is {metadata_status!r}")
            if status == "active" and metadata_status not in ACTIVE_METADATA:
                errors.append(f"active {record['id']} metadata status is {metadata_status!r}")

    archived = root / "conductor" / "tracks" / "event_log_registry_readiness_20260721"
    archived_metadata = json.loads((archived / "metadata.json").read_text(encoding="utf-8"))
    if archived_metadata.get("status") != "completed":
        errors.append("archived bounded registry track must remain completed")
    _, archived_progress, archived_pending = checkbox_counts(archived / "plan.md")
    if archived_progress or archived_pending:
        errors.append("archived bounded registry plan has unfinished checkboxes")
    if "deferred full-corpus expansion placeholder" not in registry_markdown:
        errors.append("tracks.md must distinguish deferred #63 scope from bounded completion")

    evidence_dir = root / "conductor" / "evidence"
    hf_receipt = json.loads(
        (evidence_dir / "hf-reviewed-fixture-publication.json").read_text(encoding="utf-8")
    )
    if hf_receipt.get("scope") != "reviewed_synthetic_fixtures_only":
        errors.append("HF receipt must preserve the reviewed synthetic-fixture boundary")
    boundaries = set(hf_receipt.get("boundaries", []))
    if {"not_real_data_publication_evidence", "not_full_corpus_evidence"} - boundaries:
        errors.append("HF receipt is missing real-data/full-corpus non-claim boundaries")

    release_receipt = json.loads(
        (evidence_dir / "v0.2.0-release-verification.json").read_text(encoding="utf-8")
    )
    if release_receipt.get("scope") != "apache_2_0_code_release_not_production_data":
        errors.append("release receipt must distinguish code rights from production data")
    if release_receipt.get("release", {}).get("commit") != (
        "71da1b84ff8d0a50894348f61ad60947906c6359"
    ):
        errors.append("v0.2.0 receipt does not bind the verified release commit")
    assets = release_receipt.get("assets", [])
    if len(assets) != 6 or any(asset.get("attestation") != "verified" for asset in assets):
        errors.append("v0.2.0 receipt must record six verified asset attestations")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Conductor registry lifecycle and plan invariants passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
