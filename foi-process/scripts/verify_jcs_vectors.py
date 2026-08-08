"""Verify the ASCII/integer RFC 8785 fixture subset with an independent oracle."""

import hashlib
import json
import sys
from pathlib import Path


def canonical_subset(value: object) -> bytes:
    """Canonicalise the fixture subset shared by Rust serde and this oracle."""
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def main(path: str) -> int:
    vectors = json.loads(Path(path).read_text(encoding="utf-8"))
    for vector in vectors:
        actual = hashlib.sha256(canonical_subset(vector["value"])).hexdigest()
        if actual != vector["sha256"]:
            raise SystemExit(f"{vector['name']}: {actual} != {vector['sha256']}")
    print(f"verified {len(vectors)} independent JCS vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
