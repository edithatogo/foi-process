#!/usr/bin/env python3
"""Regression checks for the fail-closed jurisdiction intake boundary."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from validate_jurisdiction_intake import validate


ROOT = Path(__file__).resolve().parents[1]
RECORD = json.loads((ROOT / "examples/input/jurisdiction-intake.synthetic.json").read_text())


def expect_invalid(record: dict[str, object]) -> None:
    try:
        validate(record)
    except ValueError:
        return
    raise AssertionError("invalid record unexpectedly accepted")


validate(RECORD)
missing_pin = copy.deepcopy(RECORD)
missing_pin["source_pins"] = []
expect_invalid(missing_pin)
auto_legal = copy.deepcopy(RECORD)
auto_legal["promotion"]["legal_determinations"] = "automated"
expect_invalid(auto_legal)
promoted_without_review = copy.deepcopy(RECORD)
promoted_without_review["maturity"] = "promoted"
expect_invalid(promoted_without_review)
