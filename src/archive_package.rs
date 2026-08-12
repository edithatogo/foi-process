//! Fail-closed intake for immutable packages produced by `fyi-archive`.

use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Component, Path, PathBuf},
};

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{canonical_json_bytes, validate_event, ProcessEvent, Severity, Sha256Digest};

pub const ARCHIVE_PACKAGE_SCHEMA_VERSION: &str = "1.0.0";
pub const ARCHIVE_PACKAGE_MANIFEST: &str = "archive-package.json";

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArchivePackageManifest {
    pub schema_version: String,
    pub package_id: Sha256Digest,
    pub instance_id: String,
    pub archive_revision: u64,
    pub takedown_revision: Sha256Digest,
    pub source: ArchivePackageSource,
    pub ordering: ArchivePackageOrdering,
    pub counts: ArchivePackageCounts,
    pub files: Vec<ArchivePackageFile>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArchivePackageSource {
    /// HTTPS repository or dataset URI used to transport the archive package.
    pub repository: String,
    /// Full 40-character Git or Hugging Face commit identifier.
    pub revision: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArchivePackageOrdering {
    pub event_key: String,
    pub first_source_sequence: Option<u64>,
    pub last_source_sequence: Option<u64>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArchivePackageCounts {
    pub file_count: u64,
    pub case_count: u64,
    pub event_count: u64,
    pub attachment_count: u64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ArchivePackageFileRole {
    Cases,
    Events,
    Attachments,
    Other,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArchivePackageFile {
    /// One-based order in the immutable package manifest.
    pub order: u64,
    pub path: String,
    pub role: ArchivePackageFileRole,
    pub media_type: String,
    pub sha256: Sha256Digest,
    pub byte_count: u64,
    pub row_count: Option<u64>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArchivePackageIntakePolicy {
    pub expected_instance_id: String,
    pub expected_archive_revision: u64,
    pub expected_takedown_revision: Sha256Digest,
    pub expected_repository: String,
    pub expected_repository_revision: String,
    pub allowed_archive_hosts: BTreeSet<String>,
    pub source_site_hosts: BTreeSet<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArchivePackageReceipt {
    pub package_id: Sha256Digest,
    pub manifest_sha256: Sha256Digest,
    pub instance_id: String,
    pub archive_revision: u64,
    pub takedown_revision: Sha256Digest,
    pub repository: String,
    pub repository_revision: String,
    pub counts: ArchivePackageCounts,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct ValidatedArchivePackage {
    pub receipt: ArchivePackageReceipt,
    pub events: Vec<ProcessEvent>,
}

#[derive(Debug, Error)]
pub enum ArchivePackageError {
    #[error("cannot read archive package manifest: {0}")]
    ReadManifest(#[source] std::io::Error),
    #[error("invalid archive package manifest JSON: {0}")]
    ParseManifest(#[source] serde_json::Error),
    #[error("unsupported archive package schema version {0}")]
    SchemaVersion(String),
    #[error("instance mismatch: expected {expected}, got {actual}")]
    InstanceMismatch { expected: String, actual: String },
    #[error("archive revision mismatch: expected {expected}, got {actual}")]
    ArchiveRevisionMismatch { expected: u64, actual: u64 },
    #[error("archive revision must be positive")]
    InvalidArchiveRevision,
    #[error("takedown revision mismatch")]
    TakedownRevisionMismatch,
    #[error("repository mismatch: expected {expected}, got {actual}")]
    RepositoryMismatch { expected: String, actual: String },
    #[error("repository URI must be an HTTPS archive transport URI")]
    InvalidRepositoryUri,
    #[error("repository host {0} is not in the archive transport allowlist")]
    RepositoryHostNotAllowed(String),
    #[error("source-site host {0} cannot be used as an archive package transport")]
    SourceSiteRepository(String),
    #[error(
        "repository revision must be a full immutable 40-character lowercase hexadecimal commit"
    )]
    MutableRepositoryRevision,
    #[error("repository revision mismatch: expected {expected}, got {actual}")]
    RepositoryRevisionMismatch { expected: String, actual: String },
    #[error("package identity mismatch: expected {expected}, got {actual}")]
    PackageIdentityMismatch {
        expected: Sha256Digest,
        actual: Sha256Digest,
    },
    #[error("archive package manifest cannot be canonicalised: {0}")]
    Canonicalisation(#[from] serde_json::Error),
    #[error("file_count {declared} does not match {actual} file entries")]
    FileCountMismatch { declared: u64, actual: usize },
    #[error("package file order must be exactly 1..={0}")]
    InvalidFileOrder(usize),
    #[error("duplicate package path {0}")]
    DuplicatePath(String),
    #[error("package path must be a relative local path: {0}")]
    InvalidPackagePath(String),
    #[error("package path escapes the package root: {0}")]
    PackagePathEscape(String),
    #[error("cannot read package file {path}: {source}")]
    ReadPackageFile {
        path: String,
        #[source]
        source: std::io::Error,
    },
    #[error("byte_count mismatch for {path}: expected {expected}, got {actual}")]
    ByteCountMismatch {
        path: String,
        expected: u64,
        actual: usize,
    },
    #[error("checksum mismatch for {path}: expected {expected}, got {actual}")]
    ChecksumMismatch {
        path: String,
        expected: Sha256Digest,
        actual: Sha256Digest,
    },
    #[error("row_count is required for {role:?} file {path}")]
    RowCountMissing {
        path: String,
        role: ArchivePackageFileRole,
    },
    #[error("row_count mismatch for {path}: expected {expected}, got {actual}")]
    RowCountMismatch {
        path: String,
        expected: u64,
        actual: u64,
    },
    #[error("counted package table {path} must use application/x-ndjson")]
    InvalidCountedMediaType { path: String },
    #[error("declared {role:?} count {declared} does not match {actual} rows")]
    RoleCountMismatch {
        role: ArchivePackageFileRole,
        declared: u64,
        actual: u64,
    },
    #[error("event ordering key must be source_sequence_then_event_id")]
    UnsupportedEventOrdering,
    #[error("invalid event NDJSON in {path} at row {row}: {source}")]
    InvalidEventRow {
        path: String,
        row: u64,
        #[source]
        source: serde_json::Error,
    },
    #[error("process event {event_id} in {path} at row {row} failed validation")]
    InvalidProcessEvent {
        path: String,
        row: u64,
        event_id: String,
        findings: Vec<crate::ValidationFinding>,
    },
    #[error("event row {row} in {path} is missing source_sequence or event_id")]
    EventOrderKeyMissing { path: String, row: u64 },
    #[error("event rows are not strictly ordered by source_sequence then event_id")]
    EventOrderViolation,
    #[error("declared event sequence bounds do not match package rows")]
    EventSequenceBoundsMismatch,
}

#[derive(Serialize)]
struct PackageIdentityMaterial<'a> {
    schema_version: &'a str,
    instance_id: &'a str,
    archive_revision: u64,
    takedown_revision: &'a Sha256Digest,
    source: &'a ArchivePackageSource,
    ordering: &'a ArchivePackageOrdering,
    counts: &'a ArchivePackageCounts,
    files: &'a [ArchivePackageFile],
}

/// Derive the package identity from every manifest field except the identity itself.
pub fn archive_package_id(
    manifest: &ArchivePackageManifest,
) -> Result<Sha256Digest, serde_json::Error> {
    let material = PackageIdentityMaterial {
        schema_version: &manifest.schema_version,
        instance_id: &manifest.instance_id,
        archive_revision: manifest.archive_revision,
        takedown_revision: &manifest.takedown_revision,
        source: &manifest.source,
        ordering: &manifest.ordering,
        counts: &manifest.counts,
        files: &manifest.files,
    };
    Ok(Sha256Digest::of(&canonical_json_bytes(&material)?))
}

pub fn load_and_validate_archive_package(
    root: &Path,
    policy: &ArchivePackageIntakePolicy,
) -> Result<ArchivePackageReceipt, ArchivePackageError> {
    Ok(load_validated_archive_package(root, policy)?.receipt)
}

pub fn load_validated_archive_package(
    root: &Path,
    policy: &ArchivePackageIntakePolicy,
) -> Result<ValidatedArchivePackage, ArchivePackageError> {
    let bytes =
        fs::read(root.join(ARCHIVE_PACKAGE_MANIFEST)).map_err(ArchivePackageError::ReadManifest)?;
    let manifest = serde_json::from_slice(&bytes).map_err(ArchivePackageError::ParseManifest)?;
    validate_archive_package(root, &manifest, policy, Sha256Digest::of(&bytes))
}

fn validate_archive_package(
    root: &Path,
    manifest: &ArchivePackageManifest,
    policy: &ArchivePackageIntakePolicy,
    manifest_sha256: Sha256Digest,
) -> Result<ValidatedArchivePackage, ArchivePackageError> {
    validate_identity(manifest, policy)?;
    let events = validate_files(root, manifest)?;
    Ok(ValidatedArchivePackage {
        receipt: ArchivePackageReceipt {
            package_id: manifest.package_id.clone(),
            manifest_sha256,
            instance_id: manifest.instance_id.clone(),
            archive_revision: manifest.archive_revision,
            takedown_revision: manifest.takedown_revision.clone(),
            repository: manifest.source.repository.clone(),
            repository_revision: manifest.source.revision.clone(),
            counts: manifest.counts.clone(),
        },
        events,
    })
}

fn validate_identity(
    manifest: &ArchivePackageManifest,
    policy: &ArchivePackageIntakePolicy,
) -> Result<(), ArchivePackageError> {
    if manifest.schema_version != ARCHIVE_PACKAGE_SCHEMA_VERSION {
        return Err(ArchivePackageError::SchemaVersion(
            manifest.schema_version.clone(),
        ));
    }
    if manifest.instance_id != policy.expected_instance_id {
        return Err(ArchivePackageError::InstanceMismatch {
            expected: policy.expected_instance_id.clone(),
            actual: manifest.instance_id.clone(),
        });
    }
    if manifest.archive_revision == 0 {
        return Err(ArchivePackageError::InvalidArchiveRevision);
    }
    if manifest.archive_revision != policy.expected_archive_revision {
        return Err(ArchivePackageError::ArchiveRevisionMismatch {
            expected: policy.expected_archive_revision,
            actual: manifest.archive_revision,
        });
    }
    if manifest.takedown_revision != policy.expected_takedown_revision {
        return Err(ArchivePackageError::TakedownRevisionMismatch);
    }
    if manifest.source.repository != policy.expected_repository {
        return Err(ArchivePackageError::RepositoryMismatch {
            expected: policy.expected_repository.clone(),
            actual: manifest.source.repository.clone(),
        });
    }
    let host =
        https_host(&manifest.source.repository).ok_or(ArchivePackageError::InvalidRepositoryUri)?;
    if policy
        .source_site_hosts
        .iter()
        .any(|source| host_matches(&host, source))
    {
        return Err(ArchivePackageError::SourceSiteRepository(host));
    }
    if !policy
        .allowed_archive_hosts
        .iter()
        .any(|allowed| host_matches(&host, allowed))
    {
        return Err(ArchivePackageError::RepositoryHostNotAllowed(host));
    }
    if !is_full_commit(&manifest.source.revision) {
        return Err(ArchivePackageError::MutableRepositoryRevision);
    }
    if manifest.source.revision != policy.expected_repository_revision {
        return Err(ArchivePackageError::RepositoryRevisionMismatch {
            expected: policy.expected_repository_revision.clone(),
            actual: manifest.source.revision.clone(),
        });
    }
    let expected = archive_package_id(manifest)?;
    if manifest.package_id != expected {
        return Err(ArchivePackageError::PackageIdentityMismatch {
            expected,
            actual: manifest.package_id.clone(),
        });
    }
    Ok(())
}

fn validate_files(
    root: &Path,
    manifest: &ArchivePackageManifest,
) -> Result<Vec<ProcessEvent>, ArchivePackageError> {
    if manifest.counts.file_count != manifest.files.len() as u64 {
        return Err(ArchivePackageError::FileCountMismatch {
            declared: manifest.counts.file_count,
            actual: manifest.files.len(),
        });
    }
    if manifest.ordering.event_key != "source_sequence_then_event_id" {
        return Err(ArchivePackageError::UnsupportedEventOrdering);
    }

    let root = root
        .canonicalize()
        .map_err(ArchivePackageError::ReadManifest)?;
    let mut paths = BTreeSet::new();
    let mut role_rows = BTreeMap::<u8, u64>::new();
    let mut previous_event_key: Option<(u64, String)> = None;
    let mut first_sequence = None;
    let mut last_sequence = None;
    let mut events = Vec::with_capacity(manifest.counts.event_count as usize);

    for (index, entry) in manifest.files.iter().enumerate() {
        if entry.order != index as u64 + 1 {
            return Err(ArchivePackageError::InvalidFileOrder(manifest.files.len()));
        }
        validate_relative_path(&entry.path)?;
        if !paths.insert(entry.path.clone()) {
            return Err(ArchivePackageError::DuplicatePath(entry.path.clone()));
        }
        let candidate = root.join(&entry.path);
        let path =
            candidate
                .canonicalize()
                .map_err(|source| ArchivePackageError::ReadPackageFile {
                    path: entry.path.clone(),
                    source,
                })?;
        if !path.starts_with(&root) {
            return Err(ArchivePackageError::PackagePathEscape(entry.path.clone()));
        }
        let bytes = fs::read(&path).map_err(|source| ArchivePackageError::ReadPackageFile {
            path: entry.path.clone(),
            source,
        })?;
        if bytes.len() as u64 != entry.byte_count {
            return Err(ArchivePackageError::ByteCountMismatch {
                path: entry.path.clone(),
                expected: entry.byte_count,
                actual: bytes.len(),
            });
        }
        let actual = Sha256Digest::of(&bytes);
        if actual != entry.sha256 {
            return Err(ArchivePackageError::ChecksumMismatch {
                path: entry.path.clone(),
                expected: entry.sha256.clone(),
                actual,
            });
        }

        if entry.role != ArchivePackageFileRole::Other {
            if entry.media_type != "application/x-ndjson" {
                return Err(ArchivePackageError::InvalidCountedMediaType {
                    path: entry.path.clone(),
                });
            }
            let declared = entry
                .row_count
                .ok_or_else(|| ArchivePackageError::RowCountMissing {
                    path: entry.path.clone(),
                    role: entry.role,
                })?;
            let actual = nonempty_lines(&bytes);
            if actual != declared {
                return Err(ArchivePackageError::RowCountMismatch {
                    path: entry.path.clone(),
                    expected: declared,
                    actual,
                });
            }
            *role_rows.entry(role_key(entry.role)).or_default() += actual;
        }

        if entry.role == ArchivePackageFileRole::Events {
            validate_event_rows(
                &entry.path,
                &bytes,
                &mut previous_event_key,
                &mut first_sequence,
                &mut last_sequence,
                &mut events,
            )?;
        }
    }

    for (role, declared) in [
        (ArchivePackageFileRole::Cases, manifest.counts.case_count),
        (ArchivePackageFileRole::Events, manifest.counts.event_count),
        (
            ArchivePackageFileRole::Attachments,
            manifest.counts.attachment_count,
        ),
    ] {
        let actual = role_rows.get(&role_key(role)).copied().unwrap_or(0);
        if actual != declared {
            return Err(ArchivePackageError::RoleCountMismatch {
                role,
                declared,
                actual,
            });
        }
    }
    if first_sequence != manifest.ordering.first_source_sequence
        || last_sequence != manifest.ordering.last_source_sequence
    {
        return Err(ArchivePackageError::EventSequenceBoundsMismatch);
    }
    Ok(events)
}

fn validate_event_rows(
    path: &str,
    bytes: &[u8],
    previous: &mut Option<(u64, String)>,
    first_sequence: &mut Option<u64>,
    last_sequence: &mut Option<u64>,
    events: &mut Vec<ProcessEvent>,
) -> Result<(), ArchivePackageError> {
    for (index, line) in bytes.split(|byte| *byte == b'\n').enumerate() {
        if line.iter().all(u8::is_ascii_whitespace) {
            continue;
        }
        let event: ProcessEvent = serde_json::from_slice(line).map_err(|source| {
            ArchivePackageError::InvalidEventRow {
                path: path.to_string(),
                row: index as u64 + 1,
                source,
            }
        })?;
        let findings = validate_event(&event);
        if findings
            .iter()
            .any(|finding| finding.severity >= Severity::Error)
        {
            return Err(ArchivePackageError::InvalidProcessEvent {
                path: path.to_string(),
                row: index as u64 + 1,
                event_id: event.event_id.to_string(),
                findings,
            });
        }
        let sequence = event.position.sequence;
        let event_id = event.event_id.to_string();
        let key = (sequence, event_id);
        if previous.as_ref().is_some_and(|prior| key <= *prior) {
            return Err(ArchivePackageError::EventOrderViolation);
        }
        first_sequence.get_or_insert(sequence);
        *last_sequence = Some(sequence);
        *previous = Some(key);
        events.push(event);
    }
    Ok(())
}

fn nonempty_lines(bytes: &[u8]) -> u64 {
    bytes
        .split(|byte| *byte == b'\n')
        .filter(|line| !line.iter().all(u8::is_ascii_whitespace))
        .count() as u64
}

fn validate_relative_path(path: &str) -> Result<(), ArchivePackageError> {
    let candidate = PathBuf::from(path);
    let invalid = path.is_empty()
        || path.contains("\\")
        || path.contains("://")
        || candidate.is_absolute()
        || candidate
            .components()
            .any(|component| !matches!(component, Component::Normal(_)));
    if invalid {
        return Err(ArchivePackageError::InvalidPackagePath(path.to_string()));
    }
    Ok(())
}

fn is_full_commit(value: &str) -> bool {
    value.len() == 40
        && value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
}

fn https_host(uri: &str) -> Option<String> {
    let rest = uri.strip_prefix("https://")?;
    let authority = rest.split(['/', '?', '#']).next()?;
    if authority.is_empty() || authority.contains('@') || authority.contains(':') {
        return None;
    }
    Some(authority.trim_end_matches('.').to_ascii_lowercase())
}

fn host_matches(host: &str, configured: &str) -> bool {
    let configured = configured.trim_end_matches('.').to_ascii_lowercase();
    host == configured || host.ends_with(&format!(".{configured}"))
}

fn role_key(role: ArchivePackageFileRole) -> u8 {
    match role {
        ArchivePackageFileRole::Cases => 0,
        ArchivePackageFileRole::Events => 1,
        ArchivePackageFileRole::Attachments => 2,
        ArchivePackageFileRole::Other => 3,
    }
}
