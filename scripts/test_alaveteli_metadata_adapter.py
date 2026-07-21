"""Regression checks for the metadata-only Alaveteli adapter."""

from __future__ import annotations

import json
from pathlib import Path

from alaveteli_metadata_adapter import adapt

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    envelope = json.loads(
        (ROOT / "examples" / "input" / "alaveteli-request-envelope.sample.json").read_text(encoding="utf-8")
    )
    first = adapt(envelope)
    second = adapt(envelope)
    if first != second:
        raise SystemExit("adapter output is not deterministic")
    required = {
        "schema_version", "event_id", "logical_event_id", "revision", "operation",
        "site", "jurisdiction", "case_id", "activity", "observed_at", "captured_at",
        "processed_at", "position", "assertion_status", "objects", "evidence",
        "provenance", "privacy",
    }
    if required - first.keys():
        raise SystemExit(f"missing ProcessEvent fields: {sorted(required - first.keys())}")
    if first["assertion_status"] != "candidate":
        raise SystemExit("live adapter output must remain candidate")
    if first["privacy"]["disposition"] != "needs_review" or first["privacy"]["human_reviewed"]:
        raise SystemExit("live adapter output must remain review-gated")
    if any(key in first for key in ("text", "body", "attachments", "messages")):
        raise SystemExit("adapter output must not retain raw request content")
    print("validated deterministic, review-gated Alaveteli adapter output")


if __name__ == "__main__":
    main()
