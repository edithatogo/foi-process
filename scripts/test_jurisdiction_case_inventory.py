#!/usr/bin/env python3
"""Regression checks for the bounded NZ T11 case inventory."""

import json

from build_jurisdiction_case_inventory import DEFAULT_PACKAGE, build


def main() -> None:
    inventory = build()
    assert inventory["sampling_frame"] == {
        "method": "census_of_verified_bounded_release",
        "source_release": "nz-real-batches-150-200",
        "bounded_case_count": 75,
        "included_case_count": 75,
        "full_corpus": False,
        "representativeness_claim": "bounded_release_only",
    }
    assert inventory["coverage"] == {
        "case_count": 75,
        "event_count": 425,
        "attachment_count": 179,
        "source_order_preserved": True,
    }
    assert len({case["case_id"] for case in inventory["cases"]}) == 75
    assert all(case["annotation_status"] == "pending_independent_adjudication" for case in inventory["cases"])
    assert all(case["promotion_boundary"] == "engineering_only" for case in inventory["cases"])
    source_rows = [
        json.loads(line)
        for line in (DEFAULT_PACKAGE / "event_log.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    expected_order = list(dict.fromkeys(row["logical_request_id"] for row in source_rows))
    assert [case["case_id"] for case in inventory["cases"]] == expected_order
    forbidden = {
        "request_text",
        "correspondence_text",
        "attachment_uri",
        "attachment_filename",
        "attachment_bytes",
        "requester_name",
        "requester_email",
        "third_party_identity",
        "ocr_text",
        "embeddings",
    }
    assert all(not (forbidden & case.keys()) for case in inventory["cases"])
    assert inventory["governance"]["status"] == "approved_for_repository_engineering_evidence"
    assert inventory["governance"]["external_publication_performed"] is False
    assert inventory["governance"]["independent_case_adjudication_complete"] is False
    print("jurisdiction case inventory checks passed")


if __name__ == "__main__":
    main()
