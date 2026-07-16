use std::{
    fs::{File, OpenOptions},
    io::{BufRead, BufReader, BufWriter, Write},
    path::{Path, PathBuf},
};

use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use foi_process::*;
use serde::{de::DeserializeOwned, Serialize};

#[derive(Debug, Parser)]
#[command(
    name = "foi-process",
    version,
    about = "Rust-first FOI event replay and process-mining integration"
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    /// Validate a ProcessEvent JSON document.
    ValidateEvent { path: PathBuf },
    /// Validate a NormalizedBundle JSON document, including reference integrity.
    ValidateBundle { path: PathBuf },
    /// Convert a current fyi-archive manifest snapshot into deterministic EvidenceDelta NDJSON.
    FyiArchiveManifestToDeltas {
        input: PathBuf,
        output: PathBuf,
        #[arg(long)]
        captured_at: String,
    },
    /// Verify fyi-cli derived-store attachment bytes and emit EvidenceDelta NDJSON.
    FyiArchiveDerivedStoreToDeltas {
        #[arg(long)]
        input: PathBuf,
        #[arg(long)]
        derived_root: PathBuf,
        #[arg(long)]
        output: PathBuf,
        #[arg(long)]
        captured_at: String,
        #[arg(long)]
        report: Option<PathBuf>,
    },
    /// Replay EvidenceDelta NDJSON through the deterministic normalizer.
    Replay {
        input: PathBuf,
        output: PathBuf,
        #[arg(long)]
        profile: Option<PathBuf>,
        #[arg(long)]
        processed_at: String,
    },
    /// Produce only the normalized bundle from EvidenceDelta NDJSON.
    NormalizeDeltas {
        input: PathBuf,
        output: PathBuf,
        #[arg(long)]
        profile: Option<PathBuf>,
        #[arg(long)]
        processed_at: String,
    },
    /// Replay EvidenceDelta NDJSON and stream normalized tables to an output directory.
    ReplayStream {
        input: PathBuf,
        output_dir: PathBuf,
        #[arg(long)]
        profile: Option<PathBuf>,
        #[arg(long)]
        processed_at: String,
        #[arg(long)]
        state_in: Option<PathBuf>,
        #[arg(long)]
        state_out: Option<PathBuf>,
    },
    /// Build a compact, revision-aware dashboard summary from ProcessEvent NDJSON.
    Summarize { input: PathBuf, output: PathBuf },
    /// Project a bundle into portable OCEL table rows.
    ProjectOcel { input: PathBuf, output: PathBuf },
    /// Produce a privacy-safe dashboard projection.
    ProjectPublic {
        input: PathBuf,
        output: PathBuf,
        #[arg(long)]
        policy: Option<PathBuf>,
    },
    /// Write bounded Arrow/Parquet tables. Requires --features parquet.
    #[cfg(feature = "parquet")]
    WriteParquet {
        input: PathBuf,
        output_dir: PathBuf,
        #[arg(long, default_value_t = 65_536)]
        row_group_size: usize,
        #[arg(long, default_value_t = 3)]
        zstd_level: i32,
    },
    /// Compute a canonical SHA-256 content identifier for a JSON document.
    ContentId { namespace: String, path: PathBuf },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Command::ValidateEvent { path } => {
            let event: ProcessEvent = read_json(path)?;
            write_json_stdout(&validate_event(&event))?;
        }
        Command::ValidateBundle { path } => {
            let bundle: NormalizedBundle = read_json(path)?;
            write_json_stdout(&validate_bundle(&bundle))?;
        }
        Command::FyiArchiveManifestToDeltas {
            input,
            output,
            captured_at,
        } => {
            let manifest: FyiArchiveManifest = read_json(input)?;
            let captured_at = Timestamp::parse(captured_at)?;
            let deltas = fyi_archive_manifest_to_deltas(manifest, captured_at)?;
            write_ndjson_file(output, &deltas)?;
        }
        Command::FyiArchiveDerivedStoreToDeltas {
            input,
            derived_root,
            output,
            captured_at,
            report,
        } => {
            let manifest_input = input.display().to_string();
            let derived_store_root = derived_root.display().to_string();
            let manifest: FyiArchiveManifest = read_json(input)?;
            let attachment_count = manifest
                .requests
                .iter()
                .map(|request| request.attachments.len())
                .sum::<usize>();
            let captured_at = Timestamp::parse(captured_at)?;
            let retriever = FyiArchiveFilesystemRetriever::new(derived_root);
            let deltas =
                fyi_archive_manifest_to_deltas_with_retriever(manifest, captured_at, &retriever)?;
            write_ndjson_file(output, &deltas)?;
            if let Some(report) = report {
                write_json(
                    report,
                    &AttachmentVerificationReport {
                        schema: "foi-process/fyi-archive-attachment-verification/v1",
                        status: "verified",
                        manifest_input,
                        derived_store_root,
                        attachment_count,
                        delta_count: deltas.len(),
                        raw_bytes_written: false,
                    },
                )?;
            }
        }
        Command::Replay {
            input,
            output,
            profile,
            processed_at,
        } => {
            let (outcomes, bundle) = replay_file(input, profile, processed_at)?;
            write_json(output, &ReplayExport { outcomes, bundle })?;
        }
        Command::NormalizeDeltas {
            input,
            output,
            profile,
            processed_at,
        } => {
            let (_, bundle) = replay_file(input, profile, processed_at)?;
            write_json(output, &bundle)?;
        }
        Command::ReplayStream {
            input,
            output_dir,
            profile,
            processed_at,
            state_in,
            state_out,
        } => {
            let profile = load_profile(profile)?;
            let processed_at = Timestamp::parse(processed_at)?;
            std::fs::create_dir_all(&output_dir)?;
            let normalizer = DeterministicNormalizer::new(profile, env!("CARGO_PKG_VERSION"));
            let resuming = state_in.is_some();
            let mut replay = match state_in {
                Some(path) => ReplayEngine::from_snapshot(read_json(path)?)?,
                None => ReplayEngine::default(),
            };
            let mut writers = StreamWriters::new(&output_dir, resuming)?;
            for_each_ndjson(input, |delta: EvidenceDelta| {
                let quarantined_delta = delta.clone();
                let (outcome, bundle) = replay.apply(delta, processed_at.clone(), &normalizer);
                writers.write_outcome(&outcome)?;
                if !matches!(
                    outcome.status,
                    ApplyStatus::Accepted | ApplyStatus::Duplicate
                ) {
                    writers.write_quarantine(&QuarantinedDelta {
                        outcome: outcome.clone(),
                        delta: quarantined_delta,
                    })?;
                }
                writers.write_bundle(&bundle)
            })?;
            writers.flush_and_sync()?;
            let consumer = StableId::parse("urn:foi-process:consumer:cli-stream")?;
            let checkpoint = replay.checkpoint(consumer.clone(), processed_at.clone())?;
            let snapshot = replay.snapshot(consumer, processed_at)?;
            write_json(
                state_out.unwrap_or_else(|| output_dir.join("replay-snapshot.json")),
                &snapshot,
            )?;
            write_json(output_dir.join("checkpoint.json"), &checkpoint)?;
        }
        Command::Summarize { input, output } => {
            let mut summary = RevisableProcessSummary::default();
            for_each_ndjson(input, |event: ProcessEvent| {
                summary.apply_event(event);
                Ok(())
            })?;
            write_json(output, &summary.snapshot())?;
        }
        Command::ProjectOcel { input, output } => {
            let bundle: NormalizedBundle = read_json(input)?;
            write_json(output, &project_ocel(&bundle))?;
        }
        Command::ProjectPublic {
            input,
            output,
            policy,
        } => {
            let bundle: NormalizedBundle = read_json(input)?;
            let policy = match policy {
                Some(path) => read_json(path)?,
                None => PublicationPolicy::dashboard_default(),
            };
            write_json(output, &project_public(&bundle, &policy))?;
        }
        #[cfg(feature = "parquet")]
        Command::WriteParquet {
            input,
            output_dir,
            row_group_size,
            zstd_level,
        } => {
            let bundle: NormalizedBundle = read_json(input)?;
            let report = write_normalized_bundle_parquet(
                &bundle,
                output_dir,
                ParquetWriteOptions {
                    row_group_size,
                    zstd_level,
                },
            )?;
            write_json_stdout(&report)?;
        }
        Command::ContentId { namespace, path } => {
            let value: serde_json::Value = read_json(path)?;
            println!("{}", content_id(&namespace, &value)?);
        }
    }
    Ok(())
}

#[derive(Debug, Serialize)]
struct AttachmentVerificationReport {
    schema: &'static str,
    status: &'static str,
    manifest_input: String,
    derived_store_root: String,
    attachment_count: usize,
    delta_count: usize,
    raw_bytes_written: bool,
}

fn load_profile(path: Option<PathBuf>) -> Result<MappingProfile> {
    match path {
        Some(path) => read_json(path),
        None => Ok(MappingProfile::fyi_minimal()),
    }
}

fn replay_file(
    input: PathBuf,
    profile: Option<PathBuf>,
    processed_at: String,
) -> Result<(Vec<ApplyOutcome>, NormalizedBundle)> {
    let profile = load_profile(profile)?;
    let processed_at = Timestamp::parse(processed_at)?;
    let normalizer = DeterministicNormalizer::new(profile, env!("CARGO_PKG_VERSION"));
    let deltas: Vec<EvidenceDelta> = read_ndjson(input)?;
    let mut replay = ReplayEngine::default();
    let mut bundle = NormalizedBundle::default();
    let mut outcomes = Vec::new();
    for delta in deltas {
        let (outcome, delta_bundle) = replay.apply(delta, processed_at.clone(), &normalizer);
        outcomes.push(outcome);
        bundle.extend(delta_bundle);
    }
    bundle.checkpoint = Some(replay.checkpoint(
        StableId::parse("urn:foi-process:consumer:cli")?,
        processed_at,
    )?);
    Ok((outcomes, bundle))
}

#[derive(Debug, serde::Serialize)]
struct ReplayExport {
    outcomes: Vec<ApplyOutcome>,
    bundle: NormalizedBundle,
}

#[derive(Debug, serde::Serialize)]
struct QuarantinedDelta {
    outcome: ApplyOutcome,
    delta: EvidenceDelta,
}

fn read_json<T: DeserializeOwned>(path: PathBuf) -> Result<T> {
    let file = File::open(&path).with_context(|| format!("failed to open {}", path.display()))?;
    serde_json::from_reader(BufReader::new(file))
        .with_context(|| format!("invalid JSON in {}", path.display()))
}

fn read_ndjson<T: DeserializeOwned>(path: PathBuf) -> Result<Vec<T>> {
    let reader = ndjson_reader(&path)?;
    let mut values = Vec::new();
    for (index, line) in reader.lines().enumerate() {
        let line = line.with_context(|| format!("failed to read line {}", index + 1))?;
        if line.trim().is_empty() {
            continue;
        }
        values.push(
            serde_json::from_str(&line)
                .with_context(|| format!("invalid NDJSON at line {}", index + 1))?,
        );
    }
    Ok(values)
}

fn for_each_ndjson<T, F>(path: PathBuf, mut apply: F) -> Result<()>
where
    T: DeserializeOwned,
    F: FnMut(T) -> Result<()>,
{
    let reader = ndjson_reader(&path)?;
    for (index, line) in reader.lines().enumerate() {
        let line = line.with_context(|| format!("failed to read line {}", index + 1))?;
        if line.trim().is_empty() {
            continue;
        }
        let value = serde_json::from_str(&line)
            .with_context(|| format!("invalid NDJSON at line {}", index + 1))?;
        apply(value)?;
    }
    Ok(())
}

fn ndjson_reader(path: &Path) -> Result<Box<dyn BufRead>> {
    if path == Path::new("-") {
        return Ok(Box::new(BufReader::new(std::io::stdin())));
    }
    let file = File::open(path).with_context(|| format!("failed to open {}", path.display()))?;
    Ok(Box::new(BufReader::new(file)))
}

fn write_ndjson_file<T: Serialize>(path: PathBuf, values: &[T]) -> Result<()> {
    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    std::fs::create_dir_all(parent)?;
    let file_name = path
        .file_name()
        .and_then(|value| value.to_str())
        .context("output path must have a UTF-8 file name")?;
    let temporary = parent.join(format!(".{file_name}.{}.tmp", std::process::id()));
    let result = (|| -> Result<()> {
        let file = File::create(&temporary)?;
        let mut writer = BufWriter::new(file);
        for value in values {
            write_ndjson_value(&mut writer, value)?;
        }
        writer.flush()?;
        writer.get_ref().sync_all()?;
        drop(writer);
        std::fs::rename(&temporary, &path)?;
        sync_parent_directory(parent)
    })();
    if result.is_err() {
        let _ = std::fs::remove_file(&temporary);
    }
    result
}

struct StreamWriters {
    outcomes: BufWriter<File>,
    events: BufWriter<File>,
    evidence: BufWriter<File>,
    objects: BufWriter<File>,
    object_links: BufWriter<File>,
    object_changes: BufWriter<File>,
    document_signals: BufWriter<File>,
    findings: BufWriter<File>,
    human_reviews: BufWriter<File>,
    quarantine: BufWriter<File>,
}

impl StreamWriters {
    fn new(directory: &Path, resuming: bool) -> Result<Self> {
        Ok(Self {
            outcomes: BufWriter::new(open_journal(directory.join("outcomes.ndjson"), resuming)?),
            events: BufWriter::new(open_journal(directory.join("events.ndjson"), resuming)?),
            evidence: BufWriter::new(open_journal(directory.join("evidence.ndjson"), resuming)?),
            objects: BufWriter::new(open_journal(directory.join("objects.ndjson"), resuming)?),
            object_links: BufWriter::new(open_journal(
                directory.join("object-links.ndjson"),
                resuming,
            )?),
            object_changes: BufWriter::new(open_journal(
                directory.join("object-changes.ndjson"),
                resuming,
            )?),
            document_signals: BufWriter::new(open_journal(
                directory.join("document-signals.ndjson"),
                resuming,
            )?),
            findings: BufWriter::new(open_journal(directory.join("findings.ndjson"), resuming)?),
            human_reviews: BufWriter::new(open_journal(
                directory.join("human-reviews.ndjson"),
                resuming,
            )?),
            quarantine: BufWriter::new(open_journal(
                directory.join("quarantine.ndjson"),
                resuming,
            )?),
        })
    }

    fn write_outcome(&mut self, outcome: &ApplyOutcome) -> Result<()> {
        write_ndjson_value(&mut self.outcomes, outcome)
    }

    fn write_quarantine(&mut self, value: &QuarantinedDelta) -> Result<()> {
        write_ndjson_value(&mut self.quarantine, value)
    }

    fn write_bundle(&mut self, bundle: &NormalizedBundle) -> Result<()> {
        for value in &bundle.events {
            write_ndjson_value(&mut self.events, value)?;
        }
        for value in &bundle.evidence {
            write_ndjson_value(&mut self.evidence, value)?;
        }
        for value in &bundle.objects {
            write_ndjson_value(&mut self.objects, value)?;
        }
        for value in &bundle.object_links {
            write_ndjson_value(&mut self.object_links, value)?;
        }
        for value in &bundle.object_changes {
            write_ndjson_value(&mut self.object_changes, value)?;
        }
        for value in &bundle.document_signals {
            write_ndjson_value(&mut self.document_signals, value)?;
        }
        for value in &bundle.findings {
            write_ndjson_value(&mut self.findings, value)?;
        }
        for value in &bundle.human_reviews {
            write_ndjson_value(&mut self.human_reviews, value)?;
        }
        Ok(())
    }

    fn flush_and_sync(&mut self) -> Result<()> {
        sync_writer(&mut self.outcomes)?;
        sync_writer(&mut self.events)?;
        sync_writer(&mut self.evidence)?;
        sync_writer(&mut self.objects)?;
        sync_writer(&mut self.object_links)?;
        sync_writer(&mut self.object_changes)?;
        sync_writer(&mut self.document_signals)?;
        sync_writer(&mut self.findings)?;
        sync_writer(&mut self.human_reviews)?;
        sync_writer(&mut self.quarantine)?;
        Ok(())
    }
}

fn open_journal(path: PathBuf, resuming: bool) -> Result<File> {
    let mut options = OpenOptions::new();
    options.write(true);
    if resuming {
        options.create(true).append(true);
    } else {
        options.create_new(true);
    }
    options
        .open(&path)
        .with_context(|| format!("failed to open journal {}", path.display()))
}

fn sync_writer(writer: &mut BufWriter<File>) -> Result<()> {
    writer.flush()?;
    writer.get_ref().sync_all()?;
    Ok(())
}

fn write_ndjson_value<T: Serialize>(writer: &mut BufWriter<File>, value: &T) -> Result<()> {
    serde_json::to_writer(&mut *writer, value)?;
    writer.write_all(b"\n")?;
    Ok(())
}

fn write_json<T: Serialize>(path: PathBuf, value: &T) -> Result<()> {
    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    std::fs::create_dir_all(parent)?;
    let file_name = path
        .file_name()
        .and_then(|value| value.to_str())
        .context("output path must have a UTF-8 file name")?;
    let temporary = parent.join(format!(".{file_name}.{}.tmp", std::process::id()));
    let result = (|| -> Result<()> {
        let file = File::create(&temporary)
            .with_context(|| format!("failed to create {}", temporary.display()))?;
        let mut writer = BufWriter::new(file);
        serde_json::to_writer_pretty(&mut writer, value)?;
        writer.write_all(b"\n")?;
        writer.flush()?;
        writer.get_ref().sync_all()?;
        drop(writer);
        std::fs::rename(&temporary, &path).with_context(|| {
            format!(
                "failed to atomically replace {} with {}",
                path.display(),
                temporary.display()
            )
        })?;
        sync_parent_directory(parent)
    })();
    if result.is_err() {
        let _ = std::fs::remove_file(&temporary);
    }
    result
}

#[cfg(unix)]
fn sync_parent_directory(path: &Path) -> Result<()> {
    File::open(path)?.sync_all()?;
    Ok(())
}

#[cfg(not(unix))]
fn sync_parent_directory(_path: &Path) -> Result<()> {
    Ok(())
}

fn write_json_stdout<T: Serialize>(value: &T) -> Result<()> {
    let stdout = std::io::stdout();
    let mut writer = BufWriter::new(stdout.lock());
    serde_json::to_writer_pretty(&mut writer, value)?;
    writer.write_all(b"\n")?;
    Ok(())
}
