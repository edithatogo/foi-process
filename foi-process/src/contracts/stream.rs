use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::{Sha256Digest, StableId, Timestamp, CONTRACT_VERSION};

#[derive(
    Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize, JsonSchema,
)]
#[serde(deny_unknown_fields)]
pub struct StreamPosition {
    pub source: StableId,
    pub partition: String,
    pub sequence: u64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum LateEventDisposition {
    OnTime,
    AcceptedLate,
    Quarantined,
    Rejected,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PartitionCheckpoint {
    pub source: StableId,
    pub partition: String,
    pub last_sequence: u64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub watermark: Option<Timestamp>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct StreamCheckpoint {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub checkpoint_id: StableId,
    pub consumer: StableId,
    pub created_at: Timestamp,
    pub partitions: Vec<PartitionCheckpoint>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub state_hash: Option<Sha256Digest>,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub attributes: BTreeMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct RecordRevisionSnapshot {
    pub logical_record_id: StableId,
    pub revision: u64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub current_digest: Option<Sha256Digest>,
    pub last_delta_id: StableId,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub last_event_id: Option<StableId>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ReplaySnapshot {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub snapshot_id: StableId,
    pub consumer: StableId,
    pub created_at: Timestamp,
    pub records: Vec<RecordRevisionSnapshot>,
    pub partitions: Vec<PartitionCheckpoint>,
    pub state_hash: Sha256Digest,
}

fn default_contract_version() -> String {
    CONTRACT_VERSION.to_string()
}
