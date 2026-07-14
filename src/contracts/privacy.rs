use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::StableId;

#[derive(
    Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize, JsonSchema,
)]
#[serde(rename_all = "snake_case")]
pub enum SensitivityClass {
    Public,
    Personal,
    SensitivePersonal,
    Restricted,
    Unknown,
}

#[derive(
    Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize, JsonSchema,
)]
#[serde(rename_all = "snake_case")]
pub enum AccessTier {
    Public,
    Research,
    Restricted,
    Embargoed,
}

#[derive(
    Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize, JsonSchema,
)]
#[serde(rename_all = "snake_case")]
pub enum PublicationDisposition {
    Publish,
    PublishMetadataOnly,
    Withhold,
    NeedsReview,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PrivacyAssessment {
    pub sensitivity: SensitivityClass,
    pub access_tier: AccessTier,
    pub disposition: PublicationDisposition,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub reason_codes: Vec<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub assessed_by: Option<StableId>,
    #[serde(default)]
    pub human_reviewed: bool,
}

impl Default for PrivacyAssessment {
    fn default() -> Self {
        Self {
            sensitivity: SensitivityClass::Unknown,
            access_tier: AccessTier::Restricted,
            disposition: PublicationDisposition::NeedsReview,
            reason_codes: vec!["privacy:not_assessed".to_string()],
            assessed_by: None,
            human_reviewed: false,
        }
    }
}
