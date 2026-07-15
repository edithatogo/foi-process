#!/usr/bin/env python3
"""Build a reproducible, checksummed release evidence directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def command_output(command: list[str]) -> str:
    return subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()


def spdx_id(package: dict[str, Any]) -> str:
    stem = re.sub(r"[^A-Za-z0-9.-]", "-", f"{package['name']}-{package['version']}")
    suffix = hashlib.sha256(package["id"].encode("utf-8")).hexdigest()[:12]
    return f"SPDXRef-Package-{stem}-{suffix}"


def build_sbom(created_at: str, software_commit: str) -> dict[str, Any]:
    metadata = json.loads(command_output(["cargo", "metadata", "--locked", "--format-version", "1"]))
    packages = sorted(metadata["packages"], key=lambda package: package["id"])
    identifiers = {package["id"]: spdx_id(package) for package in packages}
    spdx_packages = []
    for package in packages:
        license_value = package.get("license") or "NOASSERTION"
        source = package.get("source")
        spdx_packages.append(
            {
                "SPDXID": identifiers[package["id"]],
                "name": package["name"],
                "versionInfo": package["version"],
                "downloadLocation": source if source else "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": license_value,
                "copyrightText": "NOASSERTION",
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": f"pkg:cargo/{package['name']}@{package['version']}",
                    }
                ],
            }
        )

    root_id = metadata["resolve"]["root"]
    relationships = [
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relationshipType": "DESCRIBES",
            "relatedSpdxElement": identifiers[root_id],
        }
    ]
    for node in sorted(metadata["resolve"]["nodes"], key=lambda item: item["id"]):
        for dependency in sorted(node["dependencies"]):
            relationships.append(
                {
                    "spdxElementId": identifiers[node["id"]],
                    "relationshipType": "DEPENDS_ON",
                    "relatedSpdxElement": identifiers[dependency],
                }
            )
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "foi-process-release-sbom",
        "documentNamespace": f"https://github.com/edithatogo/foi-process/sbom/{software_commit}",
        "creationInfo": {"created": created_at, "creators": ["Tool: foi-process/build_release_evidence.py"]},
        "packages": spdx_packages,
        "relationships": relationships,
    }


def artifact(path: Path, relative: str, media_type: str) -> dict[str, Any]:
    digest = sha256(path)
    return {
        "artifact_id": f"urn:foi-process:artifact:sha256:{digest}",
        "path_or_uri": relative,
        "media_type": media_type,
        "sha256": digest,
        "byte_length": path.stat().st_size,
    }


def build(output: Path, benchmark: Path, created_at: str, software_commit: str, source_revision: str) -> None:
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"output directory must be absent or empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="foi-process-release-") as temporary:
        dataset = Path(temporary) / "dataset"
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_hf_dataset.py"), "--output", str(dataset)],
            cwd=ROOT,
            check=True,
        )
        dataset_manifest = dataset / "manifest.json"
        dataset_target = output / "dataset-manifest.json"
        shutil.copyfile(dataset_manifest, dataset_target)

    benchmark_target = output / "rust-scale-benchmark.json"
    shutil.copyfile(benchmark, benchmark_target)
    shutil.copyfile(ROOT / "Cargo.lock", output / "Cargo.lock")

    sbom_target = output / "sbom.spdx.json"
    write_json(sbom_target, build_sbom(created_at, software_commit))
    sbom_descriptor = artifact(sbom_target, "sbom.spdx.json", "application/spdx+json")
    input_descriptor = artifact(dataset_target, "dataset-manifest.json", "application/json")
    benchmark_descriptor = artifact(benchmark_target, "rust-scale-benchmark.json", "application/json")

    rust_version = command_output(["rustc", "--version"])
    manifest_identity = {
        "source_manifest_sha256": input_descriptor["sha256"],
        "software_commit": software_commit,
        "source_revision": source_revision,
        "benchmark_sha256": benchmark_descriptor["sha256"],
        "sbom_sha256": sbom_descriptor["sha256"],
    }
    run_digest = hashlib.sha256(
        json.dumps(manifest_identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    mining_manifest = {
        "schema_version": "1.0.0-draft.1",
        "run_id": f"urn:foi-process:mining-run:sha256:{run_digest}",
        "created_at": created_at,
        "source_dataset": "urn:huggingface:dataset:edithatogo/foi-process-event-logs",
        "source_revision": source_revision,
        "source_manifest_sha256": input_descriptor["sha256"],
        "software_commit": software_commit,
        "rust_version": rust_version,
        "rust4pm_version": "0.6.0",
        "foi_process_version": "0.1.0",
        "parameters": {"benchmark_profiles": "1k,10k,full", "publication": "synthetic-fixture"},
        "privacy_profile": {
            "sensitivity": "public",
            "access_tier": "public",
            "disposition": "publish",
            "reason_codes": ["privacy:fixture_reviewed"],
            "human_reviewed": True,
        },
        "inputs": [input_descriptor],
        "outputs": [benchmark_descriptor, sbom_descriptor],
        "sbom_artifact_id": sbom_descriptor["artifact_id"],
        "environment": {"generation": "release-evidence-builder"},
    }
    write_json(output / "mining-run-manifest.json", mining_manifest)

    evidence_files = []
    for path in sorted(output.iterdir(), key=lambda item: item.name.casefold()):
        if path.is_file():
            evidence_files.append(
                {"path": path.name, "byte_length": path.stat().st_size, "sha256": sha256(path)}
            )
    release_manifest = {
        "schema_version": "1.0.0",
        "created_at": created_at,
        "software_commit": software_commit,
        "source_revision": source_revision,
        "files": evidence_files,
    }
    write_json(output / "release-evidence-manifest.json", release_manifest)

    checksum_paths = sorted(
        (path for path in output.iterdir() if path.is_file() and path.name != "SHA256SUMS"),
        key=lambda item: item.name.casefold(),
    )
    checksums = "".join(f"{sha256(path)}  {path.name}\n" for path in checksum_paths)
    (output / "SHA256SUMS").write_bytes(checksums.encode("ascii"))
    print(f"built release evidence at {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--created-at", default="2026-07-15T00:00:00Z")
    parser.add_argument("--software-commit")
    parser.add_argument("--source-revision", default="v0.1.0")
    args = parser.parse_args()
    software_commit = args.software_commit or command_output(["git", "rev-parse", "HEAD"])
    build(
        args.output.resolve(),
        args.benchmark.resolve(),
        args.created_at,
        software_commit,
        args.source_revision,
    )


if __name__ == "__main__":
    main()
