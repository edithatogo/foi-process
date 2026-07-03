#!/usr/bin/env python3
"""Workspace Doctor - NZ Legislation environment diagnostics.

Checks:
    - Python 3.10+ runtime version
    - Node.js >= 18 availability
    - uv (Python package manager) installation
    - Required environment variables:
        NZ_LEGISLATION_API_KEY, HF_TOKEN, ZENODO_TOKEN
    - API connectivity:
        - NZ Legislation API (api.legislation.govt.nz)
        - Hugging Face API (huggingface.co)
        - Zenodo API (zenodo.org / sandbox.zenodo.org)
    - Subproject dependency manifests (all 7 subprojects):
        - cli-legislation-nz: package.json
        - corpus-law-nz, corpus-nz-hansard, corpus-cases-medilegal-nz,
          nlp-policy-nz, sm-govt-nz, hathi-nz: pyproject.toml / requirements.txt
        - Key dependencies: ruff, pytest, vitest, typescript, etc.

Output:
    Clean console with [PASS]/[FAIL] indicators.
    TIP: resolution advice for any failed checks.

Exit codes:
    0 - all checks passed
    1 - one or more checks failed

Usage:
    python scripts/workspace_doctor.py
    python scripts/workspace_doctor.py --verbose
"""

from __future__ import annotations

import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import NoReturn

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_PYTHON_MAJOR: int = 3
MIN_PYTHON_MINOR: int = 10
MIN_NODE_MAJOR: int = 18

REQUIRED_ENV_VARS: dict[str, str] = {
    "NZ_LEGISLATION_API_KEY": "API key for NZ Legislation API",
    "HF_TOKEN": "Hugging Face authentication token",
    "ZENODO_TOKEN": "Zenodo API token",
}

PLACEHOLDER_VALUES: set[str] = {
    "your_api_key_here",
    "your_hf_token_here",
    "your_zenodo_token_here",
    "",
    "placeholder",
    "changeme",
    "replace_me",
}

# Workspace root — resolved relative to this script's location
WORKSPACE_ROOT: Path = Path(__file__).resolve().parent.parent
WORKSPACE_ENV_FILE: Path = WORKSPACE_ROOT / ".env"

# ---------------------------------------------------------------------------
# Subproject registry
# ---------------------------------------------------------------------------

SUBPROJECTS: dict[str, dict[str, object]] = {
    "cli-legislation-nz": {
        "language": "TypeScript",
        "manifests": ["package.json"],
        "key_deps": ["typescript", "vitest", "commander"],
    },
    "corpus-law-nz": {
        "language": "Python",
        "manifests": ["pyproject.toml"],
        "key_deps": ["ruff", "pytest", "pyarrow", "polars", "pydantic"],
    },
    "corpus-nz-hansard": {
        "language": "Python",
        "manifests": ["pyproject.toml", "requirements.txt"],
        "key_deps": ["ruff", "pytest", "polars", "duckdb", "pyarrow"],
    },
    "corpus-cases-medilegal-nz": {
        "language": "Python",
        "manifests": ["pyproject.toml"],
        "key_deps": ["ruff", "pytest", "polars", "pydantic"],
    },
    "nlp-policy-nz": {
        "language": "Python",
        "manifests": ["pyproject.toml"],
        "key_deps": ["ruff", "pytest", "spacy", "transformers", "torch"],
    },
    "sm-govt-nz": {
        "language": "Python",
        "manifests": ["pyproject.toml", "requirements.txt"],
        "key_deps": ["ruff", "pytest"],
    },
    "hathi-nz": {
        "language": "Python",
        "manifests": ["pyproject.toml", "requirements.txt"],
        "key_deps": ["ruff", "pytest", "duckdb", "polars", "pyarrow"],
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok(message: str) -> None:
    """Print a passing check."""
    print(f"  [PASS]  {message}")


def _fail(message: str, advice: str = "") -> None:
    """Print a failing check with optional resolution advice."""
    print(f"  [FAIL]  {message}")
    if advice:
        print(f"          TIP: {advice}")


def _run(args: list[str], timeout: int = 15) -> subprocess.CompletedProcess | None:
    """Run a subprocess command, returning None on failure."""
    try:
        shell = os.name == "nt"
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=shell,
        )
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None
    except OSError:
        return None


def _is_placeholder(value: str) -> bool:
    """Check if an environment variable value is a placeholder."""
    return value.strip().lower() in PLACEHOLDER_VALUES


def load_workspace_env(env_file: Path = WORKSPACE_ENV_FILE) -> list[str]:
    """Load required workspace credentials from root .env when unset.

    The workspace root .env is the local source of truth for shared credentials.
    Values are never printed, and existing process environment variables win.
    """
    loaded: list[str] = []
    if not env_file.is_file():
        return loaded

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name not in REQUIRED_ENV_VARS or os.environ.get(name):
            continue
        os.environ[name] = value.strip().strip('"').strip("'")
        loaded.append(name)
    return loaded


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_python() -> bool:
    """Verify Python interpreter meets minimum version (3.10+)."""
    info = sys.version_info
    ok = (info.major, info.minor) >= (MIN_PYTHON_MAJOR, MIN_PYTHON_MINOR)
    version_str = f"{info.major}.{info.minor}.{info.micro}"
    if ok:
        _ok(f"Python {version_str} (>= {MIN_PYTHON_MAJOR}.{MIN_PYTHON_MINOR})")
    else:
        _fail(
            f"Python {version_str} is too old",
            f"Install Python {MIN_PYTHON_MAJOR}.{MIN_PYTHON_MINOR}+ from "
            "https://www.python.org/downloads/",
        )
    return ok


def check_node() -> bool:
    """Verify Node.js is installed and meets minimum version (>= 18)."""
    proc = _run(["node", "--version"])
    if proc is None or proc.returncode != 0:
        _fail(
            "Node.js not found",
            "Install Node.js 18+ from https://nodejs.org/",
        )
        return False

    version_str = proc.stdout.strip().lstrip("v")
    try:
        parts = tuple(int(x) for x in version_str.split("."))
    except (ValueError, TypeError):
        _fail(
            f"Could not parse Node.js version: {proc.stdout.strip()!r}",
            "Check your Node.js installation",
        )
        return False

    ok = parts[0] >= MIN_NODE_MAJOR
    if ok:
        _ok(f"Node.js {version_str} (>= {MIN_NODE_MAJOR}.0.0)")
    else:
        _fail(
            f"Node.js {version_str} is too old",
            f"Upgrade to Node.js {MIN_NODE_MAJOR}+ from https://nodejs.org/",
        )
    return ok


def check_uv() -> bool:
    """Verify uv (Python package manager) is installed."""
    proc = _run(["uv", "--version"])
    if proc is None or proc.returncode != 0:
        _fail(
            "uv not found",
            "Install uv with: pip install uv",
        )
        return False

    version_str = proc.stdout.strip()
    _ok(f"uv {version_str}")
    return True


def check_env_vars() -> bool:
    """Verify required environment variables are set and not placeholders."""
    all_ok = True
    for var_name, description in REQUIRED_ENV_VARS.items():
        value = os.environ.get(var_name)
        if value is None:
            _fail(
                f"{var_name} is not set",
                f"Set the {var_name} environment variable ({description})",
            )
            all_ok = False
        elif _is_placeholder(value):
            _fail(
                f"{var_name} is set to a placeholder value: {value!r}",
                f"Replace the placeholder with a real {description}",
            )
            all_ok = False
        else:
            preview = value[:8] + "..." if len(value) > 12 else value
            _ok(f"{var_name}: {preview}")
    return all_ok


# ---------------------------------------------------------------------------
# API connectivity checks
# ---------------------------------------------------------------------------


def _http_get(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: int = 15,
) -> tuple[int, str]:
    """Perform a GET request and return (status_code, reason)."""
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return (resp.status, "OK")
    except urllib.error.HTTPError as exc:
        return (exc.code, str(exc.reason))
    except urllib.error.URLError as exc:
        return (-1, str(exc.reason))
    except OSError as exc:
        return (-1, str(exc))


def check_nz_legislation_api() -> bool:
    """Verify the NZ Legislation API endpoint is reachable and the API key works."""
    api_key = os.environ.get("NZ_LEGISLATION_API_KEY")
    if api_key is None or _is_placeholder(api_key):
        _fail(
            "NZ Legislation API: skipped (NZ_LEGISLATION_API_KEY not set or "
            "placeholder)",
            "Set NZ_LEGISLATION_API_KEY to your API key for "
            "api.legislation.govt.nz",
        )
        return False

    url = "https://api.legislation.govt.nz/v0/works?limit=1"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    status, reason = _http_get(url, headers=headers)
    if status == 200:
        _ok("NZ Legislation API reachable and credentials accepted")
        return True
    if status in (401, 403):
        _fail(
            f"NZ Legislation API returned HTTP {status} ({reason})",
            "Check that your NZ_LEGISLATION_API_KEY is valid and has not expired",
        )
        return False
    _fail(
        f"NZ Legislation API returned HTTP {status} ({reason})",
        "Check network connectivity or API endpoint status at "
        "https://api.legislation.govt.nz/",
    )
    return False


def check_huggingface_api() -> bool:
    """Verify the Hugging Face API is reachable and HF_TOKEN is valid."""
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token is None or _is_placeholder(hf_token):
        _fail(
            "Hugging Face API: skipped (HF_TOKEN not set or placeholder)",
            "Set HF_TOKEN to your Hugging Face access token "
            "(https://huggingface.co/settings/tokens)",
        )
        return False

    url = "https://huggingface.co/api/whoami-v2"
    headers = {
        "Authorization": f"Bearer {hf_token}",
    }
    status, reason = _http_get(url, headers=headers)
    if status == 200:
        _ok("Hugging Face API reachable and HF_TOKEN is valid")
        return True
    if status == 401:
        _fail(
            "Hugging Face API rejected the token (HTTP 401)",
            "Generate a new token at https://huggingface.co/settings/tokens",
        )
        return False
    _fail(
        f"Hugging Face API returned HTTP {status} ({reason})",
        "Check network connectivity or https://status.huggingface.co/",
    )
    return False


def check_zenodo_api() -> bool:
    """Verify the Zenodo API is reachable and ZENODO_TOKEN is valid."""
    zenodo_token = os.environ.get("ZENODO_TOKEN")
    if zenodo_token is None or _is_placeholder(zenodo_token):
        _fail(
            "Zenodo API: skipped (ZENODO_TOKEN not set or placeholder)",
            "Set ZENODO_TOKEN to your Zenodo API token "
            "(https://zenodo.org/account/settings/tokens/)",
        )
        return False

    # Try production Zenodo first, fallback to sandbox
    for label, base_url in [
        ("Zenodo (production)", "https://zenodo.org/api"),
        ("Zenodo (sandbox)", "https://sandbox.zenodo.org/api"),
    ]:
        url = f"{base_url}/deposit/depositions?size=1"
        headers = {
            "Authorization": f"Bearer {zenodo_token}",
        }
        status, reason = _http_get(url, headers=headers)
        if status == 200:
            _ok(f"{label} API reachable and ZENODO_TOKEN is valid")
            return True
        if status == 401:
            continue  # Try next environment
        _fail(
            f"{label} returned HTTP {status} ({reason})",
            "Check network connectivity or API docs at "
            "https://developers.zenodo.org/",
        )
        return False

    _fail(
        "Zenodo API rejected token on both production and sandbox (HTTP 401)",
        "Generate a new token at "
        "https://zenodo.org/account/settings/tokens/",
    )
    return False


# ---------------------------------------------------------------------------
# Subproject dependency checks
# ---------------------------------------------------------------------------


def check_subproject_manifests() -> bool:
    """Verify each subproject has its required dependency manifests and key deps.

    Scans all entries in SUBPROJECTS, checking that manifest files (package.json,
    pyproject.toml, requirements.txt) exist on disk, and reports missing items.
    Also verifies that key dependencies (ruff, pytest, vitest, etc.) are declared.

    Returns:
        True if all subproject manifests and key deps are present.
    """
    all_ok = True

    for name, info in SUBPROJECTS.items():
        language: str = info["language"]  # type: ignore[assignment]
        manifests: list[str] = info["manifests"]  # type: ignore[assignment]
        key_deps: list[str] = info["key_deps"]  # type: ignore[assignment]

        subproject_path = WORKSPACE_ROOT / name
        if not subproject_path.is_dir():
            _fail(
                f"  {name}: subproject directory not found",
                f"Ensure {subproject_path} exists",
            )
            all_ok = False
            continue

        # Check manifest files exist
        for manifest in manifests:
            manifest_path = subproject_path / manifest
            if manifest_path.is_file():
                _ok(f"{name}: {manifest} found")
            else:
                _fail(
                    f"{name}: missing {manifest}",
                    f"Create {manifest} in {subproject_path}",
                )
                all_ok = False

        # Check key dependencies (basic text scan of manifest files)
        dep_issues = _check_key_deps_in_manifests(
            subproject_path, manifests, language, key_deps
        )
        if dep_issues:
            for dep_name in dep_issues:
                _fail(
                    f"{name}: key dependency {dep_name!r} not found in manifests",
                    f"Add {dep_name} to one of {manifests}",
                )
            all_ok = False
        else:
            _ok(f"{name}: key dependencies present ({', '.join(key_deps)})")

    return all_ok


def _check_key_deps_in_manifests(
    subproject_path: Path,
    manifests: list[str],
    language: str,
    key_deps: list[str],
) -> list[str]:
    """Check that key dependencies are declared in the manifest files.

    Returns a list of missing dependency names (empty list if all present).
    """
    missing: list[str] = []
    manifest_text = ""

    for manifest in manifests:
        mpath = subproject_path / manifest
        if mpath.is_file():
            manifest_text += mpath.read_text(encoding="utf-8", errors="replace")

    if not manifest_text:
        return key_deps  # All are missing if no manifests found

    for dep in key_deps:
        # Simple substring match — sufficient for our scan purposes
        if dep not in manifest_text:
            missing.append(dep)

    return missing


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def check_lockfiles() -> bool:
    """Verify lockfile standardization across the workspace."""
    all_ok = True
    lockfile_policies = {
        "cli-legislation-nz": {"expected": ["pnpm-lock.yaml"], "disallowed": ["uv.lock", "pixi.lock"]},
        "corpus-law-nz": {"expected": ["uv.lock"], "disallowed": ["pixi.lock", "pnpm-lock.yaml"]},
        "corpus-nz-hansard": {"expected": ["uv.lock"], "disallowed": ["pixi.lock", "pnpm-lock.yaml"]},
        "corpus-cases-medilegal-nz": {"expected": ["uv.lock"], "disallowed": ["pixi.lock", "pixi.toml"]},
        "hathi-nz": {"expected": ["pixi.lock"], "disallowed": ["uv.lock", "pnpm-lock.yaml"]},
        "nlp-policy-nz": {"expected": ["pixi.lock"], "disallowed": ["uv.lock", "pnpm-lock.yaml"]},
        "sm-govt-nz": {"expected": ["uv.lock"], "disallowed": ["pixi.lock", "pnpm-lock.yaml"]},
    }
    for name, policy in lockfile_policies.items():
        proj_dir = WORKSPACE_ROOT / name
        if not proj_dir.is_dir():
            continue
        for f in policy["expected"]:
            if not (proj_dir / f).is_file():
                _fail(f"{name}: missing canonical lockfile {f}")
                all_ok = False
        for f in policy["disallowed"]:
            if (proj_dir / f).is_file():
                _fail(f"{name}: found disallowed file {f} (should standardize)")
                all_ok = False
    if all_ok:
        _ok("Lockfiles standard and canonical")
    return all_ok


def run_diagnostics(verbose: bool = False) -> int:
    """Run all diagnostic checks and return exit code."""
    loaded_env = load_workspace_env()
    print("=" * 58)
    print("  NZ Legislation Workspace Doctor")
    print("=" * 58)
    print()

    checks: list[bool] = []

    print("  --- Environment & Runtime ---")
    if verbose and loaded_env:
        print(
            "  Loaded required workspace variables from .env: "
            + ", ".join(sorted(loaded_env))
        )
    checks.append(check_python())
    checks.append(check_node())
    checks.append(check_uv())
    print()

    print("  --- Environment Variables ---")
    checks.append(check_env_vars())
    print()

    print("  --- API Connectivity ---")
    checks.append(check_nz_legislation_api())
    checks.append(check_huggingface_api())
    checks.append(check_zenodo_api())
    print()

    print("  --- Subproject Dependencies ---")
    checks.append(check_subproject_manifests())
    checks.append(check_lockfiles())
    print()

    print("=" * 58)
    total = len(checks)
    passed = sum(1 for c in checks if c)
    failed = total - passed

    if failed == 0:
        print(f"  All {total} check(s) passed!")
    else:
        print(f"  {passed}/{total} passed, {failed} failed")
        print()
        print("  Resolution steps:")
        print("    - Set required environment variables")
        print("    - Install missing tools via the links above")
        print("    - Restart your terminal after making changes")

    print("=" * 58)
    return 0 if failed == 0 else 1


def main() -> NoReturn:
    """Entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    sys.exit(run_diagnostics(verbose))


if __name__ == "__main__":
    main()

