#!/usr/bin/env python3
"""Validate markdown learning logs against the track-18 learning schema."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_FIELDS = {
    "entry_id",
    "observed_on",
    "repo",
    "scope",
    "trigger",
    "lessons_learned",
    "next_check_to_add",
}

SCHEMA_SCOPE = {"track", "workflow", "skill", "tooling", "environment", "governance"}
SCHEMA_SEVERITY = {"low", "medium", "high", "critical"}
SCHEMA_STATUS = {"open", "resolved", "verified"}
ENTRY_ID_RE = re.compile(r"^track-18-[a-z0-9-]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SCALAR_KEY_RE = re.compile(r"^\s*-\s*`([^`]+)`:\s*(.*)\s*$")
SCALAR_VALUE_RE = re.compile(r"`([^`]*)`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate learning-log markdown entries against expected fields."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["conductor/learning-log.md"],
        help="One or more conductor/learning-log.md paths (default: conductor/learning-log.md)",
    )
    return parser.parse_args()


def _field_from_line(line: str) -> tuple[str, str] | None:
    match = SCALAR_KEY_RE.match(line)
    if not match:
        return None
    key = match.group(1).strip()
    raw_value = match.group(2).strip()
    value_match = SCALAR_VALUE_RE.search(raw_value)
    value = value_match.group(1) if value_match else raw_value
    return key, value.strip()


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        errors.append(f"{path}: file not found")
        return errors

    in_entry = False
    current_entry: dict[str, str] = {}
    present_fields: set[str] = set()
    entry_seen = False

    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.rstrip()
        if stripped.startswith("## "):
            if in_entry:
                for field in REQUIRED_FIELDS - present_fields:
                    errors.append(f"{path}:{line_no}: missing required field '{field}' in prior entry")
            in_entry = True
            entry_seen = True
            current_entry = {}
            present_fields = set()
            continue

        parsed = _field_from_line(stripped)
        if parsed:
            key, value = parsed
            if key in REQUIRED_FIELDS:
                present_fields.add(key)
            if key == "entry_id" and value and not ENTRY_ID_RE.match(value):
                errors.append(f"{path}:{line_no}: invalid entry_id '{value}'")
            if key == "observed_on" and value and not DATE_RE.match(value):
                errors.append(f"{path}:{line_no}: invalid observed_on '{value}', expected YYYY-MM-DD")
            if key == "scope" and value and value not in SCHEMA_SCOPE:
                errors.append(f"{path}:{line_no}: invalid scope '{value}', expected one of {sorted(SCHEMA_SCOPE)}")
            if key == "severity" and value and value not in SCHEMA_SEVERITY:
                errors.append(f"{path}:{line_no}: invalid severity '{value}', expected one of {sorted(SCHEMA_SEVERITY)}")
            if key == "status" and value and value not in SCHEMA_STATUS:
                errors.append(f"{path}:{line_no}: invalid status '{value}', expected one of {sorted(SCHEMA_STATUS)}")
            current_entry[key] = value
        elif stripped.startswith("- ") or stripped.startswith("  - "):
            if not stripped.startswith("  - "):
                continue
            if current_entry.get("lessons_learned") is not None:
                present_fields.add("lessons_learned")
            if current_entry.get("next_check_to_add") is not None:
                present_fields.add("next_check_to_add")

    if in_entry:
        for field in REQUIRED_FIELDS - present_fields:
            errors.append(f"{path}: end-of-file: missing required field '{field}' in final entry")

    if not entry_seen:
        errors.append(f"{path}: no entries found (expected at least one ## section)")

    return errors


def main() -> None:
    args = parse_args()
    all_errors: list[str] = []
    for path_text in args.paths:
        all_errors.extend(validate_file(Path(path_text)))

    if all_errors:
        print("Learning log validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("Learning log validation passed.")


if __name__ == "__main__":
    main()
