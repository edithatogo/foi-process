#!/usr/bin/env python3
"""Fail closed if the publication gate permits production data prematurely."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_GATES = {
    "requester_privacy_and_third_party_data",
    "ocr_and_embedding_amplification",
    "tikanga_and_data_governance",
    "licensing_and_attribution",
    "removal_and_appeal",
    "threat_model",
    "human_owner_approval",
}


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("governance/publication_gate.json")
    gate = json.loads(path.read_text(encoding="utf-8"))
    statuses = gate.get("gates", {})
    missing = sorted(REQUIRED_GATES - statuses.keys())
    if missing:
        raise SystemExit(f"publication gate missing required reviews: {', '.join(missing)}")
    if gate.get("production_data_publication") != "blocked":
        raise SystemExit("production data publication must remain blocked until human review is complete")
    if gate.get("status") != "synthetic-only":
        raise SystemExit("publication gate status must remain synthetic-only")
    if any(status in {"approved", "complete"} for key, status in statuses.items() if key in REQUIRED_GATES):
        raise SystemExit("human review statuses cannot be partially represented as approved")
    print(f"governance gate valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
