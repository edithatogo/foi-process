"""Validate paired Mermaid and BPMN jurisdiction-profile contracts.

Historical foundation profiles retain their label-pairing contract only while
their exact registered path and SHA-256 remain allowlisted. Registered v2
profiles use strict graph, semantic-kind, branch, pin, and fixture validation;
document content cannot select a weaker validation mode.
"""

from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from datetime import date, datetime
from pathlib import Path
from typing import Any, TypedDict

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "docs" / "jurisdictions"
FIXTURE_PATH = (
    ROOT / "examples" / "input" / "australian-state-profile-template-fixtures.json"
)

BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
KIND_NS = "https://foi-process.dev/ns/profile"
PIN_NAMES = {"profile", "source", "effective_date", "transformation", "ontology"}
SEMANTIC_KINDS = {
    "observed",
    "deterministic",
    "interpretive",
    "human_only",
    "state",
    "gateway",
    "event",
}
NODE_TAGS = {"startEvent", "endEvent", "task", "exclusiveGateway"}
STRICT_MARKER = "foi-process-profile-v2"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class StrictProfileRegistration(TypedDict):
    """Repository-owned identity for a strict profile contract."""

    template_id: str
    fixture_path: Path


STRICT_PROFILE_REGISTRY: dict[Path, StrictProfileRegistration] = {
    Path("docs/jurisdictions/australian-state-profile-template.md"): {
        "template_id": "foi-process:template:au-state-synthetic:v1",
        "fixture_path": Path(
            "examples/input/australian-state-profile-template-fixtures.json"
        ),
    }
}

LEGACY_PROFILE_SHA256_ALLOWLIST: dict[Path, str] = {
    Path(
        "docs/jurisdictions/alaveteli-deployment-audit.md"
    ): "4f3b56db366fd3bb66b96d0ba3f35bee54fe5291d1b2fb75b0e05ed4858c38dd",
    Path(
        "docs/jurisdictions/au-commonwealth-foundation.md"
    ): "4b69e8016a8c3466c2f2bfe13801d96abc6fd451a43dbc386929983e2e329059",
    Path(
        "docs/jurisdictions/canada-federal-foundation.md"
    ): "50086c862f5e00aa8ff0eec197825ba777fd8026aba306bdf355bb0482b00221",
    Path(
        "docs/jurisdictions/germany-foundation.md"
    ): "62f865ad3d2775d5805a9fd0b0994793ee30674913b1d2689a46eaa09b39b648",
    Path(
        "docs/jurisdictions/ireland-foundation.md"
    ): "29afced2371e64ccc6b5b440e00faa4394fe8f74bd3debef25ad8c69e8ff4244",
    Path(
        "docs/jurisdictions/nz-foundation.md"
    ): "84b55424afc82ac7610215a6870fd02e92f835ea3f588ebc3c585537f747a9c0",
    Path(
        "docs/jurisdictions/south-africa-foundation.md"
    ): "59f1249a40bd6f26f14d54dfa9f7f6e7b7341d6f4a58494385000d93bba04770",
    Path(
        "docs/jurisdictions/spain-foundation.md"
    ): "70ff28f60841e1e79e708c99b4ad61d7de6c6439b8a08088007ddd3ce9d5980c",
    Path(
        "docs/jurisdictions/uk-foundation.md"
    ): "e3882c5c7e7908ac325a6cf65292fd3f32650c6b0d1b73be88ee95ed7a3786c1",
    Path(
        "docs/jurisdictions/us-federal-foundation.md"
    ): "d78c6d34bc9f3c4566ff6feb92aa78a3a6d2dcbd9cfb7371a9a5e8999dd1d34e",
}


class ProfileValidationError(ValueError):
    """A fail-closed profile contract violation."""


def _contract_path(profile: Path) -> Path:
    """Return the physical repository path used as the profile identity."""

    try:
        return profile.resolve(strict=True).relative_to(ROOT.resolve(strict=True))
    except ValueError as error:
        raise ProfileValidationError(
            "profile path is outside the registered repository"
        ) from error


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _block(text: str, language: str) -> str:
    match = re.search(rf"```{re.escape(language)}\s+(.*?)```", text, re.DOTALL)
    if not match:
        raise ProfileValidationError(f"missing {language} block")
    return match.group(1).strip()


def _legacy_labels(profile: Path) -> tuple[set[str], set[str]]:
    text = profile.read_text(encoding="utf-8")
    mermaid = _block(text, "mermaid")
    bpmn = _block(text, "xml")
    mermaid_labels = {
        value.strip().strip('"') for value in re.findall(r"\w+\[([^\]]+)\]", mermaid)
    }
    bpmn_labels = {value.strip() for value in re.findall(r'name="([^"]+)"', bpmn)}
    if not mermaid_labels or not bpmn_labels:
        raise ProfileValidationError("both representations need activity labels")
    return mermaid_labels, bpmn_labels


def _validate_legacy_profile(
    profile: Path, registered_path: Path, expected_sha256: str
) -> str:
    if _sha256(profile) != expected_sha256:
        raise ProfileValidationError(
            f"legacy profile hash differs for {registered_path.as_posix()}"
        )
    mermaid, bpmn = _legacy_labels(profile)
    missing = mermaid - bpmn
    if missing:
        raise ProfileValidationError(
            f"BPMN is missing Mermaid labels: {sorted(missing)}"
        )
    return f"{len(mermaid)} legacy Mermaid labels paired"


def _strict_contract(text: str) -> dict[str, Any] | None:
    pattern = rf"```{re.escape(STRICT_MARKER)}\s+(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise ProfileValidationError(
            f"invalid strict contract JSON: {error}"
        ) from error
    if not isinstance(value, dict):
        raise ProfileValidationError("strict contract must be an object")
    return value


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_mermaid(
    source: str,
) -> tuple[dict[str, tuple[str, str]], set[tuple[str, str, str]]]:
    nodes: dict[str, tuple[str, str]] = {}
    edges: set[tuple[str, str, str]] = set()
    node_pattern = re.compile(
        r"^\s*([A-Za-z][\w-]*)\s*"
        r'(?:\[\s*"([^"]+)"\s*\]|\{\s*"([^"]+)"\s*\}|\(\[\s*"([^"]+)"\s*\]\))'
        r"\s*:::(\w+)\s*$"
    )
    edge_pattern = re.compile(
        r"^\s*([A-Za-z][\w-]*)\s*-->\s*(?:\|([^|]+)\|\s*)?([A-Za-z][\w-]*)\s*$"
    )
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("flowchart ", "%%")):
            continue
        node = node_pattern.match(line)
        if node:
            node_id = node.group(1)
            if node_id in nodes:
                raise ProfileValidationError(f"duplicate Mermaid node {node_id}")
            label = next(value for value in node.groups()[1:4] if value is not None)
            nodes[node_id] = (label.strip(), node.group(5))
            continue
        edge = edge_pattern.match(line)
        if edge:
            value = (edge.group(1), edge.group(3), (edge.group(2) or "").strip())
            if value in edges:
                raise ProfileValidationError(f"duplicate Mermaid edge {value}")
            edges.add(value)
            continue
        raise ProfileValidationError(f"unsupported Mermaid syntax: {stripped}")
    if not nodes or not edges:
        raise ProfileValidationError(
            "strict Mermaid graph needs declared nodes and edges"
        )
    return nodes, edges


def _parse_bpmn(
    source: str,
) -> tuple[dict[str, tuple[str, str, str]], set[tuple[str, str, str]]]:
    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        raise ProfileValidationError(f"invalid BPMN XML: {error}") from error
    if root.tag != f"{{{BPMN_NS}}}definitions":
        raise ProfileValidationError("BPMN root must be BPMN 2.0 definitions")
    if not root.get("targetNamespace"):
        raise ProfileValidationError("BPMN definitions require targetNamespace")
    processes = root.findall(f"{{{BPMN_NS}}}process")
    if len(processes) != 1:
        raise ProfileValidationError("BPMN must contain exactly one process")
    process = processes[0]
    if process.get("isExecutable") != "false":
        raise ProfileValidationError("engineering template BPMN must be non-executable")

    nodes: dict[str, tuple[str, str, str]] = {}
    edges: set[tuple[str, str, str]] = set()
    flow_ids: set[str] = set()
    for element in process:
        tag = _local_name(element.tag)
        if tag in NODE_TAGS:
            node_id = element.get("id", "")
            label = element.get("name", "")
            kind = element.get(f"{{{KIND_NS}}}kind", "")
            if not node_id or not label or not kind:
                raise ProfileValidationError(
                    f"BPMN {tag} requires id, name, and foip:kind"
                )
            if node_id in nodes:
                raise ProfileValidationError(f"duplicate BPMN node {node_id}")
            nodes[node_id] = (label, kind, tag)
        elif tag == "sequenceFlow":
            flow_id = element.get("id", "")
            source_id = element.get("sourceRef", "")
            target_id = element.get("targetRef", "")
            label = element.get("name", "")
            if not flow_id or not source_id or not target_id:
                raise ProfileValidationError(
                    "BPMN sequenceFlow requires id, sourceRef, and targetRef"
                )
            if flow_id in flow_ids:
                raise ProfileValidationError(
                    f"duplicate BPMN sequenceFlow id {flow_id}"
                )
            flow_ids.add(flow_id)
            value = (source_id, target_id, label)
            if value in edges:
                raise ProfileValidationError(f"duplicate BPMN edge {value}")
            edges.add(value)
        else:
            raise ProfileValidationError(f"unsupported BPMN process element {tag}")
    if not nodes or not edges:
        raise ProfileValidationError("BPMN graph needs nodes and sequence flows")
    return nodes, edges


def _validate_pins(contract: dict[str, Any]) -> None:
    pins = contract.get("pins")
    if not isinstance(pins, dict) or set(pins) != PIN_NAMES:
        raise ProfileValidationError(f"pins must contain exactly {sorted(PIN_NAMES)}")
    for name, pin in pins.items():
        if (
            not isinstance(pin, dict)
            or not isinstance(pin.get("id"), str)
            or not pin["id"].strip()
        ):
            raise ProfileValidationError(f"{name} pin requires an id")
        if not SHA256.fullmatch(str(pin.get("sha256", ""))):
            raise ProfileValidationError(
                f"{name} pin requires an exact lowercase SHA-256"
            )
    interval = pins["effective_date"]
    try:
        start = date.fromisoformat(interval["from"])
        end = date.fromisoformat(interval["to"])
    except (KeyError, TypeError, ValueError) as error:
        raise ProfileValidationError(
            "effective_date pin requires ISO from/to dates"
        ) from error
    if start > end:
        raise ProfileValidationError("effective_date pin has an inverted interval")


def _validate_graph(
    contract: dict[str, Any],
    mermaid_nodes: dict[str, tuple[str, str]],
    mermaid_edges: set[tuple[str, str, str]],
    bpmn_nodes: dict[str, tuple[str, str, str]],
    bpmn_edges: set[tuple[str, str, str]],
) -> None:
    if set(mermaid_nodes) != set(bpmn_nodes):
        raise ProfileValidationError("Mermaid and BPMN node IDs differ")
    for node_id, (label, kind) in mermaid_nodes.items():
        if kind not in SEMANTIC_KINDS:
            raise ProfileValidationError(f"{node_id}: unsupported semantic kind {kind}")
        bpmn_label, bpmn_kind, tag = bpmn_nodes[node_id]
        if (label, kind) != (bpmn_label, bpmn_kind):
            raise ProfileValidationError(
                f"{node_id}: Mermaid/BPMN label or kind differs"
            )
        if kind == "gateway" and tag != "exclusiveGateway":
            raise ProfileValidationError(
                f"{node_id}: gateway kind must use BPMN exclusiveGateway"
            )
        if kind == "event" and tag not in {"startEvent", "endEvent"}:
            raise ProfileValidationError(f"{node_id}: event kind must use a BPMN event")
        if kind not in {"gateway", "event"} and tag != "task":
            raise ProfileValidationError(
                f"{node_id}: semantic work/state must use a BPMN task"
            )
    if mermaid_edges != bpmn_edges:
        raise ProfileValidationError(
            "Mermaid and BPMN sequence flows or branch labels differ"
        )

    starts = [
        node_id for node_id, value in bpmn_nodes.items() if value[2] == "startEvent"
    ]
    ends = {node_id for node_id, value in bpmn_nodes.items() if value[2] == "endEvent"}
    if len(starts) != 1 or not ends:
        raise ProfileValidationError(
            "graph requires exactly one start and at least one end"
        )

    outgoing: dict[str, list[tuple[str, str]]] = defaultdict(list)
    incoming: dict[str, list[str]] = defaultdict(list)
    for source_id, target_id, label in bpmn_edges:
        if source_id not in bpmn_nodes or target_id not in bpmn_nodes:
            raise ProfileValidationError("sequence flow references an unknown node")
        outgoing[source_id].append((target_id, label))
        incoming[target_id].append(source_id)
    for node_id, (_, _, tag) in bpmn_nodes.items():
        if tag == "exclusiveGateway":
            branches = outgoing[node_id]
            labels = [label for _, label in branches]
            if len(branches) < 2 or any(not label for label in labels):
                raise ProfileValidationError(
                    f"{node_id}: gateway needs at least two named branches"
                )
            if len(labels) != len(set(labels)):
                raise ProfileValidationError(
                    f"{node_id}: gateway branch labels must be unique"
                )
        elif tag == "endEvent":
            if outgoing[node_id]:
                raise ProfileValidationError(f"{node_id}: end event has outgoing flow")
        elif not outgoing[node_id]:
            raise ProfileValidationError(
                f"{node_id}: non-end node has no outgoing flow"
            )
        if tag != "startEvent" and not incoming[node_id]:
            raise ProfileValidationError(
                f"{node_id}: non-start node has no incoming flow"
            )

    reached: set[str] = set()
    queue = deque(starts)
    while queue:
        node_id = queue.popleft()
        if node_id in reached:
            continue
        reached.add(node_id)
        queue.extend(target for target, _ in outgoing[node_id])
    if reached != set(bpmn_nodes):
        raise ProfileValidationError(
            f"unreachable graph nodes: {sorted(set(bpmn_nodes) - reached)}"
        )

    required_kinds = set(contract.get("required_semantic_kinds", []))
    actual_kinds = {kind for _, kind in mermaid_nodes.values()}
    if required_kinds != SEMANTIC_KINDS or not required_kinds <= actual_kinds:
        raise ProfileValidationError(
            "contract must require every registered semantic kind"
        )
    required_states = contract.get("required_states")
    if not isinstance(required_states, dict) or set(required_states) != {
        "unresolved",
        "unsupported",
    }:
        raise ProfileValidationError(
            "contract must declare unresolved and unsupported states"
        )
    for state_name, node_id in required_states.items():
        if mermaid_nodes.get(node_id, ("", ""))[1] != "state":
            raise ProfileValidationError(f"{state_name} must resolve to a state node")

    rejection_values = contract.get("required_rejection_edges")
    if (
        not isinstance(rejection_values, list)
        or not rejection_values
        or not all(
            isinstance(edge, dict) and set(edge) == {"source", "target", "label"}
            for edge in rejection_values
        )
    ):
        raise ProfileValidationError("contract requires structured rejection edges")
    rejection_edges = {
        (edge["source"], edge["target"], edge["label"]) for edge in rejection_values
    }
    if not rejection_edges or not rejection_edges <= mermaid_edges:
        raise ProfileValidationError("declared rejection paths are missing")
    remediation_edge = contract.get("required_remediation_edge")
    if not isinstance(remediation_edge, dict) or set(remediation_edge) != {
        "source",
        "target",
        "label",
    }:
        raise ProfileValidationError("contract must declare a remediation edge")
    remediation = (
        remediation_edge.get("source", ""),
        remediation_edge.get("target", ""),
        remediation_edge.get("label", ""),
    )
    if remediation[0] == remediation[1] or remediation not in mermaid_edges:
        raise ProfileValidationError("declared remediation loop edge is missing")

    def can_reach(source_id: str, target_id: str) -> bool:
        pending = deque([source_id])
        visited: set[str] = set()
        while pending:
            current = pending.popleft()
            if current == target_id:
                return True
            if current in visited:
                continue
            visited.add(current)
            pending.extend(target for target, _ in outgoing[current])
        return False

    if not can_reach(remediation[1], remediation[0]):
        raise ProfileValidationError("declared remediation edge does not form a loop")
    for node_id in bpmn_nodes:
        if not any(can_reach(node_id, end_id) for end_id in ends):
            raise ProfileValidationError(f"{node_id}: no terminal state is reachable")


def _parse_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timezone required")
    return parsed


def _validate_fixtures(contract: dict[str, Any], fixture_path: Path) -> None:
    try:
        fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProfileValidationError(f"invalid fixture bundle: {error}") from error
    if not isinstance(fixtures, dict) or fixtures.get("schema_version") != "1.0.0":
        raise ProfileValidationError("fixture bundle requires schema_version 1.0.0")
    if fixtures.get("template_id") != contract.get("template_id"):
        raise ProfileValidationError("fixture bundle template_id differs")
    rows = fixtures.get("fixtures")
    if (
        not isinstance(rows, list)
        or len(rows) != 4
        or not all(isinstance(row, dict) for row in rows)
        or {row.get("scenario_kind") for row in rows}
        != {"positive", "negative", "temporal", "non_equivalence"}
    ):
        raise ProfileValidationError("fixtures must contain exact scenario kinds")
    fixture_ids = [row.get("fixture_id") for row in rows]
    if any(
        not isinstance(fixture_id, str) or not fixture_id for fixture_id in fixture_ids
    ) or len(set(fixture_ids)) != len(fixture_ids):
        raise ProfileValidationError("fixtures require unique non-empty IDs")
    for row in rows:
        if row.get("pins") != contract.get("pins"):
            raise ProfileValidationError(
                f"{row.get('fixture_id')}: fixture pins differ"
            )
        if row.get("legal_conclusion") is not None:
            raise ProfileValidationError(
                f"{row.get('fixture_id')}: legal conclusion is forbidden"
            )
        if row.get("evidence_class") != "synthetic_engineering_only":
            raise ProfileValidationError(
                f"{row.get('fixture_id')}: fixture escaped synthetic scope"
            )
        try:
            _parse_datetime(str(row["observed_at"]))
        except (KeyError, TypeError, ValueError) as error:
            raise ProfileValidationError(
                f"{row.get('fixture_id')}: observed_at requires a timezone"
            ) from error

    interval = contract["pins"]["effective_date"]
    start = date.fromisoformat(interval["from"])
    end = date.fromisoformat(interval["to"])
    by_kind = {row["scenario_kind"]: row for row in rows}
    temporal = by_kind["temporal"]
    observed_date = _parse_datetime(temporal["observed_at"]).date()
    if start <= observed_date <= end or temporal.get("expected_state") != "unresolved":
        raise ProfileValidationError(
            "temporal fixture must fall outside the pinned interval"
        )
    non_equivalence = by_kind["non_equivalence"]
    comparison = non_equivalence.get("comparison_profile")
    if (
        non_equivalence.get("equivalence_claim") is not False
        or not isinstance(comparison, dict)
        or not isinstance(comparison.get("id"), str)
        or not comparison["id"]
        or comparison.get("sha256") == contract["pins"]["profile"]["sha256"]
        or not SHA256.fullmatch(str(comparison.get("sha256", "")))
    ):
        raise ProfileValidationError(
            "non-equivalence fixture must pin a distinct profile"
        )
    if by_kind["positive"].get("expected_state") != "candidate_ready":
        raise ProfileValidationError("positive fixture must reach candidate_ready")
    if by_kind["negative"].get("expected_state") != "unsupported":
        raise ProfileValidationError("negative fixture must preserve unsupported")
    if non_equivalence.get("expected_state") != "unsupported":
        raise ProfileValidationError(
            "non-equivalence fixture must preserve unsupported"
        )


def _validate_strict_profile(
    text: str,
    fixture_path: Path | None,
    registration: StrictProfileRegistration,
    registered_path: Path,
) -> str:
    contract = _strict_contract(text)
    if contract is None:
        raise ProfileValidationError(
            f"registered strict profile is missing {STRICT_MARKER}: "
            f"{registered_path.as_posix()}"
        )
    if contract.get("schema_version") != "2.0.0":
        raise ProfileValidationError("strict contract requires schema_version 2.0.0")
    if contract.get("template_id") != registration["template_id"]:
        raise ProfileValidationError(
            "strict contract template_id differs from registry"
        )
    if contract.get("evidence_class") != "synthetic_engineering_only":
        raise ProfileValidationError(
            "strict template must remain synthetic engineering evidence"
        )
    if contract.get("legal_conclusions_allowed") is not False:
        raise ProfileValidationError("strict template must forbid legal conclusions")
    _validate_pins(contract)
    mermaid_nodes, mermaid_edges = _parse_mermaid(_block(text, "mermaid"))
    bpmn_nodes, bpmn_edges = _parse_bpmn(_block(text, "xml"))
    _validate_graph(contract, mermaid_nodes, mermaid_edges, bpmn_nodes, bpmn_edges)
    selected_fixture = (
        fixture_path
        if fixture_path is not None
        else ROOT / registration["fixture_path"]
    )
    _validate_fixtures(contract, selected_fixture)
    return f"{len(mermaid_nodes)} strict nodes and {len(mermaid_edges)} flows paired"


def validate_profile(profile: Path, fixture_path: Path | None = None) -> str:
    registered_path = _contract_path(profile)
    text = profile.read_text(encoding="utf-8")
    registration = STRICT_PROFILE_REGISTRY.get(registered_path)
    if registration is None:
        expected_sha256 = LEGACY_PROFILE_SHA256_ALLOWLIST.get(registered_path)
        if expected_sha256 is None:
            raise ProfileValidationError(
                f"unregistered jurisdiction profile path: {registered_path.as_posix()}"
            )
        return _validate_legacy_profile(profile, registered_path, expected_sha256)

    return _validate_strict_profile(text, fixture_path, registration, registered_path)


def main() -> None:
    profiles = sorted(PROFILE_DIR.glob("*.md"))
    if not profiles:
        raise SystemExit("no jurisdiction profiles found")
    failed = False
    for profile in profiles:
        try:
            result = validate_profile(profile)
        except (OSError, ProfileValidationError) as error:
            failed = True
            print(f"FAIL {profile}: {error}")
        else:
            print(f"validated {profile.name}: {result}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
