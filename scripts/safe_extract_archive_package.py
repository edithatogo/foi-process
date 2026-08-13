#!/usr/bin/env python3
"""Extract an immutable archive-package ZIP without path or link traversal."""

from __future__ import annotations

import argparse
import stat
import zipfile
from pathlib import Path, PurePosixPath

MAX_MEMBERS = 2_048
MAX_FILE_BYTES = 256 * 1024 * 1024
MAX_TOTAL_BYTES = 1024 * 1024 * 1024
COPY_BLOCK_BYTES = 1024 * 1024


def extract(
    source: Path,
    destination: Path,
    *,
    max_members: int = MAX_MEMBERS,
    max_file_bytes: int = MAX_FILE_BYTES,
    max_total_bytes: int = MAX_TOTAL_BYTES,
) -> None:
    with zipfile.ZipFile(source) as archive:
        members = archive.infolist()
        if not members:
            raise ValueError("archive package ZIP is empty")
        if len(members) > max_members:
            raise ValueError("archive package ZIP exceeds member-count limit")
        total_declared = 0
        seen: set[PurePosixPath] = set()
        for member in members:
            path = PurePosixPath(member.filename)
            mode = member.external_attr >> 16
            if (
                path.is_absolute()
                or not path.parts
                or any(part in {"", ".", ".."} for part in path.parts)
                or "\\" in member.filename
                or stat.S_ISLNK(mode)
            ):
                raise ValueError(f"unsafe archive member: {member.filename}")
            if path in seen:
                raise ValueError(f"duplicate archive member: {member.filename}")
            seen.add(path)
            if not member.is_dir():
                if member.file_size > max_file_bytes:
                    raise ValueError(f"archive member exceeds per-file limit: {member.filename}")
                total_declared += member.file_size
                if total_declared > max_total_bytes:
                    raise ValueError("archive package ZIP exceeds total uncompressed-size limit")

        destination.mkdir(parents=True, exist_ok=False)
        total_written = 0
        for member in members:
            path = PurePosixPath(member.filename)
            target = destination.joinpath(*path.parts)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as reader, target.open("xb") as writer:
                file_written = 0
                while block := reader.read(COPY_BLOCK_BYTES):
                    file_written += len(block)
                    total_written += len(block)
                    if file_written > max_file_bytes:
                        raise ValueError(
                            f"archive member exceeds per-file limit: {member.filename}"
                        )
                    if total_written > max_total_bytes:
                        raise ValueError(
                            "archive package ZIP exceeds total uncompressed-size limit"
                        )
                    writer.write(block)
                if file_written != member.file_size:
                    raise ValueError(
                        f"archive member size differs from ZIP metadata: {member.filename}"
                    )
    if not (destination / "archive-package.json").is_file():
        raise ValueError("archive package ZIP must contain archive-package.json at its root")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    extract(args.source.resolve(), args.destination.resolve())


if __name__ == "__main__":
    main()
