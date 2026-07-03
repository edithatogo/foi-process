#!/usr/bin/env python3
"""Workspace-wide naming convention lint checker."""
from __future__ import annotations
import json, os, re, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import NoReturn

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

IGNORE_DIRS = {".git", ".swarm", "node_modules", ".pytest_cache",
    "__pycache__", ".venv", "venv", "env", ".ruff_cache", ".mypy_cache",
    ".pyright", ".hypothesis", ".uv-cache", ".changeset", ".husky",
    "dist", "build", ".devcontainer", "lancedb_data", ".antigravitycli",
    "data", "derived", "generated", "parquet", "raw_xml", "raw",
    "processed", "manifests", "seeds", "archive", "dist/archive",
    ".tmp", "historical_archive",
    "historical_archive_normalized", "historical_archive_raw",
    "profile_archive", "lancedb_data", "output", "spaces",
    "test_export.csv", "benchmarks", "integrations",
    "distribution", "examples", "scratch", "schemas"}

KEBAB_CASE_EXTENSIONS = {".yaml", ".yml", ".md", ".json", ".toml",
    ".ini", ".cfg", ".jsonl"}

EXEMPT_FILES = {"__init__.py", "__main__.py", "conftest.py",
    ".gitignore", ".gitattributes", ".env.example", ".env.local",
    ".markdownlint.json", ".prettierrc", ".prettierignore",
    ".eslintrc.json", ".lintstagedrc.json", ".gitkeep", ".dockerignore",
    "Dockerfile", "Makefile", "LICENSE", "CACHEDIR.TAG"}

EXEMPT_PREFIXES = ("-", "_")
VALID_FIXTURE_DIRS = {"fixtures"}

_SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*\.[a-z0-9]+$")
_KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*\.[a-z0-9.]+$")
_DIR_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$|^[a-z][a-z0-9]*(_[a-z0-9]+)*$")

@dataclass
class Violation:
    path: str; rule: str; message: str
    def to_dict(self): return {"path": self.path, "rule": self.rule, "message": self.message}

@dataclass
class CheckResult:
    passed: bool
    violations: list[Violation] = field(default_factory=list)

def _skip_path(rp): return any(p in IGNORE_DIRS for p in rp.parts)
def _has_spaces(n): return " " in n
def _is_snake_case(n): return bool(_SNAKE_CASE_RE.match(n))
def _is_kebab_case(n): return bool(_KEBAB_CASE_RE.match(n))
def _is_valid_dir_name(n):
    if n.startswith("."): return True
    return bool(_DIR_NAME_RE.match(n))

def _to_snake_case(name):
    stem, ext = Path(name).stem, Path(name).suffix
    return re.sub(r"[- ]", "_", stem).lower() + ext

def _to_kebab_case(name):
    stem = Path(name).stem
    sfx = Path(name).suffixes
    k = re.sub(r"[_ ]", "-", stem).lower()
    return k + (sfx[-1] if len(sfx) > 1 else (sfx[0] if sfx else ""))


def _walk(root):
    """Walk with os.walk pruning ignored/huge dirs."""
    for dirpath, dirnames, filenames in os.walk(str(root)):
        rel = Path(dirpath).relative_to(root)
        parts = set(rel.parts)
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith('.') and d != '__pycache__']
        yield rel, dirnames, filenames

def check_spaces(root=WORKSPACE_ROOT):
    v = []
    for rel, dirnames, filenames in _walk(root):
        for name in dirnames + filenames:
            if _has_spaces(name):
                p = str((rel / name).as_posix())
                v.append(Violation(p, "no-spaces",
                    f"Path contains spaces: {name!r}"))
    return CheckResult(len(v)==0, v)

def check_python_filenames(root=WORKSPACE_ROOT):
    v = []
    for rel, dirnames, filenames in _walk(root):
        for name in filenames:
            if not name.endswith('.py'): continue
            if name in EXEMPT_FILES or name.startswith(EXEMPT_PREFIXES): continue
            if not _is_snake_case(name):
                p = str((rel / name).as_posix())
                v.append(Violation(p, "python-snake-case",
                    f"Python file not snake_case: {name!r}"))
    return CheckResult(len(v)==0, v)

def check_config_doc_filenames(root=WORKSPACE_ROOT):
    v = []
    for rel, dirnames, filenames in _walk(root):
        for name in filenames:
            ext = Path(name).suffix.lower()
            if ext not in KEBAB_CASE_EXTENSIONS: continue
            if name in EXEMPT_FILES or name.startswith(EXEMPT_PREFIXES): continue
            if name.startswith("."):
                if not _is_kebab_case(name.lstrip(".")):
                    p = str((rel / name).as_posix())
                    v.append(Violation(p, "config-kebab-case",
                        f"Config/doc file not kebab-case: {name!r}"))
                continue
            if not _is_kebab_case(name):
                p = str((rel / name).as_posix())
                v.append(Violation(p, "config-kebab-case",
                    f"Config/doc file not kebab-case: {name!r}"))
    return CheckResult(len(v)==0, v)


def check_fixture_dirs(root=WORKSPACE_ROOT):
    v = []
    seen = set()
    for rel, dirnames, filenames in _walk(root):
        for name in dirnames:
            nl = name.lower()
            if "fixture" in nl and nl not in VALID_FIXTURE_DIRS:
                p = str((rel / name).as_posix())
                if p not in seen:
                    seen.add(p)
                    v.append(Violation(p, "fixture-dir-name",
                        f"Fixture dir should be 'fixtures/', not {name!r}"))
    return CheckResult(len(v)==0, v)

def check_test_filenames(root=WORKSPACE_ROOT):
    v = []
    for rel, dirnames, filenames in _walk(root):
        if "tests" in rel.parts or rel.name == "tests" or any(d == "tests" for d in rel.parts):
            for name in filenames:
                if not name.endswith('.py'): continue
                if name in EXEMPT_FILES: continue
                if not name.startswith("test_"):
                    p = str((rel / name).as_posix())
                    v.append(Violation(p, "test-file-pattern",
                        f"Test file should start with 'test_': {name!r}"))
    return CheckResult(len(v)==0, v)

def check_directory_names(root=WORKSPACE_ROOT):
    v = []
    for rel, dirnames, filenames in _walk(root):
        for name in dirnames:
            if name.startswith("."): continue
            if not _is_valid_dir_name(name):
                p = str((rel / name).as_posix())
                v.append(Violation(p, "dir-name-format",
                    f"Dir name should be snake_case or kebab-case: {name!r}"))
    return CheckResult(len(v)==0, v)

def check_subproject_dirs(root=WORKSPACE_ROOT):
    v = []
    skip = IGNORE_DIRS | {"logs", "tests", "scripts", "conductor", "test-tmp"}
    for e in root.iterdir():
        if not e.is_dir() or e.name.startswith(".") or e.name in skip: continue
        if not (e/"pyproject.toml").exists() and not (e/"package.json").exists(): continue
        if not re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", e.name):
            v.append(Violation(e.name, "subproject-dir-kebab",
                f"Subproject dir should be kebab-case: {e.name!r}"))
    return CheckResult(len(v)==0, v)

def run_all_checks(root=WORKSPACE_ROOT, verbose=False, json_output=False):
    checks = [
        ("No spaces in paths", check_spaces(root)),
        ("Python files snake_case", check_python_filenames(root)),
        ("Config/doc files kebab-case", check_config_doc_filenames(root)),
        ("Fixture directory names", check_fixture_dirs(root)),
        ("Test file patterns (test_*.py)", check_test_filenames(root)),
        ("Directory name format", check_directory_names(root)),
        ("Subproject dir kebab-case", check_subproject_dirs(root)),
    ]
    tv = 0
    if json_output:
        out = {}
        for t, r in checks:
            out[t] = {"passed": r.passed, "violations": [x.to_dict() for x in r.violations]}
            tv += len(r.violations)
        out["summary"] = {"total_violations": tv, "passed": tv == 0}
        print(json.dumps(out, indent=2))
        return 0 if tv == 0 else 1

    print("="*58)
    print("  NZ Legislation Workspace - Naming Convention Check")
    print("="*58)
    print()
    for t, r in checks:
        print(f"  --- {t} ---")
        if r.passed:
            print("  [PASS]  OK")
        else:
            for x in r.violations:
                print(f"  [FAIL]  {x.path}")
                print(f"          Rule: {x.rule}")
                if verbose: print(f"          {x.message}")
            tv += len(r.violations)
        print()
    print("="*58)
    if tv == 0:
        print(f"  All {len(checks)} naming check(s) passed!")
    else:
        print(f"  {tv} naming violation(s) found.")
        print()
        print("  Quick reference:")
        print("    - Python files -> snake_case")
        print("    - Config/docs  -> kebab-case")
        print("    - No spaces    -> use hyphens or underscores")
        print("    - Fixture dirs -> always 'fixtures/'")
        print("    - Test files   -> always start with 'test_'")
        print("    - Subprojects  -> kebab-case")
    print("="*58)
    return 0 if tv == 0 else 1

def main():
    v = "--verbose" in sys.argv or "-v" in sys.argv
    j = "--json" in sys.argv
    sys.exit(run_all_checks(verbose=v, json_output=j))

if __name__ == "__main__":
    main()
