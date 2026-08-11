//! Confidential-source identifiers.
//!
//! The secret is supplied by an external secret manager and is never part of a public export.

use hmac::{Hmac, KeyInit, Mac};
use sha2::Sha256;
use thiserror::Error;

use crate::StableId;

type HmacSha256 = Hmac<Sha256>;

#[derive(Debug, Error)]
pub enum PseudonymError {
    #[error("invalid key length for HMAC")]
    InvalidKeyLength(#[from] hmac::digest::InvalidLength),
}

/// Derive a stable, non-reversible case identifier for a confidential source.
///
/// Callers must keep `key` outside repositories, datasets, logs, and dashboard assets. Rotating
/// the key intentionally rotates the pseudonym namespace and therefore requires a migration plan.
pub fn pseudonymize_case_id(key: &[u8], source_case_id: &str) -> Result<StableId, PseudonymError> {
    let mut mac = HmacSha256::new_from_slice(key)?;
    mac.update(b"foi-process/confidential-case/v1\0");
    mac.update(source_case_id.as_bytes());
    let digest = mac.finalize().into_bytes();
    Ok(StableId::content("foi-process:confidential-case", &digest))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pseudonyms_are_stable_but_key_scoped() {
        let first = pseudonymize_case_id(b"test-only-secret", "internal-case-42").unwrap();
        assert_eq!(
            first,
            pseudonymize_case_id(b"test-only-secret", "internal-case-42").unwrap()
        );
        assert_ne!(
            first,
            pseudonymize_case_id(b"rotated-secret", "internal-case-42").unwrap()
        );
        assert!(!first.as_str().contains("internal-case-42"));
    }
}
