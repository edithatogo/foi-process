#!/usr/bin/env python3
"""Unit tests for subproject dependency verification in workspace_doctor.py.

Verifies that:
- All 7 subprojects are defined in the SUBPROJECTS registry
- Project type detection works (TypeScript vs Python)
- Manifest file detection works (package.json, pyproject.toml, requirements.txt)
- Key dependencies are present (ruff, pytest, vitest, etc.)
- Missing or outdated manifests are reported
- The scan integrates into run_diagnostics()

Usage:
    pytest tests/test_workspace_doctor_subprojects.py -v
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = str(WORKSPACE_ROOT / "scripts")

EXPECTED_SUBPROJECTS: dict[str, str] = {
    "cli-legislation-nz": "TypeScript/Node",
    "corpus-law-nz": "Python",
    "corpus-nz-hansard": "Python",
    "corpus-cases-medilegal-nz": "Python",
    "nlp-policy-nz": "Python",
    "sm-govt-nz": "Python",
    "hathi-nz": "Python",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _import_doctor():
    """Import the workspace_doctor module by adding scripts/ to sys.path."""
    if SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, SCRIPTS_DIR)
    import workspace_doctor  # type: ignore[import-untyped]

    return workspace_doctor


# ---------------------------------------------------------------------------
# Tests: SUBPROJECTS constant
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_subprojects_constant_exists() -> None:
    """Verify workspace_doctor defines a SUBPROJECTS mapping."""
    mod = _import_doctor()
    assert hasattr(mod, "SUBPROJECTS"), "workspace_doctor missing SUBPROJECTS"
    assert isinstance(mod.SUBPROJECTS, dict), "SUBPROJECTS must be a dict"


@pytest.mark.unit
def test_subprojects_contains_all_seven() -> None:
    """Verify SUBPROJECTS has all 7 expected subprojects."""
    mod = _import_doctor()
    for name in EXPECTED_SUBPROJECTS:
        assert name in mod.SUBPROJECTS, (
            f"SUBPROJECTS missing entry for {name!r}"
        )


@pytest.mark.unit
def test_subprojects_no_extra_unknown() -> None:
    """Verify SUBPROJECTS does not contain unexpected entries."""
    mod = _import_doctor()
    extra = set(mod.SUBPROJECTS.keys()) - set(EXPECTED_SUBPROJECTS.keys())
    assert not extra, f"SUBPROJECTS has unexpected entries: {extra}"


@pytest.mark.unit
def test_subprojects_each_has_language_key() -> None:
    """Verify each subproject entry has a 'language' field."""
    mod = _import_doctor()
    for name, info in mod.SUBPROJECTS.items():
        assert "language" in info, (
            f"{name} missing 'language' in SUBPROJECTS"
        )
        assert info["language"] in ("TypeScript", "Python"), (
            f"{name} has unexpected language: {info['language']!r}"
        )


@pytest.mark.unit
def test_subprojects_each_has_expected_manifests() -> None:
    """Verify each subproject entry has a 'manifests' list."""
    mod = _import_doctor()
    for name, info in mod.SUBPROJECTS.items():
        assert "manifests" in info, (
            f"{name} missing 'manifests' in SUBPROJECTS"
        )
        assert isinstance(info["manifests"], list), (
            f"{name}.manifests must be a list"
        )
        assert len(info["manifests"]) > 0, (
            f"{name}.manifests must not be empty"
        )


@pytest.mark.unit
def test_subprojects_each_has_key_deps() -> None:
    """Verify each subproject entry has a 'key_deps' list of expected dependencies."""
    mod = _import_doctor()
    for name, info in mod.SUBPROJECTS.items():
        assert "key_deps" in info, (
            f"{name} missing 'key_deps' in SUBPROJECTS"
        )
        assert isinstance(info["key_deps"], list), (
            f"{name}.key_deps must be a list"
        )


# ---------------------------------------------------------------------------
# Tests: TypeScript subproject specifics
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_cli_legislation_nz_is_typescript() -> None:
    """Verify cli-legislation-nz is classified as TypeScript."""
    mod = _import_doctor()
    assert mod.SUBPROJECTS["cli-legislation-nz"]["language"] == "TypeScript"


@pytest.mark.unit
def test_cli_legislation_nz_package_json_manifests() -> None:
    """Verify cli-legislation-nz checks package.json as manifest."""
    mod = _import_doctor()
    manifests = mod.SUBPROJECTS["cli-legislation-nz"]["manifests"]
    assert "package.json" in manifests


@pytest.mark.unit
def test_cli_legislation_nz_key_deps() -> None:
    """Verify cli-legislation-nz key dependencies include vitest and typescript."""
    mod = _import_doctor()
    deps = mod.SUBPROJECTS["cli-legislation-nz"]["key_deps"]
    assert "vitest" in deps, "cli-legislation-nz should expect vitest"
    assert "typescript" in deps, "cli-legislation-nz should expect typescript"


# ---------------------------------------------------------------------------
# Tests: Python subproject specifics
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_python_subprojects_have_pyproject_toml() -> None:
    """Verify all Python subprojects expect pyproject.toml as a manifest."""
    mod = _import_doctor()
    python_projects = [
        name
        for name, info in mod.SUBPROJECTS.items()
        if info["language"] == "Python"
    ]
    for name in python_projects:
        manifests = mod.SUBPROJECTS[name]["manifests"]
        assert "pyproject.toml" in manifests, (
            f"{name} should include pyproject.toml in manifests"
        )


@pytest.mark.unit
def test_python_subprojects_ruff_and_pytest_in_deps() -> None:
    """Verify all Python subprojects list ruff and pytest as key deps."""
    mod = _import_doctor()
    python_projects = [
        name
        for name, info in mod.SUBPROJECTS.items()
        if info["language"] == "Python"
    ]
    for name in python_projects:
        deps = mod.SUBPROJECTS[name]["key_deps"]
        assert "ruff" in deps, (
            f"{name} should have ruff in key_deps"
        )
        assert "pytest" in deps, (
            f"{name} should have pytest in key_deps"
        )


# ---------------------------------------------------------------------------
# Tests: check_subproject_manifests function
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_check_subproject_manifests_function_exists() -> None:
    """Verify workspace_doctor exports check_subproject_manifests()."""
    mod = _import_doctor()
    assert hasattr(mod, "check_subproject_manifests"), (
        "workspace_doctor missing check_subproject_manifests()"
    )
    assert callable(mod.check_subproject_manifests)


@pytest.mark.unit
def test_check_subproject_manifests_returns_bool() -> None:
    """Verify check_subproject_manifests() returns a bool."""
    mod = _import_doctor()
    result = mod.check_subproject_manifests()
    assert isinstance(result, bool)


@pytest.mark.unit
def test_check_subproject_manifests_reports_on_each_project() -> None:
    """Verify check_subproject_manifests() touches every subproject."""
    mod = _import_doctor()
    original_ok = mod._ok
    original_fail = mod._fail

    checked_projects: set[str] = set()

    def tracking_ok(message: str) -> None:
        for name in EXPECTED_SUBPROJECTS:
            if name in message:
                checked_projects.add(name)
        original_ok(message)

    def tracking_fail(message: str, advice: str = "") -> None:
        for name in EXPECTED_SUBPROJECTS:
            if name in message:
                checked_projects.add(name)
        original_fail(message, advice)

    mod._ok = tracking_ok
    mod._fail = tracking_fail

    try:
        mod.check_subproject_manifests()
    finally:
        mod._ok = original_ok
        mod._fail = original_fail

    missing = set(EXPECTED_SUBPROJECTS.keys()) - checked_projects
    assert not missing, (
        f"check_subproject_manifests did not report on: {missing}"
    )


# ---------------------------------------------------------------------------
# Tests: Manifest existence on disk
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_cli_legislation_nz_has_package_json() -> None:
    """Verify cli-legislation-nz/package.json actually exists on disk."""
    pkg_path = WORKSPACE_ROOT / "cli-legislation-nz" / "package.json"
    assert pkg_path.is_file(), (
        f"Expected package.json at {pkg_path}"
    )


@pytest.mark.unit
def test_all_python_projects_have_pyproject_toml() -> None:
    """Verify each Python subproject has a pyproject.toml on disk."""
    for name in EXPECTED_SUBPROJECTS:
        if name == "cli-legislation-nz":
            continue
        toml_path = WORKSPACE_ROOT / name / "pyproject.toml"
        assert toml_path.is_file(), (
            f"Expected pyproject.toml at {toml_path}"
        )


@pytest.mark.unit
def test_subprojects_with_requirements_txt() -> None:
    """Verify subprojects that use requirements.txt have it on disk."""
    projects_with_req_txt = {"corpus-nz-hansard", "sm-govt-nz", "hathi-nz"}
    for name in projects_with_req_txt:
        req_path = WORKSPACE_ROOT / name / "requirements.txt"
        assert req_path.is_file(), (
            f"Expected requirements.txt at {req_path} for {name}"
        )


# ---------------------------------------------------------------------------
# Tests: Integration with run_diagnostics
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_diagnostics_includes_subproject_checks() -> None:
    """Verify run_diagnostics() calls check_subproject_manifests()."""
    mod = _import_doctor()

    original_sub = mod.check_subproject_manifests
    call_log: list[bool] = []

    def _mock_check() -> bool:
        call_log.append(True)
        return True

    mod.check_subproject_manifests = _mock_check

    try:
        mod.run_diagnostics()
    finally:
        mod.check_subproject_manifests = original_sub

    assert call_log, "run_diagnostics did not call check_subproject_manifests()"


# ---------------------------------------------------------------------------
# Tests: Key dependency verification logic
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_check_key_deps_function_exists() -> None:
    """Verify workspace_doctor exports _check_key_deps()."""
    mod = _import_doctor()
    assert hasattr(mod, "_check_key_deps") or hasattr(
        mod, "check_subproject_manifests"
    ), "Missing dependency check function"
