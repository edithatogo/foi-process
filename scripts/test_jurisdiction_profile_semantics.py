"""Adversarial tests for the strict jurisdiction-profile semantic contract."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from validate_jurisdiction_profiles import (
    FIXTURE_PATH,
    PROFILE_DIR,
    ProfileValidationError,
    validate_profile,
)

PROFILE = PROFILE_DIR / "australian-state-profile-template.md"


def _must_fail(
    name: str,
    *,
    profile_transform=lambda value: value,
    fixture_transform=lambda value: value,
) -> None:
    with tempfile.TemporaryDirectory(prefix="foi-process-profile-test-") as directory:
        root = Path(directory)
        profile = root / "profile.md"
        fixture = root / "fixtures.json"
        profile.write_text(
            profile_transform(PROFILE.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        fixture.write_text(
            json.dumps(
                fixture_transform(json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))),
                indent=2,
            ),
            encoding="utf-8",
        )
        try:
            validate_profile(profile, fixture)
        except ProfileValidationError:
            return
        raise AssertionError(f"{name}: invalid contract was accepted")


def _missing_source_pin(text: str) -> str:
    return text.replace('"source": {', '"source_missing": {', 1)


def _bpmn_label_drift(text: str) -> str:
    return text.replace(
        'name="Observed request event" foip:kind="observed"',
        'name="Observed request changed" foip:kind="observed"',
        1,
    )


def _bpmn_kind_drift(text: str) -> str:
    return text.replace(
        'name="Map event to pinned ontology" foip:kind="interpretive"',
        'name="Map event to pinned ontology" foip:kind="deterministic"',
        1,
    )


def _unparsed_mermaid_node(text: str) -> str:
    return text.replace(
        '  obs_request["Observed request event"]:::observed\n',
        '  obs_request["Observed request event"]:::observed\n'
        '  hidden["Unpaired hidden node"]\n',
        1,
    )


def _remove_mapping_branch(text: str) -> str:
    text = text.replace(
        "  gw_mapping -->|unresolved| state_unresolved\n",
        "",
        1,
    )
    return text.replace(
        '    <sequenceFlow id="flow-10" name="unresolved" '
        'sourceRef="gw_mapping" targetRef="state_unresolved"/>\n',
        "",
        1,
    )


def _remove_remediation_loop(text: str) -> str:
    text = text.replace(
        "  human_remediate -->|reassess| calc_temporal\n",
        "",
        1,
    )
    return text.replace(
        '    <sequenceFlow id="flow-19" name="reassess" '
        'sourceRef="human_remediate" targetRef="calc_temporal"/>\n',
        "",
        1,
    )


def _temporal_inside(bundle: dict) -> dict:
    row = next(row for row in bundle["fixtures"] if row["scenario_kind"] == "temporal")
    row["observed_at"] = "2026-06-15T00:00:00+10:00"
    return bundle


def _claim_equivalence(bundle: dict) -> dict:
    row = next(
        row for row in bundle["fixtures"] if row["scenario_kind"] == "non_equivalence"
    )
    row["equivalence_claim"] = True
    return bundle


def _malformed_pin(bundle: dict) -> dict:
    bundle["fixtures"][0]["pins"]["ontology"]["sha256"] = "not-a-digest"
    return bundle


def main() -> None:
    result = validate_profile(PROFILE, FIXTURE_PATH)
    assert result == "17 strict nodes and 19 flows paired"
    _must_fail("missing source pin", profile_transform=_missing_source_pin)
    _must_fail("BPMN label drift", profile_transform=_bpmn_label_drift)
    _must_fail("BPMN kind drift", profile_transform=_bpmn_kind_drift)
    _must_fail("unparsed Mermaid node", profile_transform=_unparsed_mermaid_node)
    _must_fail("gateway branch deletion", profile_transform=_remove_mapping_branch)
    _must_fail("remediation loop deletion", profile_transform=_remove_remediation_loop)
    _must_fail("temporal fixture inside interval", fixture_transform=_temporal_inside)
    _must_fail("false cross-profile equivalence", fixture_transform=_claim_equivalence)
    _must_fail("malformed fixture pin", fixture_transform=_malformed_pin)
    print("validated strict jurisdiction profile with 9 adversarial mutations")


if __name__ == "__main__":
    main()
