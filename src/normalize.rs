//! Deterministic conversion of archive/live evidence deltas into process events.
//!
//! Archived snapshots are first represented as `EvidenceDelta` records, so archive and live
//! ingestion use exactly the same normaliser and replay semantics.

use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use crate::contracts::*;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct MappingProfile {
    pub profile_id: StableId,
    pub profile_version: String,
    /// Maps platform-native activity/status labels to FOI-O terms.
    pub platform_activities: BTreeMap<String, TermId>,
    /// Attribute keys copied to process events. Everything else remains evidence-side.
    #[serde(default)]
    pub event_attribute_allowlist: Vec<String>,
}

impl MappingProfile {
    pub fn fyi_minimal() -> Self {
        let mappings = [
            ("platform_state_observed", "foip:PlatformStateObserved"),
            ("request_created", "foio:RequestCreated"),
            ("request_sent", "foio:RequestSent"),
            ("authority_response", "foio:AuthorityResponseReceived"),
            ("extension", "foio:ExtensionNotified"),
            ("transfer", "foio:TransferNotified"),
            ("clarification_requested", "foio:ClarificationRequested"),
            ("clarification_provided", "foio:ClarificationProvided"),
            ("information_released", "foio:InformationReleased"),
            ("partial_release", "foio:PartialReleaseObserved"),
            ("refusal", "foio:RefusalNotified"),
            ("follow_up", "foio:FollowUpSent"),
            ("closed", "foio:ClosedObserved"),
        ]
        .into_iter()
        .map(|(key, value)| {
            (
                key.to_string(),
                TermId::parse(value).expect("static term is valid"),
            )
        })
        .collect();

        Self {
            profile_id: StableId::parse("urn:foi-process:profile:fyi-minimal").unwrap(),
            profile_version: "1.0.0-draft.1".to_string(),
            platform_activities: mappings,
            event_attribute_allowlist: vec![
                "authority_id".to_string(),
                "authority_name".to_string(),
                "request_title".to_string(),
                "request_url".to_string(),
                "platform_state".to_string(),
                "message_direction".to_string(),
            ],
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ArchiveManifestRecord {
    pub record_id: StableId,
    pub logical_record_id: StableId,
    pub revision: u64,
    pub site: StableId,
    pub jurisdiction: TermId,
    pub request_id: StableId,
    pub url: String,
    pub content_sha256: Sha256Digest,
    pub captured_at: Timestamp,
    pub position: StreamPosition,
    pub media_type: String,
    pub source_kind: TermId,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_time: Option<TemporalInstant>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub warc_record_id: Option<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub warc_record_ids: Vec<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub byte_length: Option<u64>,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub attributes: BTreeMap<String, serde_json::Value>,
}

pub fn archive_record_to_delta(
    record: ArchiveManifestRecord,
) -> Result<EvidenceDelta, serde_json::Error> {
    let evidence = EvidenceRecord {
        schema_version: CONTRACT_VERSION.to_string(),
        evidence_id: content_id(
            "foi-process:evidence",
            &(
                record.logical_record_id.clone(),
                record.revision,
                record.content_sha256.clone(),
            ),
        )?,
        logical_record_id: record.logical_record_id.clone(),
        revision: record.revision,
        source_kind: record.source_kind,
        media_type: record.media_type,
        locator: EvidenceLocator {
            uri: Some(record.url),
            warc_record_id: record.warc_record_id,
            warc_record_ids: record.warc_record_ids,
            wacz_path: None,
            blob_path: None,
        },
        content_sha256: record.content_sha256.clone(),
        byte_length: record.byte_length,
        captured_at: record.captured_at.clone(),
        source_time: record.source_time,
        privacy: PrivacyAssessment::default(),
        attributes: BTreeMap::new(),
    };

    let delta_id = content_id(
        "foi-process:delta",
        &(
            record.logical_record_id.clone(),
            record.revision,
            &record.content_sha256,
            &record.position,
        ),
    )?;

    Ok(EvidenceDelta {
        schema_version: CONTRACT_VERSION.to_string(),
        delta_id,
        logical_record_id: record.logical_record_id,
        revision: record.revision,
        operation: DeltaOperation::Upsert,
        site: record.site,
        jurisdiction: record.jurisdiction,
        position: record.position,
        observed_at: record.captured_at.clone(),
        captured_at: record.captured_at,
        previous_content_sha256: None,
        current_content_sha256: Some(record.content_sha256),
        evidence: Some(evidence),
        request_hint: Some(record.request_id),
        supersedes_delta_id: None,
        correlation_id: None,
        causation_id: None,
        attributes: record.attributes,
    })
}

#[derive(Debug, Clone)]
pub struct DeterministicNormalizer {
    profile: MappingProfile,
    producer: StableId,
    producer_version: String,
}

impl DeterministicNormalizer {
    pub fn new(profile: MappingProfile, producer_version: impl Into<String>) -> Self {
        Self {
            profile,
            producer: StableId::parse("urn:foi-process:normalizer:deterministic").unwrap(),
            producer_version: producer_version.into(),
        }
    }

    pub fn profile(&self) -> &MappingProfile {
        &self.profile
    }

    pub fn normalize(&self, delta: &EvidenceDelta, processed_at: Timestamp) -> NormalizedBundle {
        let mut bundle = NormalizedBundle::default();
        if let Some(evidence) = &delta.evidence {
            bundle.evidence.push(evidence.clone());
        }

        let Some(case_id) = delta.request_hint.clone() else {
            bundle.findings.push(ValidationFinding {
                rule_id: TermId::parse("foip:MissingCaseHint").unwrap(),
                layer: FindingLayer::Structural,
                severity: Severity::ReviewNeeded,
                message: "Evidence delta cannot be mapped to a process case without request_hint"
                    .to_string(),
                subject_id: Some(delta.delta_id.clone()),
                evidence: Vec::new(),
                requires_human_review: true,
                details: BTreeMap::new(),
            });
            return bundle;
        };

        let native_activity = delta
            .attributes
            .get("platform_activity")
            .and_then(serde_json::Value::as_str)
            .unwrap_or("unmapped");
        let mapped_activity = self
            .profile
            .platform_activities
            .get(native_activity)
            .cloned();
        let was_mapped = mapped_activity.is_some();
        let (activity, mut assertion_status, confidence) = match mapped_activity {
            Some(activity) => (activity, AssertionStatus::Observed, None),
            None => (
                TermId::parse("foip:UnmappedPlatformEvent").unwrap(),
                AssertionStatus::Candidate,
                Confidence::new(0.0).ok(),
            ),
        };
        if delta.operation == DeltaOperation::Delete && delta.evidence.is_none() {
            assertion_status = AssertionStatus::Asserted;
        }

        let logical_event_id = content_id(
            "foi-process:event-logical",
            &(
                delta.site.clone(),
                case_id.clone(),
                delta.logical_record_id.clone(),
            ),
        )
        .expect("serialising the deterministic event identity cannot fail");
        let event_id = content_id(
            "foi-process:event",
            &(logical_event_id.clone(), delta.revision, delta.operation),
        )
        .expect("serialising the deterministic event revision cannot fail");

        let operation = match delta.operation {
            DeltaOperation::Delete => EventOperation::Retract,
            DeltaOperation::Upsert | DeltaOperation::Recapture | DeltaOperation::Repair => {
                EventOperation::Upsert
            }
        };

        let evidence = delta
            .evidence
            .as_ref()
            .map(|record| EvidenceRef {
                evidence_id: record.evidence_id.clone(),
                selector: None,
                role: Some(TermId::parse("prov:primarySource").unwrap()),
            })
            .into_iter()
            .collect();

        let request_type = TermId::parse("foio:Request").unwrap();
        let request_object = EventObjectLink {
            object_id: case_id.clone(),
            object_type: request_type.clone(),
            qualifier: TermId::parse("foip:case").unwrap(),
        };
        let mut event_objects = vec![request_object];
        bundle.objects.push(ObjectRecord {
            schema_version: CONTRACT_VERSION.to_string(),
            object_id: case_id.clone(),
            object_type: request_type,
            privacy: delta
                .evidence
                .as_ref()
                .map(|record| record.privacy.clone())
                .unwrap_or_default(),
            attributes: BTreeMap::new(),
            evidence: delta
                .evidence
                .as_ref()
                .map(|record| {
                    vec![EvidenceRef {
                        evidence_id: record.evidence_id.clone(),
                        selector: None,
                        role: Some(TermId::parse("prov:primarySource").unwrap()),
                    }]
                })
                .unwrap_or_default(),
        });

        if let Some(authority_id) = delta
            .attributes
            .get("authority_id")
            .and_then(serde_json::Value::as_str)
            .and_then(|value| StableId::parse(value).ok())
        {
            let authority_type = TermId::parse("foio:Authority").unwrap();
            let authority_name = delta
                .attributes
                .get("authority_name")
                .and_then(serde_json::Value::as_str)
                .unwrap_or_default();
            let mut authority_attributes = BTreeMap::new();
            if !authority_name.is_empty() {
                authority_attributes.insert(
                    "name".to_string(),
                    serde_json::Value::String(authority_name.to_string()),
                );
            }
            bundle.objects.push(ObjectRecord {
                schema_version: CONTRACT_VERSION.to_string(),
                object_id: authority_id.clone(),
                object_type: authority_type.clone(),
                privacy: PrivacyAssessment::default(),
                attributes: authority_attributes,
                evidence: Vec::new(),
            });
            bundle.object_links.push(ObjectObjectLink {
                source_object_id: case_id.clone(),
                target_object_id: authority_id.clone(),
                qualifier: TermId::parse("foip:addressedTo").unwrap(),
                valid_from: None,
                valid_to: None,
                evidence: Vec::new(),
            });
            event_objects.push(EventObjectLink {
                object_id: authority_id,
                object_type: authority_type,
                qualifier: TermId::parse("foip:authority").unwrap(),
            });
        }

        let mut attributes = BTreeMap::new();
        for key in &self.profile.event_attribute_allowlist {
            if let Some(value) = delta.attributes.get(key) {
                attributes.insert(key.clone(), value.clone());
            }
        }
        attributes.insert(
            "native_activity".to_string(),
            serde_json::Value::String(native_activity.to_string()),
        );

        let event_time = delta
            .attributes
            .get("event_time")
            .and_then(serde_json::Value::as_str)
            .and_then(|value| Timestamp::parse(value).ok())
            .map(TemporalInstant::exact);

        bundle.events.push(ProcessEvent {
            schema_version: CONTRACT_VERSION.to_string(),
            event_id,
            logical_event_id,
            revision: delta.revision,
            operation,
            site: delta.site.clone(),
            jurisdiction: delta.jurisdiction.clone(),
            case_id,
            activity,
            event_time,
            observed_at: delta.observed_at.clone(),
            captured_at: delta.captured_at.clone(),
            processed_at,
            position: delta.position.clone(),
            assertion_status,
            confidence,
            objects: event_objects,
            evidence,
            document_signal_ids: Vec::new(),
            rule_result_ids: Vec::new(),
            supersedes_event_id: None,
            retracts_event_id: None,
            correlation_id: delta.correlation_id.clone(),
            causation_id: delta.causation_id.clone(),
            provenance: Provenance {
                producer: self.producer.clone(),
                producer_version: self.producer_version.clone(),
                software_commit: None,
                run_id: None,
                input_ids: vec![delta.delta_id.clone()],
                parameters: BTreeMap::from([(
                    "mapping_profile".to_string(),
                    serde_json::Value::String(self.profile.profile_id.to_string()),
                )]),
            },
            privacy: delta
                .evidence
                .as_ref()
                .map(|record| record.privacy.clone())
                .unwrap_or_default(),
            attributes,
        });

        if delta.operation == DeltaOperation::Delete && delta.evidence.is_none() {
            bundle.findings.push(ValidationFinding {
                rule_id: TermId::parse("foip:RetractionWithoutTombstoneEvidence").unwrap(),
                layer: FindingLayer::DataQuality,
                severity: Severity::ReviewNeeded,
                message: "Deletion was reported without a captured tombstone/source response"
                    .to_string(),
                subject_id: bundle.events.first().map(|event| event.event_id.clone()),
                evidence: Vec::new(),
                requires_human_review: true,
                details: BTreeMap::new(),
            });
        }

        if !was_mapped {
            bundle.findings.push(ValidationFinding {
                rule_id: TermId::parse("foip:UnmappedNativeActivity").unwrap(),
                layer: FindingLayer::Semantic,
                severity: Severity::ReviewNeeded,
                message: format!("No mapping exists for platform activity '{native_activity}'"),
                subject_id: bundle.events.first().map(|event| event.event_id.clone()),
                evidence: bundle
                    .events
                    .first()
                    .map(|event| event.evidence.clone())
                    .unwrap_or_default(),
                requires_human_review: true,
                details: BTreeMap::new(),
            });
        }

        bundle
    }
}
