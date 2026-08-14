#!/usr/bin/env python3
"""Validate that a release commit has the expected Release Please subject."""

from __future__ import annotations

import argparse
import re


def subject_matches_release(subject: str, version: str) -> bool:
    expected = f"chore(main): release {version}"
    return subject == expected or re.fullmatch(
        rf"{re.escape(expected)} \(#[1-9][0-9]*\)", subject
    ) is not None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("subject")
    parser.add_argument("version")
    args = parser.parse_args()

    if subject_matches_release(args.subject, args.version):
        return 0
    parser.error(
        "commit subject is not the expected Release Please subject "
        "(optionally followed by a numeric GitHub pull-request suffix)"
    )


if __name__ == "__main__":
    raise SystemExit(main())
