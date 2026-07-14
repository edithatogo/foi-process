use schemars::JsonSchema;
use serde::{de::Error as _, Deserialize, Deserializer, Serialize, Serializer};
use thiserror::Error;

#[derive(Debug, Error, Clone, PartialEq)]
#[error("confidence must be finite and within 0.0..=1.0")]
pub struct ConfidenceError;

#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, JsonSchema)]
#[schemars(transparent)]
pub struct Confidence(f32);

impl Confidence {
    pub fn new(value: f32) -> Result<Self, ConfidenceError> {
        if value.is_finite() && (0.0..=1.0).contains(&value) {
            Ok(Self(value))
        } else {
            Err(ConfidenceError)
        }
    }

    pub fn get(self) -> f32 {
        self.0
    }
}

impl Serialize for Confidence {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_f32(self.0)
    }
}

impl<'de> Deserialize<'de> for Confidence {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value = f32::deserialize(deserializer)?;
        Self::new(value).map_err(D::Error::custom)
    }
}
