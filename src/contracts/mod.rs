//! Versioned wire and storage contracts.

mod bundle;
mod confidence;
mod conformance;
mod document;
mod event;
mod evidence;
mod ids;
mod manifest;
mod object;
mod privacy;
mod stream;
mod temporal;

pub use bundle::*;
pub use confidence::*;
pub use conformance::*;
pub use document::*;
pub use event::*;
pub use evidence::*;
pub use ids::*;
pub use manifest::*;
pub use object::*;
pub use privacy::*;
pub use stream::*;
pub use temporal::*;

pub const CONTRACT_VERSION: &str = "1.0.0-draft.1";
pub const CONTRACT_BASE_URI: &str = "https://w3id.org/foi-process/schema/";
