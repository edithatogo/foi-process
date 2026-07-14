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
