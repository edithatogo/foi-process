#!/usr/bin/env python3
"""Regression checks for the bounded real release validator."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from validate_bounded_real_release import DEFAULT_PACKAGE, validate


def main() -> None:
    manifest = validate()
    assert (manifest["request_count"], manifest["event_count"], manifest["attachment_count"]) == (75, 425, 179)
    with tempfile.TemporaryDirectory() as temporary:
        package = Path(temporary) / "package"
        shutil.copytree(DEFAULT_PACKAGE, package)
        with (package / "event_log.jsonl").open("a", encoding="utf-8") as stream:
            stream.write("{}\n")
        try:
            validate(package)
        except ValueError as error:
            assert "SHA256SUMS mismatch" in str(error)
        else:
            raise AssertionError("modified event log was accepted")
    print("bounded real release regression checks passed")


if __name__ == "__main__":
    main()
