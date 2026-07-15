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

#[test]
fn archive_adapter_accepts_live_nullable_timestamps() {
    let mut manifest: FyiArchiveManifest = serde_json::from_str(include_str!(
        "../examples/input/fyi-archive-manifest.sample.json"
    ))
    .unwrap();
    manifest.requests[0].first_seen = None;
    manifest.requests[0].last_updated = None;
    let deltas =
        fyi_archive_manifest_to_deltas(manifest, Timestamp::parse("2026-06-29T11:47:00Z").unwrap())
            .unwrap();
    assert_eq!(deltas.len(), 2);
    assert!(deltas[0]
        .attributes
        .get("event_time")
        .and_then(serde_json::Value::as_str)
        .is_some());
}

#[test]
fn archive_adapter_derives_live_request_urls_when_manifest_omits_them() {
    let mut manifest: FyiArchiveManifest = serde_json::from_str(include_str!(
        "../examples/input/fyi-archive-manifest.sample.json"
    ))
    .unwrap();
    manifest.requests[0].request_url.clear();
    manifest.requests[0].json_api_url.clear();
    let deltas =
        fyi_archive_manifest_to_deltas(manifest, Timestamp::parse("2026-06-29T11:47:00Z").unwrap())
            .unwrap();
    assert_eq!(
        deltas[0]
            .evidence
            .as_ref()
            .and_then(|evidence| evidence.locator.uri.as_deref()),
        Some("https://fyi.org.nz/request/first-request")
    );
    assert_eq!(
        deltas[0]
            .attributes
            .get("json_api_url")
            .and_then(serde_json::Value::as_str),
        Some("https://fyi.org.nz/request/first-request.json")
    );
}

#[test]
fn archive_adapter_accepts_fyi_cli_attachment_field_names() {
    let attachment: FyiArchiveAttachment = serde_json::from_value(serde_json::json!({
        "url": "https://fyi.org.nz/request/26953/response/103126/attach/3/example.pdf",
        "name": "example.pdf",
        "content_type": "application/pdf",
        "size": 358253,
        "path": "data/attachments/example"
    }))
    .unwrap();
    assert_eq!(attachment.filename, "example.pdf");
    assert_eq!(attachment.mime_type.as_deref(), Some("application/pdf"));
    assert_eq!(attachment.size_bytes, Some(358253));
}
