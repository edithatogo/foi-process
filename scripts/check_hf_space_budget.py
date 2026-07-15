#!/usr/bin/env python3
"""Enforce a bounded production asset budget for the Static Space."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


LIMITS = {
    "javascript_bytes": 800_000,
    "css_bytes": 25_000,
    "dashboard_data_bytes": 100_000,
}


def total_bytes(paths: list[Path]) -> int:
    return sum(path.stat().st_size for path in paths)


def check(dist: Path, dashboard_data: Path) -> dict[str, int]:
    if not (dist / "index.html").is_file():
        raise ValueError("Space build is missing dist/index.html")
    javascript = sorted((dist / "assets").glob("*.js"))
    styles = sorted((dist / "assets").glob("*.css"))
    if not javascript or not styles:
        raise ValueError("Space build must contain JavaScript and CSS assets")
    if not dashboard_data.is_file():
        raise ValueError("dashboard projection is missing")

    actual = {
        "javascript_bytes": total_bytes(javascript),
        "css_bytes": total_bytes(styles),
        "dashboard_data_bytes": dashboard_data.stat().st_size,
    }
    failures = [
        f"{name} is {actual[name]} bytes; limit is {limit}"
        for name, limit in LIMITS.items()
        if actual[name] > limit
    ]
    if failures:
        raise ValueError("Space asset budget exceeded: " + "; ".join(failures))
    return actual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--dashboard-data", type=Path, required=True)
    args = parser.parse_args()
    result = check(args.dist.resolve(), args.dashboard_data.resolve())
    print(json.dumps({"limits": LIMITS, "actual": result}, sort_keys=True))


if __name__ == "__main__":
    main()
