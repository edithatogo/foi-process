#!/usr/bin/env python3
"""Fail closed when code-release workflow safety invariants drift."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
FULL_SHA_USE = re.compile(r"^\s*-?\s*uses:\s*[^@\s]+@([0-9a-f]{40})(?:\s+#.*)?$", re.MULTILINE)
ANY_USE = re.compile(r"^\s*-?\s*uses:\s*[^@\s]+@([^\s]+)", re.MULTILINE)


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = (
        "branches: [main]",
        "contents: read",
        "pull-requests: write",
        "skip-github-release",
        "gh release create \"$release_tag\" --draft",
        "python scripts/check_release_commit_subject.py",
        ".object.sha)\" = \"$GITHUB_SHA\"",
        "scripts/check_release_metadata.py",
        "scripts/build_release_evidence.py",
        "scripts/verify_release_evidence.py",
        "actions/attest-build-provenance@",
        "gh workflow run ci.yml",
        "gh workflow run security-fuzz.yml",
        "-f mode=pr-smoke",
        ".headBranchName // empty",
    )
    missing = [fragment for fragment in required if fragment not in text]
    if missing:
        raise AssertionError("release workflow safety contract missing: " + ", ".join(missing))
    if "workflow_dispatch:" in text or "pull_request:" in text:
        raise AssertionError("release publication controller must run only after a main push")
    if "--slurp" in text:
        raise AssertionError("release lookup must remain compatible with the runner gh version")

    uses = ANY_USE.findall(text)
    pinned = FULL_SHA_USE.findall(text)
    if not uses or len(uses) != len(pinned):
        raise AssertionError("every release workflow action must use a full commit SHA")
    if text.index("Attest release evidence") > text.index("Publish the verified draft release"):
        raise AssertionError("release publication must follow evidence attestation")
    print("Release workflow safety contract passed.")


if __name__ == "__main__":
    main()
