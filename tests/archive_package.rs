use std::collections::BTreeSet;

use foi_process::*;

const REPOSITORY: &str = "https://huggingface.co/datasets/edithatogo/fyi-archive-nz";
const REVISION: &str = "0123456789abcdef0123456789abcdef01234567";

fn digest(value: &[u8]) -> Sha256Digest {
    Sha256Digest::of(value)
}

fn write_fixture() -> (tempfile::TempDir, ArchivePackageManifest) {
    let root = tempfile::tempdir().unwrap();
    let cases = b"{\"case_id\":\"case-1\"}\n";
    let events = concat!(
        "{\"source_sequence\":10,\"event_id\":\"event-a\"}\n",
        "{\"position\":{\"sequence\":10},\"event_id\":\"event-b\"}\n",
        "{\"source_sequence\":12,\"event_id\":\"event-c\"}\n"
    )
    .as_bytes();
    let attachments = b"{\"attachment_id\":\"attachment-1\"}\n";
    std::fs::write(root.path().join("cases.ndjson"), cases).unwrap();
    std::fs::write(root.path().join("events.ndjson"), events).unwrap();
    std::fs::write(root.path().join("attachments.ndjson"), attachments).unwrap();

    let mut manifest = ArchivePackageManifest {
        schema_version: ARCHIVE_PACKAGE_SCHEMA_VERSION.to_string(),
        package_id: digest(b"placeholder"),
        instance_id: "nz-fyi".to_string(),
        archive_revision: 42,
        takedown_revision: digest(b"takedown-inventory"),
        source: ArchivePackageSource {
            repository: REPOSITORY.to_string(),
            revision: REVISION.to_string(),
        },
        ordering: ArchivePackageOrdering {
            event_key: "source_sequence_then_event_id".to_string(),
            first_source_sequence: Some(10),
            last_source_sequence: Some(12),
        },
        counts: ArchivePackageCounts {
            file_count: 3,
            case_count: 1,
            event_count: 3,
            attachment_count: 1,
        },
        files: vec![
            file(1, "cases.ndjson", ArchivePackageFileRole::Cases, cases, 1),
            file(
                2,
                "events.ndjson",
                ArchivePackageFileRole::Events,
                events,
                3,
            ),
            file(
                3,
                "attachments.ndjson",
                ArchivePackageFileRole::Attachments,
                attachments,
                1,
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

fn file(
    order: u64,
    path: &str,
    role: ArchivePackageFileRole,
    bytes: &[u8],
    rows: u64,
) -> ArchivePackageFile {
    ArchivePackageFile {
        order,
        path: path.to_string(),
        role,
        media_type: "application/x-ndjson".to_string(),
        sha256: digest(bytes),
        byte_count: bytes.len() as u64,
        row_count: Some(rows),
    }
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

fn persist(root: &tempfile::TempDir, manifest: &ArchivePackageManifest) {
    std::fs::write(
        root.path().join(ARCHIVE_PACKAGE_MANIFEST),
        serde_json::to_vec_pretty(manifest).unwrap(),
    )
    .unwrap();
}

#[test]
fn immutable_archive_package_validates_and_emits_a_receipt() {
    let (root, manifest) = write_fixture();
    let receipt = load_and_validate_archive_package(root.path(), &policy(&manifest)).unwrap();
    assert_eq!(receipt.package_id, manifest.package_id);
    assert_eq!(receipt.instance_id, "nz-fyi");
    assert_eq!(receipt.archive_revision, 42);
    assert_eq!(receipt.repository_revision, REVISION);
    assert_eq!(receipt.counts.event_count, 3);
}

#[test]
fn intake_rejects_moving_or_unexpected_revision_identity() {
    let (root, mut manifest) = write_fixture();
    manifest.source.revision = "latest".to_string();
    manifest.package_id = archive_package_id(&manifest).unwrap();
    persist(&root, &manifest);
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &policy(&manifest)),
        Err(ArchivePackageError::MutableRepositoryRevision)
    ));

    let (root, manifest) = write_fixture();
    let mut unexpected = policy(&manifest);
    unexpected.expected_repository_revision =
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa".to_string();
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &unexpected),
        Err(ArchivePackageError::RepositoryRevisionMismatch { .. })
    ));
}

#[test]
fn intake_rejects_a_stale_canonical_package_identity() {
    let (root, mut manifest) = write_fixture();
    manifest.counts.case_count = 2;
    persist(&root, &manifest);
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &policy(&manifest)),
        Err(ArchivePackageError::PackageIdentityMismatch { .. })
    ));
}

#[test]
fn intake_rejects_source_site_transport_urls() {
    let (root, mut manifest) = write_fixture();
    manifest.source.repository = "https://fyi.org.nz/request/1".to_string();
    manifest.package_id = archive_package_id(&manifest).unwrap();
    persist(&root, &manifest);
    let mut intake = policy(&manifest);
    intake
        .allowed_archive_hosts
        .insert("fyi.org.nz".to_string());
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &intake),
        Err(ArchivePackageError::SourceSiteRepository(host)) if host == "fyi.org.nz"
    ));
}

#[test]
fn intake_rejects_checksum_and_count_tampering() {
    let (root, manifest) = write_fixture();
    std::fs::write(root.path().join("cases.ndjson"), b"tampered\n").unwrap();
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &policy(&manifest)),
        Err(ArchivePackageError::ByteCountMismatch { .. })
            | Err(ArchivePackageError::ChecksumMismatch { .. })
    ));

    let (root, mut manifest) = write_fixture();
    manifest.counts.event_count = 4;
    manifest.package_id = archive_package_id(&manifest).unwrap();
    persist(&root, &manifest);
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &policy(&manifest)),
        Err(ArchivePackageError::RoleCountMismatch {
            role: ArchivePackageFileRole::Events,
            ..
        })
    ));
}

#[test]
fn intake_rejects_wrong_instance_archive_or_takedown_revision() {
    let (root, manifest) = write_fixture();
    let mut intake = policy(&manifest);
    intake.expected_instance_id = "au-rtk".to_string();
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &intake),
        Err(ArchivePackageError::InstanceMismatch { .. })
    ));

    let mut intake = policy(&manifest);
    intake.expected_archive_revision += 1;
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &intake),
        Err(ArchivePackageError::ArchiveRevisionMismatch { .. })
    ));

    let mut intake = policy(&manifest);
    intake.expected_takedown_revision = digest(b"different-takedown-inventory");
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &intake),
        Err(ArchivePackageError::TakedownRevisionMismatch)
    ));
}

#[test]
fn intake_rejects_out_of_order_events_and_url_payload_paths() {
    let (root, mut manifest) = write_fixture();
    let unordered = concat!(
        "{\"source_sequence\":12,\"event_id\":\"event-b\"}\n",
        "{\"source_sequence\":10,\"event_id\":\"event-a\"}\n"
    )
    .as_bytes();
    std::fs::write(root.path().join("events.ndjson"), unordered).unwrap();
    manifest.files[1].sha256 = digest(unordered);
    manifest.files[1].byte_count = unordered.len() as u64;
    manifest.files[1].row_count = Some(2);
    manifest.counts.event_count = 2;
    manifest.package_id = archive_package_id(&manifest).unwrap();
    persist(&root, &manifest);
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &policy(&manifest)),
        Err(ArchivePackageError::EventOrderViolation)
    ));

    manifest.files[1].path = "https://fyi.org.nz/request/1".to_string();
    manifest.package_id = archive_package_id(&manifest).unwrap();
    persist(&root, &manifest);
    assert!(matches!(
        load_and_validate_archive_package(root.path(), &policy(&manifest)),
        Err(ArchivePackageError::InvalidPackagePath(_))
    ));
}
