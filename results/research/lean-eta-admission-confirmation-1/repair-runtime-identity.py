#!/usr/bin/env python3
"""Deterministically replace Lean's generated worktree-misidentified githash header."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


BANNER = "// Automatically generated file, DO NOT EDIT\n"
BAD = BANNER + '#define LEAN_GITHASH "ref: refs/heads/master"\n'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: repair-runtime-identity.py SOURCE_TREE HEADER REVISION")
    source = Path(sys.argv[1]).resolve()
    header = Path(sys.argv[2]).resolve()
    revision = sys.argv[3]
    if len(revision) != 40 or any(ch not in "0123456789abcdef" for ch in revision):
        raise SystemExit("revision must be a lowercase 40-byte Git hash")
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if actual != revision:
        raise SystemExit(f"source revision mismatch: {actual}")
    before = header.read_bytes()
    if before != BAD.encode():
        raise SystemExit(f"unexpected generated header before repair: {digest(before)}")
    after = (BANNER + f'#define LEAN_GITHASH "{revision}"\n').encode()
    header.write_bytes(after)
    if header.read_bytes() != after:
        raise SystemExit("generated header write did not persist")
    print(f"source_revision={revision}")
    print(f"before_sha256={digest(before)}")
    print(f"after_sha256={digest(after)}")


if __name__ == "__main__":
    main()
