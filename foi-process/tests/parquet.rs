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
