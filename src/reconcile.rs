//! Transactional reconciliation of one immutable `fyi-archive` snapshot package.

use std::{
    fs::{self, File},
    io::Write,
    path::{Path, PathBuf},
    time::{SystemTime, UNIX_EPOCH},
};

use serde::{de::DeserializeOwned, Deserialize, Serialize};
use thiserror::Error;

use crate::{
    load_validated_archive_package, ArchivePackageError, ArchivePackageIntakePolicy,
    ArchivePackageReceipt, Sha256Digest,
};

pub const ARCHIVE_RECONCILIATION_SCHEMA_VERSION: &str = "1.0.0";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ReconciliationStatus {
    Applied,
    NoOp,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArchiveReconciliationState {
    pub schema_version: String,
    pub instance_id: String,
    pub package_id: Sha256Digest,
    pub manifest_sha256: Sha256Digest,
    pub archive_revision: u64,
    pub takedown_revision: Sha256Digest,
    pub repository: String,
    pub repository_revision: String,
    pub validated_event_count: u64,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArchiveReconciliationReceipt {
    pub schema_version: String,
    pub package: ArchivePackageReceipt,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub previous_package_id: Option<Sha256Digest>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub previous_state_sha256: Option<Sha256Digest>,
    pub state_sha256: Sha256Digest,
    pub validated_event_count: u64,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ArchiveReconciliationOutcome {
    pub status: ReconciliationStatus,
    pub state: ArchiveReconciliationState,
    pub receipt: ArchiveReconciliationReceipt,
    pub state_path: PathBuf,
    pub receipt_path: PathBuf,
}

#[derive(Debug, Error)]
pub enum ArchiveReconciliationError {
    #[error(transparent)]
    ArchivePackage(#[from] ArchivePackageError),
    #[error("the first package for an instance requires explicit bootstrap")]
    BootstrapRequired,
    #[error("cannot bootstrap an instance that already has reconciliation state")]
    BootstrapAlreadyCompleted,
    #[error("reconciliation state belongs to {actual}, not {expected}")]
    InstanceMismatch { expected: String, actual: String },
    #[error("archive revision regressed from {current} to {incoming}")]
    RevisionRegression { current: u64, incoming: u64 },
    #[error("archive revision {revision} has conflicting package identities")]
    RevisionConflict { revision: u64 },
    #[error("archive revision gap: expected {expected}, got {incoming}")]
    RevisionGap { expected: u64, incoming: u64 },
    #[error("reconciliation for this output is already locked")]
    Locked,
    #[error("cannot access reconciliation output {path}: {source}")]
    OutputIo {
        path: PathBuf,
        #[source]
        source: std::io::Error,
    },
    #[error("invalid reconciliation JSON in {path}: {source}")]
    InvalidOutputJson {
        path: PathBuf,
        #[source]
        source: serde_json::Error,
    },
    #[error("unsupported reconciliation schema {actual} in {path}")]
    UnsupportedStoredSchema { path: PathBuf, actual: String },
    #[error("reconciliation state hash mismatch in {0}")]
    StateHashMismatch(PathBuf),
    #[error("stored reconciliation receipt does not match its state in {0}")]
    StoredReceiptMismatch(PathBuf),
    #[error("multiple package identities exist for archive revision {0}")]
    AmbiguousStoredRevision(u64),
    #[error("cannot serialise reconciliation output: {0}")]
    Serialisation(#[from] serde_json::Error),
}

struct ReconciliationLock {
    path: PathBuf,
}

impl Drop for ReconciliationLock {
    fn drop(&mut self) {
        let _ = fs::remove_dir(&self.path);
    }
}

struct StoredGeneration {
    state: ArchiveReconciliationState,
    receipt: ArchiveReconciliationReceipt,
    state_sha256: Sha256Digest,
    state_path: PathBuf,
    receipt_path: PathBuf,
}

pub fn reconcile_archive_package(
    package_root: &Path,
    policy: &ArchivePackageIntakePolicy,
    output_root: &Path,
    bootstrap: bool,
) -> Result<ArchiveReconciliationOutcome, ArchiveReconciliationError> {
    create_dir_all(output_root)?;
    let _lock = acquire_lock(output_root)?;
    let generations = output_root.join("generations");
    create_dir_all(&generations)?;

    let current = load_latest_generation(&generations)?;
    if bootstrap && current.is_some() {
        return Err(ArchiveReconciliationError::BootstrapAlreadyCompleted);
    }

    let package = load_validated_archive_package(package_root, policy)?;
    if let Some(stored) = &current {
        if stored.state.instance_id != package.receipt.instance_id {
            return Err(ArchiveReconciliationError::InstanceMismatch {
                expected: stored.state.instance_id.clone(),
                actual: package.receipt.instance_id.clone(),
            });
        }
        if stored.state.package_id == package.receipt.package_id {
            return Ok(ArchiveReconciliationOutcome {
                status: ReconciliationStatus::NoOp,
                state: stored.state.clone(),
                receipt: stored.receipt.clone(),
                state_path: stored.state_path.clone(),
                receipt_path: stored.receipt_path.clone(),
            });
        }
        match package
            .receipt
            .archive_revision
            .cmp(&stored.state.archive_revision)
        {
            std::cmp::Ordering::Less => {
                return Err(ArchiveReconciliationError::RevisionRegression {
                    current: stored.state.archive_revision,
                    incoming: package.receipt.archive_revision,
                });
            }
            std::cmp::Ordering::Equal => {
                return Err(ArchiveReconciliationError::RevisionConflict {
                    revision: package.receipt.archive_revision,
                });
            }
            std::cmp::Ordering::Greater
                if package.receipt.archive_revision != stored.state.archive_revision + 1 =>
            {
                return Err(ArchiveReconciliationError::RevisionGap {
                    expected: stored.state.archive_revision + 1,
                    incoming: package.receipt.archive_revision,
                });
            }
            std::cmp::Ordering::Greater => {}
        }
    } else if !bootstrap {
        return Err(ArchiveReconciliationError::BootstrapRequired);
    }

    let state = ArchiveReconciliationState {
        schema_version: ARCHIVE_RECONCILIATION_SCHEMA_VERSION.to_string(),
        instance_id: package.receipt.instance_id.clone(),
        package_id: package.receipt.package_id.clone(),
        manifest_sha256: package.receipt.manifest_sha256.clone(),
        archive_revision: package.receipt.archive_revision,
        takedown_revision: package.receipt.takedown_revision.clone(),
        repository: package.receipt.repository.clone(),
        repository_revision: package.receipt.repository_revision.clone(),
        validated_event_count: package.events.len() as u64,
    };
    let state_bytes = pretty_json_bytes(&state)?;
    let state_sha256 = Sha256Digest::of(&state_bytes);
    let receipt = ArchiveReconciliationReceipt {
        schema_version: ARCHIVE_RECONCILIATION_SCHEMA_VERSION.to_string(),
        package: package.receipt,
        previous_package_id: current
            .as_ref()
            .map(|stored| stored.state.package_id.clone()),
        previous_state_sha256: current.as_ref().map(|stored| stored.state_sha256.clone()),
        state_sha256,
        validated_event_count: package.events.len() as u64,
    };
    let receipt_bytes = pretty_json_bytes(&receipt)?;
    let generation_name = format!(
        "{:020}-{}",
        state.archive_revision,
        state.package_id.as_str()
    );
    let generation = generations.join(generation_name);
    let (state_path, receipt_path) =
        commit_generation(&generations, &generation, &state_bytes, &receipt_bytes)?;

    Ok(ArchiveReconciliationOutcome {
        status: ReconciliationStatus::Applied,
        state,
        receipt,
        state_path,
        receipt_path,
    })
}

fn acquire_lock(output_root: &Path) -> Result<ReconciliationLock, ArchiveReconciliationError> {
    let path = output_root.join(".reconcile.lock");
    match fs::create_dir(&path) {
        Ok(()) => Ok(ReconciliationLock { path }),
        Err(source) if source.kind() == std::io::ErrorKind::AlreadyExists => {
            Err(ArchiveReconciliationError::Locked)
        }
        Err(source) => Err(io_error(path, source)),
    }
}

fn load_latest_generation(
    generations: &Path,
) -> Result<Option<StoredGeneration>, ArchiveReconciliationError> {
    let mut latest: Option<StoredGeneration> = None;
    for entry in fs::read_dir(generations).map_err(|source| io_error(generations, source))? {
        let entry = entry.map_err(|source| io_error(generations, source))?;
        let path = entry.path();
        if !entry
            .file_type()
            .map_err(|source| io_error(&path, source))?
            .is_dir()
            || entry.file_name().to_string_lossy().starts_with(".stage-")
        {
            continue;
        }
        let stored = load_generation(&path)?;
        match &latest {
            Some(previous) if stored.state.archive_revision < previous.state.archive_revision => {}
            Some(previous) if stored.state.archive_revision == previous.state.archive_revision => {
                if stored.state.package_id != previous.state.package_id {
                    return Err(ArchiveReconciliationError::AmbiguousStoredRevision(
                        stored.state.archive_revision,
                    ));
                }
            }
            _ => latest = Some(stored),
        }
    }
    Ok(latest)
}

fn load_generation(path: &Path) -> Result<StoredGeneration, ArchiveReconciliationError> {
    let state_path = path.join("state.json");
    let receipt_path = path.join("receipt.json");
    let state_bytes = read_bytes(&state_path)?;
    let receipt_bytes = read_bytes(&receipt_path)?;
    let state: ArchiveReconciliationState = parse_json(&state_path, &state_bytes)?;
    let receipt: ArchiveReconciliationReceipt = parse_json(&receipt_path, &receipt_bytes)?;
    if state.schema_version != ARCHIVE_RECONCILIATION_SCHEMA_VERSION {
        return Err(ArchiveReconciliationError::UnsupportedStoredSchema {
            path: state_path,
            actual: state.schema_version,
        });
    }
    if receipt.schema_version != ARCHIVE_RECONCILIATION_SCHEMA_VERSION {
        return Err(ArchiveReconciliationError::UnsupportedStoredSchema {
            path: receipt_path,
            actual: receipt.schema_version,
        });
    }
    let state_sha256 = Sha256Digest::of(&state_bytes);
    if receipt.state_sha256 != state_sha256 {
        return Err(ArchiveReconciliationError::StateHashMismatch(state_path));
    }
    if receipt.package.package_id != state.package_id
        || receipt.package.manifest_sha256 != state.manifest_sha256
        || receipt.package.instance_id != state.instance_id
        || receipt.package.archive_revision != state.archive_revision
        || receipt.package.takedown_revision != state.takedown_revision
        || receipt.package.repository != state.repository
        || receipt.package.repository_revision != state.repository_revision
        || receipt.validated_event_count != state.validated_event_count
    {
        return Err(ArchiveReconciliationError::StoredReceiptMismatch(
            receipt_path,
        ));
    }
    Ok(StoredGeneration {
        state,
        receipt,
        state_sha256,
        state_path,
        receipt_path,
    })
}

fn commit_generation(
    generations: &Path,
    generation: &Path,
    state_bytes: &[u8],
    receipt_bytes: &[u8],
) -> Result<(PathBuf, PathBuf), ArchiveReconciliationError> {
    if generation.exists() {
        return Err(ArchiveReconciliationError::RevisionConflict {
            revision: generation_revision(generation).unwrap_or_default(),
        });
    }
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    let stage = generations.join(format!(".stage-{}-{nonce}", std::process::id()));
    fs::create_dir(&stage).map_err(|source| io_error(&stage, source))?;
    let result = (|| {
        write_synced(&stage.join("state.json"), state_bytes)?;
        write_synced(&stage.join("receipt.json"), receipt_bytes)?;
        sync_directory(&stage)?;
        fs::rename(&stage, generation).map_err(|source| io_error(generation, source))?;
        sync_directory(generations)?;
        Ok((
            generation.join("state.json"),
            generation.join("receipt.json"),
        ))
    })();
    if result.is_err() {
        let _ = fs::remove_dir_all(&stage);
    }
    result
}

fn generation_revision(path: &Path) -> Option<u64> {
    path.file_name()?.to_str()?.split('-').next()?.parse().ok()
}

fn pretty_json_bytes<T: Serialize>(value: &T) -> Result<Vec<u8>, serde_json::Error> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    Ok(bytes)
}

fn read_bytes(path: &Path) -> Result<Vec<u8>, ArchiveReconciliationError> {
    fs::read(path).map_err(|source| io_error(path, source))
}

fn parse_json<T: DeserializeOwned>(
    path: &Path,
    bytes: &[u8],
) -> Result<T, ArchiveReconciliationError> {
    serde_json::from_slice(bytes).map_err(|source| ArchiveReconciliationError::InvalidOutputJson {
        path: path.to_path_buf(),
        source,
    })
}

fn write_synced(path: &Path, bytes: &[u8]) -> Result<(), ArchiveReconciliationError> {
    let mut file = File::create(path).map_err(|source| io_error(path, source))?;
    file.write_all(bytes)
        .map_err(|source| io_error(path, source))?;
    file.sync_all().map_err(|source| io_error(path, source))
}

fn create_dir_all(path: &Path) -> Result<(), ArchiveReconciliationError> {
    fs::create_dir_all(path).map_err(|source| io_error(path, source))
}

fn io_error(path: impl AsRef<Path>, source: std::io::Error) -> ArchiveReconciliationError {
    ArchiveReconciliationError::OutputIo {
        path: path.as_ref().to_path_buf(),
        source,
    }
}

#[cfg(unix)]
fn sync_directory(path: &Path) -> Result<(), ArchiveReconciliationError> {
    File::open(path)
        .and_then(|directory| directory.sync_all())
        .map_err(|source| io_error(path, source))
}

#[cfg(not(unix))]
fn sync_directory(_path: &Path) -> Result<(), ArchiveReconciliationError> {
    Ok(())
}
