"""Regression checks for the metadata-only Alaveteli adapter."""

from __future__ import annotations

import json
from pathlib import Path

from alaveteli_metadata_adapter import adapt

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    paths = [
        ROOT / "examples" / "input" / "alaveteli-request-envelope.sample.json",
        ROOT / "examples" / "input" / "alaveteli-request-envelope.asktheeu-1338.json",
    ]
    required = {
        "schema_version", "event_id", "logical_event_id", "revision", "operation",
        "site", "jurisdiction", "case_id", "activity", "observed_at", "captured_at",
        "processed_at", "position", "assertion_status", "objects", "evidence",
        "provenance", "privacy",
    }
    outputs = []
    for path in paths:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        first = adapt(envelope)
        second = adapt(envelope)
        if first != second:
            raise SystemExit(f"{path.name}: adapter output is not deterministic")
        if required - first.keys():
            raise SystemExit(f"{path.name}: missing ProcessEvent fields: {sorted(required - first.keys())}")
        if first["assertion_status"] != "candidate":
            raise SystemExit(f"{path.name}: live adapter output must remain candidate")
        if first["privacy"]["disposition"] != "needs_review" or first["privacy"]["human_reviewed"]:
            raise SystemExit(f"{path.name}: live adapter output must remain review-gated")
        if any(key in first for key in ("text", "body", "attachments", "messages")):
            raise SystemExit(f"{path.name}: adapter output must not retain raw request content")
        outputs.append(first)
    if outputs[0]["position"]["sequence"] >= outputs[1]["position"]["sequence"]:
        raise SystemExit("source ordering must preserve request sequence")
    print(f"validated {len(outputs)} deterministic, review-gated Alaveteli adapter outputs")


if __name__ == "__main__":
    main()
