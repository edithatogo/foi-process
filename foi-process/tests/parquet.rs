#![cfg(feature = "parquet")]

use foi_process::*;

#[test]
fn normalized_fixture_writes_bounded_parquet_tables() {
    let bundle: NormalizedBundle =
        serde_json::from_str(include_str!("../examples/generated/normalized-bundle.json")).unwrap();
    let directory = tempfile::tempdir().unwrap();
    let report = write_normalized_bundle_parquet(
        &bundle,
        directory.path(),
        ParquetWriteOptions {
            row_group_size: 2,
            zstd_level: 3,
        },
    )
    .unwrap();
    assert_eq!(report.tables.len(), 6);
    assert!(report
        .tables
        .iter()
        .all(|table| table.sha256.as_str().len() == 64));
    assert!(directory.path().join("events.parquet").is_file());
    assert!(directory.path().join("dataset-report.json").is_file());
}

#[test]
fn event_partition_path_is_hive_style_and_path_safe() {
    let bundle: NormalizedBundle =
        serde_json::from_str(include_str!("../examples/generated/normalized-bundle.json")).unwrap();
    let path = event_partition_directory(&bundle.events[0]);
    assert_eq!(
        path.to_string_lossy().replace('\\', "/"),
        "site=urn%3Aalaveteli%3Asite%3Afyi.org.nz/\
jurisdiction=jurisdiction%3ANZ/event_year=2025"
    );
}
