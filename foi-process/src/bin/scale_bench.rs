use std::time::Instant;

use foi_process::*;
use serde::Serialize;

#[derive(Debug, Serialize)]
struct BenchmarkResult {
    schema_version: &'static str,
    cases: usize,
    events_per_case: usize,
    input_revisions: usize,
    corrections: usize,
    retractions: usize,
    active_cases: u64,
    active_events: u64,
    elapsed_seconds: f64,
    revisions_per_second: f64,
    peak_resident_bytes: Option<u64>,
    output_json_bytes: usize,
    output_sha256: String,
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
        .unwrap_or("5")
        .parse::<usize>()?;
    let correction_every = arguments
        .next()
        .as_deref()
        .unwrap_or("100")
        .parse::<usize>()?;
    let retraction_every = arguments
        .next()
        .as_deref()
        .unwrap_or("1000")
        .parse::<usize>()?;

    let started = Instant::now();
    let mut summary = RevisableProcessSummary::default();
    let mut revisions = 0_usize;
    let mut corrections = 0_usize;
    let mut retractions = 0_usize;
    for case_index in 0..cases {
        for event_index in 0..events_per_case {
            summary.apply_event(make_event(case_index, event_index, 1, false)?);
            revisions += 1;
            let global_event_index = case_index * events_per_case + event_index;
            if correction_every > 0 && global_event_index % correction_every == 0 {
                summary.apply_event(make_event(case_index, event_index, 2, false)?);
                revisions += 1;
                corrections += 1;
            }
            if retraction_every > 0 && global_event_index % retraction_every == 0 {
                summary.apply_event(make_event(case_index, event_index, 3, true)?);
                revisions += 1;
                retractions += 1;
            }
        }
    }
    let snapshot = summary.snapshot();
    let elapsed = started.elapsed();
    let seconds = elapsed.as_secs_f64().max(f64::EPSILON);
    let output = canonical_json_bytes(&snapshot)?;
    let result = BenchmarkResult {
        schema_version: "1.0.0",
        cases,
        events_per_case,
        input_revisions: revisions,
        corrections,
        retractions,
        active_cases: snapshot.case_count,
        active_events: snapshot.active_event_count,
        elapsed_seconds: seconds,
        revisions_per_second: revisions as f64 / seconds,
        peak_resident_bytes: peak_resident_bytes(),
        output_json_bytes: output.len(),
        output_sha256: Sha256Digest::of(&output).to_string(),
    };
    serde_json::to_writer_pretty(std::io::stdout().lock(), &result)?;
    println!();
    Ok(())
}

#[cfg(target_os = "linux")]
fn peak_resident_bytes() -> Option<u64> {
    let status = std::fs::read_to_string("/proc/self/status").ok()?;
    let line = status.lines().find(|line| line.starts_with("VmHWM:"))?;
    line.split_whitespace()
        .nth(1)?
        .parse::<u64>()
        .ok()
        .map(|kb| kb * 1024)
}

#[cfg(windows)]
fn peak_resident_bytes() -> Option<u64> {
    use std::ffi::c_void;

    #[repr(C)]
    struct ProcessMemoryCounters {
        cb: u32,
        page_fault_count: u32,
        peak_working_set_size: usize,
        working_set_size: usize,
        quota_peak_paged_pool_usage: usize,
        quota_paged_pool_usage: usize,
        quota_peak_non_paged_pool_usage: usize,
        quota_non_paged_pool_usage: usize,
        pagefile_usage: usize,
        peak_pagefile_usage: usize,
    }

    #[link(name = "kernel32")]
    extern "system" {
        fn GetCurrentProcess() -> *mut c_void;
    }
    #[link(name = "psapi")]
    extern "system" {
        fn GetProcessMemoryInfo(
            process: *mut c_void,
            counters: *mut ProcessMemoryCounters,
            size: u32,
        ) -> i32;
    }

    let mut counters = ProcessMemoryCounters {
        cb: std::mem::size_of::<ProcessMemoryCounters>() as u32,
        page_fault_count: 0,
        peak_working_set_size: 0,
        working_set_size: 0,
        quota_peak_paged_pool_usage: 0,
        quota_paged_pool_usage: 0,
        quota_peak_non_paged_pool_usage: 0,
        quota_non_paged_pool_usage: 0,
        pagefile_usage: 0,
        peak_pagefile_usage: 0,
    };
    // SAFETY: both functions are stable Win32 APIs and `counters` has the documented layout/size.
    let success = unsafe { GetProcessMemoryInfo(GetCurrentProcess(), &mut counters, counters.cb) };
    (success != 0).then_some(counters.peak_working_set_size as u64)
}

#[cfg(not(any(target_os = "linux", windows)))]
fn peak_resident_bytes() -> Option<u64> {
    None
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
