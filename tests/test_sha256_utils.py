"""Tests for scripts/sha256_utils.py — shared SHA256 utilities for idempotent ingestion."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from scripts.sha256_utils import (
    build_change_report,
    content_sha256,
    manifest_sha256,
    sha256_bytes,
    sha256_file,
    sha256_text,
)


# ---------------------------------------------------------------------------
# Low-level SHA256 helpers
# ---------------------------------------------------------------------------


class TestSha256Bytes:
    def test_sha256_bytes_is_deterministic(self) -> None:
        assert sha256_bytes(b"hello") == sha256_bytes(b"hello")

    def test_sha256_bytes_returns_64_hex_chars(self) -> None:
        assert len(sha256_bytes(b"any data")) == 64

    def test_sha256_bytes_differs_for_different_input(self) -> None:
        assert sha256_bytes(b"foo") != sha256_bytes(b"bar")


class TestSha256Text:
    def test_sha256_text_matches_sha256_bytes_of_utf8_encoding(self) -> None:
        text = "Māori text with accents →"
        assert sha256_text(text) == sha256_bytes(text.encode("utf-8"))


class TestSha256File:
    def test_sha256_file_is_deterministic(self, tmp_path: Path) -> None:
        path = tmp_path / "test.bin"
        path.write_bytes(b"data")
        assert sha256_file(path) == sha256_file(path)

    def test_sha256_file_matches_sha256_bytes_of_content(self, tmp_path: Path) -> None:
        content = b"file content"
        path = tmp_path / "test.bin"
        path.write_bytes(content)
        assert sha256_file(path) == sha256_bytes(content)

    def test_sha256_file_handles_large_content(self, tmp_path: Path) -> None:
        content = b"x" * (2 * 1024 * 1024)  # 2 MB
        path = tmp_path / "large.bin"
        path.write_bytes(content)
        digest = sha256_file(path)
        assert len(digest) == 64
        assert digest == sha256_bytes(content)


# ---------------------------------------------------------------------------
# Content-signature hashing
# ---------------------------------------------------------------------------


class TestContentSha256:
    def test_content_sha256_is_stable_for_unchanged_payload(self) -> None:
        payload = {
            "schema_version": "1.1",
            "record_count": 42,
            "files": [
                {"path": "a.txt", "size_bytes": 10, "sha256": "abc"},
            ],
            "generated_at_utc": "2026-06-14T00:00:00",
            "pipeline_version": "v1",
        }
        h1 = content_sha256(payload)
        h2 = content_sha256(payload)
        assert h1 == h2

    def test_content_sha256_changes_when_record_count_changes(self) -> None:
        payload_a = {
            "schema_version": "1.1",
            "record_count": 42,
            "files": [{"path": "a.txt", "size_bytes": 10, "sha256": "abc"}],
        }
        payload_b = {
            "schema_version": "1.1",
            "record_count": 99,
            "files": [{"path": "a.txt", "size_bytes": 10, "sha256": "abc"}],
        }
        assert content_sha256(payload_a) != content_sha256(payload_b)

    def test_content_sha256_changes_when_file_hash_changes(self) -> None:
        payload_a = {
            "schema_version": "1.1",
            "record_count": 42,
            "files": [{"path": "a.txt", "size_bytes": 10, "sha256": "abc"}],
        }
        payload_b = {
            "schema_version": "1.1",
            "record_count": 42,
            "files": [{"path": "a.txt", "size_bytes": 10, "sha256": "xyz"}],
        }
        assert content_sha256(payload_a) != content_sha256(payload_b)

    def test_content_sha256_is_insensitive_to_generated_at(self) -> None:
        payload_a = {
            "schema_version": "1.1",
            "record_count": 5,
            "files": [],
            "generated_at_utc": "2026-01-01T00:00:00",
        }
        payload_b = {
            "schema_version": "1.1",
            "record_count": 5,
            "files": [],
            "generated_at_utc": "2026-12-31T23:59:59",
        }
        assert content_sha256(payload_a) == content_sha256(payload_b)

    def test_content_sha256_excludes_pipeline_metadata(self) -> None:
        payload_a = {
            "schema_version": "1.1",
            "record_count": 5,
            "files": [],
            "pipeline_version": "v1",
            "github_run_id": "1234",
        }
        payload_b = {
            "schema_version": "1.1",
            "record_count": 5,
            "files": [],
            "pipeline_version": "v2",
            "github_run_id": "5678",
        }
        assert content_sha256(payload_a) == content_sha256(payload_b)


# ---------------------------------------------------------------------------
# Manifest hashing
# ---------------------------------------------------------------------------


class TestManifestSha256:
    def test_manifest_sha256_is_deterministic(self) -> None:
        payload = {
            "schema_version": "1.1",
            "record_count": 10,
            "files": [],
            "generated_at_utc": "2026-06-14T00:00:00",
            "pipeline_version": "abc123",
        }
        assert manifest_sha256(payload) == manifest_sha256(payload)

    def test_manifest_sha256_differs_when_pipeline_version_changes(self) -> None:
        payload_a = {
            "schema_version": "1.1",
            "record_count": 10,
            "files": [],
            "pipeline_version": "abc",
        }
        payload_b = {
            "schema_version": "1.1",
            "record_count": 10,
            "files": [],
            "pipeline_version": "xyz",
        }
        assert manifest_sha256(payload_a) != manifest_sha256(payload_b)

    def test_manifest_sha256_excludes_generated_at_by_default(self) -> None:
        """generated_at_utc should NOT affect the manifest hash by default."""
        payload_a = {
            "schema_version": "1.1",
            "record_count": 10,
            "files": [],
            "generated_at_utc": "2026-01-01T00:00:00",
            "pipeline_version": "abc",
        }
        payload_b = {
            "schema_version": "1.1",
            "record_count": 10,
            "files": [],
            "generated_at_utc": "2026-12-31T23:59:59",
            "pipeline_version": "abc",
        }
        assert manifest_sha256(payload_a) == manifest_sha256(payload_b)

    def test_manifest_sha256_returns_64_hex_chars(self) -> None:
        payload = {"schema_version": "1.1", "files": []}
        assert len(manifest_sha256(payload)) == 64


# ---------------------------------------------------------------------------
# Change-report generation
# ---------------------------------------------------------------------------


class TestBuildChangeReport:
    def test_no_previous_marks_all_files_as_added(self) -> None:
        current = {
            "manifest_sha256": "abc",
            "content_sha256": "def",
            "files": [{"path": "a.txt", "sha256": "h1"}],
        }
        report = build_change_report(None, current)
        assert report["added"] == ["a.txt"]
        assert report["removed"] == []
        assert report["changed"] == []
        assert report["has_changes"] is True
        assert report["previous_manifest_sha256"] is None
        assert report["current_manifest_sha256"] == "abc"

    def test_no_changes_reports_has_changes_false(self) -> None:
        previous = {
            "manifest_sha256": "abc",
            "content_sha256": "def",
            "files": [{"path": "a.txt", "sha256": "h1"}],
        }
        current = {
            "manifest_sha256": "abc",
            "content_sha256": "def",
            "files": [{"path": "a.txt", "sha256": "h1"}],
        }
        report = build_change_report(previous, current)
        assert report["added"] == []
        assert report["removed"] == []
        assert report["changed"] == []
        assert report["has_changes"] is False

    def test_detects_added_files(self) -> None:
        previous = {
            "manifest_sha256": "abc",
            "content_sha256": "def",
            "files": [{"path": "a.txt", "sha256": "h1"}],
        }
        current = {
            "manifest_sha256": "xyz",
            "content_sha256": "uvw",
            "files": [
                {"path": "a.txt", "sha256": "h1"},
                {"path": "b.txt", "sha256": "h2"},
            ],
        }
        report = build_change_report(previous, current)
        assert report["added"] == ["b.txt"]
        assert report["has_changes"] is True

    def test_detects_removed_files(self) -> None:
        previous = {
            "manifest_sha256": "abc",
            "content_sha256": "def",
            "files": [
                {"path": "a.txt", "sha256": "h1"},
                {"path": "b.txt", "sha256": "h2"},
            ],
        }
        current = {
            "manifest_sha256": "xyz",
            "content_sha256": "uvw",
            "files": [{"path": "a.txt", "sha256": "h1"}],
        }
        report = build_change_report(previous, current)
        assert report["removed"] == ["b.txt"]
        assert report["has_changes"] is True

    def test_detects_changed_file_content(self) -> None:
        previous = {
            "manifest_sha256": "abc",
            "content_sha256": "def",
            "files": [{"path": "a.txt", "sha256": "h1"}],
        }
        current = {
            "manifest_sha256": "xyz",
            "content_sha256": "uvw",
            "files": [{"path": "a.txt", "sha256": "h2"}],
        }
        report = build_change_report(previous, current)
        assert report["changed"] == ["a.txt"]
        assert report["has_changes"] is True

    def test_detects_content_signature_change_only(self) -> None:
        """Same files, same file hashes, but different content signature."""
        previous = {
            "manifest_sha256": "abc",
            "content_sha256": "def",
            "files": [{"path": "a.txt", "sha256": "h1"}],
        }
        current = {
            "manifest_sha256": "abc",
            "content_sha256": "xyz",
            "files": [{"path": "a.txt", "sha256": "h1"}],
        }
        report = build_change_report(previous, current)
        assert report["added"] == []
        assert report["removed"] == []
        assert report["changed"] == []
        assert report["has_changes"] is True

    def test_fallback_to_manifest_sha256_when_content_sha256_missing(self) -> None:
        previous = {"manifest_sha256": "abc", "files": []}
        current = {"manifest_sha256": "def", "files": []}
        report = build_change_report(previous, current)
        assert report["previous_content_sha256"] == "abc"
        assert report["current_content_sha256"] == "def"
        assert report["has_changes"] is True

    def test_complex_add_remove_change_scenario(self) -> None:
        previous = {
            "manifest_sha256": "abc",
            "content_sha256": "def",
            "files": [
                {"path": "a.txt", "sha256": "h1"},
                {"path": "b.txt", "sha256": "h2"},
                {"path": "c.txt", "sha256": "h3"},
            ],
        }
        current = {
            "manifest_sha256": "xyz",
            "content_sha256": "uvw",
            "files": [
                {"path": "a.txt", "sha256": "h1_changed"},
                {"path": "c.txt", "sha256": "h3"},
                {"path": "d.txt", "sha256": "h4"},
            ],
        }
        report = build_change_report(previous, current)
        assert report["added"] == ["d.txt"]
        assert report["removed"] == ["b.txt"]
        assert report["changed"] == ["a.txt"]
        assert report["has_changes"] is True
