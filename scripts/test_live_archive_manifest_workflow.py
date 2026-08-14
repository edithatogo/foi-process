#!/usr/bin/env python3
"""Static safety contract for the live archive acceptance workflow."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    workflow = (ROOT / ".github" / "workflows" / "live_archive_manifest_acceptance.yml").read_text(
        encoding="utf-8"
    )
    required = (
        "benchmark_only:",
        "benchmark_only requires workflow_dispatch",
        "Recurring acceptance skipped: FYI_TAKEDOWN_REVISION is not configured.",
        "steps.gate.outputs.enabled == 'true'",
        "foi-process/live-archive-manifest-profile/v2",
        "scripts/download_allowlisted.py",
        "--expected-sha256 \"$MANIFEST_SHA256\"",
        'f"/resolve/{revision}/"',
        '"source_revision": os.environ["SOURCE_REVISION"]',
        '"benchmark_only_nonpublication"',
        '"publication_performed": False',
        '"raw_content_retained": False',
        "/usr/bin/time -f '%e %M'",
        "retention-days: 30",
    )
    for token in required:
        assert token in workflow, f"live archive workflow is missing safety token: {token}"
    assert workflow.count("if: steps.gate.outputs.enabled == 'true'") == 3
    assert "curl --fail" not in workflow
    print("live archive manifest workflow safety contract passed")


if __name__ == "__main__":
    main()
