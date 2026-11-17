#!/usr/bin/env python3
"""Canonicalize the frozen semantic fixtures for Nanoda's unique DAG parser."""
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
CONTROL = RUN / "inputs" / "control-r2.ndjson"
CANDIDATE = RUN / "inputs" / "candidate-r2.ndjson"
AUDIT = RUN / "fixture-audit-r2.json"

spec = importlib.util.spec_from_file_location("frozen_prepare_r1", RUN / "prepare.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load frozen revision-1 generator")
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)


def rewrite_expr_refs(value: Any, mapping: dict[int, int]) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, child in value.items():
            if key in frozen.EXPR_KEYS - {"ie"}:
                if type(child) is int:
                    if child not in mapping:
                        raise frozen.AuditError(f"forward or missing expression reference {child}")
                    result[key] = mapping[child]
                elif isinstance(child, list) and all(type(item) is int for item in child):
                    if any(item not in mapping for item in child):
                        raise frozen.AuditError("forward or missing expression list reference")
                    result[key] = [mapping[item] for item in child]
                else:
                    result[key] = rewrite_expr_refs(child, mapping)
            else:
                result[key] = rewrite_expr_refs(child, mapping)
        return result
    if isinstance(value, list):
        return [rewrite_expr_refs(item, mapping) for item in value]
    return value


def canonicalize(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[int, int], int]:
    output: list[dict[str, Any]] = []
    mapping: dict[int, int] = {}
    seen: dict[str, int] = {}
    dropped = 0
    for row in rows:
        if "ie" not in row:
            output.append(rewrite_expr_refs(copy.deepcopy(row), mapping))
            continue
        old = row["ie"]
        if old in mapping:
            raise frozen.AuditError("duplicate expression back-reference before canonicalization")
        payload = rewrite_expr_refs({key: value for key, value in row.items() if key != "ie"}, mapping)
        key = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        if key in seen:
            mapping[old] = seen[key]
            dropped += 1
            continue
        new = len(seen)
        seen[key] = new
        mapping[old] = new
        output.append({"ie": new, **payload})
    return output, mapping, dropped


def audit_pair(control: list[dict[str, Any]], candidate: list[dict[str, Any]],
               control_map: dict[int, int], candidate_map: dict[int, int],
               dropped: tuple[int, int]) -> dict[str, Any]:
    control_block_index, control_block = frozen.find_target_block(control)
    candidate_block_index, candidate_block = frozen.find_target_block(candidate)
    control_rec = frozen.find_recursor(control_block, frozen.TARGET_RECURSOR_NAME)
    candidate_rec = frozen.find_recursor(candidate_block, frozen.TARGET_RECURSOR_NAME)
    control_root = control_rec["rules"][0]["rhs"]
    candidate_root = candidate_rec["rules"][0]["rhs"]
    if control_root != control_map[frozen.TARGET_RULE_ROOT]:
        raise frozen.AuditError("control rule root was not preserved by canonicalization")
    if candidate_root != candidate_map[117]:
        raise frozen.AuditError("candidate rule root was not preserved by canonicalization")
    if frozen.collect_levels(control, control_root) != {2}:
        raise frozen.AuditError("control rule no longer uses only declared level v")
    if frozen.collect_levels(candidate, candidate_root) != {3}:
        raise frozen.AuditError("candidate rule no longer uses only free level u")
    differences = frozen.scalar_differences(control, candidate)
    expected = [{
        "pointer": f"/{control_block_index}/inductive/recs/1/rules/0/rhs",
        "control": control_root,
        "candidate": candidate_root,
    }]
    if control_block_index != candidate_block_index or differences != expected:
        raise frozen.AuditError(f"canonical pair has unexpected differences: {differences}")
    for rows in (control, candidate):
        expressions = [row for row in rows if "ie" in row]
        if [row["ie"] for row in expressions] != list(range(len(expressions))):
            raise frozen.AuditError("canonical expression back-references are not continuous")
        structural = [json.dumps({k: v for k, v in row.items() if k != "ie"},
                                 sort_keys=True, separators=(",", ":")) for row in expressions]
        if len(structural) != len(set(structural)):
            raise frozen.AuditError("canonical export still contains duplicate expressions")
    names = frozen.decode_names(control)
    theorem = [row["thm"] for row in control if row.get("thm")
               and names[row["thm"]["name"]] == "LALNest.mainConsumer_iota"]
    if len(theorem) != 1 or theorem[0]["levelParams"] != []:
        raise frozen.AuditError("observer universe boundary changed")
    return {
        "schema_version": 1,
        "repair_for": "Nanoda parser requires structural uniqueness for expression DAG rows",
        "semantic_source_control": "explorations/runs/EXPLORE-NANODA-NESTED-RECURSOR-UNIVERSE-CAPTURE-1/inputs/control.ndjson",
        "semantic_source_candidate": "explorations/runs/EXPLORE-NANODA-NESTED-RECURSOR-UNIVERSE-CAPTURE-1/inputs/candidate.ndjson",
        "canonicalization": "Replace every structurally duplicate expression with the earlier canonical pointer and rewrite all later references; no declaration or expression meaning changes.",
        "dropped_duplicate_expressions": {"control": dropped[0], "candidate": dropped[1]},
        "records": {"control": len(control), "candidate": len(candidate)},
        "target": {
            "type": "LALNest",
            "numNested": 1,
            "declared_universes": ["v"],
            "control_rule_root": control_root,
            "candidate_rule_root": candidate_root,
            "control_rule_levels": [2],
            "candidate_rule_levels": [3],
            "candidate_rule_free_universe": "u"
        },
        "observer": {"declaration": "LALNest.mainConsumer_iota", "declared_universes": []},
        "pair_differences": differences,
        "nanoda_parser_constraints": {"continuous_expression_ids": True, "unique_expressions": True}
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    original_control, original_candidate, _ = frozen.build_pair()
    control, control_map, control_dropped = canonicalize(original_control)
    candidate, candidate_map, candidate_dropped = canonicalize(original_candidate)
    report = audit_pair(control, candidate, control_map, candidate_map,
                        (control_dropped, candidate_dropped))
    control_raw = frozen.encoded(control)
    candidate_raw = frozen.encoded(candidate)
    report["control"] = {"path": str(CONTROL.relative_to(ROOT)),
                         "sha256": hashlib.sha256(control_raw).hexdigest(), "bytes": len(control_raw)}
    report["candidate"] = {"path": str(CANDIDATE.relative_to(ROOT)),
                           "sha256": hashlib.sha256(candidate_raw).hexdigest(), "bytes": len(candidate_raw)}
    audit_raw = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    expected = {CONTROL: control_raw, CANDIDATE: candidate_raw, AUDIT: audit_raw}
    if args.check:
        for path, raw in expected.items():
            if not path.is_file() or path.read_bytes() != raw:
                raise frozen.AuditError(f"revision-2 output is stale: {path.relative_to(ROOT)}")
    else:
        if any(path.exists() for path in expected):
            raise frozen.AuditError("refusing to overwrite revision-2 fixture evidence")
        for path, raw in expected.items():
            path.write_bytes(raw)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
