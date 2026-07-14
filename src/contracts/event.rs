use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::{
    Confidence, EventObjectLink, EvidenceRef, PrivacyAssessment, StableId, StreamPosition,
    TemporalInstant, TermId, Timestamp, CONTRACT_VERSION,
};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum AssertionStatus {
    Observed,
    Candidate,
    Inferred,
    Asserted,
    HumanCertified,
    Unknown,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum EventOperation {
    Upsert,
    Retract,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct Provenance {
    pub producer: StableId,
    pub producer_version: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub software_commit: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub run_id: Option<StableId>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub input_ids: Vec<StableId>,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub parameters: BTreeMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ProcessEvent {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub event_id: StableId,
    pub logical_event_id: StableId,
    pub revision: u64,
    pub operation: EventOperation,
    pub site: StableId,
    pub jurisdiction: TermId,
    pub case_id: StableId,
    pub activity: TermId,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub event_time: Option<TemporalInstant>,
    pub observed_at: Timestamp,
    pub captured_at: Timestamp,
    pub processed_at: Timestamp,
    pub position: StreamPosition,
    pub assertion_status: AssertionStatus,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub confidence: Option<Confidence>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub objects: Vec<EventObjectLink>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub evidence: Vec<EvidenceRef>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub document_signal_ids: Vec<StableId>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub rule_result_ids: Vec<StableId>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub supersedes_event_id: Option<StableId>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub retracts_event_id: Option<StableId>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub correlation_id: Option<StableId>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub causation_id: Option<StableId>,
    pub provenance: Provenance,
    #[serde(default)]
    pub privacy: PrivacyAssessment,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub attributes: BTreeMap<String, serde_json::Value>,
}

impl ProcessEvent {
    pub fn mining_time(&self) -> &Timestamp {
        self.event_time
            .as_ref()
            .map(|t| &t.timestamp)
            .unwrap_or(&self.observed_at)
    }

    pub fn order_key(&self) -> EventOrderKey {
        EventOrderKey {
            time: self.mining_time().clone(),
            source_sequence: self.position.sequence,
            event_id: self.event_id.clone(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct EventOrderKey {
    pub time: Timestamp,
    pub source_sequence: u64,
    pub event_id: StableId,
}

fn default_contract_version() -> String {
    CONTRACT_VERSION.to_string()
}
