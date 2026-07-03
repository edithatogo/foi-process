"""Tests for idempotent sync behavior using SHA256 checksum comparisons.

These tests verify that the shared sha256_utils can be used to detect
when ingestion is redundant (no changes) vs. when re-ingestion is
required (content changed).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.sha256_utils import (
    build_change_report,
    content_sha256,
    manifest_sha256,
    sha256_file,
)


def _make_manifest_payload(
    files: list[dict],
    record_count: int = 5,
    pipeline_version: str = "test-v1",
) -> dict:
    """Helper to build a realistic manifest payload for testing."""
    payload = {
        "schema_version": "1.1",
        "record_count": record_count,
        "files": files,
        "generated_at_utc": "2026-06-14T12:00:00",
        "pipeline_version": pipeline_version,
        "github_repository": "test-org/test-repo",
        "github_run_id": "12345",
    }
    payload["content_sha256"] = content_sha256(payload)
    payload["manifest_sha256"] = manifest_sha256(payload)
    return payload


# ---------------------------------------------------------------------------
# Idempotency: same inputs -> same hashes -> no change
# ---------------------------------------------------------------------------


class TestIdempotentSyncNoChange:
    """When source files have not changed, the sync should be idempotent."""

    def test_same_files_produce_same_content_hash(self) -> None:
        files = [
            {"path": "data/records.jsonl", "size_bytes": 100, "sha256": "a" * 64},
            {"path": "data/parquet/year=2026/file.parquet", "size_bytes": 500, "sha256": "b" * 64},
        ]
        payload_a = _make_manifest_payload(files, record_count=42)
        payload_b = _make_manifest_payload(files, record_count=42)
        assert payload_a["content_sha256"] == payload_b["content_sha256"]

    def test_same_manifests_produce_no_change_report(self) -> None:
        files = [
            {"path": "data/records.jsonl", "size_bytes": 100, "sha256": "a" * 64},
        ]
        previous = _make_manifest_payload(files, record_count=10)
        current = _make_manifest_payload(files, record_count=10)
        report = build_change_report(previous, current)
        assert report["has_changes"] is False

    def test_sha256_file_unchanged_produces_deterministic_hash(self, tmp_path: Path) -> None:
        """The same file content always produces the same SHA256."""
        path = tmp_path / "stable.txt"
        path.write_text("Hello, world!", encoding="utf-8")
        h1 = sha256_file(path)
        h2 = sha256_file(path)
        assert h1 == h2


# ---------------------------------------------------------------------------
# Change detection: different inputs trigger re-ingestion
# ---------------------------------------------------------------------------


class TestIdempotentSyncDetectsChange:
    """When source files change, the pipeline must detect and re-ingest."""

    def test_record_count_change_detected_in_content_hash(self) -> None:
        files = [{"path": "data/records.jsonl", "size_bytes": 100, "sha256": "a" * 64}]
        payload_a = _make_manifest_payload(files, record_count=10)
        payload_b = _make_manifest_payload(files, record_count=99)
        assert payload_a["content_sha256"] != payload_b["content_sha256"]

    def test_file_added_detected_in_change_report(self) -> None:
        previous = _make_manifest_payload(
            [{"path": "a.txt", "size_bytes": 10, "sha256": "h1"}],
            record_count=1,
        )
        current = _make_manifest_payload(
            [
                {"path": "a.txt", "size_bytes": 10, "sha256": "h1"},
                {"path": "b.txt", "size_bytes": 20, "sha256": "h2"},
            ],
            record_count=2,
        )
        report = build_change_report(previous, current)
        assert report["has_changes"] is True
        assert report["added"] == ["b.txt"]

    def test_file_removed_detected_in_change_report(self) -> None:
        previous = _make_manifest_payload(
            [
                {"path": "a.txt", "size_bytes": 10, "sha256": "h1"},
                {"path": "b.txt", "size_bytes": 20, "sha256": "h2"},
            ],
            record_count=2,
        )
        current = _make_manifest_payload(
            [{"path": "a.txt", "size_bytes": 10, "sha256": "h1"}],
            record_count=1,
        )
        report = build_change_report(previous, current)
        assert report["has_changes"] is True
        assert report["removed"] == ["b.txt"]

    def test_file_content_changed_detected(self, tmp_path: Path) -> None:
        """Verify that changing a file's bytes changes its SHA256 hash."""
        path = tmp_path / "content.txt"
        path.write_text("original content", encoding="utf-8")
        original_hash = sha256_file(path)

        path.write_text("modified content", encoding="utf-8")
        new_hash = sha256_file(path)

        assert original_hash != new_hash

    def test_pipeline_version_change_does_not_affect_content_hash(self) -> None:
        """The content hash should only reflect data content, not pipeline metadata."""
        files = [{"path": "data/records.jsonl", "size_bytes": 100, "sha256": "a" * 64}]
        payload_a = _make_manifest_payload(files, record_count=10, pipeline_version="v1")
        payload_b = _make_manifest_payload(files, record_count=10, pipeline_version="v2")
        assert payload_a["content_sha256"] == payload_b["content_sha256"]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestIdempotentSyncEdgeCases:
    def test_empty_directory_produces_no_change_when_no_files(self) -> None:
        previous = _make_manifest_payload([], record_count=0)
        current = _make_manifest_payload([], record_count=0)
        report = build_change_report(previous, current)
        assert report["has_changes"] is False

    def test_first_run_always_has_changes(self) -> None:
        current = _make_manifest_payload(
            [{"path": "a.txt", "size_bytes": 10, "sha256": "h1"}],
            record_count=1,
        )
        report = build_change_report(None, current)
        assert report["has_changes"] is True

    def test_content_hash_insensitive_to_generated_timestamp(self) -> None:
        """Content hash must not change when only generated_at_utc changes."""
        files = [{"path": "a.txt", "size_bytes": 10, "sha256": "h1"}]
        base = {
            "schema_version": "1.1",
            "record_count": 5,
            "files": files,
        }
        base["content_sha256"] = content_sha256(base)

        later = {
            "schema_version": "1.1",
            "record_count": 5,
            "files": files,
            "generated_at_utc": "2099-01-01T00:00:00",
        }
        later["content_sha256"] = content_sha256(later)

        assert base["content_sha256"] == later["content_sha256"]

    def test_manifest_hash_is_sensitive_to_timestamp_by_default(self) -> None:
        """manifest_sha256 should exclude generated_at_utc by default."""
        files = [{"path": "a.txt", "size_bytes": 10, "sha256": "h1"}]
        base = {
            "schema_version": "1.1",
            "record_count": 5,
            "files": files,
            "generated_at_utc": "2026-01-01T00:00:00",
        }
        later = {
            "schema_version": "1.1",
            "record_count": 5,
            "files": files,
            "generated_at_utc": "2099-01-01T00:00:00",
        }
        assert manifest_sha256(base) == manifest_sha256(later)
