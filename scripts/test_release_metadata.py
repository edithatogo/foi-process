#!/usr/bin/env python3
"""Regression tests for fail-closed code-release metadata parity."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import check_release_metadata


def write_fixture(root: Path, version: str = "0.1.0", zenodo_license: str = "Apache-2.0") -> None:
    (root / "Cargo.toml").write_text(f'[package]\nname = "foi-process"\nversion = "{version}"\n', encoding="utf-8")
    (root / "Cargo.lock").write_text(
        f'version = 4\n\n[[package]]\nname = "foi-process"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    (root / "CITATION.cff").write_text(f"version: {version}\n", encoding="utf-8")
    (root / ".release-please-manifest.json").write_text(json.dumps({".": version}), encoding="utf-8")
    (root / ".zenodo.json").write_text(
        json.dumps(
            {
                "version": version,
                "license": zenodo_license,
                "creators": [{"name": "Test", "orcid": "0000-0000-0000-0000"}],
            }
        ),
        encoding="utf-8",
    )


def expect_rejected(tag: str, expected_fragment: str) -> None:
    try:
        check_release_metadata.check(tag)
    except ValueError as error:
        assert expected_fragment in str(error)
    else:
        raise AssertionError(f"release metadata unexpectedly accepted {tag}")


def replace(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def main() -> None:
    original_root = check_release_metadata.ROOT
    try:
        with tempfile.TemporaryDirectory(prefix="foi-process-release-metadata-") as temporary:
            root = Path(temporary)
            check_release_metadata.ROOT = root
            write_fixture(root)
            check_release_metadata.check("v0.1.0")
            expect_rejected("v9.9.9", "does not match")
            expect_rejected("0.1.0", "invalid release tag")
            for relative, old in (
                ("Cargo.lock", 'version = "0.1.0"'),
                ("CITATION.cff", "version: 0.1.0"),
                (".release-please-manifest.json", '"0.1.0"'),
                (".zenodo.json", '"version": "0.1.0"'),
            ):
                write_fixture(root)
                replace(root / relative, old, old.replace("0.1.0", "0.0.9"))
                expect_rejected("v0.1.0", relative)
            write_fixture(root, zenodo_license="other")
            expect_rejected("v0.1.0", "Apache-2.0")
    finally:
        check_release_metadata.ROOT = original_root
    print("Release metadata regression tests passed.")


if __name__ == "__main__":
    main()
