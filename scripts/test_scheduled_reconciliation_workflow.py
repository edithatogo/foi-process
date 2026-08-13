#!/usr/bin/env python3
"""Static safety contract for scheduled per-instance reconciliation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/scheduled_archive_reconciliation.yml"
DOWNLOADER = ROOT / "scripts/download_allowlisted.py"


def require(value: str, text: str) -> None:
    if value not in text:
        raise AssertionError(f"workflow is missing required contract: {value}")


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    for required in (
        "schedule:",
        "workflow_dispatch:",
        "instance_id:",
        "group: archive-reconciliation-${{ inputs.instance_id || 'nz-fyi-fixture' }}",
        "cancel-in-progress: false",
        "permissions:\n  contents: read",
        "reconcile-archive-package",
        "actions/cache/restore@0400d5f644dc74513175e3cd8d07132dd4860809",
        "actions/cache/save@0400d5f644dc74513175e3cd8d07132dd4860809",
        "retention-days: 14",
        "persist-credentials: false",
        "download_allowlisted.py",
        "--connect-timeout 10",
        "--overall-timeout 120",
        "--max-bytes 536870912",
        "safe_extract_archive_package.py",
        '"$SOURCE_MODE" == fixture',
        "classification=accepted",
        "classification=no_change",
        "classification=quarantined",
        "classification=failed",
    ):
        require(required, text)
    for forbidden in (
        "HF_TOKEN",
        "ZENODO_TOKEN",
        "contents: write",
        "packages: write",
        "matrix:",
        "publish",
        "curl ",
    ):
        if forbidden in text:
            raise AssertionError(f"workflow contains forbidden surface: {forbidden}")
    downloader = DOWNLOADER.read_text(encoding="utf-8")
    for required in (
        'ALLOWED_HOSTS = frozenset({"huggingface.co", "cdn-lfs.hf.co"})',
        "validate_url(newurl)",
        "MAX_REDIRECTS = 5",
        "overall download timeout",
        "download exceeds max-bytes",
    ):
        require(required, downloader)
    print("scheduled reconciliation workflow contract passed")


if __name__ == "__main__":
    main()
