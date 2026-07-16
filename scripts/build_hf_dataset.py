#!/usr/bin/env python3
"""Build the deterministic, public-safe Hugging Face fixture dataset bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from generate_synthetic_scenarios import generate as generate_scenarios


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DISPOSITIONS = {"publish", "publish_metadata_only"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    path.write_bytes(content.encode("utf-8"))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    path.write_bytes(content.encode("utf-8"))


def require_fixture_review(privacy: dict[str, Any], subject: str) -> None:
    if privacy.get("disposition") not in ALLOWED_DISPOSITIONS:
        raise ValueError(f"{subject}: publication disposition is not public-safe")
    if privacy.get("human_reviewed") is not True:
        raise ValueError(f"{subject}: fixture is not marked human reviewed")
    if "privacy:fixture_reviewed" not in privacy.get("reason_codes", []):
        raise ValueError(f"{subject}: fixture review reason code is missing")


def validate_public_tree(value: Any, subject: str, path: str = "$") -> None:
    """Validate every nested privacy assessment before an artefact is deposited."""
    if isinstance(value, dict):
        if "privacy" in value:
            if not isinstance(value["privacy"], dict):
                raise ValueError(f"{subject}{path}.privacy: expected an object")
            require_fixture_review(value["privacy"], f"{subject}{path}")
            if value["privacy"].get("disposition") == "publish_metadata_only":
                forbidden = {"text", "inline_text", "raw_text", "embedding", "embeddings"}
                leaked = sorted(key for key in forbidden if key in value)
                if leaked:
                    raise ValueError(f"{subject}{path}: metadata-only object contains {leaked}")
        for key, child in value.items():
            validate_public_tree(child, subject, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_public_tree(child, subject, f"{path}[{index}]")
    elif isinstance(value, str) and value.strip().lower() == "to-be-recorded":
        raise ValueError(f"{subject}{path}: unresolved licensing value")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dataset_card() -> str:
    return """---
license: apache-2.0
language:
- en
pretty_name: FOI Process Event Logs
tags:
- process-mining
- freedom-of-information
- ocel
- event-log
- synthetic
configs:
- config_name: event_log
  data_files:
  - split: demo
    path: data/event_log/*.jsonl
- config_name: event_revisions
  data_files:
  - split: demo
    path: data/event_revisions/*.jsonl
- config_name: evidence_deltas
  data_files:
  - split: demo
    path: data/evidence_deltas/*.jsonl
- config_name: process_edges
  data_files:
  - split: demo
    path: data/process_edges/*.jsonl
- config_name: process_variants
  data_files:
  - split: demo
    path: data/process_variants/*.jsonl
- config_name: conformance_findings
  data_files:
  - split: demo
    path: data/conformance_findings/*.jsonl
- config_name: ocel_events
  data_files:
  - split: demo
    path: data/ocel_events/*.jsonl
- config_name: ocel_objects
  data_files:
  - split: demo
    path: data/ocel_objects/*.jsonl
- config_name: ocel_event_object_links
  data_files:
  - split: demo
    path: data/ocel_event_object_links/*.jsonl
- config_name: simulation_event_log
  data_files:
  - split: simulation
    path: data/simulation_event_log/*.jsonl
- config_name: simulation_event_revisions
  data_files:
  - split: simulation
    path: data/simulation_event_revisions/*.jsonl
- config_name: simulation_cases
  data_files:
  - split: simulation
    path: data/simulation_cases/*.jsonl
- config_name: simulation_daily_metrics
  data_files:
  - split: simulation
    path: data/simulation_daily_metrics/*.jsonl
- config_name: simulation_summaries
  data_files:
  - split: simulation
    path: data/simulation_summaries/*.jsonl
- config_name: simulation_ocel_events
  data_files:
  - split: simulation
    path: data/simulation_ocel_events/*.jsonl
- config_name: simulation_ocel_objects
  data_files:
  - split: simulation
    path: data/simulation_ocel_objects/*.jsonl
- config_name: simulation_ocel_event_object_links
  data_files:
  - split: simulation
    path: data/simulation_ocel_event_object_links/*.jsonl
---

# FOI Process Event Logs

Deterministic demonstration data for the `foi-process` replay, process-mining and dashboard contracts.

## Data classification

This release contains **synthetic, explicitly reviewed fixtures only**. It is not a publication of
real requester correspondence or personal information. A production export must pass the separate
privacy, tikanga/data-governance and threat-model gates before it may replace or supplement these
fixtures.

## Contents

- active public event log for process discovery and performance analysis;
- full synthetic event revision history and EvidenceDelta replay stream;
- process-map edges and variants;
- OCEL events, objects and event-object links;
- synthetic conformance findings;
- deterministic baseline, demand-surge, concept-drift and correction-stress event logs;
- synthetic scenario revision history, OCEL links, daily metrics and comparative summaries;
- dashboard, public projection, OCEL and mining-run artefacts;
- portable JSON Schemas and a SHA-256 publication manifest.

`manifest.json` records every deposited file, byte length, row count where applicable and SHA-256
digest. FOI-O remains authoritative for legal semantics; conformance examples are not certified
legal conclusions.
"""


def build(output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    revisions = read_jsonl(ROOT / "examples/input/process-events.ndjson")
    for event in revisions:
        require_fixture_review(event["privacy"], event["event_id"])

    deltas = read_jsonl(ROOT / "examples/input/evidence-deltas.ndjson")
    for delta in deltas:
        evidence = delta.get("evidence")
        if evidence is not None:
            require_fixture_review(evidence["privacy"], delta["delta_id"])

    public = read_json(ROOT / "examples/generated/public-projection.json")
    dashboard = read_json(ROOT / "examples/generated/dashboard-summary.json")
    ocel = read_json(ROOT / "examples/generated/ocel-projection.json")
    conformance = read_json(ROOT / "examples/generated/conformance-trace.json")
    mining_run = read_json(ROOT / "examples/generated/mining-run-manifest.json")
    for name, artefact in {
        "public-projection": public,
        "dashboard-summary": dashboard,
        "ocel-projection": ocel,
        "conformance-trace": conformance,
        "mining-run-manifest": mining_run,
    }.items():
        validate_public_tree(artefact, name)

    event_log = []
    for event in public["events"]:
        timestamp = event.get("event_time", {}).get("timestamp")
        event_log.append(
            {
                "event_id": event["event_id"],
                "logical_event_id": event["logical_event_id"],
                "case_id": event["case_id"],
                "activity": event["activity"],
                "timestamp": timestamp,
                "source_sequence": event.get("position", {}).get("sequence", 0),
                "site": event["site"],
                "jurisdiction": event["jurisdiction"],
                "assertion_status": event["assertion_status"],
                "authority_id": event.get("attributes", {}).get("authority_id"),
                "evidence_count": len(event.get("evidence", [])),
            }
        )

    edges = [
        {"source": item["edge"]["from"], "target": item["edge"]["to"], "count": item["count"]}
        for item in dashboard["edges"]
    ]
    variants = [
        {"variant_id": index + 1, "activities": item["activities"], "count": item["count"]}
        for index, item in enumerate(dashboard["variants"])
    ]
    findings = [
        {
            "trace_id": conformance["trace_id"],
            "case_id": conformance["case_id"],
            "profile_id": conformance["profile_id"],
            **finding,
        }
        for finding in conformance["findings"]
    ]

    datasets = {
        "event_log": event_log,
        "event_revisions": revisions,
        "evidence_deltas": deltas,
        "process_edges": edges,
        "process_variants": variants,
        "conformance_findings": findings,
        "ocel_events": ocel["events"],
        "ocel_objects": ocel["objects"],
        "ocel_event_object_links": ocel["event_object_links"],
    }
    datasets.update(generate_scenarios())
    for name, rows in datasets.items():
        write_jsonl(output / "data" / name / "demo-00000-of-00001.jsonl", rows)

    artifacts = {
        "dashboard-summary.json": dashboard,
        "public-projection.json": public,
        "ocel-projection.json": ocel,
        "conformance-trace.json": conformance,
        "mining-run-manifest.json": mining_run,
    }
    for name, value in artifacts.items():
        write_json(output / "artifacts" / name, value)

    for schema_path in sorted((ROOT / "schemas/portable").glob("*.json")):
        write_json(output / "schemas" / schema_path.name, read_json(schema_path))
    (output / "README.md").write_bytes(dataset_card().replace("\r\n", "\n").encode("utf-8"))

    files = []
    paths = sorted(
        output.rglob("*"),
        key=lambda path: path.relative_to(output).as_posix().casefold(),
    )
    for path in paths:
        if not path.is_file() or path.name == "manifest.json":
            continue
        relative = path.relative_to(output).as_posix()
        row_count = None
        if path.suffix == ".jsonl":
            row_count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line)
        files.append(
            {
                "path": relative,
                "byte_length": path.stat().st_size,
                "row_count": row_count,
                "sha256": sha256(path),
            }
        )
    manifest = {
        "schema_version": "1.0.0",
        "dataset_id": "edithatogo/foi-process-event-logs",
        "classification": "synthetic-fixture",
        "source_release": "v0.1.0",
        "generated_at": mining_run["created_at"],
        "files": files,
    }
    write_json(output / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.output.resolve())
    print(f"built Hugging Face dataset bundle at {args.output.resolve()}")


if __name__ == "__main__":
    main()
