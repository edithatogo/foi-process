#!/usr/bin/env python3
"""Verify release evidence checksums and manifest consistency."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


CHECKSUM_LINE = re.compile(r"^([0-9a-f]{64})  ([^/\\]+)$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(directory: Path) -> None:
    expected: dict[str, str] = {}
    for line in (directory / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        match = CHECKSUM_LINE.fullmatch(line)
        if not match:
            raise ValueError(f"invalid SHA256SUMS line: {line!r}")
        digest, name = match.groups()
        if name in expected:
            raise ValueError(f"duplicate checksum entry: {name}")
        expected[name] = digest
    actual_names = {path.name for path in directory.iterdir() if path.is_file()}
    if actual_names != set(expected) | {"SHA256SUMS"}:
        raise ValueError("SHA256SUMS does not cover exactly the release evidence files")
    for name, digest in expected.items():
        actual = sha256(directory / name)
        if actual != digest:
            raise ValueError(f"checksum mismatch for {name}: {actual}")

    manifest = json.loads((directory / "release-evidence-manifest.json").read_text(encoding="utf-8"))
    manifest_files = {entry["path"]: entry for entry in manifest["files"]}
    covered = set(expected) - {"release-evidence-manifest.json"}
    if set(manifest_files) != covered:
        raise ValueError("release evidence manifest does not cover its pre-manifest artifacts")
    for name, entry in manifest_files.items():
        path = directory / name
        if entry["sha256"] != sha256(path) or entry["byte_length"] != path.stat().st_size:
            raise ValueError(f"release evidence manifest mismatch for {name}")
    print(f"verified {len(expected)} release evidence files in {directory}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    verify(args.directory.resolve())


if __name__ == "__main__":
    main()
