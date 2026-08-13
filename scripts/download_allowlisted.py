#!/usr/bin/env python3
"""Download an immutable archive input through a strict HTTPS host allowlist."""

from __future__ import annotations

import argparse
import hashlib
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ALLOWED_HOSTS = frozenset({"huggingface.co", "cdn-lfs.hf.co"})
MAX_REDIRECTS = 5
READ_SIZE = 1024 * 1024


def validate_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError(f"invalid URL port: {value}") from error
    if parsed.scheme != "https":
        raise ValueError("download URL must use HTTPS")
    if not parsed.hostname or parsed.hostname.lower() not in ALLOWED_HOSTS:
        raise ValueError(f"download host is not allowlisted: {parsed.hostname or '<missing>'}")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("download URL must not contain userinfo")
    if parsed.fragment:
        raise ValueError("download URL must not contain a fragment")
    if port not in (None, 443):
        raise ValueError("download URL must not use a non-default port")
    return value


class AllowlistedRedirectHandler(urllib.request.HTTPRedirectHandler):
    max_redirections = MAX_REDIRECTS

    def __init__(self, deadline: float) -> None:
        super().__init__()
        self.deadline = deadline

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        if time.monotonic() >= self.deadline:
            raise TimeoutError("overall download timeout expired during redirect")
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(
    url: str,
    destination: Path,
    expected_sha256: str,
    connect_timeout: float,
    overall_timeout: float,
    max_bytes: int,
) -> None:
    validate_url(url)
    if connect_timeout <= 0 or overall_timeout <= 0 or max_bytes <= 0:
        raise ValueError("timeouts and max-bytes must be positive")
    if len(expected_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in expected_sha256
    ):
        raise ValueError("expected SHA-256 must be 64 lowercase hexadecimal characters")

    started = time.monotonic()
    deadline = started + overall_timeout
    opener = urllib.request.build_opener(AllowlistedRedirectHandler(deadline))
    request = urllib.request.Request(url, headers={"User-Agent": "foi-process-reconciler/1"})
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.part")
    digest = hashlib.sha256()
    downloaded = 0
    try:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("overall download timeout expired before connection")
        with opener.open(request, timeout=min(connect_timeout, remaining)) as response:
            validate_url(response.geturl())
            declared = response.headers.get("Content-Length")
            if declared is not None and int(declared) > max_bytes:
                raise ValueError("download Content-Length exceeds max-bytes")
            with temporary.open("xb") as output:
                while True:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("overall download timeout expired")
                    block = response.read(min(READ_SIZE, max_bytes - downloaded + 1))
                    if not block:
                        break
                    downloaded += len(block)
                    if downloaded > max_bytes:
                        raise ValueError("download exceeds max-bytes")
                    digest.update(block)
                    output.write(block)
                output.flush()
                os.fsync(output.fileno())
        actual = digest.hexdigest()
        if actual != expected_sha256:
            raise ValueError(f"download SHA-256 mismatch: expected {expected_sha256}, got {actual}")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--connect-timeout", type=float, required=True)
    parser.add_argument("--overall-timeout", type=float, required=True)
    parser.add_argument("--max-bytes", type=int, required=True)
    args = parser.parse_args()
    download(
        args.url,
        args.destination.resolve(),
        args.expected_sha256,
        args.connect_timeout,
        args.overall_timeout,
        args.max_bytes,
    )


if __name__ == "__main__":
    main()
