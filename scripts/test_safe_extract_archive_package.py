#!/usr/bin/env python3
"""Focused tests for fail-closed archive-package ZIP extraction."""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from safe_extract_archive_package import extract


def expect_rejected(entries: dict[str, bytes], **limits: int) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        archive = root / "package.zip"
        with zipfile.ZipFile(archive, "w") as output:
            for name, content in entries.items():
                output.writestr(name, content)
        try:
            extract(archive, root / "output", **limits)
        except ValueError:
            return
        raise AssertionError(f"unsafe archive was accepted: {sorted(entries)}")


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        archive = root / "package.zip"
        with zipfile.ZipFile(archive, "w") as output:
            output.writestr("archive-package.json", b"{}\n")
            output.writestr("events.ndjson", b"{}\n")
        extract(archive, root / "output")
        assert (root / "output/archive-package.json").read_bytes() == b"{}\n"

    expect_rejected({"../escape": b"bad", "archive-package.json": b"{}"})
    expect_rejected({"nested/archive-package.json": b"{}"})
    expect_rejected({"/absolute": b"bad", "archive-package.json": b"{}"})
    expect_rejected(
        {"archive-package.json": b"{}", "events.ndjson": b"{}"}, max_members=1
    )
    expect_rejected(
        {"archive-package.json": b"{}"}, max_file_bytes=1
    )
    expect_rejected(
        {"archive-package.json": b"{}", "events.ndjson": b"{}"},
        max_total_bytes=3,
    )
    print("safe archive-package extraction tests passed")


if __name__ == "__main__":
    main()
