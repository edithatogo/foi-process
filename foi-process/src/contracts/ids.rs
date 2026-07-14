use std::{fmt, str::FromStr};

use schemars::JsonSchema;
use serde::{de::Error as _, Deserialize, Deserializer, Serialize, Serializer};
use sha2::{Digest as _, Sha256};
use thiserror::Error;

#[derive(Debug, Error, Clone, PartialEq, Eq)]
pub enum IdentifierError {
    #[error("identifier must not be empty")]
    Empty,
    #[error("identifier is too long (maximum 512 bytes)")]
    TooLong,
    #[error("identifier must contain a namespace separator ':'")]
    MissingNamespace,
    #[error("identifier contains whitespace or a control character")]
    InvalidCharacter,
    #[error("SHA-256 digest must be exactly 64 lowercase hexadecimal characters")]
    InvalidDigest,
}

/// Globally scoped identifier used across repositories and event streams.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, JsonSchema)]
#[schemars(transparent)]
pub struct StableId(String);

impl StableId {
    pub fn parse(value: impl Into<String>) -> Result<Self, IdentifierError> {
        let value = value.into();
        if value.is_empty() {
            return Err(IdentifierError::Empty);
        }
        if value.len() > 512 {
            return Err(IdentifierError::TooLong);
        }
        if !value.contains(':') {
            return Err(IdentifierError::MissingNamespace);
        }
        if value.chars().any(|c| c.is_whitespace() || c.is_control()) {
            return Err(IdentifierError::InvalidCharacter);
        }
        Ok(Self(value))
    }

    pub fn content(namespace: &str, bytes: &[u8]) -> Self {
        let digest = Sha256Digest::of(bytes);
        Self(format!("urn:{namespace}:sha256:{}", digest.as_str()))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for StableId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}

impl FromStr for StableId {
    type Err = IdentifierError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Self::parse(s)
    }
}

impl Serialize for StableId {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(&self.0)
    }
}

impl<'de> Deserialize<'de> for StableId {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value = String::deserialize(deserializer)?;
        Self::parse(value).map_err(D::Error::custom)
    }
}

/// CURIE/IRI-like identifier for activities, object types, roles, and vocabulary terms.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, JsonSchema)]
#[schemars(transparent)]
pub struct TermId(String);

impl TermId {
    pub fn parse(value: impl Into<String>) -> Result<Self, IdentifierError> {
        StableId::parse(value).map(|id| Self(id.0))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for TermId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}

impl FromStr for TermId {
    type Err = IdentifierError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Self::parse(s)
    }
}

impl Serialize for TermId {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(&self.0)
    }
}

impl<'de> Deserialize<'de> for TermId {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value = String::deserialize(deserializer)?;
        Self::parse(value).map_err(D::Error::custom)
    }
}

/// Canonical lower-case SHA-256 digest.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, JsonSchema)]
#[schemars(transparent)]
pub struct Sha256Digest(String);

impl Sha256Digest {
    pub fn parse(value: impl Into<String>) -> Result<Self, IdentifierError> {
        let value = value.into();
        let valid = value.len() == 64
            && value
                .bytes()
                .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b));
        if !valid {
            return Err(IdentifierError::InvalidDigest);
        }
        Ok(Self(value))
    }

    pub fn of(bytes: &[u8]) -> Self {
        let digest = Sha256::digest(bytes);
        let mut output = String::with_capacity(64);
        for byte in digest {
            use fmt::Write as _;
            write!(&mut output, "{byte:02x}").expect("writing to String cannot fail");
        }
        Self(output)
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for Sha256Digest {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}

impl Serialize for Sha256Digest {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(&self.0)
    }
}

impl<'de> Deserialize<'de> for Sha256Digest {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value = String::deserialize(deserializer)?;
        Self::parse(value).map_err(D::Error::custom)
    }
}

pub fn canonical_json_bytes<T: Serialize>(value: &T) -> Result<Vec<u8>, serde_json::Error> {
    // RFC 8785 JSON Canonicalization Scheme gives content identifiers stable semantics across
    // languages, key insertion orders, and conforming implementations.
    serde_json_canonicalizer::to_vec(value)
}

pub fn content_id<T: Serialize>(namespace: &str, value: &T) -> Result<StableId, serde_json::Error> {
    Ok(StableId::content(namespace, &canonical_json_bytes(value)?))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn canonicalisation_is_key_order_independent() {
        let a = json!({"b": 2, "a": {"d": 4, "c": 3}});
        let b = json!({"a": {"c": 3, "d": 4}, "b": 2});
        assert_eq!(
            canonical_json_bytes(&a).unwrap(),
            canonical_json_bytes(&b).unwrap()
        );
        assert_eq!(
            content_id("test", &a).unwrap(),
            content_id("test", &b).unwrap()
        );
    }
}
