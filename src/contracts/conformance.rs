use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::{AssertionStatus, EvidenceRef, StableId, TermId, Timestamp, CONTRACT_VERSION};

#[derive(
    Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, JsonSchema,
)]
#[serde(rename_all = "snake_case")]
pub enum Severity {
    Info,
    Warning,
    ReviewNeeded,
    Error,
    Critical,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum FindingLayer {
    Structural,
    Semantic,
    Process,
    Statutory,
    Privacy,
    DataQuality,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ValidationFinding {
    pub rule_id: TermId,
    pub layer: FindingLayer,
    pub severity: Severity,
    pub message: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub subject_id: Option<StableId>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub evidence: Vec<EvidenceRef>,
    #[serde(default)]
    pub requires_human_review: bool,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub details: BTreeMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum TraceStepKind {
    Input,
    EvidenceCheck,
    Calculation,
    Decision,
    ProcessConstraint,
    Notice,
    ExternalReference,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ConformanceTraceStep {
    pub step_id: StableId,
    pub kind: TraceStepKind,
    pub label: String,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub input_ids: Vec<StableId>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub output_ids: Vec<StableId>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub evidence: Vec<EvidenceRef>,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub details: BTreeMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ConformanceTrace {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub trace_id: StableId,
    pub case_id: StableId,
    pub profile_id: StableId,
    pub engine_id: StableId,
    pub engine_version: String,
    pub created_at: Timestamp,
    pub assertion_status: AssertionStatus,
    pub steps: Vec<ConformanceTraceStep>,
    pub findings: Vec<ValidationFinding>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ReviewDecision {
    Confirm,
    Correct,
    Reject,
    Defer,
    Escalate,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct HumanReviewRecord {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    pub review_id: StableId,
    pub subject_id: StableId,
    pub reviewer_id: StableId,
    pub profile_id: StableId,
    pub reviewed_at: Timestamp,
    pub decision: ReviewDecision,
    pub previous_status: AssertionStatus,
    pub resulting_status: AssertionStatus,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub evidence: Vec<EvidenceRef>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub rationale: Option<String>,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub corrected_values: BTreeMap<String, serde_json::Value>,
}

fn default_contract_version() -> String {
    CONTRACT_VERSION.to_string()
}
