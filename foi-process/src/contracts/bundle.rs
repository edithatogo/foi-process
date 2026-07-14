use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::{
    DocumentSignal, EvidenceRecord, HumanReviewRecord, ObjectChange, ObjectObjectLink,
    ObjectRecord, ProcessEvent, StreamCheckpoint, ValidationFinding, CONTRACT_VERSION,
};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct NormalizedBundle {
    #[serde(default = "default_contract_version")]
    pub schema_version: String,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub evidence: Vec<EvidenceRecord>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub objects: Vec<ObjectRecord>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub object_links: Vec<ObjectObjectLink>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub object_changes: Vec<ObjectChange>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub document_signals: Vec<DocumentSignal>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub events: Vec<ProcessEvent>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub findings: Vec<ValidationFinding>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub human_reviews: Vec<HumanReviewRecord>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub checkpoint: Option<StreamCheckpoint>,
}

impl Default for NormalizedBundle {
    fn default() -> Self {
        Self {
            schema_version: CONTRACT_VERSION.to_string(),
            evidence: Vec::new(),
            objects: Vec::new(),
            object_links: Vec::new(),
            object_changes: Vec::new(),
            document_signals: Vec::new(),
            events: Vec::new(),
            findings: Vec::new(),
            human_reviews: Vec::new(),
            checkpoint: None,
        }
    }
}

impl NormalizedBundle {
    pub fn extend(&mut self, other: Self) {
        for record in other.evidence {
            if !self
                .evidence
                .iter()
                .any(|existing| existing.evidence_id == record.evidence_id)
            {
                self.evidence.push(record);
            }
        }
        for object in other.objects {
            if let Some(existing) = self
                .objects
                .iter_mut()
                .find(|existing| existing.object_id == object.object_id)
            {
                if object.attributes.len() > existing.attributes.len() {
                    *existing = object;
                }
            } else {
                self.objects.push(object);
            }
        }
        self.object_links.extend(other.object_links);
        self.object_changes.extend(other.object_changes);
        self.document_signals.extend(other.document_signals);
        self.events.extend(other.events);
        self.findings.extend(other.findings);
        self.human_reviews.extend(other.human_reviews);
        if other.checkpoint.is_some() {
            self.checkpoint = other.checkpoint;
        }
    }
}

fn default_contract_version() -> String {
    CONTRACT_VERSION.to_string()
}
