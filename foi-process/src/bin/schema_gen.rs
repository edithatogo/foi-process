use std::{
    fs,
    path::{Path, PathBuf},
};

use anyhow::{Context, Result};
use clap::Parser;
use foi_process::*;
use schemars::schema_for;

#[derive(Debug, Parser)]
struct Args {
    /// Destination directory for generated JSON Schema snapshots.
    #[arg(default_value = "schemas/generated")]
    output: PathBuf,
}

fn main() -> Result<()> {
    let args = Args::parse();
    fs::create_dir_all(&args.output)?;
    write(
        &args.output,
        "evidence-record.schema.json",
        &schema_for!(EvidenceRecord),
    )?;
    write(
        &args.output,
        "evidence-delta.schema.json",
        &schema_for!(EvidenceDelta),
    )?;
    write(
        &args.output,
        "process-event.schema.json",
        &schema_for!(ProcessEvent),
    )?;
    write(
        &args.output,
        "document-bundle.schema.json",
        &schema_for!(DocumentBundle),
    )?;
    write(
        &args.output,
        "document-signal.schema.json",
        &schema_for!(DocumentSignal),
    )?;
    write(
        &args.output,
        "normalized-bundle.schema.json",
        &schema_for!(NormalizedBundle),
    )?;
    write(
        &args.output,
        "stream-checkpoint.schema.json",
        &schema_for!(StreamCheckpoint),
    )?;
    write(
        &args.output,
        "replay-snapshot.schema.json",
        &schema_for!(ReplaySnapshot),
    )?;
    write(
        &args.output,
        "conformance-trace.schema.json",
        &schema_for!(ConformanceTrace),
    )?;
    write(
        &args.output,
        "human-review-record.schema.json",
        &schema_for!(HumanReviewRecord),
    )?;
    write(
        &args.output,
        "mining-run-manifest.schema.json",
        &schema_for!(MiningRunManifest),
    )?;
    write(
        &args.output,
        "public-projection.schema.json",
        &schema_for!(PublicProjection),
    )?;
    write(
        &args.output,
        "dashboard-summary.schema.json",
        &schema_for!(DashboardSummary),
    )?;
    write(
        &args.output,
        "ocel-projection.schema.json",
        &schema_for!(OcelProjection),
    )?;
    Ok(())
}

fn write<T: serde::Serialize>(directory: &Path, name: &str, value: &T) -> Result<()> {
    let path = directory.join(name);
    let bytes = serde_json::to_vec_pretty(value)?;
    fs::write(&path, bytes).with_context(|| format!("failed to write {}", path.display()))
}
