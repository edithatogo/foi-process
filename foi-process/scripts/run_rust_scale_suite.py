#!/usr/bin/env python3
"""Run isolated Rust baseline/stress scale profiles and write one evidence report."""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def command_output(command: list[str]) -> str:
    return subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()


def software_commit() -> str:
    commit = command_output(["git", "rev-parse", "HEAD"])
    dirty = command_output(["git", "status", "--porcelain", "--untracked-files=no"])
    return f"{commit}-dirty" if dirty else commit


def binary_path(target_dir: Path) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    return target_dir / "release" / f"scale_bench{suffix}"


def run_profile(binary: Path, cases: int, events_per_case: int, correction_every: int, retraction_every: int) -> dict[str, Any]:
    result = subprocess.run(
        [str(binary), str(cases), str(events_per_case), str(correction_every), str(retraction_every)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def aggregate(samples: list[dict[str, Any]]) -> dict[str, Any]:
    stable_fields = {
        key: value
        for key, value in samples[0].items()
        if key not in {"elapsed_seconds", "revisions_per_second", "peak_resident_bytes"}
    }
    for sample in samples[1:]:
        comparable = {
            key: value
            for key, value in sample.items()
            if key not in {"elapsed_seconds", "revisions_per_second", "peak_resident_bytes"}
        }
        if comparable != stable_fields:
            raise ValueError("benchmark repetitions produced different deterministic outputs")
    seconds = [float(sample["elapsed_seconds"]) for sample in samples]
    throughput = [float(sample["revisions_per_second"]) for sample in samples]
    resident = [sample["peak_resident_bytes"] for sample in samples if sample["peak_resident_bytes"]]
    return {
        **stable_fields,
        "elapsed_seconds": {
            "median": statistics.median(seconds),
            "minimum": min(seconds),
            "maximum": max(seconds),
            "samples": seconds,
        },
        "revisions_per_second": {
            "median": statistics.median(throughput),
            "minimum": min(throughput),
            "maximum": max(throughput),
        },
        "peak_resident_bytes_max": max(resident) if resident else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default="1000,10000,200000")
    parser.add_argument("--events-per-case", type=int, default=5)
    parser.add_argument("--correction-every", type=int, default=20)
    parser.add_argument("--retraction-every", type=int, default=1000)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-dir", type=Path, default=ROOT / "target")
    args = parser.parse_args()
    profiles = [int(value) for value in args.profiles.split(",") if value]
    if not profiles or any(value <= 0 for value in profiles):
        raise ValueError("profiles must contain positive comma-separated case counts")
    if args.repetitions < 1:
        raise ValueError("repetitions must be at least one")

    subprocess.run(
        ["cargo", "build", "--locked", "--release", "--bin", "scale_bench"],
        cwd=ROOT,
        check=True,
        env={**os.environ, "CARGO_TARGET_DIR": str(args.target_dir.resolve())},
    )
    binary = binary_path(args.target_dir.resolve())
    runs = []
    for cases in profiles:
        baseline_samples = []
        stress_samples = []
        for repetition in range(args.repetitions):
            modes = ("baseline", "stress") if repetition % 2 == 0 else ("stress", "baseline")
            for mode in modes:
                result = run_profile(
                    binary,
                    cases,
                    args.events_per_case,
                    0 if mode == "baseline" else args.correction_every,
                    0 if mode == "baseline" else args.retraction_every,
                )
                (baseline_samples if mode == "baseline" else stress_samples).append(result)
        baseline = aggregate(baseline_samples)
        stress = aggregate(stress_samples)
        baseline_seconds = max(float(baseline["elapsed_seconds"]["median"]), 1e-12)
        runs.append(
            {
                "profile": "full" if cases == max(profiles) and cases > 10_000 else f"{cases // 1000}k",
                "cases": cases,
                "baseline": baseline,
                "correction_retraction": stress,
                "stress_elapsed_ratio": float(stress["elapsed_seconds"]["median"]) / baseline_seconds,
            }
        )

    report = {
        "schema_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "warning": "Host-specific benchmark evidence; compare like-for-like runners and release builds.",
        "software_commit": software_commit(),
        "rustc": command_output(["rustc", "--version"]),
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "logical_cpu_count": os.cpu_count(),
        },
        "parameters": {
            "events_per_case": args.events_per_case,
            "correction_every": args.correction_every,
            "retraction_every": args.retraction_every,
            "repetitions": args.repetitions,
        },
        "runs": runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
