use foi_process::*;

#[test]
fn current_archive_fixture_is_tolerant_and_deterministic() {
    let manifest: FyiArchiveManifest = serde_json::from_str(include_str!(
        "../examples/input/fyi-archive-manifest.sample.json"
    ))
    .unwrap();
    let captured_at = Timestamp::parse("2026-06-29T11:47:00Z").unwrap();
    let first = fyi_archive_manifest_to_deltas(manifest.clone(), captured_at.clone()).unwrap();
    let second = fyi_archive_manifest_to_deltas(manifest, captured_at).unwrap();
    assert_eq!(first, second);
    assert_eq!(first.len(), 2);
    assert!(first[0]
        .request_hint
        .as_ref()
        .unwrap()
        .as_str()
        .ends_with(":1001"));
    assert_eq!(
        first[0]
            .attributes
            .get("platform_activity")
            .and_then(serde_json::Value::as_str),
        Some("platform_state_observed")
    );
    assert_eq!(
        first[1].current_content_sha256.as_ref().unwrap().as_str(),
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    );
}

#[test]
fn archive_adapter_rejects_record_count_mismatch() {
    let mut manifest: FyiArchiveManifest = serde_json::from_str(include_str!(
        "../examples/input/fyi-archive-manifest.sample.json"
    ))
    .unwrap();
    manifest.meta.record_count = 3;
    let error =
        fyi_archive_manifest_to_deltas(manifest, Timestamp::parse("2026-06-29T11:47:00Z").unwrap())
            .unwrap_err();
    assert!(matches!(
        error,
        FyiArchiveAdapterError::RecordCountMismatch { .. }
    ));
}
