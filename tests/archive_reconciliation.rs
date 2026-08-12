use std::{collections::BTreeSet, path::Path, process::Command};

use foi_process::*;

const REPOSITORY: &str = "https://huggingface.co/datasets/edithatogo/fyi-archive-nz";
const REPOSITORY_REVISION: &str = "0123456789abcdef0123456789abcdef01234567";

fn digest(value: &[u8]) -> Sha256Digest {
    Sha256Digest::of(value)
}

fn sample_event() -> ProcessEvent {
    serde_json::from_str(
        include_str!("../examples/input/process-events.ndjson")
            .lines()
            .next()
            .unwrap(),
    )
    .unwrap()
}

fn event_bytes(event: &ProcessEvent) -> Vec<u8> {
    let mut bytes = serde_json::to_vec(event).unwrap();
    bytes.push(b'\n');
    bytes
}

fn package_file(
    order: u64,
    path: &str,
    role: ArchivePackageFileRole,
    bytes: &[u8],
) -> ArchivePackageFile {
    ArchivePackageFile {
        order,
        path: path.to_string(),
        role,
        media_type: "application/x-ndjson".to_string(),
        sha256: digest(bytes),
        byte_count: bytes.len() as u64,
        row_count: Some(1),
    }
}

fn write_package(
    archive_revision: u64,
    takedown_label: &str,
    event: ProcessEvent,
) -> (tempfile::TempDir, ArchivePackageManifest) {
    let root = tempfile::tempdir().unwrap();
    let cases = b"{\"case_id\":\"case-1\"}\n";
    let events = event_bytes(&event);
    let attachments = b"{\"attachment_id\":\"attachment-1\"}\n";
    std::fs::write(root.path().join("cases.ndjson"), cases).unwrap();
    std::fs::write(root.path().join("events.ndjson"), &events).unwrap();
    std::fs::write(root.path().join("attachments.ndjson"), attachments).unwrap();

    let mut manifest = ArchivePackageManifest {
        schema_version: ARCHIVE_PACKAGE_SCHEMA_VERSION.to_string(),
        package_id: digest(b"placeholder"),
        instance_id: "nz-fyi".to_string(),
        archive_revision,
        takedown_revision: digest(takedown_label.as_bytes()),
        source: ArchivePackageSource {
            repository: REPOSITORY.to_string(),
            revision: REPOSITORY_REVISION.to_string(),
        },
        ordering: ArchivePackageOrdering {
            event_key: "source_sequence_then_event_id".to_string(),
            first_source_sequence: Some(event.position.sequence),
            last_source_sequence: Some(event.position.sequence),
        },
        counts: ArchivePackageCounts {
            file_count: 3,
            case_count: 1,
            event_count: 1,
            attachment_count: 1,
        },
        files: vec![
            package_file(1, "cases.ndjson", ArchivePackageFileRole::Cases, cases),
            package_file(2, "events.ndjson", ArchivePackageFileRole::Events, &events),
            package_file(
                3,
                "attachments.ndjson",
                ArchivePackageFileRole::Attachments,
                attachments,
            ),
        ],
    };
    manifest.package_id = archive_package_id(&manifest).unwrap();
    std::fs::write(
        root.path().join(ARCHIVE_PACKAGE_MANIFEST),
        serde_json::to_vec_pretty(&manifest).unwrap(),
    )
    .unwrap();
    (root, manifest)
}

fn policy(manifest: &ArchivePackageManifest) -> ArchivePackageIntakePolicy {
    ArchivePackageIntakePolicy {
        expected_instance_id: manifest.instance_id.clone(),
        expected_archive_revision: manifest.archive_revision,
        expected_takedown_revision: manifest.takedown_revision.clone(),
        expected_repository: manifest.source.repository.clone(),
        expected_repository_revision: manifest.source.revision.clone(),
        allowed_archive_hosts: BTreeSet::from(["huggingface.co".to_string()]),
        source_site_hosts: BTreeSet::from(["fyi.org.nz".to_string()]),
    }
}

fn generation_count(output: &Path) -> usize {
    std::fs::read_dir(output.join("generations"))
        .unwrap()
        .filter_map(Result::ok)
        .filter(|entry| entry.file_type().unwrap().is_dir())
        .count()
}

#[test]
fn first_package_requires_explicit_bootstrap_and_commits_state_and_receipt_together() {
    let (package, manifest) = write_package(1, "takedown-1", sample_event());
    let output = tempfile::tempdir().unwrap();
    assert!(matches!(
        reconcile_archive_package(package.path(), &policy(&manifest), output.path(), false),
        Err(ArchiveReconciliationError::BootstrapRequired)
    ));
    assert_eq!(generation_count(output.path()), 0);

    let outcome =
        reconcile_archive_package(package.path(), &policy(&manifest), output.path(), true).unwrap();
    assert_eq!(outcome.status, ReconciliationStatus::Applied);
    assert_eq!(outcome.state.archive_revision, 1);
    assert_eq!(outcome.state.validated_event_count, 1);
    assert!(outcome.state_path.is_file());
    assert!(outcome.receipt_path.is_file());
    assert_eq!(generation_count(output.path()), 1);
}

#[test]
fn exact_package_rerun_is_an_idempotent_no_op() {
    let (package, manifest) = write_package(1, "takedown-1", sample_event());
    let output = tempfile::tempdir().unwrap();
    let first =
        reconcile_archive_package(package.path(), &policy(&manifest), output.path(), true).unwrap();
    let second =
        reconcile_archive_package(package.path(), &policy(&manifest), output.path(), false)
            .unwrap();
    assert_eq!(second.status, ReconciliationStatus::NoOp);
    assert_eq!(second.state, first.state);
    assert_eq!(second.receipt, first.receipt);
    assert_eq!(second.state_path, first.state_path);
    assert_eq!(generation_count(output.path()), 1);
}

#[test]
fn next_revision_advances_transactional_state() {
    let (first_package, first_manifest) = write_package(1, "takedown-1", sample_event());
    let (second_package, second_manifest) = write_package(2, "takedown-2", sample_event());
    let output = tempfile::tempdir().unwrap();
    let first = reconcile_archive_package(
        first_package.path(),
        &policy(&first_manifest),
        output.path(),
        true,
    )
    .unwrap();
    let second = reconcile_archive_package(
        second_package.path(),
        &policy(&second_manifest),
        output.path(),
        false,
    )
    .unwrap();
    assert_eq!(second.status, ReconciliationStatus::Applied);
    assert_eq!(second.state.archive_revision, 2);
    assert_eq!(
        second.receipt.previous_package_id,
        Some(first.state.package_id)
    );
    assert_eq!(generation_count(output.path()), 2);
}

#[test]
fn revision_regression_fails_without_advancing_state() {
    let (current_package, current_manifest) = write_package(2, "takedown-2", sample_event());
    let (old_package, old_manifest) = write_package(1, "takedown-1", sample_event());
    let output = tempfile::tempdir().unwrap();
    reconcile_archive_package(
        current_package.path(),
        &policy(&current_manifest),
        output.path(),
        true,
    )
    .unwrap();
    assert!(matches!(
        reconcile_archive_package(
            old_package.path(),
            &policy(&old_manifest),
            output.path(),
            false
        ),
        Err(ArchiveReconciliationError::RevisionRegression {
            current: 2,
            incoming: 1
        })
    ));
    assert_eq!(generation_count(output.path()), 1);
}

#[test]
fn revision_gap_fails_without_advancing_state() {
    let (first_package, first_manifest) = write_package(1, "takedown-1", sample_event());
    let (gap_package, gap_manifest) = write_package(3, "takedown-3", sample_event());
    let output = tempfile::tempdir().unwrap();
    reconcile_archive_package(
        first_package.path(),
        &policy(&first_manifest),
        output.path(),
        true,
    )
    .unwrap();
    assert!(matches!(
        reconcile_archive_package(
            gap_package.path(),
            &policy(&gap_manifest),
            output.path(),
            false
        ),
        Err(ArchiveReconciliationError::RevisionGap {
            expected: 2,
            incoming: 3
        })
    ));
    assert_eq!(generation_count(output.path()), 1);
}

#[test]
fn same_revision_conflict_fails_without_advancing_state() {
    let (first_package, first_manifest) = write_package(1, "takedown-1", sample_event());
    let (conflict_package, conflict_manifest) = write_package(1, "different", sample_event());
    let output = tempfile::tempdir().unwrap();
    reconcile_archive_package(
        first_package.path(),
        &policy(&first_manifest),
        output.path(),
        true,
    )
    .unwrap();
    assert!(matches!(
        reconcile_archive_package(
            conflict_package.path(),
            &policy(&conflict_manifest),
            output.path(),
            false
        ),
        Err(ArchiveReconciliationError::RevisionConflict { revision: 1 })
    ));
    assert_eq!(generation_count(output.path()), 1);
}

#[test]
fn invalid_process_event_fails_before_state_is_committed() {
    let (valid_package, valid_manifest) = write_package(1, "takedown-1", sample_event());
    let mut invalid = sample_event();
    invalid.revision = 0;
    let (package, manifest) = write_package(2, "takedown-2", invalid);
    let output = tempfile::tempdir().unwrap();
    let accepted = reconcile_archive_package(
        valid_package.path(),
        &policy(&valid_manifest),
        output.path(),
        true,
    )
    .unwrap();
    assert!(matches!(
        reconcile_archive_package(package.path(), &policy(&manifest), output.path(), false),
        Err(ArchiveReconciliationError::ArchivePackage(
            ArchivePackageError::InvalidProcessEvent { .. }
        ))
    ));
    assert_eq!(generation_count(output.path()), 1);
    let current = reconcile_archive_package(
        valid_package.path(),
        &policy(&valid_manifest),
        output.path(),
        false,
    )
    .unwrap();
    assert_eq!(current.status, ReconciliationStatus::NoOp);
    assert_eq!(current.state_path, accepted.state_path);
}

#[test]
fn cli_reconciles_exactly_one_package_from_a_policy_file() {
    let (package, manifest) = write_package(1, "takedown-1", sample_event());
    let output = tempfile::tempdir().unwrap();
    let policy_path = output.path().join("policy.json");
    std::fs::write(
        &policy_path,
        serde_json::to_vec_pretty(&policy(&manifest)).unwrap(),
    )
    .unwrap();

    let result = Command::new(env!("CARGO_BIN_EXE_foi-process"))
        .arg("reconcile-archive-package")
        .arg(package.path())
        .arg(output.path().join("state"))
        .arg("--policy")
        .arg(policy_path)
        .arg("--bootstrap")
        .output()
        .unwrap();
    assert!(
        result.status.success(),
        "{}",
        String::from_utf8_lossy(&result.stderr)
    );
    let outcome: serde_json::Value = serde_json::from_slice(&result.stdout).unwrap();
    assert_eq!(outcome["status"], "applied");
    assert_eq!(outcome["state"]["archive_revision"], 1);
}
