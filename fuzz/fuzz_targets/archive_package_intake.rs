#![no_main]

use std::collections::BTreeSet;

use foi_process::{
    archive_package_id, load_validated_archive_package, ArchivePackageCounts, ArchivePackageFile,
    ArchivePackageFileRole, ArchivePackageIntakePolicy, ArchivePackageManifest,
    ArchivePackageOrdering, ArchivePackageSource, Sha256Digest, ARCHIVE_PACKAGE_MANIFEST,
    ARCHIVE_PACKAGE_SCHEMA_VERSION,
};
use libfuzzer_sys::fuzz_target;

const MAX_INPUT_BYTES: usize = 64 * 1024;
const REPOSITORY: &str = "https://huggingface.co/datasets/edithatogo/fyi-archive-nz";
const REVISION: &str = "0123456789abcdef0123456789abcdef01234567";

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

fn event_manifest(event_bytes: &[u8]) -> ArchivePackageManifest {
    let event_count = event_bytes
        .split(|byte| *byte == b'\n')
        .filter(|line| !line.iter().all(u8::is_ascii_whitespace))
        .count() as u64;
    let mut manifest = ArchivePackageManifest {
        schema_version: ARCHIVE_PACKAGE_SCHEMA_VERSION.to_string(),
        package_id: Sha256Digest::of(b"placeholder"),
        instance_id: "nz-fyi".to_string(),
        archive_revision: 1,
        takedown_revision: Sha256Digest::of(b"takedown"),
        source: ArchivePackageSource {
            repository: REPOSITORY.to_string(),
            revision: REVISION.to_string(),
        },
        ordering: ArchivePackageOrdering {
            event_key: "source_sequence_then_event_id".to_string(),
            first_source_sequence: None,
            last_source_sequence: None,
        },
        counts: ArchivePackageCounts {
            file_count: 1,
            case_count: 0,
            event_count,
            attachment_count: 0,
        },
        files: vec![ArchivePackageFile {
            order: 1,
            path: "events.ndjson".to_string(),
            role: ArchivePackageFileRole::Events,
            media_type: "application/x-ndjson".to_string(),
            sha256: Sha256Digest::of(event_bytes),
            byte_count: event_bytes.len() as u64,
            row_count: Some(event_count),
        }],
    };
    manifest.package_id = archive_package_id(&manifest).expect("fixed manifest canonicalises");
    manifest
}

fuzz_target!(|data: &[u8]| {
    if data.len() > MAX_INPUT_BYTES {
        return;
    }

    let root = tempfile::tempdir().expect("temporary fuzz directory");
    let manifest = if let Ok(mut manifest) = serde_json::from_slice::<ArchivePackageManifest>(data)
    {
        manifest.package_id = archive_package_id(&manifest).expect("manifest canonicalises");
        manifest
    } else {
        std::fs::write(root.path().join("events.ndjson"), data).expect("write fuzz events");
        event_manifest(data)
    };
    std::fs::write(
        root.path().join(ARCHIVE_PACKAGE_MANIFEST),
        serde_json::to_vec(&manifest).expect("serialize fuzz manifest"),
    )
    .expect("write fuzz manifest");
    let _ = load_validated_archive_package(root.path(), &policy(&manifest));
});
