#!/usr/bin/env python3
"""Contract checks for the dashboard's fixture and bounded-real evidence."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data = json.loads((ROOT / "space/public/data/dashboard-data.json").read_text(encoding="utf-8"))
    meta = data["meta"]
    metrics = data["metrics"]
    quality = data["quality"]
    events = data["events"]
    cases = data["cases"]
    assert meta["classification"] in {"synthetic-fixture", "public-derived"}
    assert meta["source_release"] and len(meta["manifest_sha256"]) == 64
    assert metrics["case_count"] == len(cases)
    assert metrics["active_event_count"] == len(events)
    assert metrics["activity_count"] == len({event["activity"] for event in events})
    assert quality["checksums_verified"] is True
    assert quality["revision_count"] >= quality["reviewed_revision_count"]
    app = (ROOT / "space/src/App.tsx").read_text(encoding="utf-8")
    assert "Loading process evidence" in app
    assert "Dashboard data unavailable" in app
    assert "cases in scope" in app
    real_batch = Path(r"C:\tmp\realbatch30396908740\coverage.json")
    if real_batch.is_file():
        coverage = json.loads(real_batch.read_text(encoding="utf-8"))
        assert coverage["case_count"] == 5
        assert coverage["request_count_reconciles"] is True
        assert coverage["attachment_count_reconciles"] is True
        print("bounded real five-request evidence verified")
    else:
        print("bounded real five-request artifact not present locally; fixture checks passed")


if __name__ == "__main__":
    main()
