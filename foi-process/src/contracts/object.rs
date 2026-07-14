use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::{EvidenceRef, PrivacyAssessment, StableId, TemporalInstant, TermId, CONTRACT_VERSION};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ObjectRecord {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub object_id: StableId,
    pub object_type: TermId,
    #[serde(default)]
    pub privacy: PrivacyAssessment,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub attributes: BTreeMap<String, serde_json::Value>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub evidence: Vec<EvidenceRef>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct EventObjectLink {
    pub object_id: StableId,
    pub object_type: TermId,
    pub qualifier: TermId,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ObjectObjectLink {
    pub source_object_id: StableId,
    pub target_object_id: StableId,
    pub qualifier: TermId,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub valid_from: Option<TemporalInstant>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub valid_to: Option<TemporalInstant>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub evidence: Vec<EvidenceRef>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ObjectChange {
    pub object_id: StableId,
    pub attribute: TermId,
    pub value: serde_json::Value,
    pub effective_at: TemporalInstant,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub evidence: Vec<EvidenceRef>,
}

fn default_contract_version() -> String {
    CONTRACT_VERSION.to_string()
}
