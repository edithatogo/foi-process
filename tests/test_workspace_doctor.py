#!/usr/bin/env python3
"""Unit tests for workspace environment, CLI, and API checks.

Verifies that:
- Node.js and npm are installed and meet minimum version requirements.
- Python 3.10+ is installed.
- uv (Python package manager) is installed.
- Required environment variables (NZ_LEGISLATION_API_KEY, HF_TOKEN, ZENODO_TOKEN)
  are defined and not set to placeholder values.

Usage:
    pytest tests/test_workspace_doctor.py -v
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

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
}

MIN_NODE_MAJOR = 18
MIN_PYTHON_MAJOR = 3
MIN_PYTHON_MINOR = 10
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_cli(args: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a CLI command and return the completed process."""
    resolved_args = list(args)
    executable = shutil.which(resolved_args[0])
    if executable is None and os.name == "nt":
        executable = shutil.which(f"{resolved_args[0]}.cmd")
    if executable is not None:
        resolved_args[0] = executable
    return subprocess.run(
        resolved_args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _is_placeholder(value: str) -> bool:
    """Check if an environment variable value is a placeholder."""
    return value.strip().lower() in PLACEHOLDER_VALUES


def _load_required_env_from_dotenv() -> None:
    """Load required test env vars from root .env without exposing values."""
    env_file = WORKSPACE_ROOT / ".env"
    if not env_file.is_file():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name in REQUIRED_ENV_VARS and not os.environ.get(name):
            os.environ[name] = value.strip().strip('"').strip("'")


def _parse_semver(version_str: str, prefix: str = "v") -> tuple[int, ...]:
    """Parse a semver string into a tuple of integers.

    Example: 'v18.15.0' -> (18, 15, 0)
    """
    cleaned = version_str.strip()
    if prefix and cleaned.startswith(prefix):
        cleaned = cleaned[len(prefix) :]
    parts = cleaned.split(".")
    return tuple(int(p) for p in parts)


_load_required_env_from_dotenv()


# ---------------------------------------------------------------------------
# Environment checks
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_python_version_meets_minimum() -> None:
    """Verify the running Python interpreter is >= 3.10."""
    info = sys.version_info
    assert (info.major, info.minor) >= (
        MIN_PYTHON_MAJOR,
        MIN_PYTHON_MINOR,
    ), (
        f"Python {info.major}.{info.minor}.{info.micro} < "
        f"{MIN_PYTHON_MAJOR}.{MIN_PYTHON_MINOR}"
    )


@pytest.mark.unit
def test_nodejs_installed() -> None:
    """Verify Node.js is installed and meets minimum version (>= 18)."""
    result = _run_cli(["node", "--version"])
    assert result.returncode == 0, f"node --version failed: {result.stderr}"

    version = _parse_semver(result.stdout)
    assert len(version) >= 2, f"Could not parse Node.js version: {result.stdout!r}"
    assert version[0] >= MIN_NODE_MAJOR, (
        f"Node.js major version {version[0]} < {MIN_NODE_MAJOR} "
        f"(full: {result.stdout.strip()})"
    )


@pytest.mark.unit
def test_npm_installed() -> None:
    """Verify npm (Node package manager) is installed."""
    result = _run_cli(["npm", "--version"])
    assert result.returncode == 0, f"npm --version failed: {result.stderr}"
    assert result.stdout.strip(), "npm --version returned empty output"


@pytest.mark.unit
def test_uv_installed() -> None:
    """Verify uv (fast Python package manager) is installed."""
    result = _run_cli(["uv", "--version"])
    assert result.returncode == 0, f"uv --version failed: {result.stderr}"
    assert result.stdout.strip(), "uv --version returned empty output"


# ---------------------------------------------------------------------------
# Environment variable checks
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "var_name",
    [
        pytest.param("NZ_LEGISLATION_API_KEY", id="NZ_LEGISLATION_API_KEY"),
        pytest.param("HF_TOKEN", id="HF_TOKEN"),
        pytest.param("ZENODO_TOKEN", id="ZENODO_TOKEN"),
    ],
)
def test_required_env_var_defined(var_name: str) -> None:
    """Verify a required environment variable is defined and not a placeholder."""
    value = os.environ.get(var_name)
    assert value is not None, (
        f"Environment variable {var_name!r} is not set. "
        f"Description: {REQUIRED_ENV_VARS.get(var_name, 'N/A')}"
    )
    assert not _is_placeholder(value), (
        f"Environment variable {var_name!r} is set to a placeholder value: "
        f"{value!r}"
    )


@pytest.mark.unit
def test_all_required_env_vars_documented() -> None:
    """Verify REQUIRED_ENV_VARS covers NZ_LEGISLATION_API_KEY, HF_TOKEN,
    ZENODO_TOKEN."""
    expected = {"NZ_LEGISLATION_API_KEY", "HF_TOKEN", "ZENODO_TOKEN"}
    actual = set(REQUIRED_ENV_VARS.keys())
    missing = expected - actual
    assert not missing, (
        f"REQUIRED_ENV_VARS is missing expected entries: {missing}"
    )


# ---------------------------------------------------------------------------
# Helper to import workspace_doctor module
# ---------------------------------------------------------------------------


def _import_doctor():
    """Import the workspace_doctor module by adding scripts/ to sys.path."""
    scripts_dir = str(WORKSPACE_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import workspace_doctor  # type: ignore[import-untyped]

    return workspace_doctor


# ---------------------------------------------------------------------------
# API connectivity checks
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_check_nz_legislation_api_function_exists() -> None:
    """Verify workspace_doctor exports check_nz_legislation_api()."""
    mod = _import_doctor()
    assert hasattr(mod, "check_nz_legislation_api"), (
        "workspace_doctor missing check_nz_legislation_api()"
    )
    assert callable(mod.check_nz_legislation_api)


@pytest.mark.unit
def test_check_huggingface_api_function_exists() -> None:
    """Verify workspace_doctor exports check_huggingface_api()."""
    mod = _import_doctor()
    assert hasattr(mod, "check_huggingface_api"), (
        "workspace_doctor missing check_huggingface_api()"
    )
    assert callable(mod.check_huggingface_api)


@pytest.mark.unit
def test_check_zenodo_api_function_exists() -> None:
    """Verify workspace_doctor exports check_zenodo_api()."""
    mod = _import_doctor()
    assert hasattr(mod, "check_zenodo_api"), (
        "workspace_doctor missing check_zenodo_api()"
    )
    assert callable(mod.check_zenodo_api)


@pytest.mark.unit
def test_api_check_functions_return_bool() -> None:
    """Verify each API check function returns a bool when env vars are missing."""
    mod = _import_doctor()

    # Temporarily clear the relevant env vars for testing return type
    for var_name in ("NZ_LEGISLATION_API_KEY", "HF_TOKEN", "ZENODO_TOKEN"):
        original = os.environ.pop(var_name, None)
        try:
            result = mod.check_nz_legislation_api()
            assert isinstance(result, bool)
        finally:
            if original is not None:
                os.environ[var_name] = original

    for var_name in ("NZ_LEGISLATION_API_KEY", "HF_TOKEN", "ZENODO_TOKEN"):
        original = os.environ.pop(var_name, None)
        try:
            result = mod.check_huggingface_api()
            assert isinstance(result, bool)
        finally:
            if original is not None:
                os.environ[var_name] = original

    for var_name in ("NZ_LEGISLATION_API_KEY", "HF_TOKEN", "ZENODO_TOKEN"):
        original = os.environ.pop(var_name, None)
        try:
            result = mod.check_zenodo_api()
            assert isinstance(result, bool)
        finally:
            if original is not None:
                os.environ[var_name] = original


@pytest.mark.unit
def test_run_diagnostics_includes_api_checks() -> None:
    """Verify run_diagnostics() includes API connectivity checks in its output."""
    mod = _import_doctor()
    # Mock the check functions to return True so we can verify they're called
    original_nz = mod.check_nz_legislation_api
    original_hf = mod.check_huggingface_api
    original_zen = mod.check_zenodo_api

    call_log = {"nz": False, "hf": False, "zen": False}

    def _mock_nz():
        call_log["nz"] = True
        return True

    def _mock_hf():
        call_log["hf"] = True
        return True

    def _mock_zen():
        call_log["zen"] = True
        return True

    mod.check_nz_legislation_api = _mock_nz
    mod.check_huggingface_api = _mock_hf
    mod.check_zenodo_api = _mock_zen

    try:
        mod.run_diagnostics()
    finally:
        mod.check_nz_legislation_api = original_nz
        mod.check_huggingface_api = original_hf
        mod.check_zenodo_api = original_zen

    assert call_log["nz"], "run_diagnostics did not call check_nz_legislation_api()"
    assert call_log["hf"], "run_diagnostics did not call check_huggingface_api()"
    assert call_log["zen"], "run_diagnostics did not call check_zenodo_api()"


# ---------------------------------------------------------------------------
# Workspace-doctor integration
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_workspace_doctor_script_importable() -> None:
    """Verify the workspace-doctor module is valid Python."""
    doctor_path = WORKSPACE_ROOT / "scripts" / "workspace_doctor.py"

    assert doctor_path.is_file(), (
        f"workspace_doctor.py not found at {doctor_path}"
    )

    source = doctor_path.read_text(encoding="utf-8")
    compile(source, str(doctor_path), "exec")


@pytest.mark.unit
def test_workspace_doctor_runs_without_crash() -> None:
    """Verify workspace_doctor.py runs without raising an exception.

    This is a smoke test — the exit code may be non-zero due to missing
    environment variables, but it should not crash.
    """
    doctor_path = WORKSPACE_ROOT / "scripts" / "workspace_doctor.py"

    result = _run_cli([sys.executable, str(doctor_path)], timeout=30)
    assert result.returncode in (0, 1), (
        f"workspace_doctor.py crashed with return code {result.returncode}:\n"
        f"{result.stderr}"
    )
    assert result.stdout, "workspace_doctor.py produced no output"
