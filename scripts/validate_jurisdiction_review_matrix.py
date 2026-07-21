"""Keep T11 review status explicit and fail closed at promotion."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    path = ROOT / "conductor" / "tracks" / "jurisdiction_case_process_modelling_20260721" / "review-matrix.json"
    matrix = json.loads(path.read_text(encoding="utf-8"))
    if matrix.get("promotion_boundary") != "engineering_only":
        raise SystemExit("T11 review matrix must remain engineering_only")
    rows = matrix.get("rows", [])
    required = {"source_provenance", "mermaid_bpmn_pairing", "alaveteli_live_endpoint", "representative_real_case_set", "independent_annotation_adjudication", "replay_isolation_and_coverage", "legal_promotion"}
    found = {row.get("gate") for row in rows}
    if found != required:
        raise SystemExit(f"review matrix gates differ: {sorted(found ^ required)}")
    for row in rows:
        if row["status"] == "complete" and not row.get("evidence"):
            raise SystemExit(f"completed gate lacks evidence: {row['gate']}")
        if row["gate"] == "legal_promotion" and row["status"] == "complete":
            raise SystemExit("legal promotion cannot be complete in the engineering-only matrix")
    print(f"validated T11 review matrix: {len(rows)} gates; promotion remains blocked")


if __name__ == "__main__":
    main()
