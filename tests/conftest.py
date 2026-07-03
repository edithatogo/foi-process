"""Root pytest configuration.

The Windows/OneDrive environment can leave the default system pytest temp root
with ACLs that deny child writes. Keep root tests on a repo-local temp area.
"""

from __future__ import annotations

import shutil
import tempfile
import uuid
import os
from pathlib import Path

import pytest


RUNTIME_TMP = Path(
    os.environ.get(
        "LEGAL_NZ_TEST_TMP",
        str(Path.home() / "AppData" / "Local" / "Temp" / "legal-nz-tests"),
    )
)
_ORIGINAL_TEMPORARY_DIRECTORY = tempfile.TemporaryDirectory
_ORIGINAL_MKDTEMP = tempfile.mkdtemp


class _RuntimeTemporaryDirectory:
    def __init__(self, *args: object, **kwargs: object) -> None:
        del args, kwargs
        RUNTIME_TMP.mkdir(parents=True, exist_ok=True)
        self.name = str(RUNTIME_TMP / f"tmp-{uuid.uuid4().hex}")
        Path(self.name).mkdir(parents=True, exist_ok=False)

    def cleanup(self) -> None:
        shutil.rmtree(self.name, ignore_errors=True)

    def __enter__(self) -> str:
        return self.name

    def __exit__(self, *exc_info: object) -> None:
        self.cleanup()


def pytest_configure() -> None:
    RUNTIME_TMP.mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(RUNTIME_TMP)
    tempfile.TemporaryDirectory = _RuntimeTemporaryDirectory  # type: ignore[assignment]
    tempfile.mkdtemp = _mkdtemp  # type: ignore[assignment]


def _mkdtemp(*args: object, **kwargs: object) -> str:
    del args, kwargs
    RUNTIME_TMP.mkdir(parents=True, exist_ok=True)
    path = RUNTIME_TMP / f"tmp-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    return str(path)


@pytest.fixture
def tmp_path() -> Path:
    RUNTIME_TMP.mkdir(parents=True, exist_ok=True)
    path = RUNTIME_TMP / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
