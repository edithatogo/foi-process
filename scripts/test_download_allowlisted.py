#!/usr/bin/env python3
"""Regression tests for immutable input URL and redirect policy."""

from __future__ import annotations

import time
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory

import download_allowlisted as target
from download_allowlisted import AllowlistedRedirectHandler, download, validate_url


class FakeResponse:
    def __init__(self, blocks: list[bytes], delay: float = 0) -> None:
        self.blocks = blocks
        self.delay = delay
        self.headers: dict[str, str] = {}

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def geturl(self) -> str:
        return "https://huggingface.co/file"

    def read(self, _size: int) -> bytes:
        if self.delay:
            time.sleep(self.delay)
        return self.blocks.pop(0) if self.blocks else b""


class FakeOpener:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response

    def open(self, _request, timeout: float):  # noqa: ANN001
        assert timeout > 0
        return self.response


def rejected_download(response: FakeResponse, *, max_bytes: int, timeout: float) -> None:
    original = target.urllib.request.build_opener
    target.urllib.request.build_opener = lambda _handler: FakeOpener(response)
    try:
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "download"
            try:
                download(
                    "https://huggingface.co/file",
                    destination,
                    "0" * 64,
                    connect_timeout=1,
                    overall_timeout=timeout,
                    max_bytes=max_bytes,
                )
            except (TimeoutError, ValueError):
                assert not destination.exists()
                return
            raise AssertionError("bounded download was unexpectedly accepted")
    finally:
        target.urllib.request.build_opener = original


def rejected(url: str) -> None:
    try:
        validate_url(url)
    except ValueError:
        return
    raise AssertionError(f"unsafe URL was accepted: {url}")


def main() -> None:
    assert validate_url("https://huggingface.co/datasets/example/archive")
    assert validate_url("https://cdn-lfs.hf.co/file?download=true")
    assert validate_url("https://us.aws.cdn.hf.co/xet-bridge-us/object")
    assert validate_url("https://huggingface.co:443/file")
    for url in (
        "http://huggingface.co/file",
        "https://example.com/file",
        "https://user@huggingface.co/file",
        "https://user:password@huggingface.co/file",
        "https://huggingface.co:444/file",
        "https://huggingface.co/file#fragment",
        "https://huggingface.co.evil.example/file",
    ):
        rejected(url)

    handler = AllowlistedRedirectHandler(time.monotonic() + 60)
    request = urllib.request.Request("https://huggingface.co/start")
    try:
        handler.redirect_request(
            request,
            None,
            302,
            "Found",
            {},
            "https://example.com/escaped",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("redirect escaped the host allowlist")
    rejected_download(FakeResponse([b"too large"]), max_bytes=1, timeout=60)
    rejected_download(FakeResponse([b"slow"], delay=0.02), max_bytes=1024, timeout=0.001)
    print("allowlisted download URL tests passed")


if __name__ == "__main__":
    main()
