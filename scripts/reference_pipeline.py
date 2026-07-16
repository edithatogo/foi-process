#!/usr/bin/env python3
"""Development oracle for v3 fixtures.

This is not a production dependency. It makes deterministic contract/replay behaviour testable
before the Rust repository is exported and compiled.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0-draft.1"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sid(namespace: str, value: Any) -> str:
    return f"urn:{namespace}:sha256:{hashlib.sha256(canonical_bytes(value)).hexdigest()}"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def privacy(disposition="publish", sensitivity="public", access="public") -> dict[str, Any]:
    return {
        "sensitivity": sensitivity,
        "access_tier": access,
        "disposition": disposition,
        "reason_codes": ["privacy:fixture_reviewed"],
        "human_reviewed": True,
    }


def evidence_record(logical: str, revision: int, text: str, captured: str, public=True) -> dict[str, Any]:
    sha = digest(text)
    return {
        "schema_version": VERSION,
        "evidence_id": sid("foi-process:evidence", [logical, revision, sha]),
        "logical_record_id": logical,
        "revision": revision,
        "source_kind": "foip:AlaveteliJson",
        "media_type": "application/json",
        "locator": {"uri": f"https://fyi.org.nz/request/demo/{logical.rsplit(':',1)[-1]}"},
        "content_sha256": sha,
        "byte_length": len(text.encode()),
        "captured_at": captured,
        "privacy": privacy() if public else privacy("publish_metadata_only", "personal", "research"),
        "attributes": {},
    }


def delta(logical: str, revision: int, activity: str, event_time: str, sequence: int,
          request: str, text: str, previous: str | None = None, public=True, operation="upsert") -> dict[str, Any]:
    captured = "2026-07-09T00:00:00Z"
    evidence = None if operation == "delete" else evidence_record(logical, revision, text, captured, public)
    current = None if evidence is None else evidence["content_sha256"]
    body = {
        "logical_record_id": logical,
        "revision": revision,
        "operation": operation,
        "position": {"source": "urn:fyi-cli:site:fyi.org.nz", "partition": "requests", "sequence": sequence},
        "current": current,
    }
    result = {
        "schema_version": VERSION,
        "delta_id": sid("foi-process:delta", body),
        "logical_record_id": logical,
        "revision": revision,
        "operation": operation,
        "site": "urn:alaveteli:site:fyi.org.nz",
        "jurisdiction": "jurisdiction:NZ",
        "position": body["position"],
        "observed_at": captured,
        "captured_at": captured,
        "current_content_sha256": current,
        "evidence": evidence,
        "request_hint": request,
        "attributes": {"platform_activity": activity, "event_time": event_time, "authority_id": "nz:agency:demo"},
    }
    if previous:
        result["previous_content_sha256"] = previous
    if operation == "delete":
        result.pop("evidence")
        result.pop("current_content_sha256")
    return result


MAPPING = {
    "request_sent": "foio:RequestSent",
    "authority_response": "foio:AuthorityResponseReceived",
    "extension": "foio:ExtensionNotified",
    "closed": "foio:ClosedObserved",
}


@dataclass
class Replay:
    seen: set[str] = field(default_factory=set)
    records: dict[str, dict[str, Any]] = field(default_factory=dict)
    positions: dict[tuple[str, str], int] = field(default_factory=dict)

    def apply(self, d: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]:
        if d["delta_id"] in self.seen:
            return {"delta_id": d["delta_id"], "status": "duplicate"}, None, None
        current = self.records.get(d["logical_record_id"])
        if current:
            if d["revision"] < current["revision"]:
                return {"delta_id": d["delta_id"], "status": "stale"}, None, None
            if d["revision"] == current["revision"]:
                status = "duplicate" if d.get("current_content_sha256") == current.get("digest") else "conflict"
                return {"delta_id": d["delta_id"], "status": status}, None, None
            if d["revision"] > current["revision"] + 1:
                return {"delta_id": d["delta_id"], "status": "gap_detected"}, None, None
        position_key = (d["position"]["source"], d["position"]["partition"])
        previous_sequence = self.positions.get(position_key)
        if previous_sequence is not None:
            if d["position"]["sequence"] == previous_sequence:
                return {"delta_id": d["delta_id"], "status": "conflict"}, None, None
            if d["position"]["sequence"] < previous_sequence:
                return {"delta_id": d["delta_id"], "status": "position_regression"}, None, None
            if d["position"]["sequence"] > previous_sequence + 1:
                return {"delta_id": d["delta_id"], "status": "position_gap"}, None, None
        event, obj = normalize(d, current and current.get("event_id"))
        self.seen.add(d["delta_id"])
        self.positions[position_key] = d["position"]["sequence"]
        self.records[d["logical_record_id"]] = {
            "revision": d["revision"], "digest": d.get("current_content_sha256"), "event_id": event["event_id"]
        }
        return {"delta_id": d["delta_id"], "status": "accepted", "emitted_event_ids": [event["event_id"]]}, event, obj


def normalize(d: dict[str, Any], previous_event: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    activity = MAPPING.get(d["attributes"].get("platform_activity"), "foip:UnmappedPlatformEvent")
    assertion = "observed" if activity != "foip:UnmappedPlatformEvent" else "candidate"
    logical_event = sid("foi-process:event-logical", [d["site"], d["request_hint"], d["logical_record_id"]])
    event_id = sid("foi-process:event", [logical_event, d["revision"], d["operation"]])
    op = "retract" if d["operation"] == "delete" else "upsert"
    evref = []
    if d.get("evidence"):
        evref = [{"evidence_id": d["evidence"]["evidence_id"], "role": "prov:primarySource"}]
    p = d.get("evidence", {}).get("privacy", privacy("needs_review", "unknown", "restricted"))
    event = {
        "schema_version": VERSION,
        "event_id": event_id,
        "logical_event_id": logical_event,
        "revision": d["revision"],
        "operation": op,
        "site": d["site"],
        "jurisdiction": d["jurisdiction"],
        "case_id": d["request_hint"],
        "activity": activity,
        "event_time": {"timestamp": d["attributes"]["event_time"], "precision": "second"},
        "observed_at": d["observed_at"],
        "captured_at": d["captured_at"],
        "processed_at": "2026-07-09T00:05:00Z",
        "position": d["position"],
        "assertion_status": assertion,
        "objects": [{"object_id": d["request_hint"], "object_type": "foio:Request", "qualifier": "foip:case"}],
        "evidence": evref,
        "provenance": {
            "producer": "urn:foi-process:normalizer:deterministic",
            "producer_version": "0.1.0",
            "input_ids": [d["delta_id"]],
            "parameters": {"mapping_profile": "urn:foi-process:profile:fyi-minimal"},
        },
        "privacy": p,
        "attributes": {"native_activity": d["attributes"].get("platform_activity"), "authority_id": "nz:agency:demo"},
    }
    if assertion == "candidate": event["confidence"] = 0.0
    if previous_event:
        event["retracts_event_id" if op == "retract" else "supersedes_event_id"] = previous_event
    obj = {
        "schema_version": VERSION,
        "object_id": d["request_hint"],
        "object_type": "foio:Request",
        "privacy": p,
        "attributes": {},
        "evidence": evref,
    }
    return event, obj


def materialize(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for e in events:
        current = latest.get(e["logical_event_id"])
        if not current or (e["revision"], e["event_id"]) > (current["revision"], current["event_id"]):
            latest[e["logical_event_id"]] = e
    return sorted((e for e in latest.values() if e["operation"] == "upsert"), key=lambda e: (e["case_id"], e["event_time"]["timestamp"], e["position"]["sequence"], e["event_id"]))


def summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    active = materialize(events)
    cases: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in active: cases[e["case_id"]].append(e)
    nodes, edges, variants, waits = Counter(), Counter(), Counter(), Counter()
    for trace in cases.values():
        trace.sort(key=lambda e: (e["event_time"]["timestamp"], e["position"]["sequence"], e["event_id"]))
        acts = tuple(e["activity"] for e in trace)
        variants[acts] += 1
        nodes.update(acts)
        for a, b in zip(trace, trace[1:]):
            edge = (a["activity"], b["activity"]); edges[edge] += 1
            seconds = int((datetime.fromisoformat(b["event_time"]["timestamp"].replace("Z", "+00:00")) - datetime.fromisoformat(a["event_time"]["timestamp"].replace("Z", "+00:00"))).total_seconds())
            bucket = -1 if seconds < 0 else 0 if seconds == 0 else seconds.bit_length()
            waits[(edge, bucket)] += 1
    return {
        "case_count": len(cases), "active_event_count": len(active),
        "activities": [{"activity": k, "count": v} for k,v in sorted(nodes.items())],
        "edges": [{"edge": {"from": a, "to": b}, "count": v} for (a,b),v in sorted(edges.items())],
        "variants": [{"activities": list(k), "count": v} for k,v in sorted(variants.items())],
        "waiting_time_histogram": [{"key": {"edge": {"from": a, "to": b}, "log2_bucket": bucket}, "count": v} for ((a,b),bucket),v in sorted(waits.items())],
    }


def generate() -> None:
    request = "urn:fyi-nz:request:demo-1"
    d1 = delta("urn:fyi-nz:message:1", 1, "request_sent", "2025-01-06T09:00:00+13:00", 1, request, "request sent")
    d2 = delta("urn:fyi-nz:message:2", 1, "authority_response", "2025-01-07T11:00:00+13:00", 2, request, "acknowledged")
    d3 = delta("urn:fyi-nz:message:3", 1, "extension", "2025-01-20T10:00:00+13:00", 3, request, "extension 10 working days")
    d4 = delta("urn:fyi-nz:message:3", 2, "extension", "2025-01-20T10:15:00+13:00", 4, request, "extension corrected: 15 working days", d3["current_content_sha256"])
    d5 = delta("urn:fyi-nz:message:4", 1, "closed", "2025-02-14T16:00:00+13:00", 5, request, "closed", public=False)
    deltas = [d1,d2,d3,d4,d5]
    replay=Replay(); outcomes=[]; events=[]; evidence=[]; objects={}
    for d in deltas:
        outcome,event,obj=replay.apply(d); outcomes.append(outcome)
        if d.get("evidence"): evidence.append(d["evidence"])
        if event: events.append(event)
        if obj: objects[obj["object_id"]]=obj
    state_material = sorted((k,v["revision"],v.get("digest"),v.get("event_id")) for k,v in replay.records.items())
    checkpoint = {
        "schema_version": VERSION,
        "checkpoint_id": sid("foi-process:checkpoint", state_material),
        "consumer": "urn:foi-process:consumer:fixture",
        "created_at": "2026-07-09T00:05:00Z",
        "partitions": [{"source": source, "partition": partition, "last_sequence": sequence} for (source,partition),sequence in replay.positions.items()],
        "state_hash": hashlib.sha256(canonical_bytes(state_material)).hexdigest(),
        "attributes": {},
    }
    snapshot_records=[{"logical_record_id":k,"revision":v["revision"],"current_digest":v.get("digest"),"last_delta_id":next(d["delta_id"] for d in reversed(deltas) if d["logical_record_id"]==k and d["revision"]==v["revision"]),"last_event_id":v.get("event_id")} for k,v in sorted(replay.records.items())]
    snapshot={"schema_version":VERSION,"snapshot_id":sid("foi-process:replay-snapshot",[checkpoint["consumer"],checkpoint["state_hash"]]),"consumer":checkpoint["consumer"],"created_at":checkpoint["created_at"],"records":snapshot_records,"partitions":checkpoint["partitions"],"state_hash":checkpoint["state_hash"]}
    bundle={"schema_version":VERSION,"evidence":evidence,"objects":list(objects.values()),"events":events,"findings":[],"human_reviews":[],"checkpoint":checkpoint}
    public_events=[]; withheld=0; metadata=0; evid_index={e["evidence_id"]:e for e in evidence}
    for e in materialize(events):
        disp=e["privacy"]["disposition"]
        if disp in ("withhold","needs_review"): withheld+=1; continue
        links=[]
        if disp=="publish_metadata_only": metadata+=1
        else:
            for ref in e.get("evidence",[]):
                rec=evid_index.get(ref["evidence_id"])
                if rec and rec["privacy"]["disposition"]=="publish":
                    links.append({"evidence_id":rec["evidence_id"],"uri":rec["locator"].get("uri"),"media_type":rec["media_type"],"content_sha256":rec["content_sha256"]})
        public_events.append({k:e[k] for k in ["event_id","logical_event_id","site","jurisdiction","case_id","activity","event_time","assertion_status"]} | {"source_sequence":e["position"]["sequence"],"evidence":links,"attributes":{k:v for k,v in e.get("attributes",{}).items() if k in {"authority_id","native_activity"}}})
    public={"synthetic_fixture":True,"policy_id":"urn:foi-process:publication:dashboard-default","events":public_events,"withheld_event_count":withheld,"metadata_only_event_count":metadata}
    ocel={"synthetic_fixture":True,
        "events":[{"id":e["event_id"],"event_type":e["activity"],"time":e["event_time"]["timestamp"],"attributes":e.get("attributes",{})} for e in materialize(events)],
        "objects":[{"id":o["object_id"],"object_type":o["object_type"],"attributes":o.get("attributes",{})} for o in objects.values()],
        "event_object_links":[{"event_id":e["event_id"],"object_id":o["object_id"],"qualifier":o["qualifier"]} for e in materialize(events) for o in e["objects"]],
        "object_object_links":[],"object_changes":[]}

    doc_text="The time limit is extended by 15 working days."
    doc={"schema_version":VERSION,"document_id":"urn:fyi-nz:document:demo-extension","source_evidence_id":d4["evidence"]["evidence_id"],"source_sha256":d4["evidence"]["content_sha256"],"media_type":"application/pdf","created_at":"2026-07-09T00:05:00Z","extractor":{"name":"fe-reader-document-pipeline","version":"0.1.0-draft","runtime":"rust","license":"MIT OR Apache-2.0"},"pages":[{"page_number":1,"page_sha256":digest("rendered-page-1"),"width":595.0,"height":842.0,"extraction_method":"ocr","model":{"name":"ocr-adapter","version":"unselected","runtime":"onnx","license":"repository-license"},"quality_score":0.94,"segments":[{"segment_id":sid("foi-process:segment",[1,doc_text]),"reading_order":1,"text_sha256":digest(doc_text),"character_count":len(doc_text),"inline_text":doc_text,"bbox":{"page":1,"x":72.0,"y":110.0,"width":420.0,"height":24.0,"coordinate_system":"pdf_points_top_left"},"confidence":0.94,"language":"en-NZ","privacy":privacy()}]}],"privacy":privacy(),"attributes":{"ocr_required":True}}
    signal={"schema_version":VERSION,"signal_id":sid("foi-process:signal",[doc["document_id"],"foio:ExtensionNotified",doc_text]),"signal_type":"foip:ExtensionSignal","assertion_status":"candidate","confidence":0.92,"document_id":doc["document_id"],"evidence":[{"evidence_id":d4["evidence"]["evidence_id"],"selector":{"selector_type":"bounding_box","bbox":doc["pages"][0]["segments"][0]["bbox"]},"role":"prov:primarySource"}],"proposed_activity":"foio:ExtensionNotified","extracted_values":{"duration_working_days":15},"producer":{"name":"nlp-policy-nz","version":"0.1.0-draft","runtime":"rust/python","license":"repository-license"},"privacy":privacy()}
    review={"schema_version":VERSION,"review_id":sid("foi-process:human-review",[signal["signal_id"],"confirm","fixture-human"]),"subject_id":signal["signal_id"],"reviewer_id":"urn:foi-process:reviewer:fixture-human","profile_id":"urn:foi-process:review-profile:foi-o-v0","reviewed_at":"2026-07-09T00:06:00Z","decision":"confirm","previous_status":"candidate","resulting_status":"human_certified","evidence":signal["evidence"],"rationale":"Fixture demonstrating an explicit human promotion boundary.","corrected_values":{}}
    trace_finding={"rule_id":"oia-nz:IndicativeDeadlineCalculated","layer":"statutory","severity":"info","message":"An indicative deadline was calculated from observed request timing; this is not a certified legal conclusion.","subject_id":request,"evidence":[{"evidence_id":d1["evidence"]["evidence_id"],"role":"prov:primarySource"}],"requires_human_review":False,"details":{"calendar_profile":"nz:working-days:fixture"}}
    trace={"schema_version":VERSION,"trace_id":sid("foi-process:conformance-trace",[request,"oia-nz:deadline-profile:fixture",checkpoint["state_hash"]]),"case_id":request,"profile_id":"urn:rulespec-nz:oia:deadline-profile:fixture","engine_id":"urn:axiom-rules-engine:runtime","engine_version":"fixture","created_at":"2026-07-09T00:06:00Z","assertion_status":"inferred","steps":[{"step_id":"urn:foi-process:trace-step:request-time","kind":"input","label":"Read observed request-sent timestamp","input_ids":[events[0]["event_id"]],"output_ids":[],"evidence":[{"evidence_id":d1["evidence"]["evidence_id"],"role":"prov:primarySource"}],"details":{}},{"step_id":"urn:foi-process:trace-step:deadline","kind":"calculation","label":"Apply fixture working-day profile","input_ids":[events[0]["event_id"]],"output_ids":[],"evidence":[],"details":{"indicative_due_date":"2025-02-04"}},{"step_id":"urn:foi-process:trace-step:extension","kind":"evidence_check","label":"Check observed extension evidence","input_ids":[events[3]["event_id"]],"output_ids":[],"evidence":signal["evidence"],"details":{"duration_working_days":15}}],"findings":[trace_finding]}
    bundle["human_reviews"]=[review]

    generated=ROOT/'examples/generated'; input_dir=ROOT/'examples/input'; generated.mkdir(parents=True,exist_ok=True); input_dir.mkdir(parents=True,exist_ok=True)
    for name,value in {
        'normalized-bundle.json':bundle,'human-review-record.json':review,'conformance-trace.json':trace,'validation-finding.json':trace_finding,'replay-outcomes.json':outcomes,'dashboard-summary.json':{"synthetic_fixture":True,**summary(events)},'ocel-projection.json':ocel,'public-projection.json':public,'document-bundle.json':doc,'document-signal.json':signal,'stream-checkpoint.json':checkpoint,'replay-snapshot.json':snapshot}.items():
        (generated/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n")
    (input_dir/'evidence-deltas.ndjson').write_text(''.join(json.dumps(d,separators=(',',':'))+'\n' for d in deltas))
    (input_dir/'process-events.ndjson').write_text(''.join(json.dumps(e,separators=(',',':'))+'\n' for e in events))
    (input_dir/'mapping-profile.json').write_text(json.dumps({"profile_id":"urn:foi-process:profile:fyi-minimal","profile_version":VERSION,"platform_activities":MAPPING,"event_attribute_allowlist":["authority_id","platform_state","message_direction"]},indent=2)+"\n")
    manifest={"synthetic_fixture":True,"schema_version":VERSION,"run_id":sid("foi-process:mining-run",[checkpoint["state_hash"],"0.1.0"]),"created_at":"2026-07-09T00:05:00Z","source_dataset":"urn:huggingface:dataset:edithatogo/fyi-archive-nz","source_revision":"fixture","software_commit":"uncommitted-workpack-v3","rust_version":"1.88+","rust4pm_version":"0.6.0","foi_process_version":"0.1.0","parameters":{"mapping_profile":"urn:foi-process:profile:fyi-minimal"},"privacy_profile":privacy(),"inputs":[],"outputs":[],"environment":{"generation":"python-reference-oracle"}}
    (generated/'mining-run-manifest.json').write_text(json.dumps(manifest,indent=2)+"\n")

if __name__ == '__main__': generate()
