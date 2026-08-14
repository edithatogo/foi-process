#!/usr/bin/env python3
"""Regression tests for release commit subject validation."""

import unittest

from check_release_commit_subject import subject_matches_release


class ReleaseCommitSubjectTests(unittest.TestCase):
    def test_accepts_release_please_subject(self) -> None:
        self.assertTrue(subject_matches_release("chore(main): release 0.2.0", "0.2.0"))

    def test_accepts_github_squash_suffix(self) -> None:
        self.assertTrue(
            subject_matches_release("chore(main): release 0.2.0 (#129)", "0.2.0")
        )

    def test_rejects_non_numeric_or_trailing_suffixes(self) -> None:
        self.assertFalse(
            subject_matches_release("chore(main): release 0.2.0 (#release)", "0.2.0")
        )
        self.assertFalse(
            subject_matches_release("chore(main): release 0.2.0 (#129) extra", "0.2.0")
        )

    def test_rejects_wrong_version_or_subject(self) -> None:
        self.assertFalse(subject_matches_release("chore(main): release 0.2.1", "0.2.0"))
        self.assertFalse(subject_matches_release("fix: release 0.2.0 (#129)", "0.2.0"))


if __name__ == "__main__":
    unittest.main()
