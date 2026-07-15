#!/usr/bin/env python3
"""Verify published Hugging Face dataset and pre-built Static Space revisions."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_manifest(bundle: Path) -> dict[str, Any]:
    manifest_path = bundle / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("published bundle is missing manifest.json")
    manifest = read_json(manifest_path)
    for entry in manifest.get("files", []):
        path = bundle / entry["path"]
        if not path.is_file():
            raise ValueError(f"published bundle is missing {entry['path']}")
        if path.stat().st_size != entry["byte_length"]:
            raise ValueError(f"published byte length differs for {entry['path']}")
        actual = sha256(path)
        if actual != entry["sha256"]:
            raise ValueError(f"published checksum differs for {entry['path']}: {actual}")
        if entry.get("row_count") is not None:
            rows = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line)
            if rows != entry["row_count"]:
                raise ValueError(f"published row count differs for {entry['path']}")
    return manifest


def require_same_file(expected: Path, actual: Path, label: str) -> str:
    if not actual.is_file():
        raise ValueError(f"published {label} is missing")
    expected_digest = sha256(expected)
    actual_digest = sha256(actual)
    if actual_digest != expected_digest:
        raise ValueError(f"published {label} checksum differs: {actual_digest}")
    return actual_digest


def hf_json(*args: str) -> dict[str, Any]:
    result = subprocess.run(["hf", *args], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def hf_download(repo_id: str, repo_type: str, output: Path) -> None:
    subprocess.run(
        [
            "hf",
            "download",
            repo_id,
            "--repo-type",
            repo_type,
            "--local-dir",
            str(output),
            "--force-download",
            "--quiet",
        ],
        check=True,
    )


def write_attestation(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    value["verified_at"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(value, indent=2, sort_keys=True))


def verify_dataset(repo_id: str, expected_bundle: Path, output: Path) -> None:
    expected_manifest = expected_bundle / "manifest.json"
    with tempfile.TemporaryDirectory(prefix="foi-process-hf-dataset-") as temp:
        published = Path(temp)
        hf_download(repo_id, "dataset", published)
        require_same_file(expected_manifest, published / "manifest.json", "dataset manifest")
        manifest = verify_manifest(published)
        info = hf_json("datasets", "info", repo_id)
        if info.get("private") is not False:
            raise ValueError("published dataset is not public")
        siblings = {item["rfilename"] for item in info.get("siblings", [])}
        required = {"README.md", "manifest.json", *(entry["path"] for entry in manifest["files"])}
        missing = sorted(required - siblings)
        if missing:
            raise ValueError(f"dataset repository listing is incomplete: {missing}")
        write_attestation(
            output,
            {
                "surface": "huggingface_dataset",
                "repo_id": repo_id,
                "remote_revision": info["sha"],
                "classification": manifest["classification"],
                "manifest_sha256": sha256(published / "manifest.json"),
                "manifest_file_count": len(manifest["files"]),
            },
        )


def verify_local(bundle: Path) -> None:
    manifest = verify_manifest(bundle)
    print(
        json.dumps(
            {
                "classification": manifest["classification"],
                "manifest_file_count": len(manifest["files"]),
                "manifest_sha256": sha256(bundle / "manifest.json"),
            },
            indent=2,
            sort_keys=True,
        )
    )


def wait_for_space(repo_id: str, timeout_seconds: int) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_stage = "unknown"
    while time.monotonic() < deadline:
        info = hf_json("spaces", "info", repo_id)
        runtime = info.get("runtime") or {}
        last_stage = runtime.get("stage", "unknown")
        if last_stage in {"BUILD_ERROR", "CONFIG_ERROR", "RUNTIME_ERROR"}:
            detail = runtime.get("errorMessage", "no runtime error message")
            raise ValueError(f"Space entered terminal stage {last_stage}: {detail}")
        if last_stage == "RUNNING" and info.get("host"):
            try:
                with urllib.request.urlopen(info["host"], timeout=30) as response:
                    body = response.read().decode("utf-8", errors="replace")
                    if response.status == 200 and "FOI Process Explorer" in body:
                        return info
            except OSError:
                pass
        time.sleep(10)
    raise ValueError(f"Space did not become healthy within {timeout_seconds}s; stage={last_stage}")


def verify_space(repo_id: str, expected_source: Path, output: Path, timeout_seconds: int) -> None:
    with tempfile.TemporaryDirectory(prefix="foi-process-hf-space-") as temp:
        published = Path(temp)
        hf_download(repo_id, "space", published)
        checksums = {
            "README.md": require_same_file(expected_source / "README.md", published / "README.md", "README.md")
        }
        dist = expected_source / "dist"
        for expected in sorted(path for path in dist.rglob("*") if path.is_file()):
            relative = expected.relative_to(dist).as_posix()
            checksums[relative] = require_same_file(expected, published / relative, relative)
        info = wait_for_space(repo_id, timeout_seconds)
        if info.get("private") is not False:
            raise ValueError("published Space is not public")
        if info.get("sdk") != "static":
            raise ValueError(f"published Space SDK is {info.get('sdk')!r}, expected 'static'")
        write_attestation(
            output,
            {
                "surface": "huggingface_static_space_prebuilt",
                "repo_id": repo_id,
                "remote_revision": info["sha"],
                "runtime_stage": info["runtime"]["stage"],
                "host": info["host"],
                "verified_source_sha256": checksums,
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="surface", required=True)

    local = subparsers.add_parser("local")
    local.add_argument("--bundle", type=Path, required=True)

    dataset = subparsers.add_parser("dataset")
    dataset.add_argument("--repo-id", required=True)
    dataset.add_argument("--bundle", type=Path, required=True)
    dataset.add_argument("--output", type=Path, required=True)

    space = subparsers.add_parser("space")
    space.add_argument("--repo-id", required=True)
    space.add_argument("--source", type=Path, required=True)
    space.add_argument("--output", type=Path, required=True)
    space.add_argument("--timeout-seconds", type=int, default=600)

    args = parser.parse_args()
    if args.surface == "local":
        verify_local(args.bundle.resolve())
    elif args.surface == "dataset":
        verify_dataset(args.repo_id, args.bundle.resolve(), args.output.resolve())
    else:
        verify_space(args.repo_id, args.source.resolve(), args.output.resolve(), args.timeout_seconds)


if __name__ == "__main__":
    main()
