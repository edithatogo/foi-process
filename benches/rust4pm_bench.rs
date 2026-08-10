use chrono::{DateTime, FixedOffset};
use criterion::{criterion_group, criterion_main, Criterion};
use foi_process::{rust4pm::append_materialized_snapshot, NormalizedBundle};
use process_mining::{
    core::event_data::object_centric::{
        OCELEventAttribute, OCELObjectAttribute, OCELRelationship, OCELType,
    },
    AppendableOCEL,
};
use std::convert::Infallible;
use std::hint::black_box;

#[derive(Default)]
struct BlackHoleSink;

impl AppendableOCEL for BlackHoleSink {
    type Error = Infallible;

    fn declare_event_type(&mut self, _event_type: OCELType) -> Result<(), Self::Error> {
        Ok(())
    }
    fn declare_object_type(&mut self, _object_type: OCELType) -> Result<(), Self::Error> {
        Ok(())
    }
    fn append_event(
        &mut self,
        _id: String,
        _event_type: &str,
        _time: DateTime<FixedOffset>,
        _attributes: Vec<OCELEventAttribute>,
        _relationships: Vec<OCELRelationship>,
    ) -> Result<(), Self::Error> {
        Ok(())
    }
    fn append_object(
        &mut self,
        _id: String,
        _object_type: &str,
        _attributes: Vec<OCELObjectAttribute>,
        _relationships: Vec<OCELRelationship>,
    ) -> Result<(), Self::Error> {
        Ok(())
    }
    fn finalize(&mut self) -> Result<(), Self::Error> {
        Ok(())
    }
}

pub fn criterion_benchmark(c: &mut Criterion) {
    let json_data = include_str!("../examples/generated/normalized-bundle.json");
    let bundle: NormalizedBundle = serde_json::from_str(json_data).unwrap();

    // Scale up the bundle to make the benchmark more visible
    let mut large_bundle = bundle.clone();
    for _ in 0..100 {
        large_bundle.events.extend(bundle.events.clone());
        large_bundle.objects.extend(bundle.objects.clone());
    }

    c.bench_function("rust4pm append_materialized_snapshot", |b| {
        b.iter(|| {
            let mut sink = BlackHoleSink;
            append_materialized_snapshot(black_box(&large_bundle), &mut sink).unwrap();
        })
    });
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
