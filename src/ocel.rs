//! Lossless-enough portable OCEL 2.0 projection used for fixtures and dashboard preparation.
//! When the `rust4pm` feature is enabled, `rust4pm::append_bundle` writes these records through
//! Rust4PM's existing `AppendableOCEL` interface.

use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use crate::{contracts::*, replay::materialize_events};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct OcelEventRow {
    pub id: StableId,
    pub event_type: TermId,
    pub time: Timestamp,
    pub attributes: BTreeMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct OcelObjectRow {
    pub id: StableId,
    pub object_type: TermId,
    pub attributes: BTreeMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct OcelEventObjectRow {
    pub event_id: StableId,
    pub object_id: StableId,
    pub qualifier: TermId,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct OcelObjectObjectRow {
    pub source_object_id: StableId,
    pub target_object_id: StableId,
    pub qualifier: TermId,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct OcelObjectChangeRow {
    pub object_id: StableId,
    pub attribute: TermId,
    pub value: serde_json::Value,
    pub time: Timestamp,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct OcelProjection {
    pub events: Vec<OcelEventRow>,
    pub objects: Vec<OcelObjectRow>,
    pub event_object_links: Vec<OcelEventObjectRow>,
    pub object_object_links: Vec<OcelObjectObjectRow>,
    pub object_changes: Vec<OcelObjectChangeRow>,
}

pub fn project_ocel(bundle: &NormalizedBundle) -> OcelProjection {
    let materialized = materialize_events(&bundle.events);
    let events = materialized
        .iter()
        .map(|event| OcelEventRow {
            id: event.event_id.clone(),
            event_type: event.activity.clone(),
            time: event.mining_time().clone(),
            attributes: event.attributes.clone(),
        })
        .collect();
    let mut object_rows = BTreeMap::<StableId, OcelObjectRow>::new();
    for object in &bundle.objects {
        object_rows.insert(
            object.object_id.clone(),
            OcelObjectRow {
                id: object.object_id.clone(),
                object_type: object.object_type.clone(),
                attributes: object.attributes.clone(),
            },
        );
    }
    for event in &materialized {
        for object in &event.objects {
            object_rows
                .entry(object.object_id.clone())
                .or_insert_with(|| OcelObjectRow {
                    id: object.object_id.clone(),
                    object_type: object.object_type.clone(),
                    attributes: BTreeMap::new(),
                });
        }
    }
    let objects = object_rows.into_values().collect();
    let event_object_links = materialized
        .iter()
        .flat_map(|event| {
            event.objects.iter().map(move |object| OcelEventObjectRow {
                event_id: event.event_id.clone(),
                object_id: object.object_id.clone(),
                qualifier: object.qualifier.clone(),
            })
        })
        .collect();
    let object_object_links = bundle
        .object_links
        .iter()
        .map(|link| OcelObjectObjectRow {
            source_object_id: link.source_object_id.clone(),
            target_object_id: link.target_object_id.clone(),
            qualifier: link.qualifier.clone(),
        })
        .collect();
    let object_changes = bundle
        .object_changes
        .iter()
        .map(|change| OcelObjectChangeRow {
            object_id: change.object_id.clone(),
            attribute: change.attribute.clone(),
            value: change.value.clone(),
            time: change.effective_at.timestamp.clone(),
        })
        .collect();

    OcelProjection {
        events,
        objects,
        event_object_links,
        object_object_links,
        object_changes,
    }
}
