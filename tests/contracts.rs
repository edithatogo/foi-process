use foi_process::*;

#[test]
fn generated_contract_fixtures_round_trip() {
    let bundle: NormalizedBundle =
        serde_json::from_str(include_str!("../examples/generated/normalized-bundle.json")).unwrap();
    assert_eq!(bundle.events.len(), 5);
    assert_eq!(bundle.human_reviews.len(), 1);
    assert!(validate_bundle(&bundle)
        .iter()
        .all(|finding| finding.severity < Severity::Error));

    let document: DocumentBundle =
        serde_json::from_str(include_str!("../examples/generated/document-bundle.json")).unwrap();
    let born_digital: DocumentBundle = serde_json::from_str(include_str!(
        "../examples/generated/document-bundle-born-digital.json"
    ))
    .unwrap();
    assert_eq!(
        born_digital.pages[0].extraction_method,
        ExtractionMethod::BornDigital
    );
    assert_eq!(
        born_digital.attributes["ocr_required"],
        serde_json::json!(false)
    );
    let signal: DocumentSignal =
        serde_json::from_str(include_str!("../examples/generated/document-signal.json")).unwrap();
    assert_eq!(signal.assertion_status, AssertionStatus::Candidate);
    assert_eq!(signal.document_id, document.document_id);
    assert!(!signal.evidence.is_empty());
    assert!(signal.evidence.iter().all(|evidence| {
        matches!(
            evidence.selector,
            Some(EvidenceSelector::BoundingBox { ref bbox }) if bbox.page == 1
        )
    }));
    assert_eq!(document.pages.len(), 1);

    let signal: DocumentSignal =
        serde_json::from_str(include_str!("../examples/generated/document-signal.json")).unwrap();
    assert_eq!(signal.assertion_status, AssertionStatus::Candidate);

    let review: HumanReviewRecord = serde_json::from_str(include_str!(
        "../examples/generated/human-review-record.json"
    ))
    .unwrap();
    assert_eq!(review.previous_status, AssertionStatus::Candidate);
    assert_eq!(review.resulting_status, AssertionStatus::HumanCertified);

    let trace: ConformanceTrace =
        serde_json::from_str(include_str!("../examples/generated/conformance-trace.json")).unwrap();
    assert_eq!(trace.assertion_status, AssertionStatus::Inferred);
    assert_eq!(trace.findings[0].layer, FindingLayer::Statutory);
}

#[test]
fn ocel_projection_materialises_latest_revision() {
    let bundle: NormalizedBundle =
        serde_json::from_str(include_str!("../examples/generated/normalized-bundle.json")).unwrap();
    let projection = project_ocel(&bundle);
    let extensions = projection
        .events
        .iter()
        .filter(|event| event.event_type.as_str() == "foio:ExtensionNotified")
        .count();
    assert_eq!(extensions, 1);
}

#[test]
fn public_projection_does_not_publish_metadata_only_evidence() {
    let bundle: NormalizedBundle =
        serde_json::from_str(include_str!("../examples/generated/normalized-bundle.json")).unwrap();
    let projection = project_public(&bundle, &PublicationPolicy::dashboard_default());
    let closed = projection
        .events
        .iter()
        .find(|event| event.activity.as_str() == "foio:ClosedObserved")
        .unwrap();
    assert!(closed.evidence.is_empty());
    assert_eq!(projection.metadata_only_event_count, 1);
}

#[test]
fn public_projection_withholds_events_linked_to_removed_objects() {
    let mut bundle: NormalizedBundle =
        serde_json::from_str(include_str!("../examples/generated/normalized-bundle.json")).unwrap();
    bundle.objects[0].privacy.disposition = PublicationDisposition::Withhold;
    let projection = project_public(&bundle, &PublicationPolicy::dashboard_default());
    assert_eq!(projection.events.len(), 1);
    assert_eq!(projection.metadata_only_event_count, 1);
    assert_eq!(projection.withheld_event_count, 3);
    assert_eq!(
        projection.events[0].activity.as_str(),
        "foio:ClosedObserved"
    );
}

#[test]
fn dashboard_summary_is_revision_order_independent() {
    let bundle: NormalizedBundle =
        serde_json::from_str(include_str!("../examples/generated/normalized-bundle.json")).unwrap();
    let corrected = bundle
        .events
        .iter()
        .find(|event| event.activity.as_str() == "foio:ExtensionNotified" && event.revision == 2)
        .unwrap()
        .clone();
    let original = bundle
        .events
        .iter()
        .find(|event| event.activity.as_str() == "foio:ExtensionNotified" && event.revision == 1)
        .unwrap()
        .clone();

    let mut in_order = RevisableProcessSummary::default();
    in_order.apply_event(original.clone());
    in_order.apply_event(corrected.clone());

    let mut reversed = RevisableProcessSummary::default();
    reversed.apply_event(corrected);
    reversed.apply_event(original);

    assert_eq!(in_order.snapshot(), reversed.snapshot());
    assert_eq!(
        reversed
            .snapshot()
            .activities
            .iter()
            .find(|item| item.activity.as_str() == "foio:ExtensionNotified")
            .unwrap()
            .count,
        1
    );
}
