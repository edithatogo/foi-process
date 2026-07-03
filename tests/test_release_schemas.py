#!/usr/bin/env python3
"""Tests for dataset validation and release schemas."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus-law-nz"

def _s(name: str) -> dict[str, Any]:
    return json.loads((CORPUS / "schemas" / name).read_text(encoding="utf-8-sig"))
def _v(schema: dict[str, Any]) -> Draft202012Validator:
    return Draft202012Validator(schema)

def validator(name: str) -> Draft202012Validator:
    return _v(_s(name))

def _lr() -> dict[str, Any]:
    return dict(stable_id="a", record_schema_version="1.0", work_id="w",
                version_id="v", title="T", jurisdiction="New Zealand",
                country="NZ", source="API", source_url="https://ex/",
                api_url="https://ex/api", legislation_type="act",
                legislation_status="current", scrape_date="2026-01-01T00:00:00Z",
                ingest_timestamp_utc="2026-01-01T00:00:00Z", language="en",
                text="x", text_sha256="a"*64, source_hash="b"*64,
                pipeline_version="0.5.0")

def _re() -> dict[str, Any]:
    return dict(schema_version="1.0",
                artifact_class="corpus-nz-legislation-snapshot",
                generated_at_utc="2026-06-14T00:00:00Z",
                corpus_family_label="corpus-nz-legislation",
                sibling_corpus="corpus-nz-hansard",
                publication_target="zenodo",
                coverage_statement="Not proven complete.",
                source_commit_sha="abc123def456abc123def456abc123def456abc1",
                workflow=dict(name="release-zenodo", run_id="12345678",
                             run_attempt="1", ref="refs/tags/v0.1.0",
                             event_name="release"),
                dataset=dict(huggingface_repo_id="edithatogo/corpus-legislation-nz",
                           huggingface_revision="abc123d",
                           zenodo_doi="10.5281/zenodo.20592540",
                           zenodo_concept_doi="10.5281/zenodo.20592539"),
                manifest=dict(manifest_sha256="c"*64, content_sha256="d"*64,
                            schema_version="1.0", record_schema_version="1.0",
                            record_count=1000),
                subjects=[dict(path="a.zip", sha256="e"*64, size_bytes=5000000)],
                attestation_policy=dict(github_artifact_attestation="https://att/1",
                                      signed_checksums="SHA256SUMS.txt",
                                      slsa_style_provenance="prov.json"))


class TestLegislationRecordSchema:
    def test_schema_valid(self):
        Draft202012Validator.check_schema(_s("legislation_record.schema.json"))
    def test_valid_record_passes(self):
        assert list(_v(_s("legislation_record.schema.json")).iter_errors(_lr()))==[]
    def test_missing_required_fails(self):
        r=_lr(); del r["stable_id"]
        with pytest.raises(ValidationError):
            _v(_s("legislation_record.schema.json")).validate(r)
    def test_bad_sha256_fails(self):
        r=_lr(); r["text_sha256"]="bad"
        assert any("does not match" in str(e) for e in _v(_s("legislation_record.schema.json")).iter_errors(r))
    def test_optional_absent_ok(self):
        r=_lr()
        for o in ["xml_url","html_url","pdf_url","year","administering_agencies",
                  "is_latest_version","raw_xml_sha256","raw_content_sha256",
                  "id_is_ephemeral","id_ephemeral_reason","raw_version_metadata",
                  "legislation_subtype","version_date"]:
            r.pop(o,None)
        assert list(_v(_s("legislation_record.schema.json")).iter_errors(r))==[]
    def test_extra_props_allowed(self):
        r=_lr(); r["extra"]="x"
        assert list(_v(_s("legislation_record.schema.json")).iter_errors(r))==[]
    def test_bad_country_fails(self):
        r=_lr(); r["country"]="AU"
        assert any("country" in str(e) or "was expected" in str(e)
                   for e in _v(_s("legislation_record.schema.json")).iter_errors(r))


class TestReleaseEvidenceSchema:
    def test_schema_valid(self):
        Draft202012Validator.check_schema(_s("release_evidence.schema.json"))
    def test_valid_passes(self):
        assert list(_v(_s("release_evidence.schema.json")).iter_errors(_re()))==[]
    def test_missing_required_fails(self):
        r=_re(); del r["artifact_class"]
        with pytest.raises(ValidationError):
            _v(_s("release_evidence.schema.json")).validate(r)
    def test_all_required_defined(self):
        req=set(_s("release_evidence.schema.json").get("required",[]))
        for f in ["schema_version","artifact_class","generated_at_utc",
                  "corpus_family_label","sibling_corpus","publication_target",
                  "coverage_statement","source_commit_sha","workflow",
                  "dataset","manifest","subjects","attestation_policy"]:
            assert f in req
    def test_no_extra_props(self):
        r=_re(); r["x"]="y"
        assert any("Additional properties" in str(e)
                   for e in _v(_s("release_evidence.schema.json")).iter_errors(r))
    def test_sha256_pattern(self):
        r=_re(); r["manifest"]["manifest_sha256"]="short"
        assert any("does not match" in str(e)
                   for e in _v(_s("release_evidence.schema.json")).iter_errors(r))
    def test_subjects_min_1(self):
        r=_re(); r["subjects"]=[]
        assert any("too short" in str(e) or "minItems" in str(e)
                   for e in _v(_s("release_evidence.schema.json")).iter_errors(r))
    def test_subject_requires_fields(self):
        r=_re(); r["subjects"]=[{"path":"x.txt"}]
        ee=list(_v(_s("release_evidence.schema.json")).iter_errors(r))
        assert any("sha256" in str(e) for e in ee)
        assert any("size_bytes" in str(e) for e in ee)
    def test_workflow_requires_event_name(self):
        r=_re(); del r["workflow"]["event_name"]
        assert any("event_name" in str(e)
                   for e in _v(_s("release_evidence.schema.json")).iter_errors(r))
    def test_corpus_label_constant(self):
        r=_re(); r["corpus_family_label"]="other"
        assert any("corpus_family_label" in str(e)
                   for e in _v(_s("release_evidence.schema.json")).iter_errors(r))
    def test_sibling_constant(self):
        r=_re(); r["sibling_corpus"]="other"
        assert any("sibling_corpus" in str(e)
                   for e in _v(_s("release_evidence.schema.json")).iter_errors(r))



class TestCommitteeSchemas:
    """Tests for the 3 committee record schemas."""

    def _core(self) -> dict[str, Any]:
        return dict(record_id="r1", source_id="s1",
            jurisdiction="New Zealand", country="NZ",
            display_title="T", language="en",
            record_schema_version="1.0",
            canonical_uri="https://ex.org/r", source_url="https://ex.org",
            source_version="v1", effective_date="2026-01-01",
            published_date="2026-01-01", last_modified_date=None,
            content_sha256="a"*64, manifest_sha256="b"*64,
            coverage_status="partial", rights_note="R",
            provenance={"pipeline_name":"p","pipeline_version":"1.0",
                       "source_name":"S","source_record_id":"t:001",
                       "release_version":"0.1.0","release_commit":"abc1234",
                       "license_note":"L","source_retrieved_at":"2026-01-01T00:00:00Z"})

    def test_select_committee_schema_valid(self):
        Draft202012Validator.check_schema(_s("select_committee_report_record.schema.json"))
    def test_select_committee_valid(self):
        r=self._core(); r.update(corpus_id="corpus-nz-select-committee",
            document_type="select_committee_report", report_id="rep-001",
            committee_name="Finance Committee")
        assert list(validator("select_committee_report_record.schema.json").iter_errors(r))==[]
    def test_select_committee_wrong_corpus(self):
        r=self._core(); r.update(corpus_id="corpus-nz-legislation",
            document_type="select_committee_report", report_id="rep-001",
            committee_name="Finance Committee")
        assert any("corpus_id" in str(e)
            for e in validator("select_committee_report_record.schema.json").iter_errors(r))
    def test_select_committee_wrong_doc_type(self):
        r=self._core(); r.update(corpus_id="corpus-nz-select-committee",
            document_type="act", report_id="rep-001",
            committee_name="Finance Committee")
        assert any("document_type" in str(e)
            for e in validator("select_committee_report_record.schema.json").iter_errors(r))

    def test_parliament_submission_schema_valid(self):
        Draft202012Validator.check_schema(_s("parliament_submission_record.schema.json"))
    def test_parliament_submission_valid(self):
        r=self._core(); r.update(corpus_id="corpus-nz-parliament-submissions",
            document_type="parliament_submission", submission_id="sub-001",
            submitter_name="Greenpeace NZ")
        assert list(validator("parliament_submission_record.schema.json").iter_errors(r))==[]
    def test_parliament_submission_wrong_corpus(self):
        r=self._core(); r.update(corpus_id="corpus-nz-regulations-review",
            document_type="parliament_submission", submission_id="sub-001",
            submitter_name="Greenpeace NZ")
        assert any("corpus_id" in str(e)
            for e in validator("parliament_submission_record.schema.json").iter_errors(r))

    def test_regulations_review_schema_valid(self):
        Draft202012Validator.check_schema(_s("regulations_review_proceeding_record.schema.json"))
    def test_regulations_review_valid(self):
        r=self._core(); r.update(corpus_id="corpus-nz-regulations-review",
            document_type="regulations_review_proceeding", proceeding_id="pr-001",
            committee="Regulations Review Committee")
        assert list(validator("regulations_review_proceeding_record.schema.json").iter_errors(r))==[]
    def test_regulations_review_wrong_corpus(self):
        r=self._core(); r.update(corpus_id="corpus-nz-select-committee",
            document_type="regulations_review_proceeding", proceeding_id="pr-001",
            committee="Regulations Review Committee")
        assert any("corpus_id" in str(e)
            for e in validator("regulations_review_proceeding_record.schema.json").iter_errors(r))
class TestSharedNzCorpusCoreSchema:
    def test_schema_valid(self):
        Draft202012Validator.check_schema(_s("shared_nz_corpus_core.schema.json"))
    def test_valid_record_passes(self):
        r={"corpus_id":"corpus-nz-legislation","record_id":"r1","source_id":"s1",
           "jurisdiction":"New Zealand","country":"NZ","document_type":"act",
           "display_title":"T","language":"en","record_schema_version":"1.0",
           "canonical_uri":"https://ex.org/r","source_url":"https://ex.org",
           "source_version":"v1","effective_date":"2026-01-01",
           "published_date":"2026-01-01","last_modified_date":None,
           "content_sha256":"a"*64,"manifest_sha256":"b"*64,
           "coverage_status":"partial","rights_note":"R",
           "provenance":{"pipeline_name":"p","pipeline_version":"1.0",
                        "source_name":"S","source_record_id":"t:001",
                        "release_version":"0.1.0","release_commit":"abc1234",
                        "license_note":"L","source_retrieved_at":"2026-01-01T00:00:00Z"}}
        assert list(_v(_s("shared_nz_corpus_core.schema.json")).iter_errors(r))==[]
    def test_corpus_id_valid(self):
        v=_v(_s("shared_nz_corpus_core.schema.json"))
        for cid in ["corpus-nz-legislation","corpus-nz-hansard"]:
            r={"corpus_id":cid,"record_id":"r","source_id":"s",
               "jurisdiction":"New Zealand","country":"NZ",
               "document_type":"hansard_document" if "hansard" in cid else "act",
               "display_title":"T","language":"en","record_schema_version":"1.0",
               "canonical_uri":"https://ex.org/r","source_url":"https://ex.org",
               "source_version":"v1","effective_date":"2026-01-01",
               "published_date":"2026-01-01","last_modified_date":None,
               "content_sha256":"a"*64,"manifest_sha256":"b"*64,
               "coverage_status":"partial","rights_note":"R",
               "provenance":{"pipeline_name":"p","pipeline_version":"1.0",
                            "source_name":"S","source_record_id":"t:001",
                            "release_version":"0.1.0","release_commit":"abc1234",
                            "license_note":"L","source_retrieved_at":"2026-01-01T00:00:00Z"}}
            assert list(v.iter_errors(r))==[],f"Expected valid for {cid}"
    def test_corpus_id_invalid(self):
        r={"corpus_id":"corpus-nz-cases","record_id":"r","source_id":"s",
           "jurisdiction":"New Zealand","country":"NZ","document_type":"act",
           "display_title":"T","language":"en","record_schema_version":"1.0",
           "canonical_uri":"https://ex.org/r","source_url":"https://ex.org",
           "source_version":"v1","effective_date":"2026-01-01",
           "published_date":"2026-01-01","last_modified_date":None,
           "content_sha256":"a"*64,"manifest_sha256":"b"*64,
           "coverage_status":"partial","rights_note":"R",
           "provenance":{"pipeline_name":"p","pipeline_version":"1.0",
                        "source_name":"S","source_record_id":"t:001",
                        "release_version":"0.1.0","release_commit":"abc1234",
                        "license_note":"L","source_retrieved_at":"2026-01-01T00:00:00Z"}}
        assert any("corpus_id" in str(e) for e in _v(_s("shared_nz_corpus_core.schema.json")).iter_errors(r))




class TestReleaseWorkflowContracts:
    def test_hf_contract(self):
        e=_re();e["publication_target"]="huggingface"
        e["artifact_class"]="corpus-nz-legislation-hf-sync"
        assert list(_v(_s("release_evidence.schema.json")).iter_errors(e))==[]
    def test_zenodo_contract(self):
        assert list(_v(_s("release_evidence.schema.json")).iter_errors(_re()))==[]
    def test_dataset_req_fields(self):
        r=set(_s("release_evidence.schema.json")["properties"]["dataset"].get("required",[]))
        for f in ["huggingface_repo_id","huggingface_revision","zenodo_doi",
                   "zenodo_concept_doi"]:
            assert f in r
    def test_manifest_req_sha256(self):
        r=set(_s("release_evidence.schema.json")["properties"]["manifest"].get("required",[]))
        assert "manifest_sha256" in r and "content_sha256" in r
    def test_attestation_req_fields(self):
        r=set(_s("release_evidence.schema.json")["properties"]["attestation_policy"].get("required",[]))
        for f in ["github_artifact_attestation","signed_checksums","slsa_style_provenance"]:
            assert f in r
