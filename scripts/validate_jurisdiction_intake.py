#!/usr/bin/env python3
"""Fail-closed validator for jurisdiction onboarding intake records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = {
    "profile_id",
    "jurisdiction",
    "platform",
    "source_pins",
    "maturity",
    "promotion",
    "review_queue",
}
MATURITY = {"synthetic_only", "observed", "reviewed", "promoted"}


def validate(record: dict[str, object]) -> None:
    missing = REQUIRED - record.keys()
    if missing:
        raise ValueError(f"missing required fields: {', '.join(sorted(missing))}")
    if record["maturity"] not in MATURITY:
        raise ValueError("unknown maturity")
    sources = record["source_pins"]
    if not isinstance(sources, list) or not sources:
        raise ValueError("source_pins must be a non-empty list")
    for source in sources:
        if not isinstance(source, dict) or not {"uri", "sha256", "effective_from"} <= source.keys():
            raise ValueError("each source pin requires uri, sha256, and effective_from")
        digest = source["sha256"]
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError("source pin sha256 must be a 64-character digest")
    promotion = record["promotion"]
    if not isinstance(promotion, dict):
        raise ValueError("promotion must be an object")
    if promotion.get("legal_determinations") != "human_only":
        raise ValueError("legal determinations must remain human_only")
    if record["maturity"] == "promoted" and not promotion.get("independent_review_evidence"):
        raise ValueError("promoted profiles require independent review evidence")
    queue = record["review_queue"]
    if not isinstance(queue, list) or not queue:
        raise ValueError("review_queue must retain at least one unresolved review item")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    validate(json.loads(args.record.read_text(encoding="utf-8")))


if __name__ == "__main__":
    main()
