use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::{
    BoundingBox, Confidence, EvidenceRef, PrivacyAssessment, Sha256Digest, StableId, TermId,
    Timestamp, CONTRACT_VERSION,
};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ExtractionMethod {
    BornDigital,
    Ocr,
    Hybrid,
    Manual,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ModelDescriptor {
    pub name: String,
    pub version: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub runtime: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub model_sha256: Option<Sha256Digest>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub license: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct TextSegment {
    pub segment_id: StableId,
    pub reading_order: u32,
    pub text_sha256: Sha256Digest,
    pub character_count: u64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub text_blob_id: Option<StableId>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub inline_text: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bbox: Option<BoundingBox>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub confidence: Option<Confidence>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub language: Option<String>,
    #[serde(default)]
    pub privacy: PrivacyAssessment,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PageEvidence {
    pub page_number: u32,
    pub page_sha256: Sha256Digest,
    pub width: f64,
    pub height: f64,
    pub extraction_method: ExtractionMethod,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub model: Option<ModelDescriptor>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub quality_score: Option<Confidence>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub warnings: Vec<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub segments: Vec<TextSegment>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct DocumentBundle {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub document_id: StableId,
    pub source_evidence_id: StableId,
    pub source_sha256: Sha256Digest,
    pub media_type: String,
    pub created_at: Timestamp,
    pub extractor: ModelDescriptor,
    pub pages: Vec<PageEvidence>,
    #[serde(default)]
    pub privacy: PrivacyAssessment,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub attributes: BTreeMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct DocumentSignal {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub signal_id: StableId,
    pub signal_type: TermId,
    pub assertion_status: super::AssertionStatus,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub confidence: Option<Confidence>,
    pub document_id: StableId,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub evidence: Vec<EvidenceRef>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub proposed_activity: Option<TermId>,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub extracted_values: BTreeMap<String, serde_json::Value>,
    pub producer: ModelDescriptor,
    #[serde(default)]
    pub privacy: PrivacyAssessment,
}

fn default_contract_version() -> String {
    CONTRACT_VERSION.to_string()
}
