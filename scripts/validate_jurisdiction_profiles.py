"""Validate paired observed Mermaid and BPMN labels in jurisdiction profiles."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "docs" / "jurisdictions"


def labels(profile: Path) -> tuple[set[str], set[str]]:
    text = profile.read_text(encoding="utf-8")
    mermaid = re.search(r"```mermaid\s+(.*?)```", text, re.DOTALL)
    bpmn = re.search(r"```xml\s+(.*?)```", text, re.DOTALL)
    if not mermaid or not bpmn:
        raise ValueError(f"{profile}: paired Mermaid and BPMN blocks are required")
    mermaid_labels = {
        value.strip()
        for value in re.findall(r"\w+\[([^\]]+)\]", mermaid.group(1))
    }
    bpmn_labels = {
        value.strip()
        for value in re.findall(r'name="([^"]+)"', bpmn.group(1))
    }
    if not mermaid_labels or not bpmn_labels:
        raise ValueError(f"{profile}: both representations need activity labels")
    return mermaid_labels, bpmn_labels


def main() -> None:
    profiles = sorted(PROFILE_DIR.glob("*.md"))
    if not profiles:
        raise SystemExit("no jurisdiction profiles found")
    for profile in profiles:
        mermaid, bpmn = labels(profile)
        missing = mermaid - bpmn
        if missing:
            raise SystemExit(f"{profile}: BPMN is missing Mermaid labels: {sorted(missing)}")
        print(f"validated {profile.name}: {len(mermaid)} Mermaid labels paired")


if __name__ == "__main__":
    main()
