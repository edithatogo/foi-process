#!/usr/bin/env python3
"""Regression checks for the bounded NZ T11 case inventory."""

from build_jurisdiction_case_inventory import build


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
    assert all("request_text" not in case and "attachment_uri" not in case for case in inventory["cases"])
    print("jurisdiction case inventory checks passed")


if __name__ == "__main__":
    main()
