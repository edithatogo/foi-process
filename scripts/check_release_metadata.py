#!/usr/bin/env python3
"""Validate code-release version and licensing metadata."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAG_RE = re.compile(r"^v(?P<version>[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?)$")


def cargo_version() -> str:
    return str(tomllib.loads((ROOT / "Cargo.toml").read_text(encoding="utf-8"))["package"]["version"])


def cargo_lock_version() -> str:
    lock = tomllib.loads((ROOT / "Cargo.lock").read_text(encoding="utf-8"))
    matches = [package for package in lock["package"] if package.get("name") == "foi-process"]
    if len(matches) != 1:
        raise ValueError("Cargo.lock must contain exactly one foi-process package")
    return str(matches[0]["version"])


def citation_version() -> str:
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(r"^version:\s*([^\s#]+)", citation, re.MULTILINE)
    if match is None:
        raise ValueError("CITATION.cff version is missing")
    return match.group(1)


def check(expected_tag: str) -> None:
    match = TAG_RE.fullmatch(expected_tag)
    if match is None:
        raise ValueError(f"invalid release tag: {expected_tag}")
    expected = match.group("version")
    manifest = json.loads((ROOT / ".release-please-manifest.json").read_text(encoding="utf-8"))
    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    versions = {
        "Cargo.toml": cargo_version(),
        "Cargo.lock": cargo_lock_version(),
        "CITATION.cff": citation_version(),
        ".release-please-manifest.json": str(manifest.get(".")),
        ".zenodo.json": str(zenodo.get("version")),
    }
    mismatches = {name: value for name, value in versions.items() if value != expected}
    if mismatches:
        raise ValueError(f"release metadata does not match {expected_tag}: {mismatches}")
    if zenodo.get("license") != "Apache-2.0":
        raise ValueError(".zenodo.json must identify the repository code as Apache-2.0")
    if not zenodo.get("creators") or not zenodo["creators"][0].get("orcid"):
        raise ValueError(".zenodo.json must retain creator ORCID metadata")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tag", nargs="?", help="semantic release tag, for example v0.1.0")
    parser.add_argument("--print-version", action="store_true")
    args = parser.parse_args()
    if args.print_version:
        print(cargo_version())
        return
    if args.tag is None:
        parser.error("tag is required unless --print-version is used")
    check(args.tag)
    print(f"release metadata verified for {args.tag}")


if __name__ == "__main__":
    main()
