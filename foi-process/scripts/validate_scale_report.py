#!/usr/bin/env python3
"""Validate structural and deterministic invariants in a Rust scale report."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DIGEST = re.compile(r"^[0-9a-f]{64}$")


def validate(path: Path, require_standard: bool) -> None:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema_version") != "1.0.0":
        raise ValueError("unsupported scale report schema version")
    runs = report.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("scale report has no runs")
    cases = [run.get("cases") for run in runs]
    if cases != sorted(set(cases)) or any(not isinstance(value, int) or value <= 0 for value in cases):
        raise ValueError("scale report case counts must be positive, unique, and ascending")
    if require_standard and cases != [1_000, 10_000, 200_000]:
        raise ValueError("standard release report must contain 1k, 10k, and 200k case profiles")

    repetitions = report.get("parameters", {}).get("repetitions", 0)
    if not isinstance(repetitions, int) or repetitions < 3:
        raise ValueError("scale report must contain at least three repetitions")
    for run in runs:
        for mode in ("baseline", "correction_retraction"):
            result = run.get(mode, {})
            if not DIGEST.fullmatch(result.get("output_sha256", "")):
                raise ValueError(f"{run.get('profile')} {mode} has no deterministic output hash")
            timing = result.get("elapsed_seconds", {})
            samples = timing.get("samples", [])
            if len(samples) != repetitions or any(value <= 0 for value in samples):
                raise ValueError(f"{run.get('profile')} {mode} has invalid timing samples")
            if not (timing["minimum"] <= timing["median"] <= timing["maximum"]):
                raise ValueError(f"{run.get('profile')} {mode} timing summary is inconsistent")
            if result.get("peak_resident_bytes_max") is not None and result["peak_resident_bytes_max"] <= 0:
                raise ValueError(f"{run.get('profile')} {mode} peak memory is invalid")
        if run.get("stress_elapsed_ratio", 0) <= 0:
            raise ValueError(f"{run.get('profile')} stress ratio is invalid")
    print(f"validated {len(runs)} scale profiles in {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--require-standard", action="store_true")
    args = parser.parse_args()
    validate(args.report.resolve(), args.require_standard)


if __name__ == "__main__":
    main()
