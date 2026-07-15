#!/usr/bin/env python3
"""Invariant checks for the scenario process-mining Space projection."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_hf_dataset import build as build_dataset
from build_hf_space_data import build as build_space_data


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        bundle = root / "dataset"
        projection_path = root / "dashboard-data.json"
        build_dataset(bundle)
        build_space_data(bundle, projection_path)
        projection = json.loads(projection_path.read_text(encoding="utf-8"))

    summaries = {
        summary["scenario_id"]: summary for summary in projection["simulation"]["summaries"]
    }
    models = {
        model["scenario_id"]: model for model in projection["simulation"]["process_models"]
    }
    assert set(models) == set(summaries)

    for scenario_id, model in models.items():
        summary = summaries[scenario_id]
        assert sum(row["count"] for row in model["activities"]) == summary["event_count"]
        assert sum(row["count"] for row in model["edges"]) == (
            summary["event_count"] - summary["case_count"]
        )
        assert sum(row["count"] for row in model["variants"]) == summary["case_count"]
        assert len(model["variants"]) == summary["variant_count"]
        assert model["variants"][0]["activities"] == summary["dominant_variant"]
        assert all(row["mean_wait_days"] >= 0 for row in model["edges"])

    baseline_activities = {row["activity"] for row in models["baseline"]["activities"]}
    drift_activities = {row["activity"] for row in models["concept_drift"]["activities"]}
    assert "foio:ClarificationRequested" not in baseline_activities
    assert "foio:ClarificationRequested" in drift_activities
    assert len(models["concept_drift"]["variants"]) > len(models["baseline"]["variants"])
    print("HF Space projection: scenario activities, transitions, waits and variants verified")


if __name__ == "__main__":
    main()
