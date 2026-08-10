//! Idempotent replay with revision, gap, conflict, supersession, and retraction handling.

use std::collections::{BTreeMap, BTreeSet};
use std::sync::LazyLock;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{contracts::*, normalize::DeterministicNormalizer, validation::validate_delta};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ApplyStatus {
    Accepted,
    Duplicate,
    Stale,
    GapDetected,
    PositionGap,
    PositionRegression,
    Conflict,
    Invalid,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ApplyOutcome {
    pub delta_id: StableId,
    pub status: ApplyStatus,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub emitted_event_ids: Vec<StableId>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub findings: Vec<ValidationFinding>,
}

#[derive(Debug, Clone)]
struct RecordState {
    revision: u64,
    current_digest: Option<Sha256Digest>,
    last_delta_id: StableId,
    last_event_id: Option<StableId>,
}

#[derive(Debug, Error)]
pub enum ReplaySnapshotError {
    #[error("failed to canonicalize replay snapshot state: {0}")]
    Canonicalization(#[from] serde_json::Error),
    #[error("replay snapshot state hash does not match its records and partitions")]
    StateHashMismatch,
    #[error("replay snapshot contains duplicate logical record {0}")]
    DuplicateRecord(StableId),
    #[error("replay snapshot contains duplicate stream partition {stream_source}:{partition}")]
    DuplicatePartition {
        stream_source: StableId,
        partition: String,
    },
}

#[derive(Debug, Default)]
pub struct ReplayEngine {
    seen_delta_ids: BTreeSet<StableId>,
    records: BTreeMap<StableId, RecordState>,
    positions: BTreeMap<(StableId, String), u64>,
}

static RULE_REVISION_GAP: LazyLock<TermId> =
    LazyLock::new(|| TermId::parse("foip:RevisionGap").unwrap());
static RULE_INITIAL_REVISION_NOT_ONE: LazyLock<TermId> =
    LazyLock::new(|| TermId::parse("foip:InitialRevisionNotOne").unwrap());
static RULE_STREAM_POSITION_CONFLICT: LazyLock<TermId> =
    LazyLock::new(|| TermId::parse("foip:StreamPositionConflict").unwrap());
static RULE_STREAM_POSITION_REGRESSION: LazyLock<TermId> =
    LazyLock::new(|| TermId::parse("foip:StreamPositionRegression").unwrap());
static RULE_STREAM_POSITION_GAP: LazyLock<TermId> =
    LazyLock::new(|| TermId::parse("foip:StreamPositionGap").unwrap());

impl ReplayEngine {
    pub fn apply(
        &mut self,
        delta: EvidenceDelta,
        processed_at: Timestamp,
        normalizer: &DeterministicNormalizer,
    ) -> (ApplyOutcome, NormalizedBundle) {
        let mut findings = validate_delta(&delta);
        if findings
            .iter()
            .any(|finding| finding.severity >= Severity::Error)
        {
            return (
                ApplyOutcome {
                    delta_id: delta.delta_id,
                    status: ApplyStatus::Invalid,
                    emitted_event_ids: Vec::new(),
                    findings,
                },
                NormalizedBundle::default(),
            );
        }

        if self.seen_delta_ids.contains(&delta.delta_id) {
            return (
                ApplyOutcome {
                    delta_id: delta.delta_id,
                    status: ApplyStatus::Duplicate,
                    emitted_event_ids: Vec::new(),
                    findings,
                },
                NormalizedBundle::default(),
            );
        }

        if let Some(current) = self.records.get(&delta.logical_record_id) {
            if delta.revision < current.revision {
                return (
                    ApplyOutcome {
                        delta_id: delta.delta_id,
                        status: ApplyStatus::Stale,
                        emitted_event_ids: Vec::new(),
                        findings,
                    },
                    NormalizedBundle::default(),
                );
            }
            if delta.revision == current.revision {
                let status = if delta.current_content_sha256 == current.current_digest {
                    ApplyStatus::Duplicate
                } else {
                    ApplyStatus::Conflict
                };
                return (
                    ApplyOutcome {
                        delta_id: delta.delta_id,
                        status,
                        emitted_event_ids: Vec::new(),
                        findings,
                    },
                    NormalizedBundle::default(),
                );
            }
            if delta.revision > current.revision.saturating_add(1) {
                findings.push(ValidationFinding {
                    rule_id: RULE_REVISION_GAP.clone(),
                    layer: FindingLayer::DataQuality,
                    severity: Severity::ReviewNeeded,
                    message: format!(
                        "Expected revision {}, received {}",
                        current.revision + 1,
                        delta.revision
                    ),
                    subject_id: Some(delta.logical_record_id.clone()),
                    evidence: Vec::new(),
                    requires_human_review: true,
                    details: BTreeMap::new(),
                });
                return (
                    ApplyOutcome {
                        delta_id: delta.delta_id,
                        status: ApplyStatus::GapDetected,
                        emitted_event_ids: Vec::new(),
                        findings,
                    },
                    NormalizedBundle::default(),
                );
            }
        } else if delta.revision != 1 {
            findings.push(ValidationFinding {
                rule_id: RULE_INITIAL_REVISION_NOT_ONE.clone(),
                layer: FindingLayer::DataQuality,
                severity: Severity::ReviewNeeded,
                message: format!(
                    "First observed revision is {} rather than 1",
                    delta.revision
                ),
                subject_id: Some(delta.logical_record_id.clone()),
                evidence: Vec::new(),
                requires_human_review: true,
                details: BTreeMap::new(),
            });
        }

        let position_key = (
            delta.position.source.clone(),
            delta.position.partition.clone(),
        );
        if let Some(previous_sequence) = self.positions.get(&position_key).copied() {
            if delta.position.sequence == previous_sequence {
                findings.push(ValidationFinding {
                    rule_id: RULE_STREAM_POSITION_CONFLICT.clone(),
                    layer: FindingLayer::DataQuality,
                    severity: Severity::Error,
                    message: format!(
                        "Stream position {}:{}:{} was reused by a different delta",
                        delta.position.source, delta.position.partition, delta.position.sequence
                    ),
                    subject_id: Some(delta.delta_id.clone()),
                    evidence: Vec::new(),
                    requires_human_review: true,
                    details: BTreeMap::new(),
                });
                return (
                    ApplyOutcome {
                        delta_id: delta.delta_id,
                        status: ApplyStatus::Conflict,
                        emitted_event_ids: Vec::new(),
                        findings,
                    },
                    NormalizedBundle::default(),
                );
            }
            if delta.position.sequence < previous_sequence {
                findings.push(ValidationFinding {
                    rule_id: RULE_STREAM_POSITION_REGRESSION.clone(),
                    layer: FindingLayer::DataQuality,
                    severity: Severity::ReviewNeeded,
                    message: format!(
                        "Stream position regressed from {} to {}; transport replay must be reconciled before advancing the checkpoint",
                        previous_sequence, delta.position.sequence
                    ),
                    subject_id: Some(delta.delta_id.clone()),
                    evidence: Vec::new(),
                    requires_human_review: true,
                    details: BTreeMap::new(),
                });
                return (
                    ApplyOutcome {
                        delta_id: delta.delta_id,
                        status: ApplyStatus::PositionRegression,
                        emitted_event_ids: Vec::new(),
                        findings,
                    },
                    NormalizedBundle::default(),
                );
            } else if delta.position.sequence > previous_sequence.saturating_add(1) {
                findings.push(ValidationFinding {
                    rule_id: RULE_STREAM_POSITION_GAP.clone(),
                    layer: FindingLayer::DataQuality,
                    severity: Severity::ReviewNeeded,
                    message: format!(
                        "Stream position advanced from {} to {}; missing positions must be replayed before advancing the checkpoint",
                        previous_sequence, delta.position.sequence
                    ),
                    subject_id: Some(delta.delta_id.clone()),
                    evidence: Vec::new(),
                    requires_human_review: true,
                    details: BTreeMap::new(),
                });
                return (
                    ApplyOutcome {
                        delta_id: delta.delta_id,
                        status: ApplyStatus::PositionGap,
                        emitted_event_ids: Vec::new(),
                        findings,
                    },
                    NormalizedBundle::default(),
                );
            }
        }

        let previous_event_id = self
            .records
            .get(&delta.logical_record_id)
            .and_then(|state| state.last_event_id.clone());
        let mut bundle = normalizer.normalize(&delta, processed_at);
        for event in &mut bundle.events {
            match event.operation {
                EventOperation::Upsert => event.supersedes_event_id = previous_event_id.clone(),
                EventOperation::Retract => event.retracts_event_id = previous_event_id.clone(),
            }
        }
        findings.extend(bundle.findings.clone());

        self.seen_delta_ids.insert(delta.delta_id.clone());
        self.positions
            .entry(position_key)
            .and_modify(|sequence| *sequence = (*sequence).max(delta.position.sequence))
            .or_insert(delta.position.sequence);
        self.records.insert(
            delta.logical_record_id.clone(),
            RecordState {
                revision: delta.revision,
                current_digest: delta.current_content_sha256.clone(),
                last_delta_id: delta.delta_id.clone(),
                last_event_id: bundle.events.last().map(|event| event.event_id.clone()),
            },
        );

        let emitted_event_ids = bundle
            .events
            .iter()
            .map(|event| event.event_id.clone())
            .collect();
        (
            ApplyOutcome {
                delta_id: delta.delta_id,
                status: ApplyStatus::Accepted,
                emitted_event_ids,
                findings,
            },
            bundle,
        )
    }

    pub fn from_snapshot(snapshot: ReplaySnapshot) -> Result<Self, ReplaySnapshotError> {
        let expected_hash = Sha256Digest::of(&canonical_json_bytes(&(
            snapshot.records.clone(),
            snapshot.partitions.clone(),
        ))?);
        if expected_hash != snapshot.state_hash {
            return Err(ReplaySnapshotError::StateHashMismatch);
        }

        let mut records = BTreeMap::new();
        for record in snapshot.records {
            let logical_record_id = record.logical_record_id.clone();
            if records
                .insert(
                    logical_record_id.clone(),
                    RecordState {
                        revision: record.revision,
                        current_digest: record.current_digest,
                        last_delta_id: record.last_delta_id,
                        last_event_id: record.last_event_id,
                    },
                )
                .is_some()
            {
                return Err(ReplaySnapshotError::DuplicateRecord(logical_record_id));
            }
        }

        let mut positions = BTreeMap::new();
        for position in snapshot.partitions {
            let key = (position.source.clone(), position.partition.clone());
            if positions.insert(key, position.last_sequence).is_some() {
                return Err(ReplaySnapshotError::DuplicatePartition {
                    stream_source: position.source,
                    partition: position.partition,
                });
            }
        }

        Ok(Self {
            seen_delta_ids: BTreeSet::new(),
            records,
            positions,
        })
    }

    pub fn snapshot(
        &self,
        consumer: StableId,
        created_at: Timestamp,
    ) -> Result<ReplaySnapshot, serde_json::Error> {
        let records: Vec<_> = self
            .records
            .iter()
            .map(|(logical_record_id, state)| RecordRevisionSnapshot {
                logical_record_id: logical_record_id.clone(),
                revision: state.revision,
                current_digest: state.current_digest.clone(),
                last_delta_id: state.last_delta_id.clone(),
                last_event_id: state.last_event_id.clone(),
            })
            .collect();
        let partitions: Vec<_> = self
            .positions
            .iter()
            .map(|((source, partition), sequence)| PartitionCheckpoint {
                source: source.clone(),
                partition: partition.clone(),
                last_sequence: *sequence,
                watermark: None,
            })
            .collect();
        let state_hash = Sha256Digest::of(&canonical_json_bytes(&(
            records.clone(),
            partitions.clone(),
        ))?);
        let snapshot_id = content_id(
            "foi-process:replay-snapshot",
            &(consumer.clone(), state_hash.clone()),
        )?;
        Ok(ReplaySnapshot {
            schema_version: CONTRACT_VERSION.to_string(),
            snapshot_id,
            consumer,
            created_at,
            records,
            partitions,
            state_hash,
        })
    }

    pub fn checkpoint(
        &self,
        consumer: StableId,
        created_at: Timestamp,
    ) -> Result<StreamCheckpoint, serde_json::Error> {
        let snapshot = self.snapshot(consumer.clone(), created_at.clone())?;
        let checkpoint_id = content_id(
            "foi-process:checkpoint",
            &(
                consumer.clone(),
                snapshot.state_hash.clone(),
                snapshot.partitions.clone(),
            ),
        )?;
        Ok(StreamCheckpoint {
            schema_version: CONTRACT_VERSION.to_string(),
            checkpoint_id,
            consumer,
            created_at,
            partitions: snapshot.partitions,
            state_hash: Some(snapshot.state_hash),
            attributes: BTreeMap::new(),
        })
    }
}

/// Materialize the latest active revision of each logical event.
pub fn materialize_events(events: &[ProcessEvent]) -> Vec<&ProcessEvent> {
    let mut latest: BTreeMap<StableId, &ProcessEvent> = BTreeMap::new();
    for event in events {
        let replace = latest
            .get(&event.logical_event_id)
            .map(|current| {
                event.revision > current.revision
                    || (event.revision == current.revision && event.event_id > current.event_id)
            })
            .unwrap_or(true);
        if replace {
            latest.insert(event.logical_event_id.clone(), event);
        }
    }
    let mut active: Vec<_> = latest
        .into_values()
        .filter(|event| event.operation == EventOperation::Upsert)
        .collect();
    active.sort_by_key(|event| (event.case_id.clone(), event.order_key()));
    active
}
