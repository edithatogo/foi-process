"""Convert an Alaveteli JSON envelope to a metadata-only event candidate."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def stable_id(namespace: str, value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return f"urn:foi-process:{namespace}:sha256:{hashlib.sha256(payload).hexdigest()}"


def adapt(envelope: dict[str, Any]) -> dict[str, Any]:
    case_id = stable_id("case", [envelope["deployment_url"], envelope["id"]])
    event_id = stable_id("event", [case_id, "request_observed", envelope["updated_at"]])
    evidence_id = stable_id("evidence", envelope["source_response_sha256"])
    return {
        "schema_version": "1.0.0-draft.1",
        "event_id": event_id,
        "logical_event_id": stable_id("logical-event", [case_id, "request_observed"]),
        "revision": 1,
        "operation": "upsert",
        "site": "urn:alaveteli:site:asktheeu.org",
        "jurisdiction": envelope["jurisdiction"],
        "case_id": case_id,
        "activity": "foio:RequestObserved",
        "event_time": {"timestamp": envelope["created_at"], "precision": "second"},
        "observed_at": envelope["updated_at"],
        "captured_at": envelope["updated_at"],
        "processed_at": envelope["updated_at"],
        "assertion_status": "candidate",
        "position": {"source": "urn:alaveteli:asktheeu.org:json", "partition": "requests", "sequence": envelope["id"]},
        "objects": [{"object_id": case_id, "object_type": "foio:Request", "qualifier": "foip:case"}],
        "evidence": [{"evidence_id": evidence_id, "role": "prov:primarySource"}],
        "provenance": {"producer": "urn:foi-process:alaveteli-metadata-adapter", "producer_version": "0.1.0", "parameters": {"input_sha256": envelope["source_response_sha256"]}},
        "privacy": {"sensitivity": "public", "access_tier": "public", "disposition": "needs_review", "human_reviewed": False},
        "attributes": {"native_state": envelope["described_state"], "source_url": envelope["deployment_url"]},
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: alaveteli_metadata_adapter.py ENVELOPE.json")
    envelope = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    required = {"id", "created_at", "updated_at", "source_response_sha256", "deployment_url", "jurisdiction", "described_state"}
    missing = required - envelope.keys()
    if missing:
        raise SystemExit(f"missing envelope fields: {sorted(missing)}")
    print(json.dumps(adapt(envelope), sort_keys=True))


if __name__ == "__main__":
    main()
