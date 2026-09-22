"""Independent structural audit for the acceptance-impact Stage-2 artifacts.

This module intentionally does not import the Stage-2 producer.  Its expected
records and graph invariants are an independent transcription of the committed
consequence contract.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ITEM = "ACCEPTANCE-IMPACT-PILOT-1"
CONTRACT = {
    "path": "results/research/acceptance-impact-pilot-1/consequence-contract.json",
    "bytes": 6498,
    "sha256": "7e8299e3a5f0891f31d00dde2824d0d4323735e0023c60699993553f52faf932",
}
OUTPUT = "results/research/acceptance-impact-pilot-1/stage-2-artifact-audit.json"
ARTIFACT_PATHS = {
    "candidate_use": "corpus/acceptance-impact-pilot-1/five-app-candidate.ndjson",
    "control_use": "corpus/acceptance-impact-pilot-1/five-app-control.ndjson",
}
BASES = {
    "candidate_use": {
        "path": "corpus/generated/nanoda-gen-7b603be7dc87-valid-aux-type.ndjson",
        "bytes": 6332,
        "sha256": "13900d3c26371111800a6c85ba8a9cc3d472beb384cf2c5fde574b8a9e7f36bd",
    },
    "control_use": {
        "path": "corpus/generated/nanoda-gen-7b603be7dc87-valid-control.ndjson",
        "bytes": 6332,
        "sha256": "3b66763082822a74a203fb4dda773ff473e853e73077b8f564c603b56e9610ae",
    },
}

COMMON_APPEND: list[dict[str, Any]] = [
    {"in": 20, "str": {"pre": 10, "str": "rec_1_impact"}},
    {"ie": 81, "lam": {"binderInfo": "default", "body": 28, "name": 8, "type": 28}},
    {"ie": 82, "lam": {"binderInfo": "default", "body": 28, "name": 8, "type": 29}},
    {"ie": 83, "lam": {"binderInfo": "default", "body": 2, "name": 17, "type": 28}},
    {"ie": 84, "lam": {"binderInfo": "default", "body": 83, "name": 12, "type": 29}},
    {"ie": 85, "lam": {"binderInfo": "default", "body": 2, "name": 18, "type": 28}},
    {"ie": 86, "lam": {"binderInfo": "default", "body": 85, "name": 4, "type": 28}},
    {"const": {"name": 13, "us": [1]}, "ie": 87},
    {"app": {"arg": 81, "fn": 87}, "ie": 88},
    {"app": {"arg": 82, "fn": 88}, "ie": 89},
    {"app": {"arg": 84, "fn": 89}, "ie": 90},
    {"app": {"arg": 86, "fn": 90}, "ie": 91},
    {"app": {"arg": 2, "fn": 91}, "ie": 92},
]


def _tail(domain: int) -> list[dict[str, Any]]:
    return [
        {"ie": 93,
         "lam": {"binderInfo": "default", "body": 92, "name": 8, "type": domain}},
        {"forallE": {"binderInfo": "default", "body": 28, "name": 8, "type": domain},
         "ie": 94},
        {"def": {"all": [20], "hints": "opaque", "levelParams": [], "name": 20,
                 "safety": "safe", "type": 94, "value": 93}},
    ]


EXPECTED_SUFFIXES = {
    "candidate_use": COMMON_APPEND + _tail(28),
    "control_use": COMMON_APPEND + _tail(29),
}
EXPECTED_DIFFERENCES = [
    {"pointer": "/104/inductive/recs/0/type", "control": 49, "candidate": 68},
    {"pointer": "/118/lam/type", "control": 29, "candidate": 28},
    {"pointer": "/119/forallE/type", "control": 29, "candidate": 28},
]
DECLARATION_KEYS = frozenset(("axiom", "def", "thm", "opaque", "quot", "inductive"))


class Stage2AuditError(ValueError):
    """A Stage-2 artifact or audit invariant does not hold."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Stage2AuditError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise Stage2AuditError(f"non-finite JSON value: {value}")


def canonical_bytes(value: Any) -> bytes:
    try:
        return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                           allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError) as error:
        raise Stage2AuditError(f"value is not deterministic JSON: {error}") from error


def _safe(root: Path, relative: Any) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise Stage2AuditError("binding path must be repository-relative")
    root = root.resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise Stage2AuditError(f"binding path escapes repository: {relative}") from error
    return path


def binding(path: Path, root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    path = Path(path).resolve()
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as error:
        raise Stage2AuditError(f"file is outside audit root: {path}") from error
    if not path.is_file() or path.is_symlink():
        raise Stage2AuditError(f"bound file is missing or a symlink: {relative}")
    raw = path.read_bytes()
    return {"path": relative, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def verify_binding(root: Path, value: Any) -> tuple[Path, bytes]:
    if (not isinstance(value, dict) or set(value) != {"path", "bytes", "sha256"}
            or type(value["bytes"]) is not int or value["bytes"] < 0
            or not isinstance(value["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", value["sha256"]) is None):
        raise Stage2AuditError("invalid file binding")
    path = _safe(root, value["path"])
    if not path.is_file() or path.is_symlink():
        raise Stage2AuditError(f"bound file is missing or a symlink: {value['path']}")
    raw = path.read_bytes()
    if len(raw) != value["bytes"] or hashlib.sha256(raw).hexdigest() != value["sha256"]:
        raise Stage2AuditError(f"file binding mismatch: {value['path']}")
    return path, raw


def _loads(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                          parse_constant=_nonfinite)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise Stage2AuditError(f"invalid JSON in {label}: {error}") from error


def _load_ndjson(raw: bytes, label: str) -> list[dict[str, Any]]:
    if not raw.endswith(b"\n"):
        raise Stage2AuditError(f"{label} must end with one newline")
    lines = raw.splitlines()
    if len(lines) != 121:
        raise Stage2AuditError(f"{label} must contain exactly 121 records")
    rows = [_loads(line, f"{label}:{index}") for index, line in enumerate(lines, 1)]
    if any(not isinstance(row, dict) for row in rows):
        raise Stage2AuditError(f"{label} contains a non-object record")
    return rows


def _differences(control: Any, candidate: Any, pointer: str = "") -> list[dict[str, Any]]:
    if type(control) is not type(candidate):
        return [{"pointer": pointer, "control": control, "candidate": candidate}]
    if isinstance(control, dict):
        if set(control) != set(candidate):
            raise Stage2AuditError(f"structural key difference at {pointer or '/'}")
        return [difference for key in sorted(control)
                for difference in _differences(control[key], candidate[key], f"{pointer}/{key}")]
    if isinstance(control, list):
        if len(control) != len(candidate):
            raise Stage2AuditError(f"structural length difference at {pointer or '/'}")
        return [difference for index, (left, right) in enumerate(zip(control, candidate))
                for difference in _differences(left, right, f"{pointer}/{index}")]
    return [] if control == candidate else [
        {"pointer": pointer, "control": control, "candidate": candidate}
    ]


def _indexes(rows: list[dict[str, Any]]) -> tuple[dict[int, dict[str, Any]], set[int], set[int]]:
    expressions: dict[int, dict[str, Any]] = {}
    names = {0}
    levels = {0}
    for row in rows:
        if "in" in row:
            identifier = row["in"]
            if type(identifier) is not int or identifier <= 0 or identifier in names:
                raise Stage2AuditError("duplicate or invalid name identifier")
            names.add(identifier)
        if "il" in row:
            identifier = row["il"]
            if type(identifier) is not int or identifier <= 0 or identifier in levels:
                raise Stage2AuditError("duplicate or invalid level identifier")
            levels.add(identifier)
        if "ie" in row:
            identifier = row["ie"]
            if type(identifier) is not int or identifier < 0 or identifier in expressions:
                raise Stage2AuditError("duplicate or invalid expression identifier")
            expressions[identifier] = row
    return expressions, names, levels


def _check_backward_references(rows: list[dict[str, Any]]) -> None:
    names = {0}
    levels = {0}
    expressions: set[int] = set()

    def require(values: list[Any], known: set[int], label: str) -> None:
        for value in values:
            if type(value) is not int or value not in known:
                raise Stage2AuditError(f"unresolved or forward {label} reference: {value!r}")

    for row in rows:
        if "in" in row:
            variant = row.get("str", row.get("num"))
            if not isinstance(variant, dict):
                raise Stage2AuditError("invalid name record")
            require([variant.get("pre")], names, "name")
            identifier = row["in"]
            if type(identifier) is not int or identifier <= 0 or identifier in names:
                raise Stage2AuditError("duplicate or invalid name identifier")
            names.add(identifier)
        if "il" in row:
            references: list[Any] = []
            if "succ" in row:
                references = [row["succ"]]
            elif "param" in row:
                require([row["param"]], names, "level-name")
            elif "max" in row:
                references = row["max"]
            elif "imax" in row:
                references = row["imax"]
            require(references, levels, "level")
            identifier = row["il"]
            if type(identifier) is not int or identifier <= 0 or identifier in levels:
                raise Stage2AuditError("duplicate or invalid level identifier")
            levels.add(identifier)
        if "ie" in row:
            references = []
            if "sort" in row:
                require([row["sort"]], levels, "level")
            elif "bvar" in row:
                if type(row["bvar"]) is not int or row["bvar"] < 0:
                    raise Stage2AuditError("invalid bound variable")
            elif "const" in row:
                require([row["const"].get("name")], names, "constant-name")
                require(row["const"].get("us", []), levels, "constant-level")
            elif "app" in row:
                references = [row["app"].get("fn"), row["app"].get("arg")]
            elif "lam" in row:
                require([row["lam"].get("name")], names, "binder-name")
                references = [row["lam"].get("type"), row["lam"].get("body")]
            elif "forallE" in row:
                require([row["forallE"].get("name")], names, "binder-name")
                references = [row["forallE"].get("type"), row["forallE"].get("body")]
            else:
                raise Stage2AuditError(f"unsupported expression record {row['ie']}")
            require(references, expressions, "expression")
            identifier = row["ie"]
            if type(identifier) is not int or identifier < 0 or identifier in expressions:
                raise Stage2AuditError("duplicate or invalid expression identifier")
            expressions.add(identifier)
        for key in (DECLARATION_KEYS - {"inductive"}).intersection(row):
            declaration = row[key]
            if not isinstance(declaration, dict):
                raise Stage2AuditError("invalid declaration record")
            require([declaration.get("name")], names, "declaration-name")
            require(declaration.get("levelParams", []), names, "universe-name")
            if key in {"axiom", "def", "thm", "opaque", "quot"}:
                require([declaration.get("type")], expressions, "declaration-type")
            if key in {"def", "thm", "opaque"}:
                require([declaration.get("value")], expressions, "declaration-value")


def _loose_bvars(identifier: int, expressions: dict[int, dict[str, Any]],
                 depth: int = 0, active: frozenset[tuple[int, int]] = frozenset()) -> set[int]:
    key = (identifier, depth)
    if key in active:
        raise Stage2AuditError("cyclic expression graph")
    row = expressions.get(identifier)
    if row is None:
        raise Stage2AuditError(f"unknown expression {identifier}")
    active = active | {key}
    if "bvar" in row:
        index = row["bvar"]
        return set() if index < depth else {index - depth}
    if "sort" in row or "const" in row:
        return set()
    if "app" in row:
        return (_loose_bvars(row["app"]["fn"], expressions, depth, active)
                | _loose_bvars(row["app"]["arg"], expressions, depth, active))
    for kind in ("lam", "forallE"):
        if kind in row:
            node = row[kind]
            return (_loose_bvars(node["type"], expressions, depth, active)
                    | _loose_bvars(node["body"], expressions, depth + 1, active))
    raise Stage2AuditError(f"unsupported expression for closure audit: {identifier}")


def _domain_support(rows: list[dict[str, Any]]) -> dict[str, Any]:
    expressions, names, _ = _indexes(rows)
    if names != set(range(21)) or set(expressions) != set(range(95)):
        raise Stage2AuditError("name or expression identifier inventory differs")
    if expressions[28] != {"const": {"name": 10, "us": []}, "ie": 28}:
        raise Stage2AuditError("expression 28 is not rigid LALNest")
    if expressions[29] != {"app": {"arg": 28, "fn": 3}, "ie": 29}:
        raise Stage2AuditError("expression 29 is not LALWrap LALNest")
    if expressions[3] != {"const": {"name": 1, "us": []}, "ie": 3}:
        raise Stage2AuditError("expression 29 does not have rigid LALWrap head")
    if rows[3] != {"il": 1, "succ": 0}:
        raise Stage2AuditError("universe level 1 is not the closed successor of level 0")
    if rows[1] != {"in": 1, "str": {"pre": 0, "str": "LALWrap"}} \
            or rows[41] != {"in": 10, "str": {"pre": 0, "str": "LALNest"}}:
        raise Stage2AuditError("frozen inductive names differ")
    type_49 = _pi_spine(49, expressions)
    type_68 = _pi_spine(68, expressions)
    if (type_49["binder_type_ids"] != [31, 32, 38, 44, 29]
            or type_68["binder_type_ids"] != [31, 32, 38, 44, 28]
            or type_49["binder_type_ids"][:4] != type_68["binder_type_ids"][:4]):
        raise Stage2AuditError("type-49/type-68 Pi-domain distinction differs")
    expected_argument_shapes = {
        81: {"ie": 81, "lam": {"binderInfo": "default", "body": 28,
                                "name": 8, "type": 28}},
        82: {"ie": 82, "lam": {"binderInfo": "default", "body": 28,
                                "name": 8, "type": 29}},
        84: {"ie": 84, "lam": {"binderInfo": "default", "body": 83,
                                "name": 12, "type": 29}},
        86: {"ie": 86, "lam": {"binderInfo": "default", "body": 85,
                                "name": 4, "type": 28}},
    }
    if any(expressions[identifier] != expected
           for identifier, expected in expected_argument_shapes.items()):
        raise Stage2AuditError("fixed first-four argument shapes differ")
    return {
        "candidate_domain": {"expression_id": 28, "head_name_id": 10, "head": "LALNest"},
        "control_domain": {"expression_id": 29, "head_name_id": 1,
                           "head": "LALWrap", "argument_expression_id": 28},
        "syntactically_distinct_rigid_heads": True,
        "level_1": {"constructor": "succ", "predecessor_level_id": 0,
                    "closed": True},
        "retained_type_spines": {"type_49": type_49, "type_68": type_68},
        "shared_first_four_pi_domain_ids": [31, 32, 38, 44],
        "fixed_first_four_argument_expression_ids": [81, 82, 84, 86],
        "first_four_instantiated_shapes_audited": True,
        "counterfactual_tail_mismatch": {
            "candidate_fifth_argument_domain": 28,
            "type_49_required_domain": 29,
            "control_fifth_argument_domain": 29,
            "type_68_required_domain": 28,
        },
    }


def _pi_spine(identifier: int, expressions: dict[int, dict[str, Any]]) -> dict[str, Any]:
    start = identifier
    domains: list[int] = []
    while "forallE" in expressions.get(identifier, {}):
        node = expressions[identifier]["forallE"]
        domains.append(node["type"])
        identifier = node["body"]
    return {"expression_id": start, "binder_count": len(domains),
            "binder_type_ids": domains, "terminal_expression_id": identifier}


def _spine(expressions: dict[int, dict[str, Any]]) -> dict[str, Any]:
    identifier = 92
    reverse_arguments: list[int] = []
    application_ids: list[int] = []
    while "app" in expressions.get(identifier, {}):
        application_ids.append(identifier)
        node = expressions[identifier]["app"]
        reverse_arguments.append(node["arg"])
        identifier = node["fn"]
    application_ids.reverse()
    reverse_arguments.reverse()
    if (application_ids != [88, 89, 90, 91, 92]
            or reverse_arguments != [81, 82, 84, 86, 2]
            or expressions.get(identifier) != {"const": {"name": 13, "us": [1]}, "ie": 87}):
        raise Stage2AuditError("five-application recursor spine differs")
    return {
        "head_expression_id": identifier,
        "head_name": "LALNest.rec_1",
        "universe_level_ids": [1],
        "application_expression_ids": application_ids,
        "argument_expression_ids": reverse_arguments,
        "application_count": 5,
    }


def _audit_one(root: Path, role: str, artifact_binding: dict[str, Any]) -> dict[str, Any]:
    _, artifact_raw = verify_binding(root, artifact_binding)
    _, base_raw = verify_binding(root, BASES[role])
    rows = _load_ndjson(artifact_raw, artifact_binding["path"])
    base_rows = _load_ndjson_105(base_raw, BASES[role]["path"])
    if not artifact_raw.startswith(base_raw) or rows[:105] != base_rows:
        raise Stage2AuditError(f"{role} does not preserve the exact 105-record base prefix")
    if rows[105:] != EXPECTED_SUFFIXES[role]:
        raise Stage2AuditError(f"{role} appended records differ from the independent specification")
    _check_backward_references(rows)
    expressions, _, _ = _indexes(rows)
    suffix_declarations = [row for row in rows[105:] if DECLARATION_KEYS.intersection(row)]
    if len(suffix_declarations) != 1 or suffix_declarations[0] != rows[120] or "def" not in rows[120]:
        raise Stage2AuditError(f"{role} must add exactly one final definition")
    constant_occurrences = [row for row in rows[105:] if row.get("const", {}).get("name") == 13]
    if constant_occurrences != [{"const": {"name": 13, "us": [1]}, "ie": 87}]:
        raise Stage2AuditError(f"{role} recursor constant occurrence differs")
    spine = _spine(expressions)
    if _loose_bvars(92, expressions) != {0}:
        raise Stage2AuditError(f"{role} application spine must have exactly fifth-argument bvar 0 loose")
    if _loose_bvars(93, expressions) or _loose_bvars(94, expressions):
        raise Stage2AuditError(f"{role} declaration value or type is not closed")
    domain = 28 if role == "candidate_use" else 29
    if (expressions[93]["lam"]["type"] != domain
            or expressions[94]["forallE"]["type"] != domain
            or expressions[94]["forallE"]["body"] != 28):
        raise Stage2AuditError(f"{role} fifth binder or declaration domain differs")
    return {
        "binding": artifact_binding,
        "base_binding": BASES[role],
        "record_count": len(rows),
        "base_prefix_records": 105,
        "new_name_ids": [20],
        "new_expression_ids": list(range(81, 95)),
        "added_declarations": [{"record_index": 120, "kind": "def",
                                "name_id": 20, "name": "LALNest.rec_1_impact",
                                "type_expression_id": 94, "value_expression_id": 93}],
        "fifth_domain_expression_id": domain,
        "value_and_type_closed": True,
        "all_references_backward_defined": True,
        "spine": spine,
    }


def _load_ndjson_105(raw: bytes, label: str) -> list[dict[str, Any]]:
    if not raw.endswith(b"\n"):
        raise Stage2AuditError(f"{label} must end with one newline")
    lines = raw.splitlines()
    if len(lines) != 105:
        raise Stage2AuditError(f"{label} must contain exactly 105 records")
    rows = [_loads(line, f"{label}:{index}") for index, line in enumerate(lines, 1)]
    if any(not isinstance(row, dict) for row in rows):
        raise Stage2AuditError(f"{label} contains a non-object record")
    return rows


def audit_artifacts(root: Path, artifact_bindings: dict[str, dict[str, Any]]) -> dict[str, Any]:
    root = Path(root).resolve()
    if set(artifact_bindings) != {"candidate_use", "control_use"}:
        raise Stage2AuditError("artifact binding roles differ")
    artifacts = {role: _audit_one(root, role, artifact_bindings[role])
                 for role in ("candidate_use", "control_use")}
    candidate_rows = _load_ndjson(verify_binding(root, artifact_bindings["candidate_use"])[1],
                                  artifact_bindings["candidate_use"]["path"])
    control_rows = _load_ndjson(verify_binding(root, artifact_bindings["control_use"])[1],
                                artifact_bindings["control_use"]["path"])
    differences = _differences(control_rows, candidate_rows)
    if differences != EXPECTED_DIFFERENCES:
        raise Stage2AuditError(f"candidate/control scalar differences changed: {differences!r}")
    if candidate_rows[105:118] != control_rows[105:118] or candidate_rows[120] != control_rows[120]:
        raise Stage2AuditError("candidate/control common append or declaration identity differs")
    domains = _domain_support(control_rows)
    if artifacts["candidate_use"]["spine"] != artifacts["control_use"]["spine"]:
        raise Stage2AuditError("candidate/control application spines differ")
    return {
        "artifacts": artifacts,
        "scalar_differences_control_to_candidate": differences,
        "cross_domain_distinction": domains,
        "same_first_four_arguments": [81, 82, 84, 86],
        "same_fifth_argument_expression_id": 2,
        "same_five_application_spine": True,
        "same_added_declaration_identity": "LALNest.rec_1_impact",
    }


def build(root: Path = ROOT,
          artifact_bindings: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    verify_binding(root, CONTRACT)
    if artifact_bindings is None:
        artifact_bindings = {
            role: binding(root / relative, root) for role, relative in ARTIFACT_PATHS.items()
        }
    structural = audit_artifacts(root, artifact_bindings)
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "stage": "STAGE_2_CONSTRUCTION",
        "method": "Independently parse and audit the two fixed 121-record NDJSON graphs without importing or executing the producer or any observer.",
        "contract": CONTRACT,
        "current_checker_execution": False,
        "structural_audit": structural,
        "checks": [
            "strict duplicate-key-free NDJSON and exact base byte prefixes",
            "exact new name, expression and value-bearing declaration identities",
            "backward-defined references and closed declaration type/value",
            "one recursor constant and exactly five left-associated applications",
            "exact candidate/control scalar differences and shared application spine",
            "rigid cross-domain distinction between LALNest and LALWrap LALNest",
        ],
        "limits": [
            "This audit launches neither checker and makes no acceptance observation.",
            "Syntactic rigid-head distinction is mechanical support for the committed assumption, not universal semantic authority.",
            "The audit establishes a fixed five-application construction, not reduction behavior, falsehood, inconsistency or exploitability.",
        ],
    }


def check(root: Path = ROOT, output: str = OUTPUT,
          artifact_bindings: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    expected = canonical_bytes(build(root, artifact_bindings))
    path = _safe(Path(root), output)
    if path.is_symlink() or not path.is_file() or path.read_bytes() != expected:
        raise Stage2AuditError(f"stale generated Stage-2 audit: {output}")
    return {"item_id": ITEM, "status": "PASS", "output": output,
            "current_checker_execution": False}


def write(root: Path = ROOT, output: str = OUTPUT,
          artifact_bindings: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    path = _safe(root, output)
    if path.is_symlink():
        raise Stage2AuditError(f"refuse symlink output: {output}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise Stage2AuditError(f"refuse existing temporary output: {temporary}")
    value = canonical_bytes(build(root, artifact_bindings))
    with temporary.open("xb") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    return check(root, output, artifact_bindings)
