use foi_process::*;

fn deltas() -> Vec<EvidenceDelta> {
    include_str!("../examples/input/evidence-deltas.ndjson")
        .lines()
        .filter(|line| !line.trim().is_empty())
        .map(|line| serde_json::from_str(line).unwrap())
        .collect()
}

#[test]
fn duplicate_delivery_is_idempotent() {
    let normalizer = DeterministicNormalizer::new(MappingProfile::fyi_minimal(), "test");
    let processed = Timestamp::parse("2026-07-09T00:05:00Z").unwrap();
    let mut replay = ReplayEngine::default();
    let delta = deltas().remove(0);
    let (first, _) = replay.apply(delta.clone(), processed.clone(), &normalizer);
    let (second, bundle) = replay.apply(delta, processed, &normalizer);
    assert_eq!(first.status, ApplyStatus::Accepted);
    assert_eq!(second.status, ApplyStatus::Duplicate);
    assert!(bundle.events.is_empty());
}

#[test]
fn corrected_event_supersedes_previous_revision() {
    let normalizer = DeterministicNormalizer::new(MappingProfile::fyi_minimal(), "test");
    let processed = Timestamp::parse("2026-07-09T00:05:00Z").unwrap();
    let mut replay = ReplayEngine::default();
    let deltas = deltas();
    let (_, first) = replay.apply(deltas[2].clone(), processed.clone(), &normalizer);
    let (_, corrected) = replay.apply(deltas[3].clone(), processed, &normalizer);
    assert_eq!(
        corrected.events[0].supersedes_event_id.as_ref(),
        Some(&first.events[0].event_id)
    );
}

#[test]
fn stream_position_gaps_and_regressions_are_quarantinable() {
    let normalizer = DeterministicNormalizer::new(MappingProfile::fyi_minimal(), "test");
    let processed = Timestamp::parse("2026-07-09T00:05:00Z").unwrap();
    let mut replay = ReplayEngine::default();
    let fixture = deltas();
    let (first, _) = replay.apply(fixture[0].clone(), processed.clone(), &normalizer);
    assert_eq!(first.status, ApplyStatus::Accepted);

    let mut gap = fixture[1].clone();
    gap.delta_id = StableId::parse("urn:foi-process:test:position-gap").unwrap();
    gap.position.sequence = 3;
    let (gap_outcome, gap_bundle) = replay.apply(gap, processed.clone(), &normalizer);
    assert_eq!(gap_outcome.status, ApplyStatus::PositionGap);
    assert!(gap_bundle.events.is_empty());

    let mut regression = fixture[1].clone();
    regression.delta_id = StableId::parse("urn:foi-process:test:position-regression").unwrap();
    regression.position.sequence = 0;
    let (regression_outcome, regression_bundle) =
        replay.apply(regression, processed.clone(), &normalizer);
    assert_eq!(regression_outcome.status, ApplyStatus::PositionRegression);
    assert!(regression_bundle.events.is_empty());

    let snapshot = replay
        .snapshot(
            StableId::parse("urn:foi-process:test:consumer").unwrap(),
            processed,
        )
        .unwrap();
    assert_eq!(snapshot.partitions[0].last_sequence, 1);
}

mod properties {
    use super::*;
    use proptest::prelude::*;

    proptest! {
        #[test]
        fn duplicate_delivery_emits_at_most_once(repeat_count in 1usize..32) {
            let normalizer = DeterministicNormalizer::new(MappingProfile::fyi_minimal(), "test");
            let processed = Timestamp::parse("2026-07-09T00:05:00Z").unwrap();
            let mut replay = ReplayEngine::default();
            let delta = deltas().remove(0);
            let mut emitted = 0usize;

            for _ in 0..repeat_count {
                let (outcome, bundle) = replay.apply(
                    delta.clone(),
                    processed.clone(),
                    &normalizer,
                );
                if outcome.status == ApplyStatus::Accepted {
                    emitted += bundle.events.len();
                } else {
                    prop_assert_eq!(outcome.status, ApplyStatus::Duplicate);
                    prop_assert!(bundle.events.is_empty());
                }
            }
            prop_assert_eq!(emitted, 1);
        }
    }
}

#[test]
fn replay_snapshot_integrity_is_verified_before_restore() {
    let normalizer = DeterministicNormalizer::new(MappingProfile::fyi_minimal(), "test");
    let processed = Timestamp::parse("2026-07-09T00:05:00Z").unwrap();
    let mut replay = ReplayEngine::default();
    let fixture = deltas();
    replay.apply(fixture[0].clone(), processed.clone(), &normalizer);

    let snapshot = replay
        .snapshot(
            StableId::parse("urn:foi-process:test:consumer").unwrap(),
            processed.clone(),
        )
        .unwrap();
    ReplayEngine::from_snapshot(snapshot.clone()).unwrap();

    let mut tampered = snapshot;
    tampered.records[0].revision += 1;
    assert!(matches!(
        ReplayEngine::from_snapshot(tampered),
        Err(ReplaySnapshotError::StateHashMismatch)
    ));
}

#[test]
fn restored_replay_remains_idempotent() {
    let normalizer = DeterministicNormalizer::new(MappingProfile::fyi_minimal(), "test");
    let processed = Timestamp::parse("2026-07-09T00:05:00Z").unwrap();
    let delta = deltas().remove(0);
    let mut initial = ReplayEngine::default();
    let (accepted, _) = initial.apply(delta.clone(), processed.clone(), &normalizer);
    assert_eq!(accepted.status, ApplyStatus::Accepted);

    let snapshot = initial
        .snapshot(
            StableId::parse("urn:foi-process:test:consumer").unwrap(),
            processed.clone(),
        )
        .unwrap();
    let mut restored = ReplayEngine::from_snapshot(snapshot).unwrap();
    let (duplicate, bundle) = restored.apply(delta, processed, &normalizer);
    assert_eq!(duplicate.status, ApplyStatus::Duplicate);
    assert!(bundle.events.is_empty());
}
