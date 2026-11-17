#!/usr/bin/env python3
"""Repair the shifted source-universe parameter reference in revision 2."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parent
SOURCES = {
    "control": (RUN / "inputs/control-r2.ndjson", "4f00cbcbb2f30facdaad9e8da0c9dbab6cd24bd18e5a21d79152b6820056f059"),
    "candidate": (RUN / "inputs/candidate-r2.ndjson", "ef1b8dfd87ddfebd530396401ab90ebc370841c7d09c5bfe01efc4f7f2352b23"),
}
OUTPUTS = {role: RUN / f"inputs/{role}-r3.ndjson" for role in SOURCES}
AUDIT = RUN / "fixture-audit-r3.json"

spec = importlib.util.spec_from_file_location("frozen_prepare_r1", RUN / "prepare.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load frozen semantic audit helpers")
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)


def load(role: str) -> list[dict[str, Any]]:
    path, expected = SOURCES[role]
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise frozen.AuditError(f"revision-2 {role} identity changed")
    return [json.loads(line, object_pairs_hook=frozen.pairs) for line in raw.splitlines()]


def repair(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = copy.deepcopy(rows)
    matches = [row for row in output if row == {"il": 4, "param": 21}]
    if len(matches) != 1:
        raise frozen.AuditError("expected exactly one shifted universe-parameter defect")
    matches[0]["param"] = 22
    return output


def declared_params_are_available(rows: list[dict[str, Any]]) -> None:
    available: set[int] = set()
    for row in rows:
        if "il" in row and "param" in row:
            available.add(row["param"])
        declarations: list[dict[str, Any]] = []
        for key in ("axiom", "def", "thm", "opaque", "quot"):
            if key in row:
                declarations.append(row[key])
        if "inductive" in row:
            for key in ("types", "ctors", "recs"):
                declarations.extend(row["inductive"][key])
        for declaration in declarations:
            missing = set(declaration.get("levelParams", [])) - available
            if missing:
                raise frozen.AuditError(f"declaration uses unavailable universe parameters {sorted(missing)}")


def audit_pair(control: list[dict[str, Any]], candidate: list[dict[str, Any]]) -> dict[str, Any]:
    names = frozen.decode_names(control)
    if names[20] != "u" or names[22] != "u_1":
        raise frozen.AuditError("fresh and source universe names are not distinct")
    for rows in (control, candidate):
        declared_params_are_available(rows)
        params = {(row["il"], row["param"]) for row in rows if "il" in row and "param" in row}
        if not {(2, 6), (3, 20), (4, 22)}.issubset(params):
            raise frozen.AuditError("expected universe parameter levels are absent")
    control_index, control_block = frozen.find_target_block(control)
    candidate_index, candidate_block = frozen.find_target_block(candidate)
    control_rec = frozen.find_recursor(control_block, frozen.TARGET_RECURSOR_NAME)
    candidate_rec = frozen.find_recursor(candidate_block, frozen.TARGET_RECURSOR_NAME)
    control_root = control_rec["rules"][0]["rhs"]
    candidate_root = candidate_rec["rules"][0]["rhs"]
    if frozen.collect_levels(control, control_root) != {2} or frozen.collect_levels(candidate, candidate_root) != {3}:
        raise frozen.AuditError("target rule universe separation changed")
    differences = frozen.scalar_differences(control, candidate)
    expected = [{"pointer": f"/{control_index}/inductive/recs/1/rules/0/rhs",
                 "control": control_root, "candidate": candidate_root}]
    if control_index != candidate_index or differences != expected:
        raise frozen.AuditError(f"revision-3 pair has unexpected differences: {differences}")
    theorem = [row["thm"] for row in control if row.get("thm")
               and names[row["thm"]["name"]] == "LALNest.mainConsumer_iota"]
    if len(theorem) != 1 or theorem[0]["levelParams"] != []:
        raise frozen.AuditError("observer boundary changed")
    return {
        "schema_version": 1,
        "repair_for": "Revision 1 shifted name back-references but omitted the Level.param name field, so the original u_1 parameter level pointed to Eq after insertion. Revision 3 restores that source parameter reference to name 22.",
        "source_revision": 2,
        "changed_rows_per_input": [{"before": {"il": 4, "param": 21}, "after": {"il": 4, "param": 22}}],
        "universe_parameters": {"elimination_v": {"name": 6, "level": 2},
                                "fresh_candidate_u": {"name": 20, "level": 3},
                                "source_u_1": {"name": 22, "level": 4}},
        "declaration_universe_preconditions": "PASS",
        "target": {"type": "LALNest", "numNested": 1, "declared_universes": ["v"],
                   "control_rule_root": control_root, "candidate_rule_root": candidate_root,
                   "control_rule_levels": [2], "candidate_rule_levels": [3],
                   "candidate_rule_free_universe": "u"},
        "observer": {"declaration": "LALNest.mainConsumer_iota", "declared_universes": []},
        "pair_differences": differences,
        "nanoda_parser_constraints": {"continuous_expression_ids": True, "unique_expressions": True}
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    control, candidate = repair(load("control")), repair(load("candidate"))
    report = audit_pair(control, candidate)
    raws = {"control": frozen.encoded(control), "candidate": frozen.encoded(candidate)}
    for role, raw in raws.items():
        report[role] = {"path": str(OUTPUTS[role].relative_to(ROOT)),
                        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    audit_raw = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    expected = {OUTPUTS[role]: raw for role, raw in raws.items()}
    expected[AUDIT] = audit_raw
    if args.check:
        for path, raw in expected.items():
            if not path.is_file() or path.read_bytes() != raw:
                raise frozen.AuditError(f"revision-3 output is stale: {path.relative_to(ROOT)}")
    else:
        if any(path.exists() for path in expected):
            raise frozen.AuditError("refusing to overwrite revision-3 fixture evidence")
        for path, raw in expected.items():
            path.write_bytes(raw)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
