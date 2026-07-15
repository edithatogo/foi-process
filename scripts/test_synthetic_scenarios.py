#!/usr/bin/env python3
"""Invariant checks for deterministic synthetic process scenarios."""
from __future__ import annotations
import json
from generate_synthetic_scenarios import generate

def canonical(value: object) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)

def main() -> None:
    first = generate()
    second = generate()
    assert canonical(first) == canonical(second)
    summaries = {row["scenario_id"]: row for row in first["simulation_summaries"]}
    assert set(summaries) == {"baseline", "demand_surge", "concept_drift", "correction_stress"}
    assert summaries["demand_surge"]["peak_backlog"] > summaries["baseline"]["peak_backlog"]
    assert summaries["concept_drift"]["variant_count"] > summaries["baseline"]["variant_count"]
    assert summaries["concept_drift"]["p90_cycle_days"] > summaries["baseline"]["p90_cycle_days"]
    assert summaries["correction_stress"]["correction_rate"] > summaries["baseline"]["correction_rate"]

    events = first["simulation_event_log"]
    revisions = first["simulation_event_revisions"]
    assert all(event["recorded_at"] >= event["timestamp"] for event in revisions)
    assert len({event["event_id"] for event in revisions}) == len(revisions)
    assert len({event["logical_event_id"] for event in events}) == len(events)
    latest = {}
    for event in revisions:
        key = event["logical_event_id"]
        if key not in latest or event["revision"] > latest[key]["revision"]:
            latest[key] = event
    assert {event["event_id"] for event in events} == {event["event_id"] for event in latest.values()}
    active_by_case = {}
    for event in events:
        active_by_case.setdefault(event["case_id"], []).append(event)
    for case_events in active_by_case.values():
        timestamps = [event["timestamp"] for event in case_events]
        assert timestamps == sorted(timestamps)
    for event in revisions:
        if event["revision"] > 1:
            assert event["correction_of"]
            assert event["correction_of"] in {row["event_id"] for row in revisions}

    object_ids = {row["id"] for row in first["simulation_ocel_objects"]}
    ocel_event_ids = {row["id"] for row in first["simulation_ocel_events"]}
    assert len(ocel_event_ids) == len(events)
    for link in first["simulation_ocel_event_object_links"]:
        assert link["event_id"] in ocel_event_ids
        assert link["object_id"] in object_ids

    daily_by_scenario = {}
    for row in first["simulation_daily_metrics"]:
        assert row["backlog"] >= 0
        daily_by_scenario.setdefault(row["scenario_id"], []).append(row)
    for scenario_id, rows in daily_by_scenario.items():
        assert rows[-1]["backlog"] == 0, scenario_id
        assert max(row["backlog"] for row in rows) == summaries[scenario_id]["peak_backlog"]
    print("synthetic scenarios: deterministic replay, drift, corrections, backlog and OCEL links verified")

if __name__ == "__main__": main()
