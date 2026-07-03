#!/usr/bin/env python3
"""
workspace-doctor.py - NZ Legislation Workspace Diagnostics

Checks Python (>=3.11), Node (>=18), pnpm, env vars, subproject files.

Usage:
    python workspace-doctor.py [--verbose]
"""

import os, sys, subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent

REQUIRED_ENV_VARS = {
    "NZ_LEGISLATION_API_KEY": "API key for NZ Legislation API",
    "HF_TOKEN": "Hugging Face authentication token",
    "ZENODO_TOKEN": "Zenodo API token",
}

SUBPROJECTS = {
    "cli-legislation-nz": {"type": "TypeScript", "key_files": ["package.json", "tsconfig.json", ".vale.ini"]},
    "corpus-law-nz": {"type": "Python", "key_files": ["pyproject.toml", ".vale.ini", "Makefile"]},
    "corpus-nz-hansard": {"type": "Python", "key_files": ["pyproject.toml", ".vale.ini", "Makefile"]},
    "corpus-cases-medilegal-nz": {"type": "Python", "key_files": ["pyproject.toml", ".vale.ini"]},
    "hathi-nz": {"type": "Python", "key_files": ["pyproject.toml", ".vale.ini"]},
    "nlp-policy-nz": {"type": "Python", "key_files": ["pyproject.toml", ".vale.ini"]},
    "sm-govt-nz": {"type": "Python", "key_files": [".vale.ini", "requirements.txt"]},
}


def load_workspace_env():
    """Load required variables from root .env when process env is unset."""
    env_file = WORKSPACE / ".env"
    loaded = []
    if not env_file.is_file():
        return loaded
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name in REQUIRED_ENV_VARS and not os.environ.get(name):
            os.environ[name] = value.strip().strip('"').strip("'")
            loaded.append(name)
    return loaded


def check_python_version(verbose):
    v = sys.version_info
    ok = v.major >= 3 and v.minor >= 11
    print(f"  [ {'OK' if ok else 'FAIL'} ] Python: {v.major}.{v.minor}.{v.micro} (need >= 3.11)")
    return ok


def check_node_version(verbose):
    try:
        shell = os.name == "nt"
        r = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=10, shell=shell)
        ver = r.stdout.strip().lstrip("v")
        parts = tuple(int(x) for x in ver.split("."))
        ok = parts >= (18, 0, 0)
        print(f"  [ {'OK' if ok else 'FAIL'} ] Node.js: {ver} (need >= 18.0.0)")
        return ok
    except FileNotFoundError:
        print("  [ FAIL ] Node.js: NOT FOUND")
        return False
    except Exception as e:
        print(f"  [ FAIL ] Node.js: {e}")
        return False


def check_pnpm(verbose):
    try:
        shell = os.name == "nt"
        r = subprocess.run(["pnpm", "--version"], capture_output=True, text=True, timeout=10, shell=shell)
        print(f"  [ OK ] pnpm: {r.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("  [ WARN ] pnpm: NOT FOUND")
        return False
    except Exception as e:
        print(f"  [ WARN ] pnpm: {e}")
        return False


def check_env_vars(verbose):
    all_ok = True
    for var, desc in REQUIRED_ENV_VARS.items():
        val = os.environ.get(var)
        if val and val not in {
            "your_api_key_here",
            "your_hf_token_here",
            "your_zenodo_token_here",
            "placeholder",
            "changeme",
        }:
            if verbose:
                preview = val[:8] + "..." if len(val) > 12 else val
                print(f"  [ OK ] {var}: {preview}")
        else:
            print(f"  [ WARN ] {var}: not set ({desc})")
            all_ok = False
    return all_ok


def check_subprojects(verbose):
    results = {}
    for name, info in SUBPROJECTS.items():
        proj_dir = WORKSPACE / name
        if not proj_dir.is_dir():
            print(f"  [ FAIL ] {name}: directory not found")
            results[name] = {"status": "missing"}
            continue
        missing = [kf for kf in info["key_files"] if not (proj_dir / kf).is_file()]
        if missing:
            print(f"  [ WARN ] {name}: missing {', '.join(missing)}")
            results[name] = {"status": "partial", "missing": missing}
        else:
            print(f"  [ OK ] {name} ({info['type']})")
            results[name] = {"status": "ok"}
    return results


def check_vale_styles(verbose):
    all_ok = True
    for name in SUBPROJECTS:
        sd = WORKSPACE / name / ".github" / "styles"
        if sd.is_dir() and not list(sd.rglob("*.yml")):
            print(f"  [ WARN ] {name}: styles dir exists but empty")
            all_ok = False
    return all_ok


def check_lockfiles(verbose):
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
        proj_dir = WORKSPACE / name
        if not proj_dir.is_dir():
            continue
        for f in policy["expected"]:
            if not (proj_dir / f).is_file():
                print(f"  [ WARN ] {name}: missing canonical lockfile {f}")
                all_ok = False
        for f in policy["disallowed"]:
            if (proj_dir / f).is_file():
                print(f"  [ WARN ] {name}: found disallowed file {f} (should standardize)")
                all_ok = False
    if all_ok:
        print("  [ OK ] Lockfiles standard and canonical")
    return all_ok


def run_diagnostics(verbose=False):
    loaded_env = load_workspace_env()
    print("=" * 60)
    print("  NZ Legislation Workspace Doctor")
    print("=" * 60)
    print()

    checks = []

    print("--- Environment ---")
    if verbose and loaded_env:
        print(f"  [ OK ] Loaded required vars from .env: {', '.join(sorted(loaded_env))}")
    checks.append(check_python_version(verbose))
    checks.append(check_node_version(verbose))
    checks.append(check_pnpm(verbose))
    checks.append(check_env_vars(verbose))
    print()

    print("--- Subprojects ---")
    sub_results = check_subprojects(verbose)
    print()

    print("--- Quality Tooling ---")
    checks.append(check_vale_styles(verbose))
    checks.append(check_lockfiles(verbose))
    print()

    print("=" * 60)
    ok_count = sum(1 for c in checks if c)
    warn_count = sum(1 for c in checks if not c)
    print(f"  Results: {ok_count} passed, {warn_count} warnings/issues")

    ok_sp = sum(1 for r in sub_results.values() if r["status"] == "ok")
    partial_sp = sum(1 for r in sub_results.values() if r["status"] == "partial")
    total_sp = len(sub_results)
    print(f"  Subprojects: {ok_sp} ok, {partial_sp} partial, "
          f"{total_sp - ok_sp - partial_sp} missing")
    print("=" * 60)
    return 0 if warn_count == 0 else 1


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    sys.exit(run_diagnostics(verbose))
