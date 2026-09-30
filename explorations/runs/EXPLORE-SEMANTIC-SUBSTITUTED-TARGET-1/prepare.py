"""Freeze two well-typed target substitutions and the retained baseline."""
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
    target_line, target = theorems[-1]
    assert target["name"] == 20 and target["type"] == 1 and target["value"] == 24
    (HERE / "baseline.ndjson").write_bytes(encode(rows))

    changed_statement = json.loads(json.dumps(rows))
    # True -> True, proved by the identity lambda. Existing expression 4 is bvar 0.
    changed_statement[target_line:target_line] = [
        {"ie": 25, "forallE": {"binderInfo": "default", "body": 1, "name": 6, "type": 1}},
        {"ie": 26, "lam": {"binderInfo": "default", "body": 4, "name": 6, "type": 1}},
    ]
    changed_statement[target_line + 2]["thm"]["type"] = 25
    changed_statement[target_line + 2]["thm"]["value"] = 26
    (HERE / "changed-proposition.ndjson").write_bytes(encode(changed_statement))

    changed_name = json.loads(json.dumps(rows))
    name_rows = [row for row in changed_name if row.get("in") == 20]
    assert len(name_rows) == 1 and name_rows[0]["str"] == {"pre": 8, "str": "d12"}
    name_rows[0]["str"]["str"] = "d12_substituted"
    (HERE / "changed-name.ndjson").write_bytes(encode(changed_name))


if __name__ == "__main__":
    main()
