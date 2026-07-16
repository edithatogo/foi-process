use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::{
    PrivacyAssessment, Sha256Digest, StableId, StreamPosition, TemporalInstant, TermId, Timestamp,
    CONTRACT_VERSION,
};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct TextSpan {
    pub start: u64,
    pub end: u64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct BoundingBox {
    pub page: u32,
    pub x: f64,
    pub y: f64,
    pub width: f64,
    pub height: f64,
    #[serde(default = "default_coordinate_system")]
    pub coordinate_system: String,
}

fn default_coordinate_system() -> String {
    "pdf_points_top_left".to_string()
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(tag = "selector_type", rename_all = "snake_case", deny_unknown_fields)]
pub enum EvidenceSelector {
    Bytes { start: u64, end: u64 },
    Text { span: TextSpan },
    Page { page: u32 },
    BoundingBox { bbox: BoundingBox },
    JsonPointer { pointer: String },
    WarcPayload,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct EvidenceLocator {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub uri: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub warc_record_id: Option<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub warc_record_ids: Vec<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub wacz_path: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub blob_path: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct EvidenceRecord {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub evidence_id: StableId,
    pub logical_record_id: StableId,
    pub revision: u64,
    pub source_kind: TermId,
    pub media_type: String,
    pub locator: EvidenceLocator,
    pub content_sha256: Sha256Digest,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub byte_length: Option<u64>,
    pub captured_at: Timestamp,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_time: Option<TemporalInstant>,
    #[serde(default)]
    pub privacy: PrivacyAssessment,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub attributes: BTreeMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct EvidenceRef {
    pub evidence_id: StableId,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub selector: Option<EvidenceSelector>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub role: Option<TermId>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum DeltaOperation {
    Upsert,
    Delete,
    Recapture,
    Repair,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct EvidenceDelta {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub delta_id: StableId,
    pub logical_record_id: StableId,
    pub revision: u64,
    pub operation: DeltaOperation,
    pub site: StableId,
    pub jurisdiction: TermId,
    pub position: StreamPosition,
    pub observed_at: Timestamp,
    pub captured_at: Timestamp,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub previous_content_sha256: Option<Sha256Digest>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub current_content_sha256: Option<Sha256Digest>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub evidence: Option<EvidenceRecord>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub request_hint: Option<StableId>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub supersedes_delta_id: Option<StableId>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub correlation_id: Option<StableId>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub causation_id: Option<StableId>,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub attributes: BTreeMap<String, serde_json::Value>,
}

fn default_contract_version() -> String {
    CONTRACT_VERSION.to_string()
}
