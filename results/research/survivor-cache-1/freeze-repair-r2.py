#!/usr/bin/env python3
"""Bind the tested prelaunch verifier repair without changing frozen science."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.survivor_cache_runner import CODE  # noqa: E402

SOURCE = ROOT / "config/survivor-cache-0001.json"
OUTPUT = ROOT / "config/survivor-cache-0001-r2.json"


def binding(relative: str) -> dict:
    raw = (ROOT / relative).read_bytes()
    return {"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}


def main() -> None:
    revision = "r2"
    if sys.argv[1:] == ["--revision", "r3"]:
        revision = "r3"
    elif sys.argv[1:]:
        raise SystemExit("usage: freeze-repair-r2.py [--revision r3]")
    output = ROOT / f"config/survivor-cache-0001-{revision}.json"
    if output.exists():
        raise SystemExit("repair manifest already frozen")
    manifest = json.loads(SOURCE.read_text())
    manifest["tooling_inputs"] = [binding(path) for path in CODE]
    manifest["focused_test_receipt"] = binding(
        f"results/research/survivor-cache-1/focused-test-receipt-{revision}.json"
    )
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(binding(f"config/survivor-cache-0001-{revision}.json")))


if __name__ == "__main__":
    main()
