"""Deterministic, non-executing audit of the acceptance-impact frozen pair."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ITEM = "ACCEPTANCE-IMPACT-PILOT-1"
OUTPUT = "results/research/acceptance-impact-pilot-1/pair-audit.json"

CANDIDATE = {
    "path": "corpus/generated/nanoda-gen-7b603be7dc87-valid-aux-type.ndjson",
    "bytes": 6332,
    "sha256": "13900d3c26371111800a6c85ba8a9cc3d472beb384cf2c5fde574b8a9e7f36bd",
}
CONTROL = {
    "path": "corpus/generated/nanoda-gen-7b603be7dc87-valid-control.ndjson",
    "bytes": 6332,
    "sha256": "3b66763082822a74a203fb4dda773ff473e853e73077b8f564c603b56e9610ae",
}
HISTORICAL = {
    "path": "results/research/semantic-import-contract-1/historical-observations.json",
    "bytes": 54614,
    "sha256": "35786538b5adb4d4e2d04bb7399685294ea8d0f80326939b22c8c29cb91760db",
}

EXPECTED_DIFFERENCE = {
    "pointer": "/104/inductive/recs/0/type",
    "control": 49,
    "candidate": 68,
}
EXPECTED_NAME_TABLE = {
    "count": 19,
    "sha256": "93bc4e9efc1f75b3b710c403a787f4d43b76c5e5a956454aad7b80893f5868d9",
}
EXPECTED_EXPRESSION_TABLE = {
    "count": 81,
    "sha256": "593d69dac8dfa3c1e8066e60c01850b3d0a28a8a94ebe23130d073a107ad1d74",
}


class PairAuditError(ValueError):
    """A frozen-pair or audit invariant does not hold."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PairAuditError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise PairAuditError(f"non-finite JSON value: {value}")


def canonical_bytes(value: Any) -> bytes:
    try:
        return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                           allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError) as error:
        raise PairAuditError(f"value is not deterministic JSON: {error}") from error


def _object_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe(root: Path, relative: Any) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise PairAuditError("binding path must be repository-relative")
    root = root.resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise PairAuditError(f"binding path escapes repository: {relative}") from error
    return path


def verify_binding(root: Path, binding: Any) -> tuple[Path, bytes]:
    if (not isinstance(binding, dict)
            or set(binding) != {"path", "bytes", "sha256"}
            or type(binding["bytes"]) is not int or binding["bytes"] < 0
            or not isinstance(binding["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", binding["sha256"]) is None):
        raise PairAuditError("invalid file binding")
    path = _safe(root, binding["path"])
    if not path.is_file() or path.is_symlink():
        raise PairAuditError(f"bound file is missing or a symlink: {binding['path']}")
    raw = path.read_bytes()
    if len(raw) != binding["bytes"] or hashlib.sha256(raw).hexdigest() != binding["sha256"]:
        raise PairAuditError(f"file binding mismatch: {binding['path']}")
    return path, raw


def _loads(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                          parse_constant=_nonfinite)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PairAuditError(f"invalid JSON in {label}: {error}") from error


def _load_ndjson(raw: bytes, label: str) -> list[dict[str, Any]]:
    if not raw.endswith(b"\n"):
        raise PairAuditError(f"{label} must end with one newline")
    lines = raw.splitlines()
    if not lines:
        raise PairAuditError(f"{label} is empty")
    records = [_loads(line, f"{label}:{index}") for index, line in enumerate(lines, 1)]
    if any(not isinstance(record, dict) for record in records):
        raise PairAuditError(f"{label} contains a non-object record")
    return records


def _differences(control: Any, candidate: Any, pointer: str = "") -> list[dict[str, Any]]:
    if type(control) is not type(candidate):
        return [{"pointer": pointer, "control": control, "candidate": candidate}]
    if isinstance(control, dict):
        if set(control) != set(candidate):
            raise PairAuditError(f"structural key difference at {pointer or '/'}")
        return [difference for key in sorted(control)
                for difference in _differences(control[key], candidate[key], f"{pointer}/{key}")]
    if isinstance(control, list):
        if len(control) != len(candidate):
            raise PairAuditError(f"structural length difference at {pointer or '/'}")
        return [difference for index, (left, right) in enumerate(zip(control, candidate))
                for difference in _differences(left, right, f"{pointer}/{index}")]
    return [] if control == candidate else [
        {"pointer": pointer, "control": control, "candidate": candidate}
    ]


def _tables(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return ([record for record in records if "in" in record],
            [record for record in records if "ie" in record])


def _decode(records: list[dict[str, Any]]) -> tuple[dict[int, str], dict[int, dict[str, Any]]]:
    names = {0: "<anonymous>"}
    expressions: dict[int, dict[str, Any]] = {}
    for record in records:
        if "in" in record:
            identifier = record["in"]
            if type(identifier) is not int or identifier <= 0 or identifier in names:
                raise PairAuditError("invalid or duplicate name identifier")
            variants = [key for key in ("str", "num") if key in record]
            if len(variants) != 1 or not isinstance(record[variants[0]], dict):
                raise PairAuditError(f"invalid name payload for id {identifier}")
            value = record[variants[0]]
            prefix = value.get("pre")
            if type(prefix) is not int or prefix not in names:
                raise PairAuditError(f"unknown name prefix for id {identifier}")
            if variants[0] == "str":
                component = value.get("str")
                if not isinstance(component, str):
                    raise PairAuditError(f"invalid string name component for id {identifier}")
            else:
                component = value.get("i")
                if type(component) is not int or component < 0:
                    raise PairAuditError(f"invalid numeric name component for id {identifier}")
                component = str(component)
            names[identifier] = component if prefix == 0 else names[prefix] + "." + component
        if "ie" in record:
            identifier = record["ie"]
            if type(identifier) is not int or identifier < 0 or identifier in expressions:
                raise PairAuditError("invalid or duplicate expression identifier")
            expressions[identifier] = record
    return names, expressions


def _expression_text(identifier: int, names: dict[int, str],
                     expressions: dict[int, dict[str, Any]]) -> str:
    if identifier not in expressions:
        raise PairAuditError(f"unknown expression id {identifier}")
    record = expressions[identifier]
    if "bvar" in record:
        return "#" + str(record["bvar"])
    if "sort" in record:
        return "Sort(level-id=" + str(record["sort"]) + ")"
    if "const" in record:
        constant = record["const"]
        return names[constant["name"]] + ".{" + ",".join(map(str, constant["us"])) + "}"
    if "app" in record:
        return "(" + _expression_text(record["app"]["fn"], names, expressions) + " " \
            + _expression_text(record["app"]["arg"], names, expressions) + ")"
    raise PairAuditError(f"unsupported selected expression {identifier}")


def _spine(identifier: int, names: dict[int, str],
           expressions: dict[int, dict[str, Any]]) -> dict[str, Any]:
    start = identifier
    binders = []
    while "forallE" in expressions.get(identifier, {}):
        node = expressions[identifier]["forallE"]
        binders.append({
            "expression_id": identifier,
            "name_id": node["name"],
            "name": names[node["name"]],
            "binder_info": node["binderInfo"],
            "type_id": node["type"],
        })
        identifier = node["body"]
    if not binders:
        raise PairAuditError(f"expression {start} has no manifest Pi spine")
    return {
        "expression_id": start,
        "manifest_pi_arity": len(binders),
        "binders": binders,
        "final_binder_type": _expression_text(binders[-1]["type_id"], names, expressions),
        "terminal_expression_id": identifier,
        "terminal_expression": _expression_text(identifier, names, expressions),
    }


def _declarations(records: list[dict[str, Any]], names: dict[int, str]) -> list[dict[str, Any]]:
    rows = []
    for record_index, record in enumerate(records):
        if "inductive" not in record:
            continue
        inductive = record["inductive"]
        for kind in ("types", "ctors", "recs"):
            for index, declaration in enumerate(inductive.get(kind, [])):
                rows.append({
                    "pointer": f"/{record_index}/inductive/{kind}/{index}",
                    "kind": kind,
                    "name": names[declaration["name"]],
                    "type_id": declaration["type"],
                })
    return rows


def _table_summary(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    names, expressions = _tables(records)
    return {
        "names": {"count": len(names), "sha256": _object_digest(names)},
        "expressions": {"count": len(expressions), "sha256": _object_digest(expressions)},
    }


def audit_pair(root: Path, candidate_binding: dict[str, Any] = CANDIDATE,
               control_binding: dict[str, Any] = CONTROL) -> dict[str, Any]:
    _, candidate_raw = verify_binding(root, candidate_binding)
    _, control_raw = verify_binding(root, control_binding)
    candidate_records = _load_ndjson(candidate_raw, candidate_binding["path"])
    control_records = _load_ndjson(control_raw, control_binding["path"])
    if len(candidate_records) != 105 or len(control_records) != 105:
        raise PairAuditError("frozen pair must contain exactly 105 records each")

    differences = _differences(control_records, candidate_records)
    if differences != [EXPECTED_DIFFERENCE]:
        raise PairAuditError(f"frozen pair scalar difference changed: {differences!r}")

    candidate_names_raw, candidate_expressions_raw = _tables(candidate_records)
    control_names_raw, control_expressions_raw = _tables(control_records)
    if (candidate_names_raw != control_names_raw
            or candidate_expressions_raw != control_expressions_raw):
        raise PairAuditError("name or expression tables differ between pair members")
    table_summary = _table_summary(control_records)
    if (table_summary["names"] != EXPECTED_NAME_TABLE
            or table_summary["expressions"] != EXPECTED_EXPRESSION_TABLE):
        raise PairAuditError("frozen name or expression table changed")

    control_names, control_expressions = _decode(control_records)
    candidate_names, candidate_expressions = _decode(candidate_records)
    if control_names != candidate_names or control_expressions != candidate_expressions:
        raise PairAuditError("decoded name or expression tables differ")

    control_declarations = _declarations(control_records, control_names)
    candidate_declarations = _declarations(candidate_records, candidate_names)
    pointer = "/104/inductive/recs/0"
    control_changed = next((row for row in control_declarations if row["pointer"] == pointer), None)
    candidate_changed = next((row for row in candidate_declarations if row["pointer"] == pointer), None)
    changed = {
        "pointer": pointer,
        "name": "LALNest.rec_1",
        "control_type_id": 49,
        "candidate_type_id": 68,
    }
    if (control_changed is None or candidate_changed is None
            or control_changed["name"] != changed["name"]
            or candidate_changed["name"] != changed["name"]
            or control_changed["type_id"] != changed["control_type_id"]
            or candidate_changed["type_id"] != changed["candidate_type_id"]):
        raise PairAuditError("changed declaration identity or type pointer changed")

    selected = {49, 68}
    references = {
        "control": [row for row in control_declarations if row["type_id"] in selected],
        "candidate": [row for row in candidate_declarations if row["type_id"] in selected],
    }
    expected_references = {
        "control": [
            {"pointer": "/104/inductive/recs/0", "kind": "recs",
             "name": "LALNest.rec_1", "type_id": 49},
            {"pointer": "/104/inductive/recs/1", "kind": "recs",
             "name": "LALNest.rec", "type_id": 68},
        ],
        "candidate": [
            {"pointer": "/104/inductive/recs/0", "kind": "recs",
             "name": "LALNest.rec_1", "type_id": 68},
            {"pointer": "/104/inductive/recs/1", "kind": "recs",
             "name": "LALNest.rec", "type_id": 68},
        ],
    }
    if references != expected_references:
        raise PairAuditError("direct declaration type-reference set changed")

    spines = {
        "control_type_49": _spine(49, control_names, control_expressions),
        "candidate_type_68": _spine(68, candidate_names, candidate_expressions),
    }
    control_spine, candidate_spine = spines.values()
    if (control_spine["manifest_pi_arity"] != 5
            or candidate_spine["manifest_pi_arity"] != 5
            or [row["name"] for row in control_spine["binders"]]
            != ["motive_1", "motive_2", "node", "mk", "t"]
            or [row["name"] for row in candidate_spine["binders"]]
            != ["motive_1", "motive_2", "node", "mk", "t"]
            or control_spine["final_binder_type"] != "(LALWrap.{} LALNest.{})"
            or candidate_spine["final_binder_type"] != "LALNest.{}"
            or control_spine["terminal_expression"] != "(#3 #0)"
            or candidate_spine["terminal_expression"] != "(#4 #0)"):
        raise PairAuditError("selected recursor type spine changed")

    byte_differences = [
        {"offset_1_based": index + 1, "control_byte": left, "candidate_byte": right}
        for index, (left, right) in enumerate(zip(control_raw, candidate_raw)) if left != right
    ]
    if byte_differences != [
        {"offset_1_based": 5982, "control_byte": 52, "candidate_byte": 54},
        {"offset_1_based": 5983, "control_byte": 57, "candidate_byte": 56},
    ]:
        raise PairAuditError("raw byte difference changed")

    return {
        "candidate": dict(candidate_binding),
        "control": dict(control_binding),
        "record_counts": {"candidate": len(candidate_records), "control": len(control_records)},
        "raw_byte_differences": byte_differences,
        "scalar_differences": differences,
        "name_and_expression_nodes_unchanged": True,
        "tables": table_summary,
        "changed_declaration": changed,
        "direct_type_references": references,
        "type_spines": spines,
    }


def _historical_context(root: Path, pair: dict[str, Any]) -> dict[str, Any]:
    _, raw = verify_binding(root, HISTORICAL)
    history = _loads(raw, HISTORICAL["path"])
    cases = history.get("cases") if isinstance(history, dict) else None
    if not isinstance(cases, list):
        raise PairAuditError("historical evidence has no cases list")
    matches = [(index, case) for index, case in enumerate(cases)
               if isinstance(case, dict) and case.get("boundary") == "restored_aux_recursor_type"]
    if len(matches) != 1:
        raise PairAuditError("historical recursor-type case is not unique")
    index, case = matches[0]
    historical_pair = case.get("pair", {})
    if (historical_pair.get("candidate") != pair["candidate"]
            or historical_pair.get("control") != pair["control"]
            or historical_pair.get("scalar_differences") != pair["scalar_differences"]
            or historical_pair.get("name_and_expression_nodes_unchanged") is not True):
        raise PairAuditError("historical case does not bind the current frozen pair")

    cross = case.get("cross_validation", {})
    outcomes = [{
        "checker": row.get("checker"),
        "candidate": row.get("candidate_result", {}).get("normalized_outcome"),
        "control": row.get("control_result", {}).get("normalized_outcome"),
    } for row in cross.get("rows", [])]
    expected = [
        {"checker": "official", "candidate": "REJECT", "control": "ACCEPT"},
        {"checker": "lean4lean", "candidate": "REJECT", "control": "ACCEPT"},
        {"checker": "kiota", "candidate": "ACCEPT", "control": "ACCEPT"},
    ]
    if outcomes != expected or history.get("current_checker_execution") is not False \
            or history.get("normative_authority") != "NOT_ESTABLISHED_BY_THIS_AUDIT":
        raise PairAuditError("historical observation scope or outcome changed")
    return {
        "binding": dict(HISTORICAL),
        "case_pointer": f"/cases/{index}",
        "boundary": case["boundary"],
        "observation_created_at": cross.get("created_at"),
        "observer_outcomes": outcomes,
        "normative_authority": "NOT_ESTABLISHED_BY_THIS_AUDIT",
        "current_checker_execution": False,
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    pair = audit_pair(root)
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "method": "Strictly parse, hash and compare the retained NDJSON pair and bind dated historical receipts; launch no checker.",
        "current_checker_execution": False,
        "pair": pair,
        "historical_context": _historical_context(root, pair),
        "checks": [
            "exact file bindings",
            "duplicate-key-free NDJSON",
            "exactly one directed scalar difference",
            "unchanged fixed name and expression tables",
            "changed declaration identity and direct type references",
            "five-binder type-49 and type-68 spines",
            "dated historical receipt binding",
        ],
        "limits": [
            "This audit makes no current checker observation.",
            "Shared expression 68 is graph structure, not semantic authority or a harmlessness proof.",
            "Historical observer agreement or disagreement is dated context, not a normative contract.",
        ],
    }


def check(root: Path = ROOT) -> dict[str, Any]:
    expected = canonical_bytes(build(root))
    output = _safe(root, OUTPUT)
    if output.is_symlink() or not output.is_file() or output.read_bytes() != expected:
        raise PairAuditError(f"stale generated pair audit: {OUTPUT}")
    return {"item_id": ITEM, "status": "PASS", "output": OUTPUT,
            "current_checker_execution": False}


def write(root: Path = ROOT) -> dict[str, Any]:
    output = _safe(root, OUTPUT)
    if output.is_symlink():
        raise PairAuditError(f"refuse symlink output: {OUTPUT}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise PairAuditError(f"refuse existing temporary output: {temporary}")
    with temporary.open("xb") as stream:
        stream.write(canonical_bytes(build(root)))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, output)
    return check(root)
