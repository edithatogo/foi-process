//! Bounded Arrow/Parquet export for dashboard and mining tables.
//!
//! `NormalizedBundle` is materialised by the current caller, while Arrow batches and Parquet
//! row groups are bounded by `row_group_size`. A later input-streaming milestone can remove the
//! remaining whole-bundle memory requirement without changing these table contracts.

use std::{
    fs::File,
    io::{BufReader, Read, Write},
    path::{Path, PathBuf},
    sync::Arc,
};

use arrow_array::{ArrayRef, BooleanArray, Float32Array, RecordBatch, StringArray, UInt64Array};
use arrow_schema::{DataType, Field, Schema};
use chrono::Datelike;
use parquet::{
    arrow::ArrowWriter,
    basic::{Compression, ZstdLevel},
    errors::ParquetError,
    file::properties::WriterProperties,
};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use thiserror::Error;

use crate::{NormalizedBundle, ProcessEvent, Sha256Digest};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ParquetWriteOptions {
    pub row_group_size: usize,
    pub zstd_level: i32,
}

impl Default for ParquetWriteOptions {
    fn default() -> Self {
        Self {
            row_group_size: 65_536,
            zstd_level: 3,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ParquetTableReport {
    pub table: String,
    pub path: String,
    pub row_count: u64,
    pub row_group_count: u64,
    pub byte_length: u64,
    pub sha256: Sha256Digest,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ParquetDatasetReport {
    pub schema_version: String,
    pub row_group_size: usize,
    pub compression: String,
    pub tables: Vec<ParquetTableReport>,
}

#[derive(Debug, Error)]
pub enum ParquetExportError {
    #[error("row_group_size must be greater than zero")]
    ZeroRowGroupSize,
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Arrow error: {0}")]
    Arrow(#[from] arrow_schema::ArrowError),
    #[error("Parquet error: {0}")]
    Parquet(#[from] ParquetError),
    #[error("invalid SHA-256 digest: {0}")]
    Digest(#[from] crate::IdentifierError),
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
}

/// Hive-style production partition path for an event table row.
///
/// Callers group/filter a bounded `NormalizedBundle` by this key before invoking the atomic
/// writer. Percent encoding prevents path separators and reserved bytes from escaping a partition.
pub fn event_partition_directory(event: &ProcessEvent) -> PathBuf {
    PathBuf::from(format!("site={}", partition_component(event.site.as_str())))
        .join(format!(
            "jurisdiction={}",
            partition_component(event.jurisdiction.as_str())
        ))
        .join(format!(
            "event_year={}",
            event.mining_time().as_datetime().year()
        ))
}

fn partition_component(value: &str) -> String {
    let mut encoded = String::with_capacity(value.len());
    for byte in value.bytes() {
        if byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.' | b'~') {
            encoded.push(char::from(byte));
        } else {
            encoded.push_str(&format!("%{byte:02X}"));
        }
    }
    encoded
}

pub fn write_normalized_bundle_parquet(
    bundle: &NormalizedBundle,
    output_dir: impl AsRef<Path>,
    options: ParquetWriteOptions,
) -> Result<ParquetDatasetReport, ParquetExportError> {
    if options.row_group_size == 0 {
        return Err(ParquetExportError::ZeroRowGroupSize);
    }
    let output_dir = output_dir.as_ref();
    std::fs::create_dir_all(output_dir)?;
    let tables = vec![
        write_events(bundle, output_dir, &options)?,
        write_event_object_links(bundle, output_dir, &options)?,
        write_evidence(bundle, output_dir, &options)?,
        write_objects(bundle, output_dir, &options)?,
        write_object_links(bundle, output_dir, &options)?,
        write_findings(bundle, output_dir, &options)?,
    ];
    let report = ParquetDatasetReport {
        schema_version: crate::CONTRACT_VERSION.to_owned(),
        row_group_size: options.row_group_size,
        compression: format!("zstd:{}", options.zstd_level),
        tables,
    };
    write_json_atomic(output_dir.join("dataset-report.json"), &report)?;
    Ok(report)
}

fn write_events(
    bundle: &NormalizedBundle,
    output_dir: &Path,
    options: &ParquetWriteOptions,
) -> Result<ParquetTableReport, ParquetExportError> {
    let schema = Arc::new(Schema::new(vec![
        Field::new("event_id", DataType::Utf8, false),
        Field::new("logical_event_id", DataType::Utf8, false),
        Field::new("revision", DataType::UInt64, false),
        Field::new("operation", DataType::Utf8, false),
        Field::new("site", DataType::Utf8, false),
        Field::new("jurisdiction", DataType::Utf8, false),
        Field::new("case_id", DataType::Utf8, false),
        Field::new("activity", DataType::Utf8, false),
        Field::new("event_time", DataType::Utf8, true),
        Field::new("mining_time", DataType::Utf8, false),
        Field::new("observed_at", DataType::Utf8, false),
        Field::new("captured_at", DataType::Utf8, false),
        Field::new("processed_at", DataType::Utf8, false),
        Field::new("assertion_status", DataType::Utf8, false),
        Field::new("confidence", DataType::Float32, true),
        Field::new("stream_source", DataType::Utf8, false),
        Field::new("stream_partition", DataType::Utf8, false),
        Field::new("stream_sequence", DataType::UInt64, false),
        Field::new("publication_disposition", DataType::Utf8, false),
        Field::new("sensitivity", DataType::Utf8, false),
        Field::new("attributes_json", DataType::Utf8, false),
    ]));
    write_table(
        "events",
        output_dir.join("events.parquet"),
        schema.clone(),
        bundle.events.len(),
        options,
        |range| {
            let rows = &bundle.events[range];
            RecordBatch::try_new(
                schema.clone(),
                vec![
                    strings(rows.iter().map(|value| value.event_id.to_string())),
                    strings(rows.iter().map(|value| value.logical_event_id.to_string())),
                    Arc::new(UInt64Array::from_iter_values(
                        rows.iter().map(|value| value.revision),
                    )),
                    strings(rows.iter().map(|value| enum_name(&value.operation))),
                    strings(rows.iter().map(|value| value.site.to_string())),
                    strings(rows.iter().map(|value| value.jurisdiction.to_string())),
                    strings(rows.iter().map(|value| value.case_id.to_string())),
                    strings(rows.iter().map(|value| value.activity.to_string())),
                    Arc::new(StringArray::from_iter(rows.iter().map(|value| {
                        value
                            .event_time
                            .as_ref()
                            .map(|time| time.timestamp.to_string())
                    }))),
                    strings(rows.iter().map(|value| value.mining_time().to_string())),
                    strings(rows.iter().map(|value| value.observed_at.to_string())),
                    strings(rows.iter().map(|value| value.captured_at.to_string())),
                    strings(rows.iter().map(|value| value.processed_at.to_string())),
                    strings(rows.iter().map(|value| enum_name(&value.assertion_status))),
                    Arc::new(Float32Array::from_iter(rows.iter().map(|value| {
                        value.confidence.map(|confidence| confidence.get())
                    }))),
                    strings(rows.iter().map(|value| value.position.source.to_string())),
                    strings(rows.iter().map(|value| value.position.partition.clone())),
                    Arc::new(UInt64Array::from_iter_values(
                        rows.iter().map(|value| value.position.sequence),
                    )),
                    strings(
                        rows.iter()
                            .map(|value| enum_name(&value.privacy.disposition)),
                    ),
                    strings(
                        rows.iter()
                            .map(|value| enum_name(&value.privacy.sensitivity)),
                    ),
                    strings(rows.iter().map(|value| safe_json(&value.attributes))),
                ],
            )
        },
    )
}

fn write_event_object_links(
    bundle: &NormalizedBundle,
    output_dir: &Path,
    options: &ParquetWriteOptions,
) -> Result<ParquetTableReport, ParquetExportError> {
    let table = "event_object_links";
    let path = output_dir.join("event_object_links.parquet");
    let schema = Arc::new(Schema::new(vec![
        Field::new("event_id", DataType::Utf8, false),
        Field::new("object_id", DataType::Utf8, false),
        Field::new("object_type", DataType::Utf8, false),
        Field::new("qualifier", DataType::Utf8, false),
    ]));
    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    std::fs::create_dir_all(parent)?;
    let named_temp = tempfile::Builder::new()
        .prefix("parquet.")
        .suffix(".tmp")
        .tempfile_in(parent)?;
    let temporary = named_temp.into_temp_path();
    let result = (|| {
        let file = File::create(&temporary)?;
        let properties = writer_properties(options)?;
        let mut writer = ArrowWriter::try_new(file, schema.clone(), Some(properties))?;
        let mut rows =
            Vec::<(String, String, String, String)>::with_capacity(options.row_group_size);
        let mut row_count = 0_u64;
        for event in &bundle.events {
            for link in &event.objects {
                rows.push((
                    event.event_id.to_string(),
                    link.object_id.to_string(),
                    link.object_type.to_string(),
                    link.qualifier.to_string(),
                ));
                row_count += 1;
                if rows.len() == options.row_group_size {
                    writer.write(&event_object_link_batch(schema.clone(), &rows)?)?;
                    rows.clear();
                }
            }
        }
        if !rows.is_empty() {
            writer.write(&event_object_link_batch(schema, &rows)?)?;
        }
        let metadata = writer.finish()?;
        writer.inner_mut().flush()?;
        writer.inner_mut().sync_all()?;
        drop(writer);
        temporary
            .persist(&path)
            .map_err(|e| e.error)?;
        sync_directory(parent)?;
        let file_metadata = std::fs::metadata(&path)?;
        let digest = digest_file(&path)?;
        Ok(ParquetTableReport {
            table: table.to_owned(),
            path: path
                .file_name()
                .and_then(|name| name.to_str())
                .unwrap_or_default()
                .to_owned(),
            row_count,
            row_group_count: metadata.num_row_groups() as u64,
            byte_length: file_metadata.len(),
            sha256: digest,
        })
    })();

    result
}

fn event_object_link_batch(
    schema: Arc<Schema>,
    rows: &[(String, String, String, String)],
) -> Result<RecordBatch, ParquetExportError> {
    RecordBatch::try_new(
        schema,
        vec![
            strings(rows.iter().map(|value| value.0.clone())),
            strings(rows.iter().map(|value| value.1.clone())),
            strings(rows.iter().map(|value| value.2.clone())),
            strings(rows.iter().map(|value| value.3.clone())),
        ],
    )
    .map_err(ParquetExportError::from)
}

fn write_evidence(
    bundle: &NormalizedBundle,
    output_dir: &Path,
    options: &ParquetWriteOptions,
) -> Result<ParquetTableReport, ParquetExportError> {
    let schema = Arc::new(Schema::new(vec![
        Field::new("evidence_id", DataType::Utf8, false),
        Field::new("logical_record_id", DataType::Utf8, false),
        Field::new("revision", DataType::UInt64, false),
        Field::new("source_kind", DataType::Utf8, false),
        Field::new("content_sha256", DataType::Utf8, false),
        Field::new("media_type", DataType::Utf8, false),
        Field::new("byte_length", DataType::UInt64, true),
        Field::new("captured_at", DataType::Utf8, false),
        Field::new("source_time", DataType::Utf8, true),
        Field::new("uri", DataType::Utf8, true),
        Field::new("warc_record_id", DataType::Utf8, true),
        Field::new("publication_disposition", DataType::Utf8, false),
        Field::new("sensitivity", DataType::Utf8, false),
        Field::new("attributes_json", DataType::Utf8, false),
    ]));
    write_table(
        "evidence",
        output_dir.join("evidence.parquet"),
        schema.clone(),
        bundle.evidence.len(),
        options,
        |range| {
            let rows = &bundle.evidence[range];
            RecordBatch::try_new(
                schema.clone(),
                vec![
                    strings(rows.iter().map(|value| value.evidence_id.to_string())),
                    strings(rows.iter().map(|value| value.logical_record_id.to_string())),
                    Arc::new(UInt64Array::from_iter_values(
                        rows.iter().map(|value| value.revision),
                    )),
                    strings(rows.iter().map(|value| value.source_kind.to_string())),
                    strings(rows.iter().map(|value| value.content_sha256.to_string())),
                    strings(rows.iter().map(|value| value.media_type.clone())),
                    Arc::new(UInt64Array::from_iter(
                        rows.iter().map(|value| value.byte_length),
                    )),
                    strings(rows.iter().map(|value| value.captured_at.to_string())),
                    Arc::new(StringArray::from_iter(rows.iter().map(|value| {
                        value
                            .source_time
                            .as_ref()
                            .map(|time| time.timestamp.to_string())
                    }))),
                    Arc::new(StringArray::from_iter(
                        rows.iter().map(|value| value.locator.uri.clone()),
                    )),
                    Arc::new(StringArray::from_iter(
                        rows.iter()
                            .map(|value| value.locator.warc_record_id.clone()),
                    )),
                    strings(
                        rows.iter()
                            .map(|value| enum_name(&value.privacy.disposition)),
                    ),
                    strings(
                        rows.iter()
                            .map(|value| enum_name(&value.privacy.sensitivity)),
                    ),
                    strings(rows.iter().map(|value| safe_json(&value.attributes))),
                ],
            )
        },
    )
}

fn write_objects(
    bundle: &NormalizedBundle,
    output_dir: &Path,
    options: &ParquetWriteOptions,
) -> Result<ParquetTableReport, ParquetExportError> {
    let schema = Arc::new(Schema::new(vec![
        Field::new("object_id", DataType::Utf8, false),
        Field::new("object_type", DataType::Utf8, false),
        Field::new("publication_disposition", DataType::Utf8, false),
        Field::new("sensitivity", DataType::Utf8, false),
        Field::new("attributes_json", DataType::Utf8, false),
    ]));
    write_table(
        "objects",
        output_dir.join("objects.parquet"),
        schema.clone(),
        bundle.objects.len(),
        options,
        |range| {
            let rows = &bundle.objects[range];
            RecordBatch::try_new(
                schema.clone(),
                vec![
                    strings(rows.iter().map(|value| value.object_id.to_string())),
                    strings(rows.iter().map(|value| value.object_type.to_string())),
                    strings(
                        rows.iter()
                            .map(|value| enum_name(&value.privacy.disposition)),
                    ),
                    strings(
                        rows.iter()
                            .map(|value| enum_name(&value.privacy.sensitivity)),
                    ),
                    strings(rows.iter().map(|value| safe_json(&value.attributes))),
                ],
            )
        },
    )
}

fn write_object_links(
    bundle: &NormalizedBundle,
    output_dir: &Path,
    options: &ParquetWriteOptions,
) -> Result<ParquetTableReport, ParquetExportError> {
    let schema = Arc::new(Schema::new(vec![
        Field::new("source_object_id", DataType::Utf8, false),
        Field::new("target_object_id", DataType::Utf8, false),
        Field::new("qualifier", DataType::Utf8, false),
        Field::new("valid_from", DataType::Utf8, true),
        Field::new("valid_to", DataType::Utf8, true),
    ]));
    write_table(
        "object_object_links",
        output_dir.join("object_object_links.parquet"),
        schema.clone(),
        bundle.object_links.len(),
        options,
        |range| {
            let rows = &bundle.object_links[range];
            RecordBatch::try_new(
                schema.clone(),
                vec![
                    strings(rows.iter().map(|value| value.source_object_id.to_string())),
                    strings(rows.iter().map(|value| value.target_object_id.to_string())),
                    strings(rows.iter().map(|value| value.qualifier.to_string())),
                    Arc::new(StringArray::from_iter(rows.iter().map(|value| {
                        value
                            .valid_from
                            .as_ref()
                            .map(|time| time.timestamp.to_string())
                    }))),
                    Arc::new(StringArray::from_iter(rows.iter().map(|value| {
                        value
                            .valid_to
                            .as_ref()
                            .map(|time| time.timestamp.to_string())
                    }))),
                ],
            )
        },
    )
}

fn write_findings(
    bundle: &NormalizedBundle,
    output_dir: &Path,
    options: &ParquetWriteOptions,
) -> Result<ParquetTableReport, ParquetExportError> {
    let schema = Arc::new(Schema::new(vec![
        Field::new("rule_id", DataType::Utf8, false),
        Field::new("layer", DataType::Utf8, false),
        Field::new("severity", DataType::Utf8, false),
        Field::new("message", DataType::Utf8, false),
        Field::new("subject_id", DataType::Utf8, true),
        Field::new("requires_human_review", DataType::Boolean, false),
        Field::new("details_json", DataType::Utf8, false),
    ]));
    write_table(
        "validation_findings",
        output_dir.join("validation_findings.parquet"),
        schema.clone(),
        bundle.findings.len(),
        options,
        |range| {
            let rows = &bundle.findings[range];
            RecordBatch::try_new(
                schema.clone(),
                vec![
                    strings(rows.iter().map(|value| value.rule_id.to_string())),
                    strings(rows.iter().map(|value| enum_name(&value.layer))),
                    strings(rows.iter().map(|value| enum_name(&value.severity))),
                    strings(rows.iter().map(|value| value.message.clone())),
                    Arc::new(StringArray::from_iter(
                        rows.iter()
                            .map(|value| value.subject_id.as_ref().map(ToString::to_string)),
                    )),
                    Arc::new(BooleanArray::from_iter(
                        rows.iter().map(|value| value.requires_human_review),
                    )),
                    strings(rows.iter().map(|value| safe_json(&value.details))),
                ],
            )
        },
    )
}

fn write_table<F>(
    table: &str,
    path: PathBuf,
    schema: Arc<Schema>,
    row_count: usize,
    options: &ParquetWriteOptions,
    mut make_batch: F,
) -> Result<ParquetTableReport, ParquetExportError>
where
    F: FnMut(std::ops::Range<usize>) -> Result<RecordBatch, arrow_schema::ArrowError>,
{
    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    std::fs::create_dir_all(parent)?;
    let named_temp = tempfile::Builder::new()
        .prefix("parquet.")
        .suffix(".tmp")
        .tempfile_in(parent)?;
    let temporary = named_temp.into_temp_path();
    let result = (|| {
        let file = File::create(&temporary)?;
        let properties = writer_properties(options)?;
        let mut writer = ArrowWriter::try_new(file, schema, Some(properties))?;
        for start in (0..row_count).step_by(options.row_group_size) {
            let end = usize::min(start + options.row_group_size, row_count);
            writer.write(&make_batch(start..end)?)?;
        }
        let metadata = writer.finish()?;
        writer.inner_mut().flush()?;
        writer.inner_mut().sync_all()?;
        drop(writer);
        temporary
            .persist(&path)
            .map_err(|e| e.error)?;
        sync_directory(parent)?;
        let file_metadata = std::fs::metadata(&path)?;
        let digest = digest_file(&path)?;
        Ok(ParquetTableReport {
            table: table.to_owned(),
            path: path
                .file_name()
                .and_then(|name| name.to_str())
                .unwrap_or_default()
                .to_owned(),
            row_count: row_count as u64,
            row_group_count: metadata.num_row_groups() as u64,
            byte_length: file_metadata.len(),
            sha256: digest,
        })
    })();

    result
}

fn writer_properties(
    options: &ParquetWriteOptions,
) -> Result<WriterProperties, ParquetExportError> {
    let compression = Compression::ZSTD(ZstdLevel::try_new(options.zstd_level)?);
    Ok(WriterProperties::builder()
        .set_compression(compression)
        .set_max_row_group_row_count(Some(options.row_group_size))
        .build())
}

fn strings(values: impl IntoIterator<Item = String>) -> ArrayRef {
    Arc::new(StringArray::from_iter_values(values))
}

fn enum_name<T: Serialize>(value: &T) -> String {
    serde_json::to_value(value)
        .ok()
        .and_then(|value| value.as_str().map(ToOwned::to_owned))
        .unwrap_or_else(|| "unknown".to_string())
}

fn safe_json<T: Serialize>(value: &T) -> String {
    serde_json::to_string(value).unwrap_or_else(|_| "{}".to_string())
}

fn digest_file(path: &Path) -> Result<Sha256Digest, ParquetExportError> {
    let file = File::open(path)?;
    let mut reader = BufReader::new(file);
    let mut digest = Sha256::new();
    let mut buffer = [0_u8; 1024 * 1024];
    loop {
        let read = reader.read(&mut buffer)?;
        if read == 0 {
            break;
        }
        digest.update(&buffer[..read]);
    }
    let bytes = digest.finalize();
    let mut encoded = String::with_capacity(64);
    for byte in bytes {
        use std::fmt::Write as _;
        let _ = write!(&mut encoded, "{byte:02x}");
    }
    Ok(Sha256Digest::parse(encoded)?)
}

fn write_json_atomic(path: PathBuf, value: &impl Serialize) -> Result<(), ParquetExportError> {
    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    std::fs::create_dir_all(parent)?;
    let named_temp = tempfile::Builder::new()
        .prefix("json.")
        .suffix(".tmp")
        .tempfile_in(parent)?;
    let temporary = named_temp.into_temp_path();
    let bytes = serde_json::to_vec_pretty(value)?;
    let mut file = File::create(&temporary)?;
    file.write_all(&bytes)?;
    file.write_all(b"\n")?;
    file.flush()?;
    file.sync_all()?;
    drop(file);
    temporary
        .persist(&path)
        .map_err(|e| e.error)?;
    sync_directory(parent)?;
    Ok(())
}

#[cfg(unix)]
fn sync_directory(path: &Path) -> std::io::Result<()> {
    File::open(path)?.sync_all()
}

#[cfg(not(unix))]
fn sync_directory(_path: &Path) -> std::io::Result<()> {
    Ok(())
}
