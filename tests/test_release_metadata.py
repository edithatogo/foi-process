from pathlib import Path
import importlib.util


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("check_release_metadata", ROOT / "scripts" / "check_release_metadata.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_release_metadata_matches_current_version():
    MODULE.check("v0.1.0")


def test_release_metadata_rejects_mismatched_tag():
    try:
        MODULE.check("v9.9.9")
    except ValueError as error:
        assert "version" in str(error)
    else:
        raise AssertionError("mismatched release tag should fail closed")
