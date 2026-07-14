use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::{PrivacyAssessment, Sha256Digest, StableId, Timestamp, CONTRACT_VERSION};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ArtifactDescriptor {
    pub artifact_id: StableId,
    pub path_or_uri: String,
    pub media_type: String,
    pub sha256: Sha256Digest,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub byte_length: Option<u64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub row_count: Option<u64>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct MiningRunManifest {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub run_id: StableId,
    pub created_at: Timestamp,
    pub source_dataset: StableId,
    pub source_revision: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_manifest_sha256: Option<Sha256Digest>,
    pub software_commit: String,
    pub rust_version: String,
    pub rust4pm_version: String,
    pub foi_process_version: String,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub parameters: BTreeMap<String, serde_json::Value>,
    pub privacy_profile: PrivacyAssessment,
    pub inputs: Vec<ArtifactDescriptor>,
    pub outputs: Vec<ArtifactDescriptor>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub sbom_artifact_id: Option<StableId>,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub environment: BTreeMap<String, String>,
}

fn default_contract_version() -> String {
    CONTRACT_VERSION.to_string()
}
