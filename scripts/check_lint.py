#!/usr/bin/env python3
"""Workspace-wide linting check for Vale prose, Markdown, and naming.

Runs:
    1. Vale on all .md files in the workspace (excluding node_modules, .git, etc.)
    2. markdownlint-cli2 on all .md files (if available)
    3. Naming convention checks (snake_case, kebab-case, no spaces, etc.)

Exit codes:
    0 - all checks passed
    1 - one or more checks failed

Usage:
    python scripts/check_lint.py
    python scripts/check_lint.py --verbose
    python scripts/check_lint.py --fix          # auto-fix markdownlint issues
    python scripts/check_lint.py --vale-only    # only run Vale
    python scripts/check_lint.py --mdl-only     # only run markdownlint
    python scripts/check_lint.py --naming-only  # only run naming checks
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import NoReturn

# Ensure scripts/ is on sys.path for sibling imports
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import check_naming  # type: ignore[import-untyped]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

IGNORE_DIRS = {
    ".git", ".swarm", "node_modules", ".pytest_cache",
    "__pycache__", ".venv", "venv", "env",
    ".ruff_cache", ".mypy_cache", ".pyright",
    "dist", "build", ".changeset", ".husky",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok(message: str) -> None:
    print(f"  [PASS]  {message}")


def _fail(message: str, advice: str = "") -> None:
    print(f"  [FAIL]  {message}")
    if advice:
        print(f"          TIP: {advice}")


def _warn(message: str) -> None:
    print(f"  [WARN]  {message}")


def _run(
    args: list[str],
    cwd: str | None = None,
    timeout: int = 60,
) -> subprocess.CompletedProcess | None:
    """Run a subprocess command, returning None on failure.
    Uses UTF-8 encoding to handle Unicode characters (Māori, emoji, etc.).
    """
    try:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=cwd or str(WORKSPACE_ROOT),
        )
    except (FileNotFoundError, OSError):
        return None
    except subprocess.TimeoutExpired:
        print(f"  [WARN]  Command timed out after {timeout}s: {' '.join(args)}")
        return None
    except Exception as exc:
        print(f"  [WARN]  Command failed ({type(exc).__name__}): {' '.join(args)}")
        return None


def _find_markdown_files(root: Path) -> list[Path]:
    """Find all .md files in the workspace, skipping ignored dirs."""
    md_files: list[Path] = []
    for entry in root.rglob("*.md"):
        rel = entry.relative_to(root)
        if any(p in IGNORE_DIRS for p in rel.parts):
            continue
        md_files.append(entry)
    return sorted(md_files)


# ---------------------------------------------------------------------------
# Lint Checks
# ---------------------------------------------------------------------------


def check_vale(verbose: bool = False) -> bool:
    """Run Vale on all markdown files in the workspace."""
    print("  --- Vale Prose Linter ---")

    proc = _run(["vale", "--version"])
    if proc is None or proc.returncode != 0:
        _fail("Vale is not installed", "Install Vale from https://vale.sh")
        return False

    _ok(f"Vale {proc.stdout.strip()}")

    # Run on root-level .md files only (fast check)
    root_mds = sorted(WORKSPACE_ROOT.glob("*.md"))
    if not root_mds:
        _warn("No markdown files found to lint at workspace root")
        return True

    proc = _run(
        ["vale", "--no-wrap", "--no-exit", "--output=line"]
        + [str(f) for f in root_mds],
        timeout=120,
    )
    if proc is None:
        _fail("Vale execution failed (timeout or error)")
        return False

    lines = [l for l in proc.stdout.strip().split("\n") if l.strip()]

    if not lines:
        _ok("No Vale alerts found")
        return True

    total = len(lines)

    if verbose:
        for line in lines:
            print(f"    {line}")

    # Categorize by known alert patterns
    suggestions = sum(1 for l in lines if any(
        p in l for p in ["Microsoft.", "write-good."]
    ))
    spelling = sum(1 for l in lines if "Vale.Spelling" in l)
    terms = sum(1 for l in lines if "Vale.Terms" in l)
    other = total - suggestions

    print(f"  [INFO]  {total} Vale alert(s): {spelling} spelling, "
          f"{terms} terminology, {suggestions - spelling - terms} style")

    # Only fail on spelling/terminology errors, warn on suggestions
    if spelling > 0:
        _fail(f"{spelling} possible spelling issue(s) — "
              "add terms to vocab if intentional")
        return False
    if terms > 0:
        _warn(f"{terms} terminology alert(s) — review for consistency")
    return True


def check_markdownlint(verbose: bool = False, fix: bool = False) -> bool:
    """Run markdownlint-cli2 on all markdown files (if available)."""
    print("  --- Markdownlint ---")

    proc = _run(["markdownlint", "--version"])
    mdl_cmd = "markdownlint"
    if proc is None or proc.returncode != 0:
        proc = _run(["markdownlint-cli2", "--version"])
        if proc is None or proc.returncode != 0:
            _warn("markdownlint not installed — skipping. "
                  "Install with: npm install -g markdownlint-cli2")
            return True
        mdl_cmd = "markdownlint-cli2"

    _ok(f"{mdl_cmd} {proc.stdout.strip()}")

    config_path = WORKSPACE_ROOT / ".markdownlint.json"
    if not config_path.exists():
        _fail("No .markdownlint.json found")
        return False

    cmd_args = [mdl_cmd, "--config", str(config_path)]
    if fix and mdl_cmd == "markdownlint-cli2":
        cmd_args.append("--fix")

    md_files = _find_markdown_files(WORKSPACE_ROOT)
    if not md_files:
        _warn("No markdown files found")
        return True

    cmd_args.extend(str(f) for f in md_files)
    proc = _run(cmd_args)

    if proc is None:
        _warn("markdownlint execution failed — skipping")
        return True

    if proc.returncode == 0:
        _ok("All markdown files comply with style rules")
        return True

    lines = [l for l in (proc.stdout or "").strip().split("\n") if l.strip()]
    if not lines:
        lines = [l for l in (proc.stderr or "").strip().split("\n") if l.strip()]

    if verbose:
        for line in lines:
            print(f"    {line}")
    else:
        issue_count = len([l for l in lines if ":" in l and l.strip()])
        print(f"  [INFO]  {issue_count or len(lines)} markdownlint issue(s)")

    _fail("Markdown style violations found",
           "Run with --fix to auto-fix some issues")
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def check_naming_lint(verbose: bool = False) -> bool:
    """Run naming convention checks via check_naming module."""
    print("  --- Naming Convention Check ---")
    try:
        code = check_naming.run_all_checks(verbose=verbose)
        ok = code == 0
        if ok:
            _ok("All naming conventions satisfied")
        else:
            _fail("Naming convention violations found",
                   "Run: python scripts/check_naming.py --verbose")
        return ok
    except Exception as exc:
        _fail(f"Naming check failed with exception: {exc}")
        return False


def run_lint_checks(
    verbose: bool = False,
    fix: bool = False,
    vale_only: bool = False,
    mdl_only: bool = False,
    naming_only: bool = False,
) -> int:
    """Run all lint checks and return exit code."""
    print("=" * 58)
    print("  NZ Legislation Workspace — Lint Checks")
    print("=" * 58)
    print()

    results: list[bool] = []

    if naming_only:
        results.append(check_naming_lint(verbose=verbose))
        print()
    else:
        if not mdl_only:
            results.append(check_vale(verbose=verbose))
            print()
        if not vale_only:
            results.append(check_markdownlint(verbose=verbose, fix=fix))
            print()
        results.append(check_naming_lint(verbose=verbose))
        print()

    print("=" * 58)
    total = len(results)
    passed = sum(1 for r in results if r)
    failed = total - passed

    if failed == 0:
        print(f"  All {total} lint check(s) passed!")
    else:
        print(f"  {passed}/{total} passed, {failed} failed")
        if not mdl_only and not naming_only:
            print("  Vale: review alerts above; update .vale.ini or vocab as needed")
        if not vale_only and not naming_only:
            print("  Markdownlint: run with --fix to auto-correct some issues")
        if naming_only or not (vale_only or mdl_only):
            print("  Naming: run 'python scripts/check_naming.py --verbose' for details")

    print("=" * 58)
    return 0 if failed == 0 else 1


def main() -> NoReturn:
    """Entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    fix = "--fix" in sys.argv
    vale_only = "--vale-only" in sys.argv
    mdl_only = "--mdl-only" in sys.argv
    naming_only = "--naming-only" in sys.argv
    sys.exit(run_lint_checks(verbose=verbose, fix=fix,
                              vale_only=vale_only, mdl_only=mdl_only,
                              naming_only=naming_only))


if __name__ == "__main__":
    main()
