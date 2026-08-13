#!/usr/bin/env python3
"""Static regression contract for bounded security fuzzing."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/security-fuzz.yml"


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = (
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "PROPTEST_CASES: \"512\"",
        "cargo test --locked --test replay properties::duplicate_delivery_emits_at_most_once -- --exact",
        "cargo install cargo-fuzz --version 0.13.2 --locked",
        "cargo fuzz run contract_json",
        "cargo fuzz run archive_package_intake",
        "-max_len=65536",
        "-rss_limit_mb=1024",
        "-timeout=5",
        "-max_total_time=\"$MAX_TOTAL_TIME\"",
        "test \"$REQUESTED\" -ge 30 && test \"$REQUESTED\" -le 900",
        "if: failure() || cancelled()",
        "retention-days: 30",
    )
    for value in required:
        if value not in text:
            raise AssertionError(f"security fuzz workflow is missing: {value}")

    for line in text.splitlines():
        if "uses:" in line and "@" in line:
            revision = line.rsplit("@", 1)[1].split()[0]
            if len(revision) != 40 or any(character not in "0123456789abcdef" for character in revision):
                raise AssertionError(f"action is not pinned to a commit: {line.strip()}")

    if "contents: write" in text or "pull-requests: write" in text:
        raise AssertionError("fuzz workflow requests write permissions")
    print("security fuzz workflow contract passed")


if __name__ == "__main__":
    main()
