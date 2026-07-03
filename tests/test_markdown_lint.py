#!/usr/bin/env python3
"""Tests for Markdown formatter checks (Vale + markdownlint)."""

from __future__ import annotations
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"

BAD_MD = "# Bad\n\n\n- list\n```py\nx\n```\n## No blank\n_x_\n"
GOOD_MD = "# Good\n\nA paragraph.\n\n```py\nprint()\n```\n\n## Heading\n\n- Item\n"

_MDL_RESOLVED = None


def _resolve_mdl():
    """Resolve markdownlint CLI to a command list for subprocess."""
    global _MDL_RESOLVED
    if _MDL_RESOLVED is not None:
        return _MDL_RESOLVED
    for name in ("markdownlint-cli2", "markdownlint"):
        cand = shutil.which(name)
        if cand:
            _MDL_RESOLVED = [cand]
            return _MDL_RESOLVED
        for ext in (".cmd", ".bat", ".ps1"):
            cand2 = shutil.which(name + ext)
            if cand2:
                if ext == ".ps1":
                    _MDL_RESOLVED = ["powershell", "-File", cand2]
                else:
                    _MDL_RESOLVED = [cand2]
                return _MDL_RESOLVED
    if shutil.which("npx"):
        _MDL_RESOLVED = ["npx", "markdownlint-cli2"]
        return _MDL_RESOLVED
    _MDL_RESOLVED = ["markdownlint-cli2"]
    return _MDL_RESOLVED


def _run_cli(args, timeout=30, cwd=None):
    return subprocess.run(args, capture_output=True, text=True,
                          timeout=timeout,
                          cwd=cwd or str(WORKSPACE_ROOT))


def _import_check_lint():
    sys.path.insert(0, str(SCRIPTS_DIR))
    import check_lint
    return check_lint


def _create_temp_md(content):
    fd, path = tempfile.mkstemp(suffix=".md", prefix="lint_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return Path(path)


@pytest.mark.unit
def test_module_importable():
    mod = _import_check_lint()
    assert hasattr(mod, "run_lint_checks")
    assert hasattr(mod, "check_vale")
    assert hasattr(mod, "check_markdownlint")


@pytest.mark.unit
def test_script_compiles():
    p = SCRIPTS_DIR / "check_lint.py"
    assert p.is_file()
    compile(p.read_text(encoding="utf-8"), str(p), "exec")


@pytest.mark.unit
def test_vale_installed():
    r = _run_cli(["vale", "--version"])
    assert r.returncode == 0
    assert "vale" in r.stdout.lower()


@pytest.mark.unit
def test_vale_config():
    assert (WORKSPACE_ROOT / ".vale.ini").is_file()


@pytest.mark.unit
def test_vale_vocab():
    a = WORKSPACE_ROOT / ".github/styles/Vocab/NZLegal/accept.txt"
    assert a.is_file()
    c = a.read_text(encoding="utf-8")
    assert "Aotearoa" in c


@pytest.mark.unit
def test_vale_spelling():
    tmp = _create_temp_md("# T\n\nzzxzzzxyzzy\n")
    try:
        r = _run_cli(["vale", "--no-wrap", "--no-exit",
                      "--output=line", str(tmp)])
        assert r.returncode == 0
        assert len(r.stdout.strip()) > 0
    finally:
        tmp.unlink(missing_ok=True)


@pytest.mark.unit
def test_mdl_installed():
    cmd = _resolve_mdl()
    r = _run_cli(cmd + ["--version"])
    assert r.returncode == 0
    assert "markdownlint" in r.stdout.lower()


@pytest.mark.unit
def test_mdl_config():
    assert (WORKSPACE_ROOT / ".markdownlint.json").is_file()


@pytest.mark.unit
def test_mdl_detects_issues():
    tmp = _create_temp_md(BAD_MD)
    mdl = _resolve_mdl()
    try:
        r = _run_cli(mdl + ["--config",
                      str(WORKSPACE_ROOT / ".markdownlint.json"),
                      str(tmp)])
        assert r.returncode != 0
    finally:
        tmp.unlink(missing_ok=True)


@pytest.mark.unit
def test_mdl_passes_good():
    tmp = _create_temp_md(GOOD_MD)
    mdl = _resolve_mdl()
    try:
        r = _run_cli(mdl + ["--config",
                      str(WORKSPACE_ROOT / ".markdownlint.json"),
                      str(tmp)])
        assert r.returncode == 0
    finally:
        tmp.unlink(missing_ok=True)


@pytest.mark.unit
def test_lint_funcs_return_bool():
    mod = _import_check_lint()
    assert isinstance(mod.check_vale(verbose=False), bool)
    assert isinstance(mod.check_markdownlint(verbose=False), bool)


@pytest.mark.unit
def test_run_lint_returns_int():
    mod = _import_check_lint()
    r = mod.run_lint_checks(verbose=False)
    assert isinstance(r, int) and r in (0, 1)


@pytest.mark.unit
def test_check_docs_ps1_exists():
    p = SCRIPTS_DIR / "check-docs.ps1"
    assert p.is_file() and p.stat().st_size > 0


@pytest.mark.unit
def test_docs_lint_ci_exists():
    p = WORKSPACE_ROOT / ".github/workflows/docs-lint.yml"
    assert p.is_file() and p.stat().st_size > 0


@pytest.mark.unit
def test_mdl_handles_empty_file():
    tmp = _create_temp_md("")
    mdl = _resolve_mdl()
    try:
        r = _run_cli(mdl + ["--config",
                      str(WORKSPACE_ROOT / ".markdownlint.json"),
                      str(tmp)])
        assert r.returncode in (0, 1)
    finally:
        tmp.unlink(missing_ok=True)


@pytest.mark.unit
def test_vale_handles_empty_file():
    tmp = _create_temp_md("")
    try:
        r = _run_cli(["vale", "--no-wrap", "--no-exit",
                      "--output=line", str(tmp)])
        assert r.returncode == 0
    finally:
        tmp.unlink(missing_ok=True)
