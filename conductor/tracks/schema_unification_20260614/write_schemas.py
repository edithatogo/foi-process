"""Canonical schema writer for nlp-policy-nz."""
import json
from pathlib import Path

BASE = Path(r"C:\Users\60217257\OneDrive - Flinders\repos\legal-nz\nlp-policy-nz\schemas")

def write_schema(path, schema_dict):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(schema_dict, indent=2) + "\n", encoding="utf-8")
    print(f"  Wrote: {p}")


# --------------- shared provenance (used by all committee schemas) ---------------
PROVENANCE = {
    "type": "object",
    "required": ["pipeline_name", "pipeline_version", "source_name", "source_record_id",
                 "source_retrieved_at", "release_version", "release_commit", "license_note"],
    "properties": {
        "pipeline_name": {"type": "string", "minLength": 1},
        "pipeline_version": {"type": "string", "minLength": 1},
        "source_name": {"type": "string", "minLength": 1},
        "source_record_id": {"type": "string", "minLength": 1},
        "source_retrieved_at": {"type": ["string", "null"], "format": "date-time"},
        "release_version": {"type": "string", "minLength": 1},
        "release_commit": {"type": "string", "pattern": "^[0-9a-f]{7,40}$"},
        "license_note": {"type": "string", "minLength": 1}
    },
    "additionalProperties": True
}

# --------------- shared core fields (inlined for each committee schema) ---------------
CORE_REQUIRED = [
    "corpus_id", "record_id", "source_id", "jurisdiction", "country",
    "document_type", "display_title", "language", "record_schema_version",
    "canonical_uri", "source_url", "source_version",
    "effective_date", "published_date", "last_modified_date",
    "content_sha256", "manifest_sha256", "coverage_status", "rights_note", "provenance"
]

CORE_PROPS = {
    "corpus_id": {"type": "string", "minLength": 1},
    "record_id": {"type": "string", "minLength": 1},
    "source_id": {"type": "string", "minLength": 1},
    "jurisdiction": {"type": "string", "const": "New Zealand"},
    "country": {"type": "string", "const": "NZ"},
    "document_type": {"type": "string"},
    "display_title": {"type": "string", "minLength": 1},
    "language": {"type": "string", "minLength": 1},
    "record_schema_version": {"type": "string", "pattern": "^v?[0-9]+(\\.[0-9]+){0,2}$"},
    "canonical_uri": {"type": "string", "format": "uri"},
    "source_url": {"type": ["string", "null"], "format": "uri"},
    "source_version": {"type": ["string", "null"]},
    "effective_date": {"type": ["string", "null"], "format": "date"},
    "published_date": {"type": ["string", "null"], "format": "date"},
    "last_modified_date": {"type": ["string", "null"], "format": "date"},
    "content_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "manifest_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "coverage_status": {
        "type": "string",
        "enum": ["complete", "partial", "pilot", "sample", "search_derived", "unknown"]
    },
    "rights_note": {"type": "string", "minLength": 1},
    "provenance": PROVENANCE
}

def make_canonical(specific_required, specific_props, corpus_id_const, doc_type_const, title, desc, schema_id):
    """Build a canonical committee schema merging core + specific fields."""
    req = specific_required + CORE_REQUIRED
    props = dict(CORE_PROPS)
    props.update(specific_props)
    props["corpus_id"]["const"] = corpus_id_const
    props["document_type"]["const"] = doc_type_const
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://github.com/edithatogo/nlp-policy-nz/schemas/{schema_id}",
        "title": title,
        "description": desc,
        "type": "object",
        "required": req,
        "properties": props,
        "additionalProperties": True
    }

# ============================================================

select_committee = make_canonical(
    specific_required=["report_id", "committee_name"],
    specific_props={
        "report_id": {"type": "string", "minLength": 1},
        "report_title": {"type": "string"},
        "committee_name": {"type": "string", "minLength": 1},
        "report_date": {"type": "string", "format": "date"},
        "document_url": {"type": "string", "format": "uri"},
        "document_formats": {"type": "array", "items": {"type": "string"}},
        "bill_reference": {"type": "string"},
        "status": {"type": "string"},
        "text_content": {"type": "string"},
        "text_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "parsed_metadata": {
            "type": "object",
            "properties": {
                "committee_name": {"type": "string"},
                "report_title": {"type": "string"},
                "report_date": {"type": "string"},
                "recommendations": {"type": "array", "items": {"type": "string"}},
                "findings": {"type": "array", "items": {"type": "string"}},
                "referenced_legislation": {"type": "array", "items": {"type": "string"}},
                "referenced_bills": {"type": "array", "items": {"type": "string"}},
                "witnesses_submitters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "affiliation": {"type": "string"}
                        }
                    }
                }
            }
        },
        "correlation_index": {
            "type": "object",
            "properties": {
                "hansard_links": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "hansard_id": {"type": "string"},
                            "sitting_date": {"type": "string"},
                            "debate_title": {"type": "string"},
                            "relevance": {"type": "number"}
                        }
                    }
                },
                "legislation_links": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "legislation_id": {"type": "string"},
                            "legislation_type": {"type": "string"},
                            "legislation_url": {"type": "string"}
                        }
                    }
                }
            }
        },
        "ingest_timestamp_utc": {"type": "string", "format": "date-time"},
        "pipeline_version": {"type": "string"}
    },
    corpus_id_const="corpus-nz-select-committee",
    doc_type_const="select_committee_report",
    title="Select Committee Report Record (Canonical)",
    desc="Canonical schema for a normalized select committee report record with parsed metadata and cross-corpus links. Extends shared_nz_corpus_core via additive composition.",
    schema_id="select_committee_report_record.schema.json"
)

parliament_submission = make_canonical(
    specific_required=["submission_id", "submitter_name"],
    specific_props={
        "submission_id": {"type": "string", "minLength": 1},
        "submitter_name": {"type": "string", "minLength": 1},
        "submitter_normalized": {"type": "string"},
        "date": {"type": "string"},
        "date_normalized": {"type": "string", "format": "date"},
        "committee": {"type": "string"},
        "committee_normalized": {"type": "string"},
        "bill_reference": {"type": "string"},
        "bill_reference_normalized": {"type": "string"},
        "text_content": {"type": "string"},
        "text_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "document_sha256": {"type": "string"},
        "parliament_number": {"type": "integer"},
        "submission_year": {"type": "integer"},
        "bill_id": {"type": "string"},
        "linkage_confidence": {"type": "number"},
        "linkage_method": {"type": "string"},
        "ingest_timestamp_utc": {"type": "string", "format": "date-time"},
        "pipeline_version": {"type": "string"}
    },
    corpus_id_const="corpus-nz-parliament-submissions",
    doc_type_const="parliament_submission",
    title="Parliament Submission Record (Canonical)",
    desc="Canonical schema for a normalized parliamentary submission record with bill linkage metadata. Extends shared_nz_corpus_core via additive composition.",
    schema_id="parliament_submission_record.schema.json"
)

# SCHEMA DEFINITIONS
# ============================================================



regulations_review = make_canonical(
    specific_required=["proceeding_id", "committee"],
    specific_props={
        "proceeding_id": {"type": "string", "minLength": 1},
        "title": {"type": "string"},
        "committee": {"type": "string", "minLength": 1},
        "meeting_date": {"type": "string", "format": "date"},
        "document_url": {"type": "string", "format": "uri"},
        "agenda_items": {"type": "array", "items": {"type": "string"}},
        "status": {"type": "string"},
        "text_content": {"type": "string"},
        "text_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "document_sha256": {"type": "string"},
        "proceeding_metadata": {
            "type": "object",
            "properties": {
                "meeting_date": {"type": "string"},
                "agenda_items": {"type": "array", "items": {"type": "string"}},
                "committee_members": {"type": "array", "items": {"type": "string"}},
                "complaint_subjects": {"type": "array", "items": {"type": "string"}},
                "regulation_references": {"type": "array", "items": {"type": "string"}}
            }
        },
        "complaints": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "challenged_regulation": {"type": "string"},
                    "grounds": {"type": "string"},
                    "recommendation": {"type": "string"}
                }
            }
        },
        "regulation_cross_references": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "complaint_subject": {"type": "string"},
                    "legislation_key": {
                        "type": "object",
                        "properties": {
                            "prefix": {"type": "string"},
                            "year": {"type": "integer"},
                            "number": {"type": "integer"},
                            "key": {"type": "string"}
                        }
                    },
                    "api_result": {"type": "object"}
                }
            }
        },
        "ingest_timestamp_utc": {"type": "string", "format": "date-time"},
        "pipeline_version": {"type": "string"}
    },
    corpus_id_const="corpus-nz-regulations-review",
    doc_type_const="regulations_review_proceeding",
    title="Regulations Review Committee Proceeding Record (Canonical)",
    desc="Canonical schema for a normalized Regulations Review Committee proceeding record with complaint and regulation cross-reference data. Extends shared_nz_corpus_core via additive composition.",
    schema_id="regulations_review_proceeding_record.schema.json"
)

# ============================================================
# WRITE ALL
# ============================================================

schemas = {
    BASE / "select_committee_report_record.schema.json": select_committee,
    BASE / "parliament_submission_record.schema.json": parliament_submission,
    BASE / "regulations_review_proceeding_record.schema.json": regulations_review,
}

for path, schema in schemas.items():
    write_schema(path, schema)

print("Done writing 3 canonical committee schemas.")
