#![cfg(feature = "rust4pm")]

use std::convert::Infallible;

use chrono::{DateTime, FixedOffset};
use foi_process::*;
use process_mining::{
    core::event_data::object_centric::{
        OCELEventAttribute, OCELObjectAttribute, OCELRelationship, OCELType,
    },
    AppendableOCEL,
};

#[derive(Default)]
struct RecordingSink {
    declared_event_types: Vec<String>,
    declared_object_types: Vec<String>,
    events: Vec<(String, String, usize)>,
    objects: Vec<(String, String)>,
    finalized: bool,
}

impl AppendableOCEL for RecordingSink {
    type Error = Infallible;

    fn declare_event_type(&mut self, event_type: OCELType) -> Result<(), Self::Error> {
        self.declared_event_types.push(event_type.name);
        Ok(())
    }

    fn declare_object_type(&mut self, object_type: OCELType) -> Result<(), Self::Error> {
        self.declared_object_types.push(object_type.name);
        Ok(())
    }

    fn append_event(
        &mut self,
        id: String,
        event_type: &str,
        _time: DateTime<FixedOffset>,
        _attributes: Vec<OCELEventAttribute>,
        relationships: Vec<OCELRelationship>,
    ) -> Result<(), Self::Error> {
        self.events
            .push((id, event_type.to_string(), relationships.len()));
        Ok(())
    }

    fn append_object(
        &mut self,
        id: String,
        object_type: &str,
        _attributes: Vec<OCELObjectAttribute>,
        _relationships: Vec<OCELRelationship>,
    ) -> Result<(), Self::Error> {
        self.objects.push((id, object_type.to_string()));
        Ok(())
    }

    fn finalize(&mut self) -> Result<(), Self::Error> {
        self.finalized = true;
        Ok(())
    }
}

#[test]
fn rust4pm_adapter_appends_only_latest_active_revision() {
    let bundle: NormalizedBundle =
        serde_json::from_str(include_str!("../examples/generated/normalized-bundle.json")).unwrap();
    let mut sink = RecordingSink::default();

    append_materialized_snapshot(&bundle, &mut sink).unwrap();

    assert!(sink.finalized);
    assert_eq!(
        sink.events
            .iter()
            .filter(|(_, event_type, _)| event_type == "foio:ExtensionNotified")
            .count(),
        1
    );
    assert!(sink
        .events
        .iter()
        .all(|(_, _, relationship_count)| *relationship_count > 0));
    assert!(sink.objects.iter().any(
        |(id, object_type)| id == "urn:fyi-nz:request:demo-1" && object_type == "foio:Request"
    ));
}
