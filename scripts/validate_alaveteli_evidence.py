"""Validate the fail-closed Alaveteli deployment evidence contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "deployment_url",
    "deployment_revision",
    "jurisdiction",
    "api_surface",
    "authority_snapshot_sha256",
    "capture_window",
    "redaction_and_retention",
    "promotion_boundary",
}


def main() -> None:
    path = ROOT / "examples" / "input" / "alaveteli-deployment-evidence.sample.json"
    evidence = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED - evidence.keys()
    if missing:
        raise SystemExit(f"missing deployment evidence fields: {sorted(missing)}")
    if evidence["promotion_boundary"] != "engineering_only":
        raise SystemExit("sample evidence must remain engineering_only")
    if evidence.get("evidence_status") != "blocked_until_instance_capture":
        raise SystemExit("sample evidence must remain fail-closed until a real instance is captured")
    if not isinstance(evidence["api_surface"], dict):
        raise SystemExit("api_surface must be structured")
    print("validated fail-closed Alaveteli deployment evidence contract")


if __name__ == "__main__":
    main()
