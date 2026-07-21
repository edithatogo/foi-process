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
    paths = [
        ROOT / "examples" / "input" / "alaveteli-deployment-evidence.sample.json",
        ROOT / "examples" / "input" / "alaveteli-deployment-evidence.asktheeu.json",
        ROOT / "examples" / "input" / "alaveteli-request-evidence.asktheeu.json",
        ROOT / "examples" / "input" / "alaveteli-request-evidence.asktheeu-1338.json",
    ]
    for path in paths:
        evidence = json.loads(path.read_text(encoding="utf-8"))
        required = {
            "deployment_url", "promotion_boundary", "raw_content_retained",
        } if "request_url" in evidence else REQUIRED
        if "request_url" in evidence:
            required |= {"request_url", "request_id", "response_status", "response_sha256", "evidence_status"}
        missing = required - evidence.keys()
        if missing:
            raise SystemExit(f"{path.name}: missing fields: {sorted(missing)}")
        if evidence["promotion_boundary"] != "engineering_only":
            raise SystemExit(f"{path.name}: evidence escaped engineering_only")
        if "api_surface" in evidence and not isinstance(evidence["api_surface"], dict):
            raise SystemExit(f"{path.name}: api_surface must be structured")
        if path.name.endswith("sample.json") and evidence.get("evidence_status") != "blocked_until_instance_capture":
            raise SystemExit("sample evidence must remain fail-closed until a real instance is captured")
        if evidence.get("raw_content_retained") is True:
            raise SystemExit(f"{path.name}: raw public content must not be retained by this evidence fixture")
        print(f"validated Alaveteli deployment evidence: {path.name}")


if __name__ == "__main__":
    main()
