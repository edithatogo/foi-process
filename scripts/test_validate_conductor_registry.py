#!/usr/bin/env python3
"""Focused regression tests for Conductor registry validation."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from validate_conductor_registry import ROOT, parse_registry, validate


class ConductorRegistryTests(unittest.TestCase):
    def test_current_registry_passes(self) -> None:
        self.assertEqual(validate(), [])

    def test_parser_rejects_duplicate_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tracks.yaml"
            path.write_text(
                "tracks:\n- id: T00\n  status: active\n  status: completed\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate field"):
                parse_registry(path)

    def test_completed_track_cannot_gain_pending_work(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "conductor", root / "conductor")
            plan = root / "conductor" / "tracks" / "T07-dashboard-propel-hf" / "plan.md"
            plan.write_text(plan.read_text(encoding="utf-8") + "\n- [ ] stale work\n", encoding="utf-8")
            self.assertIn("completed T07 plan has unfinished checkboxes", validate(root))

    def test_markdown_cannot_omit_machine_registry_track(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "conductor", root / "conductor")
            registry = root / "conductor" / "tracks.md"
            registry.write_text(
                registry.read_text(encoding="utf-8").replace("**T00**", "**omitted-T00**"),
                encoding="utf-8",
            )
            errors = validate(root)
            self.assertTrue(any("tracks.md IDs differ" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
