#!/usr/bin/env python3
"""Build a noncanonical Eq.refl followed by the canonical Quot suffix."""
import argparse
import json
from pathlib import Path

REF_KEYS = {
    "ie": "e", "type": "e", "body": "e", "fn": "e", "arg": "e",
    "rhs": "e", "value": "e",
    "name": "n", "pre": "n", "in": "n", "param": "n",
    "levelParams": "n", "all": "n", "ctors": "n", "induct": "n",
    "ctor": "n",
    "il": "l", "sort": "l", "us": "l", "succ": "l", "max": "l",
    "imax": "l",
}


def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def declared_ids(row):
    return [(key, row[key]) for key in ("ie", "in", "il") if key in row]


def rewrite(value, maps, local, key=None):
    if isinstance(value, dict):
        return {k: rewrite(v, maps, local, k) for k, v in value.items()}
    if isinstance(value, list):
        return [rewrite(v, maps, local, key) for v in value]
    if isinstance(value, int) and key in REF_KEYS:
        domain = REF_KEYS[key]
        return maps[domain].get(value, local[domain].get(value, value))
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("alternate", type=Path)
    parser.add_argument("canonical", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("control", type=Path)
    args = parser.parse_args()

    alternate = rows(args.alternate)
    canonical = rows(args.canonical)
    if len(alternate) != 61 or len(canonical) < 61:
        raise SystemExit("unexpected template sizes")

    # Canonical expressions referenced by the Quot suffix that are already
    # present with the same meaning in the alternate Eq graph.
    maps = {
        "n": {1: 1, 3: 3, 4: 4, 11: 15},
        "l": {1: 1, 2: 2},
        "e": {1: 1, 2: 2, 3: 3, 5: 5, 13: 8, 17: 44,
              25: 20, 26: 26, 30: 30},
    }

    alternate_records = len(alternate)
    output = alternate.copy()
    for row in output:
        if row.get("in") == 1 and "str" in row:
            row["str"]["str"] = "Eq"
        if row.get("in") == 2 and "str" in row:
            row["str"]["str"] = "u_1"

    # The alternate K-disabled recursor has no independent motive universe.
    # Reintroduce the canonical Quot universe name, level, and Sort expression
    # under fresh IDs before remapping the quotient declarations.
    output += [
        {"in": 15, "str": {"pre": 0, "str": "u"}},
        {"il": 2, "param": 15},
        {"ie": 44, "sort": 2},
    ]

    used = {domain: set(mapping.values()) for domain, mapping in maps.items()}
    for row in output:
        for key, value in declared_ids(row):
            used[REF_KEYS[key]].add(value)
    next_id = {domain: max(values) + 1 for domain, values in used.items()}
    local = {domain: {} for domain in maps}
    suffix = []
    for row in canonical[60:]:
        for key, value in declared_ids(row):
            domain = REF_KEYS[key]
            if value not in local[domain]:
                local[domain][value] = next_id[domain]
                next_id[domain] += 1
        suffix.append(rewrite(row, maps, local))

    candidate_rows = output + suffix
    args.candidate.parent.mkdir(parents=True, exist_ok=True)
    args.candidate.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in candidate_rows))
    args.control.parent.mkdir(parents=True, exist_ok=True)
    args.control.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in canonical))
    print(json.dumps({
        "alternate_records": alternate_records,
        "canonical_records": len(canonical),
        "candidate_records": len(candidate_rows),
        "fresh_ids": next_id,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
