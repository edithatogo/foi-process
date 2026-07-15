#!/usr/bin/env python3
"""Generate deterministic synthetic FOI process stress scenarios."""
from __future__ import annotations
import argparse, hashlib, json, random, statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REQUEST = "foio:RequestSent"
ACK = "foio:RequestAcknowledged"
CLARIFICATION = "foio:ClarificationRequested"
DECISION = "foio:DecisionIssued"
CLOSED = "foio:ClosedObserved"
START = datetime(2025, 3, 3, 9, tzinfo=timezone.utc)
SCENARIOS = (
    {"scenario_id": "baseline", "label": "Baseline", "description": "Stable demand and processing capacity.", "case_count": 48, "surge": False, "drift": False, "correction_rate": 0.02},
    {"scenario_id": "demand_surge", "label": "Demand surge", "description": "A concentrated request surge exceeds short-run closure capacity.", "case_count": 84, "surge": True, "drift": False, "correction_rate": 0.03},
    {"scenario_id": "concept_drift", "label": "Concept drift", "description": "Later cases introduce clarification work and a slower path.", "case_count": 60, "surge": False, "drift": True, "correction_rate": 0.04},
    {"scenario_id": "correction_stress", "label": "Correction stress", "description": "High revision pressure tests latest-revision materialisation.", "case_count": 60, "surge": False, "drift": False, "correction_rate": 0.30},
)

def stable_id(kind: str, *parts: object) -> str:
    canonical = json.dumps(parts, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return f"urn:foi-process:synthetic:{kind}:sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"

def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")

def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(len(ordered) * fraction + 0.999999) - 1))
    return ordered[index]

def arrival_day(index: int, config: dict[str, Any], rng: random.Random) -> int:
    if config["surge"] and index < int(config["case_count"] * 0.62):
        return 7 + rng.randrange(7)
    return rng.randrange(24)

def make_event(scenario_id: str, case_id: str, activity: str, timestamp: datetime, sequence: int, revision: int = 1, correction_of: str | None = None) -> dict[str, Any]:
    logical_id = stable_id("logical-event", scenario_id, case_id, activity, sequence)
    return {
        "scenario_id": scenario_id, "event_id": stable_id("event", logical_id, revision),
        "logical_event_id": logical_id, "case_id": case_id, "activity": activity,
        "timestamp": iso(timestamp), "authority_id": "nz:agency:synthetic",
        "site": "synthetic-simulation", "jurisdiction": "NZ", "assertion_status": "observed",
        "evidence_count": 1, "revision": revision, "correction_of": correction_of, "synthetic": True,
    }

def generate_case(config: dict[str, Any], index: int, rng: random.Random) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    scenario_id = config["scenario_id"]
    case_id = stable_id("case", scenario_id, index)
    day = arrival_day(index, config, rng)
    request_time = START + timedelta(days=day, hours=rng.randrange(8))
    drifted = bool(config["drift"] and day >= 12)
    process_days = rng.randint(6, 12)
    if config["surge"] and 7 <= day <= 13:
        process_days += rng.randint(8, 18)
    if drifted:
        process_days += rng.randint(7, 14)
    activities = [(REQUEST, request_time), (ACK, request_time + timedelta(hours=rng.randint(4, 30)))]
    if drifted:
        activities.append((CLARIFICATION, request_time + timedelta(days=3, hours=rng.randrange(8))))
    decision_time = request_time + timedelta(days=process_days, hours=rng.randrange(8))
    activities.extend([(DECISION, decision_time), (CLOSED, decision_time + timedelta(hours=rng.randint(2, 36)))])
    active, revisions, corrected = [], [], False
    for sequence, (activity, timestamp) in enumerate(activities, start=1):
        original = make_event(scenario_id, case_id, activity, timestamp, sequence)
        revisions.append(original)
        latest = original
        if activity == DECISION and rng.random() < config["correction_rate"]:
            corrected = True
            latest = make_event(scenario_id, case_id, activity, timestamp + timedelta(hours=6), sequence, 2, original["event_id"])
            revisions.append(latest)
        active.append(latest)
    end = datetime.fromisoformat(active[-1]["timestamp"].replace("Z", "+00:00"))
    case = {
        "scenario_id": scenario_id, "case_id": case_id, "started_at": active[0]["timestamp"],
        "ended_at": active[-1]["timestamp"], "cycle_days": round((end - request_time).total_seconds() / 86400, 3),
        "variant": [event["activity"] for event in active], "corrected": corrected,
    }
    return active, revisions, case

def daily_metrics(scenario_id: str, cases: list[dict[str, Any]], revisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    arrivals = Counter(case["started_at"][:10] for case in cases)
    closures = Counter(case["ended_at"][:10] for case in cases)
    corrections = Counter(event["timestamp"][:10] for event in revisions if event["revision"] > 1)
    cycles: dict[str, list[float]] = defaultdict(list)
    for case in cases: cycles[case["ended_at"][:10]].append(case["cycle_days"])
    current = datetime.fromisoformat(min(arrivals)).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(max(closures)).replace(tzinfo=timezone.utc)
    backlog, rows = 0, []
    while current <= end:
        day = current.date().isoformat()
        backlog += arrivals[day] - closures[day]
        rows.append({"scenario_id": scenario_id, "date": day, "arrivals": arrivals[day], "closures": closures[day], "backlog": backlog, "mean_closed_cycle_days": round(statistics.fmean(cycles[day]), 3) if cycles[day] else None, "correction_events": corrections[day]})
        current += timedelta(days=1)
    return rows

def generate(seed: int = 20250715) -> dict[str, list[dict[str, Any]]]:
    tables = {name: [] for name in ("simulation_event_log", "simulation_event_revisions", "simulation_cases", "simulation_daily_metrics", "simulation_summaries", "simulation_ocel_events", "simulation_ocel_objects", "simulation_ocel_event_object_links")}
    for offset, config in enumerate(SCENARIOS):
        rng = random.Random(seed + offset * 1009)
        active, revisions, cases = [], [], []
        for index in range(config["case_count"]):
            case_active, case_revisions, case = generate_case(config, index, rng)
            active.extend(case_active); revisions.extend(case_revisions); cases.append(case)
        active.sort(key=lambda row: (row["timestamp"], row["event_id"]))
        revisions.sort(key=lambda row: (row["timestamp"], row["event_id"]))
        cases.sort(key=lambda row: row["case_id"])
        daily = daily_metrics(config["scenario_id"], cases, revisions)
        variants = Counter(tuple(case["variant"]) for case in cases)
        cycles = [case["cycle_days"] for case in cases]
        corrected = sum(case["corrected"] for case in cases)
        summary = {
            "scenario_id": config["scenario_id"], "label": config["label"], "description": config["description"],
            "case_count": len(cases), "event_count": len(active), "revision_count": len(revisions),
            "corrected_case_count": corrected, "correction_rate": round(corrected / len(cases), 4),
            "median_cycle_days": round(statistics.median(cycles), 3), "p90_cycle_days": round(percentile(cycles, 0.9), 3),
            "peak_backlog": max(row["backlog"] for row in daily), "variant_count": len(variants),
            "dominant_variant": list(variants.most_common(1)[0][0]),
        }
        tables["simulation_event_log"].extend(active); tables["simulation_event_revisions"].extend(revisions)
        tables["simulation_cases"].extend(cases); tables["simulation_daily_metrics"].extend(daily)
        tables["simulation_summaries"].append(summary)
        for case in cases:
            tables["simulation_ocel_objects"].append({"scenario_id": config["scenario_id"], "id": case["case_id"], "object_type": "foio:Request", "attributes": {"synthetic": True}})
        for event in active:
            tables["simulation_ocel_events"].append({"scenario_id": config["scenario_id"], "id": event["event_id"], "event_type": event["activity"], "time": event["timestamp"], "attributes": {"authority_id": event["authority_id"], "revision": event["revision"], "synthetic": True}})
            tables["simulation_ocel_event_object_links"].append({"scenario_id": config["scenario_id"], "event_id": event["event_id"], "object_id": event["case_id"], "qualifier": "foip:case"})
    return tables

def write(output: Path, seed: int = 20250715) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for name, rows in generate(seed).items():
        content = "".join(json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n" for row in rows)
        (output / f"{name}.jsonl").write_text(content, encoding="utf-8", newline="\n")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20250715)
    args = parser.parse_args(); write(args.output.resolve(), args.seed)
    print(f"generated synthetic scenarios at {args.output.resolve()}")

if __name__ == "__main__": main()
