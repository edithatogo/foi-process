use std::time::Instant;

use foi_process::*;
use serde::Serialize;

#[derive(Debug, Serialize)]
struct BenchmarkResult {
    cases: usize,
    events_per_case: usize,
    input_revisions: usize,
    active_cases: u64,
    active_events: u64,
    elapsed_ms: u128,
    revisions_per_second: f64,
}

fn main() -> anyhow::Result<()> {
    let mut arguments = std::env::args().skip(1);
    let cases = arguments
        .next()
        .as_deref()
        .unwrap_or("200000")
        .parse::<usize>()?;
    let events_per_case = arguments
        .next()
        .as_deref()
        .unwrap_or("1")
        .parse::<usize>()?;
    let correction_every = arguments
        .next()
        .as_deref()
        .unwrap_or("100")
        .parse::<usize>()?;

    let started = Instant::now();
    let mut summary = RevisableProcessSummary::default();
    let mut revisions = 0_usize;
    for case_index in 0..cases {
        for event_index in 0..events_per_case {
            summary.apply_event(make_event(case_index, event_index, 1, false)?);
            revisions += 1;
            if correction_every > 0
                && (case_index * events_per_case + event_index) % correction_every == 0
            {
                summary.apply_event(make_event(case_index, event_index, 2, false)?);
                revisions += 1;
            }
        }
    }
    let snapshot = summary.snapshot();
    let elapsed = started.elapsed();
    let seconds = elapsed.as_secs_f64().max(f64::EPSILON);
    let result = BenchmarkResult {
        cases,
        events_per_case,
        input_revisions: revisions,
        active_cases: snapshot.case_count,
        active_events: snapshot.active_event_count,
        elapsed_ms: elapsed.as_millis(),
        revisions_per_second: revisions as f64 / seconds,
    };
    serde_json::to_writer_pretty(std::io::stdout().lock(), &result)?;
    println!();
    Ok(())
}

fn make_event(
    case_index: usize,
    event_index: usize,
    revision: u64,
    retract: bool,
) -> anyhow::Result<ProcessEvent> {
    let case_id = StableId::parse(format!("urn:foi-process:bench:case:{case_index}"))?;
    let logical_event_id = StableId::parse(format!(
        "urn:foi-process:bench:case:{case_index}:event:{event_index}"
    ))?;
    let event_id = StableId::parse(format!(
        "urn:foi-process:bench:case:{case_index}:event:{event_index}:revision:{revision}"
    ))?;
    let second = event_index % 60;
    let minute = (event_index / 60) % 60;
    let timestamp = Timestamp::parse(format!("2026-01-01T00:{minute:02}:{second:02}Z"))?;
    Ok(ProcessEvent {
        schema_version: CONTRACT_VERSION.to_string(),
        event_id,
        logical_event_id,
        revision,
        operation: if retract {
            EventOperation::Retract
        } else {
            EventOperation::Upsert
        },
        site: StableId::parse("urn:alaveteli:site:fyi.org.nz")?,
        jurisdiction: TermId::parse("urn:jurisdiction:nz")?,
        case_id,
        activity: TermId::parse(format!("foio:BenchActivity{}", event_index % 8))?,
        event_time: Some(TemporalInstant::exact(timestamp.clone())),
        observed_at: timestamp.clone(),
        captured_at: timestamp.clone(),
        processed_at: timestamp,
        position: StreamPosition {
            source: StableId::parse("urn:foi-process:bench:source")?,
            partition: "bench".to_string(),
            sequence: (case_index * 1_000 + event_index) as u64 + revision,
        },
        assertion_status: AssertionStatus::Observed,
        confidence: None,
        objects: Vec::new(),
        evidence: Vec::new(),
        document_signal_ids: Vec::new(),
        rule_result_ids: Vec::new(),
        supersedes_event_id: None,
        retracts_event_id: None,
        correlation_id: None,
        causation_id: None,
        provenance: Provenance {
            producer: StableId::parse("urn:foi-process:bench")?,
            producer_version: env!("CARGO_PKG_VERSION").to_string(),
            software_commit: None,
            run_id: None,
            input_ids: Vec::new(),
            parameters: Default::default(),
        },
        privacy: PrivacyAssessment::default(),
        attributes: Default::default(),
    })
}
