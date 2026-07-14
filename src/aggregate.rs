//! Mergeable, revision-aware dashboard roll-ups.
//!
//! Rust4PM remains the canonical process-mining engine. These counters are deliberately small,
//! deterministic roll-ups for live dashboards. Revisions and retractions recompute only the
//! affected case, avoiding double-counting corrected events.

use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use crate::contracts::*;

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct EdgeKey {
    pub from: TermId,
    pub to: TermId,
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct WaitingTimeBucketKey {
    pub edge: EdgeKey,
    /// -1 is a negative/out-of-order duration; 0 is zero; n is [2^(n-1), 2^n) seconds.
    pub log2_bucket: i32,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct CountedActivity {
    pub activity: TermId,
    pub count: u64,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct CountedEdge {
    pub edge: EdgeKey,
    pub count: u64,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct CountedVariant {
    pub activities: Vec<TermId>,
    pub count: u64,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct CountedWaitingTimeBucket {
    pub key: WaitingTimeBucketKey,
    pub count: u64,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct DashboardSummary {
    pub case_count: u64,
    pub active_event_count: u64,
    pub activities: Vec<CountedActivity>,
    pub edges: Vec<CountedEdge>,
    pub variants: Vec<CountedVariant>,
    pub waiting_time_histogram: Vec<CountedWaitingTimeBucket>,
}

#[derive(Debug, Clone)]
struct SummaryEvent {
    logical_event_id: StableId,
    event_id: StableId,
    activity: TermId,
    time: Timestamp,
    source_sequence: u64,
}

impl SummaryEvent {
    fn from_process_event(event: &ProcessEvent) -> Self {
        Self {
            logical_event_id: event.logical_event_id.clone(),
            event_id: event.event_id.clone(),
            activity: event.activity.clone(),
            time: event.mining_time().clone(),
            source_sequence: event.position.sequence,
        }
    }

    fn compare_order(&self, other: &Self) -> std::cmp::Ordering {
        (&self.time, self.source_sequence, &self.event_id).cmp(&(
            &other.time,
            other.source_sequence,
            &other.event_id,
        ))
    }
}

#[derive(Debug, Clone)]
struct LogicalEventState {
    revision: u64,
    event_id: StableId,
    active_case: Option<StableId>,
}

/// Compact, revision-aware roll-up state for live dashboard counters.
///
/// Only the fields needed to recompute a changed case are retained. Full `ProcessEvent` records
/// stay in the event lake/OCEL snapshot rather than being duplicated in this in-memory view.
#[derive(Debug, Default)]
pub struct RevisableProcessSummary {
    case_events: std::collections::HashMap<StableId, Vec<SummaryEvent>>,
    logical_events: std::collections::HashMap<StableId, LogicalEventState>,
    nodes: BTreeMap<TermId, i64>,
    edges: BTreeMap<EdgeKey, i64>,
    variants: BTreeMap<Vec<TermId>, i64>,
    waiting: BTreeMap<WaitingTimeBucketKey, i64>,
    active_event_count: i64,
}

impl RevisableProcessSummary {
    pub fn apply_event(&mut self, event: ProcessEvent) {
        let incoming_version = (event.revision, event.event_id.clone());
        if self
            .logical_events
            .get(&event.logical_event_id)
            .is_some_and(|current| incoming_version <= (current.revision, current.event_id.clone()))
        {
            return;
        }

        let previous_case = self
            .logical_events
            .get(&event.logical_event_id)
            .and_then(|state| state.active_case.clone());
        let next_case = (event.operation == EventOperation::Upsert).then(|| event.case_id.clone());
        let mut affected_cases = Vec::with_capacity(2);
        if let Some(case_id) = previous_case.clone() {
            affected_cases.push(case_id);
        }
        if let Some(case_id) = next_case.clone() {
            if !affected_cases.contains(&case_id) {
                affected_cases.push(case_id);
            }
        }

        for case_id in &affected_cases {
            self.adjust_case_contribution(case_id, -1);
        }

        if let Some(case_id) = previous_case {
            let mut remove_case = false;
            if let Some(events) = self.case_events.get_mut(&case_id) {
                events.retain(|existing| existing.logical_event_id != event.logical_event_id);
                remove_case = events.is_empty();
            }
            if remove_case {
                self.case_events.remove(&case_id);
            }
        }

        if let Some(case_id) = next_case.clone() {
            let events = self.case_events.entry(case_id).or_default();
            events.push(SummaryEvent::from_process_event(&event));
            events.sort_unstable_by(SummaryEvent::compare_order);
        }

        self.logical_events.insert(
            event.logical_event_id,
            LogicalEventState {
                revision: event.revision,
                event_id: event.event_id,
                active_case: next_case,
            },
        );

        for case_id in &affected_cases {
            self.adjust_case_contribution(case_id, 1);
        }
    }

    pub fn apply_events<I>(&mut self, events: I)
    where
        I: IntoIterator<Item = ProcessEvent>,
    {
        for event in events {
            self.apply_event(event);
        }
    }

    pub fn snapshot(&self) -> DashboardSummary {
        DashboardSummary {
            case_count: self.case_events.len() as u64,
            active_event_count: self.active_event_count.max(0) as u64,
            activities: self
                .nodes
                .iter()
                .filter(|(_, count)| **count > 0)
                .map(|(activity, count)| CountedActivity {
                    activity: activity.clone(),
                    count: *count as u64,
                })
                .collect(),
            edges: self
                .edges
                .iter()
                .filter(|(_, count)| **count > 0)
                .map(|(edge, count)| CountedEdge {
                    edge: edge.clone(),
                    count: *count as u64,
                })
                .collect(),
            variants: self
                .variants
                .iter()
                .filter(|(_, count)| **count > 0)
                .map(|(activities, count)| CountedVariant {
                    activities: activities.clone(),
                    count: *count as u64,
                })
                .collect(),
            waiting_time_histogram: self
                .waiting
                .iter()
                .filter(|(_, count)| **count > 0)
                .map(|(key, count)| CountedWaitingTimeBucket {
                    key: key.clone(),
                    count: *count as u64,
                })
                .collect(),
        }
    }

    fn adjust_case_contribution(&mut self, case_id: &StableId, direction: i64) {
        let Some(events) = self.case_events.get(case_id) else {
            return;
        };
        if events.is_empty() {
            return;
        }

        for event in events {
            add_signed(&mut self.nodes, event.activity.clone(), direction);
        }

        let variant = events
            .iter()
            .map(|event| event.activity.clone())
            .collect::<Vec<_>>();
        add_signed(&mut self.variants, variant, direction);

        for pair in events.windows(2) {
            let edge = EdgeKey {
                from: pair[0].activity.clone(),
                to: pair[1].activity.clone(),
            };
            add_signed(&mut self.edges, edge.clone(), direction);
            let seconds = pair[1]
                .time
                .as_datetime()
                .signed_duration_since(pair[0].time.as_datetime())
                .num_seconds();
            add_signed(
                &mut self.waiting,
                WaitingTimeBucketKey {
                    edge,
                    log2_bucket: duration_bucket(seconds),
                },
                direction,
            );
        }

        self.active_event_count += direction * events.len() as i64;
    }
}

fn duration_bucket(seconds: i64) -> i32 {
    if seconds < 0 {
        -1
    } else if seconds == 0 {
        0
    } else {
        64 - seconds.leading_zeros() as i32
    }
}

fn add_signed<K: Ord>(map: &mut BTreeMap<K, i64>, key: K, delta: i64) {
    let next = map.get(&key).copied().unwrap_or_default() + delta;
    if next == 0 {
        map.remove(&key);
    } else {
        map.insert(key, next);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn duration_buckets_are_stable() {
        assert_eq!(duration_bucket(-1), -1);
        assert_eq!(duration_bucket(0), 0);
        assert_eq!(duration_bucket(1), 1);
        assert_eq!(duration_bucket(2), 2);
        assert_eq!(duration_bucket(3), 2);
        assert_eq!(duration_bucket(4), 3);
    }
}
