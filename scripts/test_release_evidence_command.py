#!/usr/bin/env python3
"""Regression tests for release-evidence command diagnostics."""

from __future__ import annotations

import sys

import build_release_evidence


def main() -> None:
    output = build_release_evidence.command_output([sys.executable, "-c", "print('ok')"])
    assert output == "ok"
    try:
        build_release_evidence.command_output(
            [sys.executable, "-c", "import sys; print('cargo detail', file=sys.stderr); raise SystemExit(7)"]
        )
    except RuntimeError as error:
        assert "cargo detail" in str(error)
        assert "after 1 attempt(s)" in str(error)
    else:
        raise AssertionError("failed command did not preserve diagnostics")
    print("Release evidence command diagnostics passed.")


if __name__ == "__main__":
    main()
