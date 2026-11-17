#!/usr/bin/env python3
"""Generate and fail-closed audit the fixed control/candidate export pair."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parent
BASE = RUN / "inputs" / "base.ndjson"
BASE_SHA256 = "b86effc857438e3d59a52eb562dd6055412ddfc16b9486457d75f28876c9d413"
CONTROL = RUN / "inputs" / "control.ndjson"
CANDIDATE = RUN / "inputs" / "candidate.ndjson"
AUDIT = RUN / "fixture-audit.json"

OLD_UNIVERSE_NAME = 6
NEW_UNIVERSE_NAME = 20
OLD_UNIVERSE_LEVEL = 2
NEW_UNIVERSE_LEVEL = 3
TARGET_TYPE_NAME = 10
TARGET_RECURSOR_NAME = 19
TARGET_AUX_RECURSOR_NAME = 13
TARGET_RULE_ROOT = 80
FIRST_LATER_EXPRESSION = 81


class AuditError(ValueError):
    pass


def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise AuditError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_ndjson(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n") or hashlib.sha256(raw).hexdigest() != BASE_SHA256:
        raise AuditError("base export identity changed")
    rows = [json.loads(line, object_pairs_hook=pairs) for line in raw.splitlines()]
    if len(rows) != 203 or any(not isinstance(row, dict) for row in rows):
        raise AuditError("unexpected base export structure")
    return rows


def encoded(rows: list[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
         + "\n").encode("utf-8") for row in rows
    )


def map_ids(value: Any, mapper, keys: set[str]) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, child in value.items():
            if key in keys:
                if type(child) is int:
                    result[key] = mapper(child)
                elif isinstance(child, list) and all(type(item) is int for item in child):
                    result[key] = [mapper(item) for item in child]
                else:
                    result[key] = map_ids(child, mapper, keys)
            else:
                result[key] = map_ids(child, mapper, keys)
        return result
    if isinstance(value, list):
        return [map_ids(item, mapper, keys) for item in value]
    return value


NAME_KEYS = {"in", "name", "pre", "induct", "ctor", "all", "ctors", "levelParams"}
LEVEL_KEYS = {"il", "sort", "succ", "max", "imax", "us"}
EXPR_KEYS = {"ie", "fn", "arg", "body", "type", "value", "expr", "rhs"}


def shift_at(cutoff: int, amount: int):
    return lambda value: value + amount if value >= cutoff else value


def expression_index(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    index = {row["ie"]: row for row in rows if "ie" in row}
    if len(index) != sum("ie" in row for row in rows):
        raise AuditError("duplicate expression id")
    return index


def expression_children(row: dict[str, Any]) -> list[int]:
    children: list[int] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in EXPR_KEYS - {"ie"} and type(child) is int:
                    children.append(child)
                else:
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit({key: value for key, value in row.items() if key != "ie"})
    return children


def reachable(index: dict[int, dict[str, Any]], root: int) -> set[int]:
    pending = [root]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        if current not in index:
            raise AuditError(f"unknown expression id {current}")
        seen.add(current)
        pending.extend(expression_children(index[current]))
    return seen


def decode_names(rows: list[dict[str, Any]]) -> dict[int, str]:
    names = {0: "<anonymous>"}
    for row in rows:
        if "in" not in row:
            continue
        ident = row["in"]
        payload = row.get("str") or row.get("num")
        prefix = payload["pre"]
        if prefix not in names:
            raise AuditError("name prefix is not defined first")
        component = payload.get("str", str(payload.get("i")))
        names[ident] = component if prefix == 0 else names[prefix] + "." + component
    return names


def find_target_block(rows: list[dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    matches = []
    for index, row in enumerate(rows):
        block = row.get("inductive")
        if block and any(item["name"] == TARGET_TYPE_NAME for item in block["types"]):
            matches.append((index, block))
    if len(matches) != 1:
        raise AuditError("target nested inductive block is not unique")
    return matches[0]


def find_recursor(block: dict[str, Any], name: int) -> dict[str, Any]:
    matches = [recursor for recursor in block["recs"] if recursor["name"] == name]
    if len(matches) != 1:
        raise AuditError("target recursor is not unique")
    return matches[0]


def collect_levels(rows: list[dict[str, Any]], root: int) -> set[int]:
    index = expression_index(rows)
    levels: set[int] = set()
    for ident in reachable(index, root):
        row = index[ident]
        if "sort" in row:
            levels.add(row["sort"])
        constant = row.get("const")
        if constant:
            levels.update(constant["us"])
    return levels


def scalar_differences(left: Any, right: Any, pointer: str = "") -> list[dict[str, Any]]:
    if type(left) is not type(right):
        return [{"pointer": pointer, "control": left, "candidate": right}]
    if isinstance(left, dict):
        if set(left) != set(right):
            raise AuditError(f"structural key difference at {pointer or '/'}")
        return [item for key in sorted(left)
                for item in scalar_differences(left[key], right[key], pointer + "/" + key)]
    if isinstance(left, list):
        if len(left) != len(right):
            raise AuditError(f"structural length difference at {pointer or '/'}")
        return [item for index, (a, b) in enumerate(zip(left, right))
                for item in scalar_differences(a, b, pointer + f"/{index}")]
    return [] if left == right else [{"pointer": pointer, "control": left, "candidate": right}]


def build_pair() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[int, int]]:
    rows = copy.deepcopy(load_ndjson(BASE))
    universe_names = [row for row in rows if row.get("in") == OLD_UNIVERSE_NAME]
    if len(universe_names) != 1 or universe_names[0] != {
        "in": OLD_UNIVERSE_NAME, "str": {"pre": 0, "str": "u"}
    }:
        raise AuditError("base elimination universe is not the expected u")
    universe_names[0]["str"]["str"] = "v"

    rows = [map_ids(row, shift_at(NEW_UNIVERSE_NAME, 1), NAME_KEYS) for row in rows]
    rows = [map_ids(row, shift_at(NEW_UNIVERSE_LEVEL, 1), LEVEL_KEYS) for row in rows]
    block_index, _ = find_target_block(rows)

    old_expressions = expression_index(rows)
    selected = sorted(reachable(old_expressions, TARGET_RULE_ROOT))
    clone_map = {old: FIRST_LATER_EXPRESSION + index for index, old in enumerate(selected)}
    clone_count = len(clone_map)
    clones: list[dict[str, Any]] = []
    for old in selected:
        clone = copy.deepcopy(old_expressions[old])
        clone = map_ids(clone, lambda value: clone_map[value], EXPR_KEYS)
        clone = map_ids(
            clone,
            lambda value: NEW_UNIVERSE_LEVEL if value == OLD_UNIVERSE_LEVEL else value,
            {"sort", "us"},
        )
        clones.append(clone)

    rows = [map_ids(row, shift_at(FIRST_LATER_EXPRESSION, clone_count), EXPR_KEYS)
            for row in rows]
    inserts = [
        {"in": NEW_UNIVERSE_NAME, "str": {"pre": 0, "str": "u"}},
        {"il": NEW_UNIVERSE_LEVEL, "param": NEW_UNIVERSE_NAME},
        *clones,
    ]
    control = rows[:block_index] + inserts + rows[block_index:]
    candidate = copy.deepcopy(control)
    _, candidate_block = find_target_block(candidate)
    candidate_recursor = find_recursor(candidate_block, TARGET_RECURSOR_NAME)
    if candidate_recursor["rules"] != [{"ctor": 11, "nfields": 1, "rhs": TARGET_RULE_ROOT}]:
        raise AuditError("target rule changed before mutation")
    candidate_recursor["rules"][0]["rhs"] = clone_map[TARGET_RULE_ROOT]
    return control, candidate, clone_map


def audit(control: list[dict[str, Any]], candidate: list[dict[str, Any]],
          clone_map: dict[int, int]) -> dict[str, Any]:
    names = decode_names(control)
    if names[OLD_UNIVERSE_NAME] != "v" or names[NEW_UNIVERSE_NAME] != "u":
        raise AuditError("u/v name construction failed")
    block_index, control_block = find_target_block(control)
    _, candidate_block = find_target_block(candidate)
    target_type = next(item for item in control_block["types"] if item["name"] == TARGET_TYPE_NAME)
    if target_type["numNested"] != 1 or target_type["levelParams"] != []:
        raise AuditError("fixture is not the fixed monomorphic genuinely nested type")
    control_rec = find_recursor(control_block, TARGET_RECURSOR_NAME)
    candidate_rec = find_recursor(candidate_block, TARGET_RECURSOR_NAME)
    aux_rec = find_recursor(control_block, TARGET_AUX_RECURSOR_NAME)
    if (control_rec["levelParams"] != [OLD_UNIVERSE_NAME]
            or candidate_rec["levelParams"] != [OLD_UNIVERSE_NAME]
            or aux_rec["levelParams"] != [OLD_UNIVERSE_NAME]
            or NEW_UNIVERSE_NAME in control_rec["levelParams"]):
        raise AuditError("owning recursor vector does not bind only v")
    control_root = control_rec["rules"][0]["rhs"]
    candidate_root = candidate_rec["rules"][0]["rhs"]
    if control_root != TARGET_RULE_ROOT or candidate_root != clone_map[TARGET_RULE_ROOT]:
        raise AuditError("rule roots do not match the fixed mutation")
    control_levels = collect_levels(control, control_root)
    candidate_levels = collect_levels(candidate, candidate_root)
    if (OLD_UNIVERSE_LEVEL not in control_levels or NEW_UNIVERSE_LEVEL in control_levels
            or NEW_UNIVERSE_LEVEL not in candidate_levels or OLD_UNIVERSE_LEVEL in candidate_levels):
        raise AuditError("rule subtree does not consistently separate v and u")

    differences = scalar_differences(control, candidate)
    expected_pointer = f"/{block_index}/inductive/recs/1/rules/0/rhs"
    expected_difference = [{
        "pointer": expected_pointer,
        "control": TARGET_RULE_ROOT,
        "candidate": clone_map[TARGET_RULE_ROOT],
    }]
    if differences != expected_difference:
        raise AuditError(f"pair has an unexpected difference: {differences}")

    theorem_matches = []
    for row in control:
        theorem = row.get("thm")
        if theorem and names[theorem["name"]] == "LALNest.mainConsumer_iota":
            theorem_matches.append(theorem)
    if len(theorem_matches) != 1 or theorem_matches[0]["levelParams"] != []:
        raise AuditError("downstream observer does not exclude u")
    theorem = theorem_matches[0]
    index = expression_index(control)
    constants = []
    for ident in reachable(index, theorem["type"]):
        constant = index[ident].get("const")
        if constant:
            constants.append((constant["name"], constant["us"]))
    if ((TARGET_RECURSOR_NAME, [1]) not in constants
            or (TARGET_AUX_RECURSOR_NAME, [1]) not in constants):
        raise AuditError("observer does not expose the fixed level-1 main/auxiliary reduction")

    return {
        "schema_version": 1,
        "base": {"path": str(BASE.relative_to(ROOT)), "sha256": BASE_SHA256},
        "control": {"path": str(CONTROL.relative_to(ROOT))},
        "candidate": {"path": str(CANDIDATE.relative_to(ROOT))},
        "records": {"base": 203, "control": len(control), "candidate": len(candidate)},
        "target": {
            "type": "LALNest", "numNested": 1,
            "recursor": "LALNest.rec", "auxiliary_recursor": "LALNest.rec_1",
            "declared_universes": ["v"], "candidate_rule_free_universe": "u",
            "control_rule_root": control_root, "candidate_rule_root": candidate_root,
            "control_rule_levels": sorted(control_levels),
            "candidate_rule_levels": sorted(candidate_levels),
        },
        "pair_differences": differences,
        "observer": {
            "declaration": "LALNest.mainConsumer_iota",
            "declared_universes": [],
            "application_level": "1",
            "neutral_children": True,
            "abstract_motives_and_minors": True,
            "expected_control_reduct": "node children (LALNest.rec_1.{1} motive_1 motive_2 node mk children)",
            "expected_candidate_reduct": "node children (LALNest.rec_1.{u} motive_1 motive_2 node mk children)",
        },
        "reconstruction": {
            "fresh_universe": "u",
            "control_alignment": "R(v)[v := u] = R(u)",
            "candidate_alignment": "R(u)[v := u] = R(u)",
            "runtime_substitution": "recursor vector [v] is instantiated; candidate-only u survives",
        },
    }


def bind_outputs(report: dict[str, Any], control_raw: bytes, candidate_raw: bytes) -> None:
    report["control"].update({"sha256": hashlib.sha256(control_raw).hexdigest(),
                              "bytes": len(control_raw)})
    report["candidate"].update({"sha256": hashlib.sha256(candidate_raw).hexdigest(),
                                "bytes": len(candidate_raw)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    control, candidate, clone_map = build_pair()
    report = audit(control, candidate, clone_map)
    control_raw, candidate_raw = encoded(control), encoded(candidate)
    bind_outputs(report, control_raw, candidate_raw)
    audit_raw = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")
    expected = {CONTROL: control_raw, CANDIDATE: candidate_raw, AUDIT: audit_raw}
    if args.check:
        for path, raw in expected.items():
            if not path.is_file() or path.read_bytes() != raw:
                raise AuditError(f"generated output is stale: {path.relative_to(ROOT)}")
    else:
        if any(path.exists() for path in expected):
            raise AuditError("refusing to overwrite a generated fixture or audit")
        for path, raw in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
