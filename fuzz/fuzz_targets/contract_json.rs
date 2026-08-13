#![no_main]

use foi_process::{
    archive_package_id, canonical_json_bytes, validate_bundle, validate_delta, validate_event,
    ArchivePackageManifest, EvidenceDelta, NormalizedBundle, ProcessEvent,
};
use libfuzzer_sys::fuzz_target;

const MAX_INPUT_BYTES: usize = 64 * 1024;

fuzz_target!(|data: &[u8]| {
    if data.len() > MAX_INPUT_BYTES {
        return;
    }

    if let Ok(value) = serde_json::from_slice::<ProcessEvent>(data) {
        let _ = validate_event(&value);
        let _ = canonical_json_bytes(&value);
    }
    if let Ok(value) = serde_json::from_slice::<EvidenceDelta>(data) {
        let _ = validate_delta(&value);
        let _ = canonical_json_bytes(&value);
    }
    if let Ok(value) = serde_json::from_slice::<NormalizedBundle>(data) {
        let _ = validate_bundle(&value);
        let _ = canonical_json_bytes(&value);
    }
    if let Ok(value) = serde_json::from_slice::<ArchivePackageManifest>(data) {
        let _ = archive_package_id(&value);
        let _ = canonical_json_bytes(&value);
    }
});
