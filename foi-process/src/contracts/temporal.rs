use std::{cmp::Ordering, fmt};

use chrono::{DateTime, FixedOffset};
use schemars::JsonSchema;
use serde::{de::Error as _, Deserialize, Deserializer, Serialize, Serializer};
use thiserror::Error;

#[derive(Debug, Error, Clone, PartialEq, Eq)]
#[error("timestamp must be RFC 3339 with an explicit UTC offset")]
pub struct TimestampError;

#[derive(Debug, Clone, PartialEq, Eq, Hash, JsonSchema)]
#[schemars(transparent)]
pub struct Timestamp(String);

impl Timestamp {
    pub fn parse(value: impl Into<String>) -> Result<Self, TimestampError> {
        let value = value.into();
        DateTime::parse_from_rfc3339(&value).map_err(|_| TimestampError)?;
        Ok(Self(value))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }

    pub fn as_datetime(&self) -> DateTime<FixedOffset> {
        DateTime::parse_from_rfc3339(&self.0).expect("Timestamp is validated at construction")
    }
}

impl fmt::Display for Timestamp {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}

impl PartialOrd for Timestamp {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Timestamp {
    fn cmp(&self, other: &Self) -> Ordering {
        self.as_datetime().cmp(&other.as_datetime())
    }
}

impl Serialize for Timestamp {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(&self.0)
    }
}

impl<'de> Deserialize<'de> for Timestamp {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value = String::deserialize(deserializer)?;
        Self::parse(value).map_err(D::Error::custom)
    }
}

#[derive(
    Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize, JsonSchema,
)]
#[serde(rename_all = "snake_case")]
pub enum TemporalPrecision {
    Second,
    Minute,
    Hour,
    Day,
    Month,
    Year,
    Unknown,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct TemporalInstant {
    pub timestamp: Timestamp,
    #[serde(default = "default_precision")]
    pub precision: TemporalPrecision,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_timezone: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub uncertainty_seconds: Option<u64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_text: Option<String>,
}

fn default_precision() -> TemporalPrecision {
    TemporalPrecision::Second
}

impl TemporalInstant {
    pub fn exact(timestamp: Timestamp) -> Self {
        Self {
            timestamp,
            precision: TemporalPrecision::Second,
            source_timezone: None,
            uncertainty_seconds: None,
            source_text: None,
        }
    }
}
