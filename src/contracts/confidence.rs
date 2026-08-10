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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn new_valid_values() {
        assert_eq!(Confidence::new(0.0).unwrap().get(), 0.0);
        assert_eq!(Confidence::new(0.5).unwrap().get(), 0.5);
        assert_eq!(Confidence::new(1.0).unwrap().get(), 1.0);
    }

    #[test]
    fn new_invalid_values() {
        assert_eq!(Confidence::new(-0.1), Err(ConfidenceError));
        assert_eq!(Confidence::new(1.1), Err(ConfidenceError));
        assert_eq!(Confidence::new(f32::NAN), Err(ConfidenceError));
        assert_eq!(Confidence::new(f32::INFINITY), Err(ConfidenceError));
        assert_eq!(Confidence::new(f32::NEG_INFINITY), Err(ConfidenceError));
    }

    #[test]
    fn serialize_confidence() {
        let confidence = Confidence::new(0.75).unwrap();
        let serialized = serde_json::to_string(&confidence).unwrap();
        assert_eq!(serialized, "0.75");
    }

    #[test]
    fn deserialize_valid_confidence() {
        let deserialized: Confidence = serde_json::from_str("0.75").unwrap();
        assert_eq!(deserialized.get(), 0.75);
    }

    #[test]
    fn deserialize_invalid_confidence() {
        let result: Result<Confidence, _> = serde_json::from_str("1.5");
        assert!(result.is_err());
        let result: Result<Confidence, _> = serde_json::from_str("-0.5");
        assert!(result.is_err());
    }
}
