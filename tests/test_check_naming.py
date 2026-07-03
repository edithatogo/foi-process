#!/usr/bin/env python3
"""Unit tests for the naming convention lint script.

Usage:
    pytest tests/test_check_naming.py -v
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = str(WORKSPACE_ROOT / "scripts")


def _import_naming():
    if SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, SCRIPTS_DIR)
    import check_naming
    return check_naming


naming = _import_naming()


# ---------------------------------------------------------------------------
# Data structure tests
# ---------------------------------------------------------------------------


class TestViolation:
    def test_to_dict(self) -> None:
        v = naming.Violation("path/to/file.py", "python-snake-case",
                              "Not snake_case")
        d = v.to_dict()
        assert d == {"path": "path/to/file.py",
                      "rule": "python-snake-case",
                      "message": "Not snake_case"}

    def test_fields(self) -> None:
        v = naming.Violation("a", "b", "c")
        assert v.path == "a"
        assert v.rule == "b"
        assert v.message == "c"


class TestCheckResult:
    def test_passed_no_violations(self) -> None:
        r = naming.CheckResult(passed=True)
        assert r.passed is True
        assert r.violations == []

    def test_failed_with_violations(self) -> None:
        v = naming.Violation("x", "y", "z")
        r = naming.CheckResult(passed=False, violations=[v])
        assert r.passed is False
        assert len(r.violations) == 1

# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_has_spaces_true(self):
        assert naming._has_spaces("my file.py") is True

    def test_has_spaces_false(self):
        assert naming._has_spaces("my_file.py") is False

    @pytest.mark.parametrize("name,expected", [
        ("my_module.py", True),
        ("test_utils.py", True),
        ("__init__.py", False),  # starts with underscore, not pure snake_case
        ("MyModule.py", False),
        ("my-module.py", False),
        ("my module.py", False),
        ("cli.py", True),
    ])
    def test_is_snake_case(self, name, expected):
        assert naming._is_snake_case(name) == expected

    @pytest.mark.parametrize("name,expected", [
        ("my-config.yaml", True),
        ("README.md", False),  # all caps, not kebab-case
        ("pyproject.toml", True),
        ("my_config.yaml", False),
        ("MyConfig.yaml", False),
    ])
    def test_is_kebab_case(self, name, expected):
        assert naming._is_kebab_case(name) == expected

    @pytest.mark.parametrize("name,expected", [
        ("my_dir", True),
        ("my-dir", True),
        ("my_dir_name", True),
        ("MyDir", False),
        ("my dir", False),
    ])
    def test_is_valid_dir_name(self, name, expected):
        assert naming._is_valid_dir_name(name) == expected

    def test_to_snake_case(self):
        assert naming._to_snake_case("my-file.py") == "my_file.py"
        assert naming._to_snake_case("MyModule.py") == "mymodule.py"

    def test_to_kebab_case(self):
        assert naming._to_kebab_case("my_file.yaml") == "my-file.yaml"


# ---------------------------------------------------------------------------
# Integration: checks on temporary directories
# ---------------------------------------------------------------------------


class TestChecksOnTempDir:
    """Run checks against small temporary directory trees."""

    def _make_temp(self, structure):
        tmp = Path(tempfile.mkdtemp())
        for rel, content in structure.items():
            full = tmp / rel
            full.parent.mkdir(parents=True, exist_ok=True)
            if content is None:
                full.mkdir(parents=True, exist_ok=True)
            else:
                full.write_text(content, encoding="utf-8")
        return tmp

    def test_check_spaces_no_violations(self):
        tmp = self._make_temp({"good_file.py": "x"})
        assert naming.check_spaces(tmp).passed is True

    def test_check_spaces_with_spaces(self):
        tmp = self._make_temp({"bad file.py": "x"})
        r = naming.check_spaces(tmp)
        assert r.passed is False

    def test_check_python_filenames_snake(self):
        tmp = self._make_temp({"my_module.py": "x"})
        assert naming.check_python_filenames(tmp).passed is True

    def test_check_python_filenames_non_snake(self):
        tmp = self._make_temp({"MyModule.py": "x"})
        assert naming.check_python_filenames(tmp).passed is False

    def test_check_python_filenames_exempt(self):
        tmp = self._make_temp({"__init__.py": "x", "conftest.py": "x"})
        assert naming.check_python_filenames(tmp).passed is True

    def test_check_fixture_dirs_correct(self):
        tmp = self._make_temp({"fixtures/file.txt": "x"})
        assert naming.check_fixture_dirs(tmp).passed is True

    def test_check_fixture_dirs_wrong(self):
        tmp = self._make_temp({"test_fixtures/file.txt": "x"})
        assert naming.check_fixture_dirs(tmp).passed is False

    def test_check_test_filenames_good(self):
        tmp = self._make_temp({"tests/test_good.py": "x"})
        assert naming.check_test_filenames(tmp).passed is True

    def test_check_test_filenames_bad(self):
        tmp = self._make_temp({"tests/helper.py": "x"})
        assert naming.check_test_filenames(tmp).passed is False

    def test_check_directory_names_good(self):
        tmp = self._make_temp({"my_dir/file.txt": "x"})
        assert naming.check_directory_names(tmp).passed is True

    def test_check_directory_names_bad(self):
        tmp = self._make_temp({"MyDir/file.txt": "x"})
        assert naming.check_directory_names(tmp).passed is False


# ---------------------------------------------------------------------------
# Integration: run_all_checks
# ---------------------------------------------------------------------------


class TestRunAllChecks:
    def test_returns_int(self):
        code = naming.run_all_checks(json_output=True)
        assert isinstance(code, int)
        assert code in (0, 1)

    def test_json_output(self, capsys):
        naming.run_all_checks(json_output=True)
        captured = capsys.readouterr()
        import json
        data = json.loads(captured.out)
        assert "summary" in data
        assert "total_violations" in data["summary"]
        assert "passed" in data["summary"]

