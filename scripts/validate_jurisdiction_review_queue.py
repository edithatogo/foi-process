"""Validate the human-review handoff without claiming independent review."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SCOPE = {"source_identity", "event_boundary", "privacy_disposition", "jurisdiction_mapping", "ordering"}


def main() -> None:
    path = ROOT / "conductor" / "tracks" / "jurisdiction_case_process_modelling_20260721" / "review-queue.ndjson"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not rows:
        raise SystemExit("review queue is empty")
    for row in rows:
        if set(row.get("review_scope", [])) != REQUIRED_SCOPE:
            raise SystemExit(f"{row.get('subject_id')}: incomplete review scope")
        if row.get("adjudication_status") != "pending" or row.get("reviewer_id") is not None:
            raise SystemExit(f"{row.get('subject_id')}: queue row must remain pending until a reviewer acts")
        if row.get("promotion_boundary") != "engineering_only":
            raise SystemExit(f"{row.get('subject_id')}: review queue escaped engineering_only")
    print(f"validated {len(rows)} fail-closed jurisdiction review queue rows")


if __name__ == "__main__":
    main()
