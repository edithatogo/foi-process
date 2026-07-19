#!/usr/bin/env python3
"""Validate a bounded fyi-cli capture without exposing captured content."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import zipfile
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    resolved = path.resolve()
    root_resolved = root.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise ValueError(f"attachment path escapes capture root: {value}")
    return resolved


def validate(
    root: Path,
    request_id: int,
    *,
    attachment: Path | None = None,
    attachment_url: str | None = None,
) -> dict[str, object]:
    raw_root = root / "data" / "raw" / "requests"
    request_files = list(raw_root.glob(f"*/{request_id}/request.json"))
    if len(request_files) != 1:
        raise ValueError(f"expected one derived request.json for {request_id}, found {len(request_files)}")
    request_path = request_files[0]
    request = json.loads(request_path.read_text(encoding="utf-8"))
    if int(request.get("id", 0)) != request_id:
        raise ValueError("derived request id does not match requested id")
    sibling = request_path.parent
    for required in ("page.html", "attachments.json", "snapshot_meta.json"):
        if not (sibling / required).is_file():
            raise ValueError(f"missing derived artifact: {required}")

    warcs = sorted((root / "data" / "warc").glob("*.warc.gz"))
    waczs = sorted((root / "dist" / "site_snapshots").glob("*.wacz"))
    if not warcs or not waczs:
        raise ValueError("capture did not produce both WARC and WACZ artifacts")

    warc_payloads = []
    for warc in warcs:
        with gzip.open(warc, "rb") as stream:
            payload = stream.read()
        if b"WARC/1.0" not in payload:
            raise ValueError(f"WARC gzip payload does not contain a WARC record: {warc}")
        warc_payloads.append(payload)
    warc_bytes = b"".join(warc_payloads)

    with zipfile.ZipFile(waczs[-1]) as archive:
        names = set(archive.namelist())
        required = {"datapackage.json", "indexes/index.cdxj"}
        if not required.issubset(names):
            raise ValueError(f"WACZ is missing required entries: {sorted(required - names)}")
        package = json.loads(archive.read("datapackage.json"))
        resources = package.get("resources", [])
        if not resources:
            raise ValueError("WACZ datapackage contains no resources")
        archive_entries = [name for name in names if name.startswith("archive/")]
        if not archive_entries:
            raise ValueError("WACZ contains no archive WARC entry")
        wacz_bytes = b"".join(archive.read(name) for name in archive_entries)

    snapshot = json.loads((sibling / "snapshot_meta.json").read_text(encoding="utf-8"))
    resource_rows = snapshot.get("resources", [])
    attachments = json.loads((sibling / "attachments.json").read_text(encoding="utf-8"))
    attachment_rows: list[dict[str, object]] = []
    for row in attachments:
        path = safe_path(root, str(row.get("path", "")))
        if not path.is_file():
            raise ValueError(f"missing attachment bytes: {path}")
        actual_size = path.stat().st_size
        actual_sha256 = sha256(path)
        if row.get("size") is not None and int(row["size"]) != actual_size:
            raise ValueError(f"attachment size mismatch: {path}")
        if row.get("sha256") and str(row["sha256"]).lower() != actual_sha256:
            raise ValueError(f"attachment digest mismatch: {path}")
        record_id = str(row.get("warc_record_id", ""))
        if record_id and record_id.encode() not in warc_bytes and record_id.encode() not in wacz_bytes:
            raise ValueError(f"attachment WARC record is not present in WARC/WACZ: {record_id}")
        attachment_rows.append({
            "url": row.get("url"),
            "size": actual_size,
            "sha256": actual_sha256,
            "warc_record_id": row.get("warc_record_id"),
        })
    report: dict[str, object] = {
        "capture_type": "bounded-real-public-fyi-request",
        "authority": "fyi.org.nz",
        "request_id": request_id,
        "request_url": f"https://fyi.org.nz/request/{request.get('url_title', request_id)}",
        "derived_request": str(sibling).replace("\\", "/"),
        "resource_count": len(resource_rows),
        "resource_kinds": sorted(row.get("kind") for row in resource_rows),
        "warc": {"path": str(warcs[-1]).replace("\\", "/"), "sha256": sha256(warcs[-1])},
        "wacz": {"path": str(waczs[-1]).replace("\\", "/"), "sha256": sha256(waczs[-1])},
        "checks": {
            "derived_store": True,
            "warc_record_signature": True,
            "wacz_datapackage": True,
            "wacz_archive_entry": True,
            "attachment_bytes": bool(attachment_rows),
            "attachment_digests": bool(attachment_rows),
            "attachment_warc_linkage": bool(attachment_rows),
        },
        "content_policy": "captured content remains outside the repository; only hashes and structural evidence are published",
    }
    if attachment_rows:
        report["attachments"] = attachment_rows
    if attachment is not None:
        if not attachment.is_file():
            raise ValueError(f"attachment does not exist: {attachment}")
        report["attachment"] = {
            "url": attachment_url,
            "path": str(attachment).replace("\\", "/"),
            "size": attachment.stat().st_size,
            "sha256": sha256(attachment),
            "content_signature": attachment.read_bytes()[:5].decode("ascii", errors="replace"),
        }
        report["checks"] = {**report["checks"], "external_attachment_hash": True}
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("capture_root", type=Path)
    parser.add_argument("--request-id", type=int, required=True)
    parser.add_argument("--attachment", type=Path)
    parser.add_argument("--attachment-url")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = validate(
            args.capture_root,
            args.request_id,
            attachment=args.attachment,
            attachment_url=args.attachment_url,
        )
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
