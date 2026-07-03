#!/usr/bin/env python3
"""Tests for workspace environment synchronization."""

from __future__ import annotations

import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import sync_workspace_env  # type: ignore[import-not-found]


def test_parse_env_file_strips_quotes(tmp_path: Path) -> None:
    """Dotenv parsing strips common quote wrappers."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        'NZ_LEGISLATION_API_KEY="abc"\nHF_TOKEN=hf_test\nZENODO_TOKEN=\'zen\'\n',
        encoding="utf-8",
    )

    values = sync_workspace_env.parse_env_file(env_file)

    assert values["NZ_LEGISLATION_API_KEY"] == "abc"
    assert values["HF_TOKEN"] == "hf_test"
    assert values["ZENODO_TOKEN"] == "zen"


def test_sync_workspace_env_preserves_local_values(tmp_path: Path) -> None:
    """Shared keys are copied while project-specific values are preserved."""
    root_env = tmp_path / ".env"
    root_env.write_text(
        "NZ_LEGISLATION_API_KEY=nz\nHF_TOKEN=hf\nZENODO_TOKEN=zen\n",
        encoding="utf-8",
    )
    subproject = tmp_path / "cli-legislation-nz"
    subproject.mkdir()
    (subproject / ".env.local").write_text("LOCAL_ONLY=keep\nHF_TOKEN=old\n", encoding="utf-8")

    updated = sync_workspace_env.sync_workspace_env(
        workspace_root=tmp_path,
        root_env_file=root_env,
    )

    assert updated == [subproject / ".env.local"]
    values = sync_workspace_env.parse_env_file(subproject / ".env.local")
    assert values["LOCAL_ONLY"] == "keep"
    assert values["NZ_LEGISLATION_API_KEY"] == "nz"
    assert values["HF_TOKEN"] == "hf"
    assert values["ZENODO_TOKEN"] == "zen"


def test_sync_workspace_env_dry_run_does_not_write(tmp_path: Path) -> None:
    """Dry-run reports pending changes without creating env files."""
    root_env = tmp_path / ".env"
    root_env.write_text(
        "NZ_LEGISLATION_API_KEY=nz\nHF_TOKEN=hf\nZENODO_TOKEN=zen\n",
        encoding="utf-8",
    )
    subproject = tmp_path / "sm-govt-nz"
    subproject.mkdir()

    updated = sync_workspace_env.sync_workspace_env(
        workspace_root=tmp_path,
        root_env_file=root_env,
        dry_run=True,
    )

    assert updated == [subproject / ".env.local"]
    assert not (subproject / ".env.local").exists()
