#!/usr/bin/env python3
"""Validate the bounded event-log registry evidence contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "registry-readiness.md"
README = ROOT / "README.md"
HF_BUILDER = ROOT / "scripts" / "build_hf_dataset.py"
REGISTRY_BUILDER = ROOT / "scripts" / "build_registry_metadata.py"

REQUIRED_EVIDENCE = (
    "10.5281/zenodo.21660296",
    "be5337073cd4a2868e1ac812087b9d6d962f2570",
    "foi-process-event-logs",
    "Croissant",
    "full-corpus",
    "license: other",
    "#63",
)


def check() -> None:
    text = DOC.read_text(encoding="utf-8")
    missing = [fragment for fragment in REQUIRED_EVIDENCE if fragment not in text]
    if missing:
        raise AssertionError("Registry evidence document missing: " + ", ".join(missing))

    if "event-log" not in README.read_text(encoding="utf-8"):
        raise AssertionError("README does not document the event-log publication surface")

    builder = HF_BUILDER.read_text(encoding="utf-8")
    for fragment in ("license: other", "foi-process-event-logs"):
        if fragment not in builder:
            raise AssertionError(f"Hugging Face builder missing {fragment!r}")

    registry_builder = REGISTRY_BUILDER.read_text(encoding="utf-8")
    required_registry_fragments = (
        "docs/source-rights-and-licensing.md",
        "validate_source_rights",
        "production-derived registry metadata requires reviewed source rights",
    )
    for fragment in required_registry_fragments:
        if fragment not in registry_builder:
            raise AssertionError(f"Registry builder missing {fragment!r}")


if __name__ == "__main__":
    check()
    print("Bounded event-log registry evidence contract passed.")
