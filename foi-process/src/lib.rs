//! Rust-first integration spine for archival and live FOI process intelligence.
//!
//! This crate intentionally keeps one publishable library surface. Generic process-mining
//! algorithms belong in Rust4PM; FOI semantics belong in FOI-O; capture belongs in fyi-cli;
//! document extraction belongs in fe-reader; semantic document signals belong in
//! nlp-policy-nz; statutory rules belong in Axiom/RuleSpec; and visualisation belongs in
//! Propel. This crate joins those outputs through deterministic contracts and replay.

pub mod aggregate;
pub mod contracts;
pub mod fyi_archive;
pub mod normalize;
pub mod ocel;
pub mod publication;
pub mod replay;
pub mod validation;

#[cfg(feature = "parquet")]
pub mod parquet;

#[cfg(feature = "rust4pm")]
pub mod rust4pm;

pub use aggregate::*;
pub use contracts::*;
pub use fyi_archive::*;
pub use normalize::*;
pub use ocel::*;
pub use publication::*;
pub use replay::*;
pub use validation::*;

#[cfg(feature = "parquet")]
pub use parquet::*;

#[cfg(feature = "rust4pm")]
pub use rust4pm::*;
