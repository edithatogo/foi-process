#!/usr/bin/env python3
"""Check release metadata consistency before a tagged publication."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAG_RE = re.compile(r"^v(?P<version>[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?)$")


def cargo_version() -> str:
    for line in (ROOT / "Cargo.toml").read_text(encoding="utf-8").splitlines():
        if line.startswith("version = "):
            return line.split('"', 2)[1]
    raise ValueError("Cargo.toml package version is missing")


def check(expected_tag: str) -> None:
    match = TAG_RE.fullmatch(expected_tag)
    if not match:
        raise ValueError(f"invalid release tag: {expected_tag}")
    version = match.group("version")
    if cargo_version() != version:
        raise ValueError(f"Cargo.toml version does not match {expected_tag}")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if f"version: {version}" not in citation:
        raise ValueError("CITATION.cff version does not match Cargo.toml")

    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    if not zenodo.get("creators") or not zenodo["creators"][0].get("orcid"):
        raise ValueError(".zenodo.json must retain creator ORCID metadata")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tag", help="semantic release tag, for example v0.1.0")
    args = parser.parse_args()
    check(args.tag)
    print(f"release metadata verified for {args.tag}")


if __name__ == "__main__":
    main()
