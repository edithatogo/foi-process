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
        "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "warc_record_ids": ["warc-a", "warc-b"],
        "path": "data/attachments/example"
    }))
    .unwrap();
    assert_eq!(attachment.filename, "example.pdf");
    assert_eq!(attachment.mime_type.as_deref(), Some("application/pdf"));
    assert_eq!(attachment.size_bytes, Some(358253));
    assert_eq!(attachment.content_sha256.as_deref(), Some("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"));
    assert_eq!(attachment.warc_record_ids, vec!["warc-a", "warc-b"]);
}

#[test]
fn archive_snapshot_revision_is_explicit_and_attachment_bytes_are_verified() {
    let mut manifest: FyiArchiveManifest = serde_json::from_str(include_str!(
        "../examples/input/fyi-archive-manifest.sample.json"
    )).unwrap();
    manifest.meta.snapshot_revision = Some(1);
    let deltas = fyi_archive_manifest_to_deltas(
        manifest,
        Timestamp::parse("2026-06-29T11:47:00Z").unwrap(),
    ).unwrap();
    assert_eq!(deltas[0].revision, 1);

    let bytes = b"attachment";
    let attachment: FyiArchiveAttachment = serde_json::from_value(serde_json::json!({
        "url": "https://example.test/a",
        "sha256": Sha256Digest::of(bytes).to_string(),
        "size": bytes.len()
    })).unwrap();
    verify_attachment_bytes(&attachment, bytes).unwrap();
    assert!(matches!(
        verify_attachment_bytes(&attachment, b"tampered!!"),
        Err(FyiArchiveAdapterError::AttachmentDigestMismatch { .. })
    ));
}

#[test]
fn archive_snapshot_sequence_requires_a_predecessor_for_non_initial_revisions() {
    let mut manifest: FyiArchiveManifest = serde_json::from_str(include_str!(
        "../examples/input/fyi-archive-manifest.sample.json"
    )).unwrap();
    manifest.meta.snapshot_revision = Some(3);
    assert!(matches!(
        fyi_archive_manifest_to_deltas(manifest, Timestamp::parse("2026-06-29T11:47:00Z").unwrap()),
        Err(FyiArchiveAdapterError::InitialSnapshotRevision(3))
    ));

    let mut manifest: FyiArchiveManifest = serde_json::from_str(include_str!(
        "../examples/input/fyi-archive-manifest.sample.json"
    )).unwrap();
    manifest.meta.snapshot_revision = Some(3);
    manifest.meta.previous_snapshot_revision = Some(2);
    assert!(fyi_archive_manifest_to_deltas(
        manifest,
        Timestamp::parse("2026-06-29T11:47:00Z").unwrap()
    ).is_ok());
}

#[test]
fn archive_source_sequence_is_preserved_over_request_id_sorting() {
    let mut manifest: FyiArchiveManifest = serde_json::from_str(include_str!(
        "../examples/input/fyi-archive-manifest.sample.json"
    )).unwrap();
    manifest.requests[0].source_sequence = Some(20);
    manifest.requests[1].source_sequence = Some(10);
    let deltas = fyi_archive_manifest_to_deltas(
        manifest,
        Timestamp::parse("2026-06-29T11:47:00Z").unwrap(),
    ).unwrap();
    assert_eq!(deltas[0].position.sequence, 10);
    assert_eq!(deltas[1].position.sequence, 20);
}
