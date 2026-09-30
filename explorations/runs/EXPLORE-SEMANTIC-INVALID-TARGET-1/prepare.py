"""Freeze the four declared checking-completeness inputs without executing them."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "results/research/pipeline-completeness-pilot-2/inputs/baseline.ndjson"


def encode(rows: list[dict]) -> bytes:
    return b"\n".join(json.dumps(row, separators=(",", ":")).encode() for row in rows) + b"\n"


def main() -> None:
    rows = [json.loads(line) for line in SOURCE.read_bytes().splitlines()]
    theorems = [(i, row["thm"]) for i, row in enumerate(rows) if "thm" in row]
    assert len(theorems) == 12
    cases = {"baseline": None, "invalid-first": 0, "invalid-middle": 5, "invalid-last": 11}
    for case, ordinal in cases.items():
        variant = json.loads(json.dumps(rows))
        if ordinal is not None:
            line, theorem = theorems[ordinal]
            assert theorem["type"] == 1 and theorem["value"] != 0
            variant[line]["thm"]["value"] = 0  # Sort 0 is not a proof of True.
        (HERE / f"{case}.ndjson").write_bytes(encode(variant))


if __name__ == "__main__":
    main()
