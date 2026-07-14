//! Privacy-aware public projection. Publicly archived material is not automatically safe to
//! amplify through OCR, search, or dashboards; only explicitly publishable metadata is emitted.

use std::collections::{BTreeMap, BTreeSet};

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use crate::{contracts::*, replay::materialize_events};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PublicationPolicy {
    pub policy_id: StableId,
    #[serde(default)]
    pub allowed_event_attribute_keys: BTreeSet<String>,
    #[serde(default)]
    pub include_public_evidence_links: bool,
}

impl PublicationPolicy {
    pub fn dashboard_default() -> Self {
        Self {
            policy_id: StableId::parse("urn:foi-process:publication:dashboard-default").unwrap(),
            allowed_event_attribute_keys: BTreeSet::from([
                "authority_id".to_string(),
                "platform_state".to_string(),
                "message_direction".to_string(),
                "native_activity".to_string(),
            ]),
            include_public_evidence_links: true,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PublicEvidenceLink {
    pub evidence_id: StableId,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub uri: Option<String>,
    pub media_type: String,
    pub content_sha256: Sha256Digest,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PublicProcessEvent {
    pub event_id: StableId,
    pub logical_event_id: StableId,
    pub site: StableId,
    pub jurisdiction: TermId,
    pub case_id: StableId,
    pub activity: TermId,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub event_time: Option<TemporalInstant>,
    pub assertion_status: AssertionStatus,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub confidence: Option<Confidence>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub evidence: Vec<PublicEvidenceLink>,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub attributes: BTreeMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PublicProjection {
    pub policy_id: StableId,
    pub events: Vec<PublicProcessEvent>,
    pub withheld_event_count: u64,
    pub metadata_only_event_count: u64,
}

pub fn project_public(bundle: &NormalizedBundle, policy: &PublicationPolicy) -> PublicProjection {
    let evidence: BTreeMap<_, _> = bundle
        .evidence
        .iter()
        .map(|record| (record.evidence_id.clone(), record))
        .collect();
    let mut output = PublicProjection {
        policy_id: policy.policy_id.clone(),
        events: Vec::new(),
        withheld_event_count: 0,
        metadata_only_event_count: 0,
    };

    for event in materialize_events(&bundle.events) {
        match event.privacy.disposition {
            PublicationDisposition::Withhold | PublicationDisposition::NeedsReview => {
                output.withheld_event_count += 1;
                continue;
            }
            PublicationDisposition::PublishMetadataOnly => {
                output.metadata_only_event_count += 1;
                output
                    .events
                    .push(public_event(event, &evidence, policy, false));
            }
            PublicationDisposition::Publish => {
                if event.privacy.sensitivity != SensitivityClass::Public
                    || event.privacy.access_tier != AccessTier::Public
                {
                    output.withheld_event_count += 1;
                    continue;
                }
                output.events.push(public_event(
                    event,
                    &evidence,
                    policy,
                    policy.include_public_evidence_links,
                ));
            }
        }
    }
    output
}

fn public_event(
    event: &ProcessEvent,
    evidence_index: &BTreeMap<StableId, &EvidenceRecord>,
    policy: &PublicationPolicy,
    include_evidence: bool,
) -> PublicProcessEvent {
    let evidence = if include_evidence {
        event
            .evidence
            .iter()
            .filter_map(|reference| evidence_index.get(&reference.evidence_id))
            .filter(|record| {
                record.privacy.disposition == PublicationDisposition::Publish
                    && record.privacy.sensitivity == SensitivityClass::Public
                    && record.privacy.access_tier == AccessTier::Public
            })
            .map(|record| PublicEvidenceLink {
                evidence_id: record.evidence_id.clone(),
                uri: record.locator.uri.clone(),
                media_type: record.media_type.clone(),
                content_sha256: record.content_sha256.clone(),
            })
            .collect()
    } else {
        Vec::new()
    };
    let attributes = event
        .attributes
        .iter()
        .filter(|(key, _)| policy.allowed_event_attribute_keys.contains(*key))
        .map(|(key, value)| (key.clone(), value.clone()))
        .collect();

    PublicProcessEvent {
        event_id: event.event_id.clone(),
        logical_event_id: event.logical_event_id.clone(),
        site: event.site.clone(),
        jurisdiction: event.jurisdiction.clone(),
        case_id: event.case_id.clone(),
        activity: event.activity.clone(),
        event_time: event.event_time.clone(),
        assertion_status: event.assertion_status,
        confidence: event.confidence,
        evidence,
        attributes,
    }
}
