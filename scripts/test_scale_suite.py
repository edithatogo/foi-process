#!/usr/bin/env python3
"""Regression checks for the isolated Rust scale-suite runner."""

from pathlib import Path

from run_rust_scale_suite import ROOT, repository_relative_path


def main() -> None:
    assert repository_relative_path(ROOT / "benchmarks" / "report.json") == "benchmarks/report.json"
    assert repository_relative_path(ROOT.parent / "external-report.json") is None
    print("scale suite helper checks passed")


if __name__ == "__main__":
    main()
