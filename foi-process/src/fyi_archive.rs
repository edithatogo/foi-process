//! Adapter for the current `fyi-archive` manifest contract.
//!
//! A manifest row is evidence that a platform/archive state was observed. It is deliberately not
//! treated as a legally certified release, refusal, extension, or transfer. Richer activities are
//! proposed later from message/document evidence and remain subject to FOI-O review boundaries.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    archive_record_to_delta, content_id, ArchiveManifestRecord, EvidenceDelta, Sha256Digest,
    StableId, StreamPosition, TemporalInstant, TermId, Timestamp,
};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FyiArchiveManifest {
    pub meta: FyiArchiveManifestMeta,
    pub requests: Vec<FyiArchiveRequest>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FyiArchiveManifestMeta {
    pub generated_at: Option<String>,
    pub source: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub instance_id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub jurisdiction: Option<String>,
    pub version: String,
    pub record_count: u64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub schema: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub schema_version: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub fetched_at: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub fyi_cli_version: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FyiArchiveRequest {
    pub request_id: u64,
    pub url_title: String,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub authority: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub body_tag: Option<String>,
    #[serde(default)]
    pub request_url: String,
    #[serde(default)]
    pub json_api_url: String,
    #[serde(default)]
    pub state: String,
    pub content_sha256: String,
    #[serde(default)]
    pub html_captured: bool,
    #[serde(default)]
    pub attachments: Vec<FyiArchiveAttachment>,
    #[serde(default)]
    pub warc_record_ids: Vec<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub license: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub attribution: Option<String>,
    #[serde(default)]
    pub first_seen: String,
    #[serde(default)]
    pub last_updated: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FyiArchiveAttachment {
    pub url: String,
    pub filename: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mime_type: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub size_bytes: Option<u64>,
}

#[derive(Debug, Error)]
pub enum FyiArchiveAdapterError {
    #[error("manifest record_count {declared} does not match {actual} request rows")]
    RecordCountMismatch { declared: u64, actual: usize },
    #[error("request_id must be positive")]
    ZeroRequestId,
    #[error("duplicate request_id {0}")]
    DuplicateRequestId(u64),
    #[error("invalid content digest for request {request_id}: {digest}")]
    InvalidDigest { request_id: u64, digest: String },
    #[error("manifest identifier conversion failed: {0}")]
    Identifier(#[from] crate::IdentifierError),
    #[error("manifest conversion failed: {0}")]
    Serialization(#[from] serde_json::Error),
}

/// Convert a complete manifest snapshot into deterministic, sorted EvidenceDelta rows.
pub fn fyi_archive_manifest_to_deltas(
    manifest: FyiArchiveManifest,
    captured_at: Timestamp,
) -> Result<Vec<EvidenceDelta>, FyiArchiveAdapterError> {
    if manifest.meta.record_count != manifest.requests.len() as u64 {
        return Err(FyiArchiveAdapterError::RecordCountMismatch {
            declared: manifest.meta.record_count,
            actual: manifest.requests.len(),
        });
    }

    let mut requests = manifest.requests;
    requests.sort_by_key(|request| request.request_id);
    let mut seen = BTreeSet::new();
    let mut deltas = Vec::with_capacity(requests.len());
    for (offset, request) in requests.into_iter().enumerate() {
        if request.request_id == 0 {
            return Err(FyiArchiveAdapterError::ZeroRequestId);
        }
        if !seen.insert(request.request_id) {
            return Err(FyiArchiveAdapterError::DuplicateRequestId(
                request.request_id,
            ));
        }
        deltas.push(fyi_archive_request_to_delta(
            &manifest.meta,
            request,
            captured_at.clone(),
            offset as u64 + 1,
        )?);
    }
    Ok(deltas)
}

fn fyi_archive_request_to_delta(
    meta: &FyiArchiveManifestMeta,
    request: FyiArchiveRequest,
    captured_at: Timestamp,
    sequence: u64,
) -> Result<EvidenceDelta, FyiArchiveAdapterError> {
    let digest_text = request.content_sha256.to_ascii_lowercase();
    let content_sha256 = Sha256Digest::parse(digest_text.clone()).map_err(|_| {
        FyiArchiveAdapterError::InvalidDigest {
            request_id: request.request_id,
            digest: request.content_sha256.clone(),
        }
    })?;
    let instance_id = meta.instance_id.as_deref().unwrap_or("nz-fyi");
    let jurisdiction_value = meta.jurisdiction.as_deref().unwrap_or("NZ");
    let instance = sanitize_component(instance_id);
    let jurisdiction_text = sanitize_component(jurisdiction_value);
    let request_id = StableId::parse(format!(
        "urn:alaveteli:{instance}:request:{}",
        request.request_id
    ))?;
    let logical_record_id = StableId::parse(format!(
        "urn:fyi-archive:{instance}:request:{}:manifest",
        request.request_id
    ))?;
    let record_id = content_id(
        "fyi-archive:manifest-record",
        &(
            meta.schema_version
                .clone()
                .unwrap_or_else(|| "legacy".to_string()),
            request.request_id,
            content_sha256.clone(),
        ),
    )?;
    let site = if meta.source.trim_end_matches('/') == "https://fyi.org.nz" {
        StableId::parse("urn:alaveteli:site:fyi.org.nz")?
    } else {
        content_id("alaveteli:site", &meta.source)?
    };
    let jurisdiction = TermId::parse(format!("urn:jurisdiction:{jurisdiction_text}"))?;
    let authority_id = content_id(
        "fyi-archive:authority",
        &(instance_id.to_string(), request.authority.clone()),
    )?;
    let source_time_text = if request.last_updated.is_empty() {
        meta.generated_at
            .clone()
            .unwrap_or_else(|| captured_at.to_string())
    } else {
        request.last_updated.clone()
    };
    let source_time = Timestamp::parse(source_time_text.clone())
        .ok()
        .map(TemporalInstant::exact);
    let resolved_request_url = request_url(meta, &request);

    let mut attributes = BTreeMap::new();
    attributes.insert(
        "platform_activity".to_string(),
        serde_json::Value::String("platform_state_observed".to_string()),
    );
    attributes.insert(
        "platform_state".to_string(),
        serde_json::Value::String(request.state.clone()),
    );
    attributes.insert(
        "authority_id".to_string(),
        serde_json::Value::String(authority_id.to_string()),
    );
    attributes.insert(
        "authority_name".to_string(),
        serde_json::Value::String(request.authority.clone()),
    );
    attributes.insert(
        "request_title".to_string(),
        serde_json::Value::String(request.title.clone()),
    );
    attributes.insert(
        "request_url".to_string(),
        serde_json::Value::String(resolved_request_url.clone()),
    );
    attributes.insert(
        "url_title".to_string(),
        serde_json::Value::String(request.url_title.clone()),
    );
    attributes.insert(
        "description".to_string(),
        serde_json::Value::String(request.description.clone()),
    );
    attributes.insert(
        "json_api_url".to_string(),
        serde_json::Value::String(request.json_api_url.clone()),
    );
    attributes.insert(
        "html_captured".to_string(),
        serde_json::Value::Bool(request.html_captured),
    );
    attributes.insert(
        "attachment_count".to_string(),
        serde_json::Value::from(request.attachments.len() as u64),
    );
    attributes.insert(
        "warc_record_count".to_string(),
        serde_json::Value::from(request.warc_record_ids.len() as u64),
    );
    attributes.insert(
        "event_time".to_string(),
        serde_json::Value::String(source_time_text),
    );
    if let Some(body_tag) = request.body_tag {
        attributes.insert("body_tag".to_string(), serde_json::Value::String(body_tag));
    }
    if let Some(license) = request.license {
        attributes.insert("license".to_string(), serde_json::Value::String(license));
    }
    if let Some(attribution) = request.attribution {
        attributes.insert(
            "attribution".to_string(),
            serde_json::Value::String(attribution),
        );
    }

    let record = ArchiveManifestRecord {
        record_id,
        logical_record_id,
        revision: 1,
        site,
        jurisdiction,
        request_id,
        url: resolved_request_url,
        content_sha256,
        captured_at: captured_at.clone(),
        position: StreamPosition {
            source: StableId::parse(format!("urn:fyi-archive:manifest:{instance}"))?,
            partition: jurisdiction_text,
            sequence,
        },
        media_type: "application/vnd.fyi-archive.manifest-record+json".to_string(),
        source_kind: TermId::parse("foip:ArchiveManifestRecord")?,
        source_time,
        warc_record_id: request.warc_record_ids.into_iter().next(),
        attributes,
    };
    Ok(archive_record_to_delta(record)?)
}

fn request_url(meta: &FyiArchiveManifestMeta, request: &FyiArchiveRequest) -> String {
    if !request.request_url.is_empty() {
        return request.request_url.clone();
    }
    format!(
        "{}/request/{}/{}",
        meta.source.trim_end_matches('/'),
        request.request_id,
        request.url_title
    )
}

fn sanitize_component(value: &str) -> String {
    let mut output = String::with_capacity(value.len());
    for character in value.chars() {
        if character.is_ascii_alphanumeric() || matches!(character, '-' | '_' | '.') {
            output.push(character.to_ascii_lowercase());
        } else {
            output.push('-');
        }
    }
    let output = output.trim_matches('-');
    if output.is_empty() {
        "unknown".to_string()
    } else {
        output.to_string()
    }
}
