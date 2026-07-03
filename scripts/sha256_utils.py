"""Root orchestration SHA256 helpers for idempotent ingestion checks.

This module belongs to the root aggregation workspace because it is used by
root quality gates and swarm/orchestration tests. Corpus repos should own their
own utility modules and must not import root workspace implementation code.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    """Return the SHA-256 hex digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    """Return the SHA-256 hex digest of the UTF-8 encoding of *text*."""
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 hex digest of the file at *path*."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def content_sha256(payload: dict[str, Any]) -> str:
    """Compute a stable content-only SHA-256 for idempotency checks."""
    content_payload = {
        "schema_version": payload.get("schema_version"),
        "record_count": payload.get("record_count"),
        "files": [
            {"path": f["path"], "size_bytes": f["size_bytes"], "sha256": f["sha256"]}
            for f in payload.get("files", [])
        ],
    }
    return sha256_text(json.dumps(content_payload, sort_keys=True, ensure_ascii=False))


def manifest_sha256(payload: dict[str, Any], *, exclude_keys: set[str] | None = None) -> str:
    """Compute a SHA-256 of the manifest payload, minus optional transient keys."""
    excluded = set(exclude_keys or {"generated_at_utc", "manifest_sha256"})
    manifest_payload = {k: v for k, v in payload.items() if k not in excluded}
    return sha256_text(json.dumps(manifest_payload, sort_keys=True, ensure_ascii=False))


def build_change_report(
    previous: dict[str, Any] | None,
    current: dict[str, Any],
) -> dict[str, Any]:
    """Compare two manifests and return a change report."""
    prev_files = {f["path"]: f for f in (previous or {}).get("files", [])}
    cur_files = {f["path"]: f for f in current.get("files", [])}

    added = sorted(set(cur_files) - set(prev_files))
    removed = sorted(set(prev_files) - set(cur_files))
    changed = sorted(
        path
        for path in set(cur_files) & set(prev_files)
        if cur_files[path].get("sha256") != prev_files[path].get("sha256")
    )

    previous_content = (previous or {}).get("content_sha256") or (previous or {}).get(
        "manifest_sha256"
    )
    current_content = current.get("content_sha256") or current.get("manifest_sha256")

    return {
        "schema_version": "1.0",
        "previous_manifest_sha256": (previous or {}).get("manifest_sha256"),
        "current_manifest_sha256": current.get("manifest_sha256"),
        "previous_content_sha256": previous_content,
        "current_content_sha256": current_content,
        "added": added,
        "removed": removed,
        "changed": changed,
        "has_changes": bool(added or removed or changed or previous_content != current_content),
    }
