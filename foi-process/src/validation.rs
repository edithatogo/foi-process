//! Structural and semantic validation. Jurisdiction-specific legal conclusions remain outside
//! this crate and must arrive as evidence-backed Axiom/RuleSpec traces.

use std::collections::{BTreeMap, BTreeSet};

use crate::contracts::*;

pub fn validate_delta(delta: &EvidenceDelta) -> Vec<ValidationFinding> {
    let mut findings = Vec::new();
    if delta.revision == 0 {
        findings.push(finding(
            "foip:RevisionMustBePositive",
            FindingLayer::Structural,
            Severity::Error,
            "EvidenceDelta revision must be greater than zero",
            Some(delta.delta_id.clone()),
        ));
    }
    match delta.operation {
        DeltaOperation::Upsert | DeltaOperation::Recapture | DeltaOperation::Repair => {
            if delta.evidence.is_none() || delta.current_content_sha256.is_none() {
                findings.push(finding(
                    "foip:UpsertRequiresEvidence",
                    FindingLayer::Structural,
                    Severity::Error,
                    "Upsert, recapture, and repair deltas require evidence and a current digest",
                    Some(delta.delta_id.clone()),
                ));
            }
        }
        DeltaOperation::Delete => {
            if delta.previous_content_sha256.is_none() {
                findings.push(finding(
                    "foip:DeleteRequiresPreviousDigest",
                    FindingLayer::DataQuality,
                    Severity::ReviewNeeded,
                    "Delete delta should identify the previous content digest",
                    Some(delta.delta_id.clone()),
                ));
            }
        }
    }
    if let (Some(record), Some(digest)) = (&delta.evidence, &delta.current_content_sha256) {
        if &record.content_sha256 != digest {
            findings.push(finding(
                "foip:DigestMismatch",
                FindingLayer::Structural,
                Severity::Error,
                "Evidence record digest differs from current_content_sha256",
                Some(delta.delta_id.clone()),
            ));
        }
        if record.logical_record_id != delta.logical_record_id || record.revision != delta.revision
        {
            findings.push(finding(
                "foip:EvidenceRevisionMismatch",
                FindingLayer::Structural,
                Severity::Error,
                "Evidence record identity/revision differs from its delta",
                Some(delta.delta_id.clone()),
            ));
        }
    }
    findings
}

pub fn validate_event(event: &ProcessEvent) -> Vec<ValidationFinding> {
    let mut findings = Vec::new();
    if event.revision == 0 {
        findings.push(finding(
            "foip:RevisionMustBePositive",
            FindingLayer::Structural,
            Severity::Error,
            "ProcessEvent revision must be greater than zero",
            Some(event.event_id.clone()),
        ));
    }
    if event.assertion_status == AssertionStatus::Observed && event.evidence.is_empty() {
        findings.push(finding(
            "foip:ObservedRequiresEvidence",
            FindingLayer::Semantic,
            Severity::Error,
            "Observed process events require at least one evidence reference",
            Some(event.event_id.clone()),
        ));
    }
    if event.assertion_status == AssertionStatus::Candidate && event.confidence.is_none() {
        findings.push(finding(
            "foip:CandidateRequiresConfidence",
            FindingLayer::Semantic,
            Severity::Error,
            "Candidate process events require confidence",
            Some(event.event_id.clone()),
        ));
    }
    if event.assertion_status == AssertionStatus::HumanCertified
        && !event.evidence.iter().any(|reference| {
            reference
                .role
                .as_ref()
                .is_some_and(|role| role.as_str() == "foip:humanReview")
        })
    {
        findings.push(finding(
            "foip:CertificationRequiresReviewEvidence",
            FindingLayer::Semantic,
            Severity::Error,
            "Human-certified events require an evidence reference qualified as human review",
            Some(event.event_id.clone()),
        ));
    }
    if event.activity.as_str() == "foio:ExtensionNotified"
        && !event
            .objects
            .iter()
            .any(|object| object.object_type.as_str() == "foio:Deadline")
    {
        findings.push(finding(
            "foip:ExtensionShouldLinkDeadline",
            FindingLayer::Semantic,
            Severity::Warning,
            "ExtensionNotified should link to a Deadline object when derivable",
            Some(event.event_id.clone()),
        ));
    }
    if event.activity.as_str() == "foio:TransferNotified" {
        let authority_count = event
            .objects
            .iter()
            .filter(|object| object.object_type.as_str() == "foio:Authority")
            .count();
        if authority_count < 2 {
            findings.push(finding(
                "foip:TransferShouldLinkAuthorities",
                FindingLayer::Semantic,
                Severity::Warning,
                "TransferNotified should link source and target authority objects when known",
                Some(event.event_id.clone()),
            ));
        }
    }
    if event.privacy.disposition == PublicationDisposition::Publish
        && event.privacy.sensitivity != SensitivityClass::Public
    {
        findings.push(finding(
            "foip:UnsafePublicationDisposition",
            FindingLayer::Privacy,
            Severity::Error,
            "Only events assessed as public may use the publish disposition",
            Some(event.event_id.clone()),
        ));
    }
    findings
}

pub fn validate_bundle(bundle: &NormalizedBundle) -> Vec<ValidationFinding> {
    let mut findings = Vec::new();

    let mut evidence_index = BTreeMap::<StableId, &EvidenceRecord>::new();
    for evidence in &bundle.evidence {
        if let Some(previous) = evidence_index.insert(evidence.evidence_id.clone(), evidence) {
            findings.push(finding(
                "foip:DuplicateEvidenceId",
                FindingLayer::Structural,
                if previous == evidence {
                    Severity::Warning
                } else {
                    Severity::Error
                },
                "Bundle contains a repeated evidence_id",
                Some(evidence.evidence_id.clone()),
            ));
        }
    }
    let evidence_ids: BTreeSet<_> = evidence_index.keys().cloned().collect();

    let mut object_index = BTreeMap::<StableId, &ObjectRecord>::new();
    for object in &bundle.objects {
        if let Some(previous) = object_index.insert(object.object_id.clone(), object) {
            findings.push(finding(
                "foip:DuplicateObjectId",
                FindingLayer::Structural,
                if previous == object {
                    Severity::Warning
                } else {
                    Severity::Error
                },
                "Bundle contains a repeated object_id",
                Some(object.object_id.clone()),
            ));
        }
    }
    let object_ids: BTreeSet<_> = object_index.keys().cloned().collect();

    let mut event_ids = BTreeMap::<StableId, &ProcessEvent>::new();
    let mut logical_revisions = BTreeMap::<(StableId, u64), StableId>::new();
    for event in &bundle.events {
        if let Some(previous) = event_ids.insert(event.event_id.clone(), event) {
            findings.push(finding(
                "foip:DuplicateEventId",
                FindingLayer::Structural,
                if previous == event {
                    Severity::Warning
                } else {
                    Severity::Error
                },
                "Bundle contains a repeated event_id",
                Some(event.event_id.clone()),
            ));
        }
        let key = (event.logical_event_id.clone(), event.revision);
        if let Some(previous_event_id) = logical_revisions.insert(key, event.event_id.clone()) {
            if previous_event_id != event.event_id {
                findings.push(finding(
                    "foip:ConflictingLogicalEventRevision",
                    FindingLayer::DataQuality,
                    Severity::Error,
                    "One logical event revision resolves to multiple event IDs",
                    Some(event.logical_event_id.clone()),
                ));
            }
        }

        findings.extend(validate_event(event));
        validate_evidence_references(
            &event.evidence,
            &evidence_ids,
            Some(event.event_id.clone()),
            &mut findings,
        );
        for object in &event.objects {
            if !object_ids.contains(&object.object_id) {
                findings.push(finding(
                    "foip:DanglingObjectReference",
                    FindingLayer::Structural,
                    Severity::Warning,
                    "Process event references an object absent from the bundle",
                    Some(event.event_id.clone()),
                ));
            }
        }
    }

    for link in &bundle.object_links {
        for object_id in [&link.source_object_id, &link.target_object_id] {
            if !object_ids.contains(object_id) {
                findings.push(finding(
                    "foip:DanglingObjectLink",
                    FindingLayer::Structural,
                    Severity::Error,
                    "Object-object link references an object absent from the bundle",
                    Some((*object_id).clone()),
                ));
            }
        }
        validate_evidence_references(
            &link.evidence,
            &evidence_ids,
            Some(link.source_object_id.clone()),
            &mut findings,
        );
    }
    for change in &bundle.object_changes {
        if !object_ids.contains(&change.object_id) {
            findings.push(finding(
                "foip:DanglingObjectChange",
                FindingLayer::Structural,
                Severity::Error,
                "Object change references an object absent from the bundle",
                Some(change.object_id.clone()),
            ));
        }
        validate_evidence_references(
            &change.evidence,
            &evidence_ids,
            Some(change.object_id.clone()),
            &mut findings,
        );
    }
    for signal in &bundle.document_signals {
        validate_evidence_references(
            &signal.evidence,
            &evidence_ids,
            Some(signal.signal_id.clone()),
            &mut findings,
        );
    }
    for bundle_finding in &bundle.findings {
        validate_evidence_references(
            &bundle_finding.evidence,
            &evidence_ids,
            bundle_finding.subject_id.clone(),
            &mut findings,
        );
    }
    for review in &bundle.human_reviews {
        validate_evidence_references(
            &review.evidence,
            &evidence_ids,
            Some(review.review_id.clone()),
            &mut findings,
        );
    }

    findings
}

fn validate_evidence_references(
    references: &[EvidenceRef],
    evidence_ids: &BTreeSet<StableId>,
    subject_id: Option<StableId>,
    findings: &mut Vec<ValidationFinding>,
) {
    for reference in references {
        if !evidence_ids.contains(&reference.evidence_id) {
            findings.push(finding(
                "foip:DanglingEvidenceReference",
                FindingLayer::Structural,
                Severity::Error,
                "Record references evidence absent from the bundle",
                subject_id.clone(),
            ));
        }
    }
}

fn finding(
    rule_id: &str,
    layer: FindingLayer,
    severity: Severity,
    message: &str,
    subject_id: Option<StableId>,
) -> ValidationFinding {
    ValidationFinding {
        rule_id: TermId::parse(rule_id).expect("static term is valid"),
        layer,
        severity,
        message: message.to_string(),
        subject_id,
        evidence: Vec::new(),
        requires_human_review: severity == Severity::ReviewNeeded,
        details: BTreeMap::new(),
    }
}
