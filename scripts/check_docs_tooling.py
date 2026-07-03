#!/usr/bin/env python
"""Flag new non-Astro documentation-site frameworks in mapped repos."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DISALLOWED_DEFAULT = {
    "docusaurus": ("package.json", "@docusaurus"),
    "mkdocs": ("mkdocs.yml", ""),
    "sphinx": ("conf.py", "sphinx"),
    "vitepress": ("package.json", "vitepress"),
    "nextra": ("package.json", "nextra"),
    "vuepress": ("package.json", "vuepress"),
    "docsify": ("package.json", "docsify"),
    "mintlify": ("mint.json", ""),
}

CHECK_LOCATIONS = (
    "package.json",
    "docs/package.json",
    "docs-site/package.json",
    "mkdocs.yml",
    "docs/mkdocs.yml",
    "docs-site/mkdocs.yml",
    "conf.py",
    "docs/conf.py",
    "docs-site/conf.py",
    "mint.json",
    "docs/mint.json",
    "docs-site/mint.json",
)


def _load_repos(root: Path) -> list[Path]:
    baseline_path = root / "conductor" / "templates" / "astro-plugin-baseline.json"
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    repos = []
    for repo_id in data.get("repositories", {}):
        path = root if repo_id == "legal-nz" else root / repo_id
        if path.exists():
            repos.append(path)
    return repos


def _has_marker(path: Path, marker: str) -> bool:
    if not marker:
        return path.exists()
    if not path.exists() or not path.is_file():
        return False
    return marker.lower() in path.read_text(encoding="utf-8", errors="ignore").lower()


def find_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for repo in _load_repos(root):
        for framework, (filename, marker) in DISALLOWED_DEFAULT.items():
            for location in CHECK_LOCATIONS:
                candidate = repo / location
                if candidate.name != filename:
                    continue
                if _has_marker(candidate, marker):
                    rel = candidate.relative_to(root)
                    violations.append(f"{rel}: disallowed docs-site framework '{framework}'")
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    violations = find_violations(args.root.resolve())
    if violations:
        print("\n".join(violations))
        return 1
    print("No disallowed docs-site frameworks detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
