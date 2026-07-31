//! Direct Rust4PM integration. This module deliberately does not reimplement OCEL or mining.

use std::collections::{BTreeMap, BTreeSet};

use process_mining::{
    core::event_data::object_centric::{OCELRelationship, OCELType},
    AppendableOCEL,
};

use crate::{contracts::*, replay::materialize_events};

#[derive(Debug)]
pub enum AppendBundleError<E> {
    Sink(E),
}

/// Append a materialized snapshot through Rust4PM's existing `AppendableOCEL` contract.
///
/// Only the latest active revision of each logical event is emitted. Declarations are emitted
/// before objects/events, and objects before events, avoiding the implementation-defined
/// misordering cases documented by Rust4PM. Because the upstream trait has no generic update or
/// retraction operation, this function is intentionally snapshot-oriented and finalizes the sink.
///
/// The reduced semantics are deliberate: the current `AppendableOCEL` contract accepts type
/// declarations, identifiers, timestamps, and relationships, but not generic FOI attributes,
/// object-property values, or revision operations. Those remain authoritative in the normalized
/// and public JSON contracts; the empty Rust4PM attribute vectors are an explicit compatibility
/// boundary, covered by the adapter regression test.
pub fn append_materialized_snapshot<T>(
    bundle: &NormalizedBundle,
    target: &mut T,
) -> Result<(), AppendBundleError<T::Error>>
where
    T: AppendableOCEL,
{
    let active_events = materialize_events(&bundle.events);
    let event_types: BTreeSet<_> = active_events
        .iter()
        .map(|event| event.activity.to_string())
        .collect();
    let mut object_index = BTreeMap::<StableId, TermId>::new();
    for object in &bundle.objects {
        object_index.insert(object.object_id.clone(), object.object_type.clone());
    }
    for event in &bundle.events {
        for object in &event.objects {
            if !object_index.contains_key(&object.object_id) {
                object_index.insert(object.object_id.clone(), object.object_type.clone());
            }
        }
    }
    let object_types: BTreeSet<_> = object_index.values().map(ToString::to_string).collect();

    for name in object_types {
        target
            .declare_object_type(OCELType {
                name,
                attributes: Vec::new(),
            })
            .map_err(AppendBundleError::Sink)?;
    }
    for name in event_types {
        target
            .declare_event_type(OCELType {
                name,
                attributes: Vec::new(),
            })
            .map_err(AppendBundleError::Sink)?;
    }

    for (object_id, object_type) in &object_index {
        let relationships = bundle
            .object_links
            .iter()
            .filter(|link| &link.source_object_id == object_id)
            .map(|link| {
                OCELRelationship::new(
                    link.target_object_id.to_string(),
                    link.qualifier.to_string(),
                )
            })
            .collect();
        target
            .append_object(
                object_id.to_string(),
                object_type.as_str(),
                Vec::new(),
                relationships,
            )
            .map_err(AppendBundleError::Sink)?;
    }

    for event in active_events {
        let relationships = event
            .objects
            .iter()
            .map(|object| {
                OCELRelationship::new(object.object_id.to_string(), object.qualifier.to_string())
            })
            .collect();
        target
            .append_event(
                event.event_id.to_string(),
                event.activity.as_str(),
                event.mining_time().as_datetime(),
                Vec::new(),
                relationships,
            )
            .map_err(AppendBundleError::Sink)?;
    }

    target.finalize().map_err(AppendBundleError::Sink)
}
