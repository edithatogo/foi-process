"""Regression tests for recursive publication privacy validation."""

from build_hf_dataset import validate_public_tree


def main() -> None:
    reviewed = {
        "nested": {
            "privacy": {
                "disposition": "publish",
                "human_reviewed": True,
                "reason_codes": ["privacy:fixture_reviewed"],
                "synthetic_fixture": True,
            }
        }
    }
    validate_public_tree(reviewed, "fixture")

    try:
        validate_public_tree(
            {
                "nested": {
                    "privacy": {
                        "disposition": "publish_metadata_only",
                        "human_reviewed": True,
                        "reason_codes": ["privacy:fixture_reviewed"],
                        "synthetic_fixture": True,
                    },
                    "inline_text": "must not publish",
                }
            },
            "fixture",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("metadata-only nested text was accepted")

    try:
        validate_public_tree({"nested": "to-be-recorded"}, "fixture")
    except ValueError:
        pass
    else:
        raise AssertionError("unresolved licensing marker was accepted")
    print("public privacy recursion: nested review and metadata-only safeguards verified")


if __name__ == "__main__":
    main()
