"""Independent fail-closed structural auditor for the representation pilot.

This module intentionally does not import the transformer or consume its maps.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class AuditError(ValueError):
    pass


PRIMITIVE = {
    "str": ("name", "in"), "num": ("name", "in"),
    "succ": ("level", "il"), "max": ("level", "il"),
    "imax": ("level", "il"), "param": ("level", "il"),
    "natVal": ("expr", "ie"), "strVal": ("expr", "ie"),
    "mdata": ("expr", "ie"), "letE": ("expr", "ie"),
    "const": ("expr", "ie"), "app": ("expr", "ie"),
    "forallE": ("expr", "ie"), "lam": ("expr", "ie"),
    "proj": ("expr", "ie"), "sort": ("expr", "ie"),
    "bvar": ("expr", "ie"),
}
DECLARATIONS = {"axiom", "def", "thm", "opaque"}
START = {"name": 1, "level": 1, "expr": 0}


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out: raise AuditError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _nonfinite(value: str) -> None:
    raise AuditError(f"non-finite JSON number: {value}")


def _exact(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise AuditError(f"{label} fields differ: expected {sorted(fields)}")
    return value


def _nat(value: Any, label: str) -> int:
    if type(value) is not int or value < 0: raise AuditError(f"{label} must be a nonnegative integer")
    return value


def _nats(value: Any, label: str) -> list[int]:
    if not isinstance(value, list): raise AuditError(f"{label} must be an array")
    return [_nat(item, f"{label}[]") for item in value]


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode()


def _digest(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


@dataclass
class Decoded:
    metadata: dict[str, Any]
    nodes: dict[str, dict[int, str]]
    descriptors: dict[str, dict[str, Any]]
    record_order: list[str]
    assigned_by_digest: dict[str, tuple[str, int]]
    declarations: list[Any]
    record_count: int

    def canonical(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata,
            "nodes": {space: sorted(self.descriptors[space].items()) for space in ("name", "level", "expr")},
            "declarations": self.declarations,
        }


def _read(data: bytes) -> list[dict[str, Any]]:
    try: text = data.decode("utf-8")
    except UnicodeDecodeError as error: raise AuditError("input is not UTF-8") from error
    if not text.endswith("\n"): raise AuditError("input must end in LF")
    rows = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line: raise AuditError(f"blank line at {line_no}")
        try:
            row = json.loads(line, object_pairs_hook=_pairs, parse_constant=_nonfinite)
        except json.JSONDecodeError as error:
            raise AuditError(f"invalid JSON at line {line_no}: {error}") from error
        if not isinstance(row, dict): raise AuditError(f"line {line_no} is not an object")
        rows.append(row)
    if not rows or set(rows[0]) != {"meta"}: raise AuditError("first record must be metadata only")
    return rows


def _meta(row: dict[str, Any]) -> dict[str, Any]:
    meta = _exact(row["meta"], {"exporter", "format", "lean"}, "meta")
    exporter = _exact(meta["exporter"], {"name", "version"}, "meta.exporter")
    fmt = _exact(meta["format"], {"version"}, "meta.format")
    lean = _exact(meta["lean"], {"githash", "version"}, "meta.lean")
    for value, label in ((exporter["name"], "exporter.name"), (exporter["version"], "exporter.version"),
                         (fmt["version"], "format.version"), (lean["githash"], "lean.githash"),
                         (lean["version"], "lean.version")):
        if not isinstance(value, str): raise AuditError(f"{label} must be a string")
    if fmt["version"] != "3.1.0": raise AuditError("only format 3.1.0 is supported")
    return meta


def _one_tag(row: dict[str, Any], allowed: set[str], label: str) -> str:
    tags = set(row).intersection(allowed)
    if len(tags) != 1: raise AuditError(f"{label} does not have exactly one known tag")
    return next(iter(tags))


def _lookup(tables: dict[str, dict[int, str]], space: str, index: Any, label: str) -> str:
    idx = _nat(index, label)
    if idx not in tables[space]: raise AuditError(f"unresolved or wrong-space {space} reference {idx} in {label}")
    return tables[space][idx]


def _primitive_descriptor(tag: str, value: Any, tables: dict[str, dict[int, str]]) -> Any:
    get = lambda space, index, label: _lookup(tables, space, index, label)
    if tag == "str":
        value = _exact(value, {"pre", "str"}, tag)
        if not isinstance(value["str"], str): raise AuditError("str.str must be string")
        return ["name", "str", get("name", value["pre"], "str.pre"), value["str"]]
    if tag == "num":
        value = _exact(value, {"pre", "i"}, tag)
        return ["name", "num", get("name", value["pre"], "num.pre"), _nat(value["i"], "num.i")]
    if tag == "succ": return ["level", "succ", get("level", value, "succ")]
    if tag in {"max", "imax"}:
        values = _nats(value, tag)
        if len(values) != 2: raise AuditError(f"{tag} needs two operands")
        return ["level", tag, *(get("level", item, tag) for item in values)]
    if tag == "param": return ["level", "param", get("name", value, "param")]
    if tag == "natVal":
        if not isinstance(value, str) or not value.isdecimal(): raise AuditError("natVal must be decimal string")
        return ["expr", "natVal", value]
    if tag == "strVal":
        if not isinstance(value, str): raise AuditError("strVal must be string")
        return ["expr", "strVal", value]
    if tag == "mdata":
        value = _exact(value, {"expr", "data"}, tag)
        return ["expr", "mdata", get("expr", value["expr"], "mdata.expr"), value["data"]]
    if tag == "letE":
        value = _exact(value, {"name", "type", "value", "body", "nondep"}, tag)
        if type(value["nondep"]) is not bool: raise AuditError("letE.nondep must be boolean")
        return ["expr", "letE", get("name", value["name"], "letE.name"),
                get("expr", value["type"], "letE.type"), get("expr", value["value"], "letE.value"),
                get("expr", value["body"], "letE.body"), value["nondep"]]
    if tag == "const":
        value = _exact(value, {"name", "us"}, tag)
        return ["expr", "const", get("name", value["name"], "const.name"),
                [get("level", item, "const.us") for item in _nats(value["us"], "const.us")]]
    if tag == "app":
        value = _exact(value, {"fn", "arg"}, tag)
        return ["expr", "app", get("expr", value["fn"], "app.fn"), get("expr", value["arg"], "app.arg")]
    if tag in {"forallE", "lam"}:
        value = _exact(value, {"name", "type", "body", "binderInfo"}, tag)
        if value["binderInfo"] not in {"default", "implicit", "strictImplicit", "instImplicit"}:
            raise AuditError(f"invalid {tag}.binderInfo")
        return ["expr", tag, get("name", value["name"], f"{tag}.name"),
                get("expr", value["type"], f"{tag}.type"), get("expr", value["body"], f"{tag}.body"),
                value["binderInfo"]]
    if tag == "proj":
        value = _exact(value, {"typeName", "idx", "struct"}, tag)
        return ["expr", "proj", get("name", value["typeName"], "proj.typeName"),
                _nat(value["idx"], "proj.idx"), get("expr", value["struct"], "proj.struct")]
    if tag == "sort": return ["expr", "sort", get("level", value, "sort")]
    if tag == "bvar": return ["expr", "bvar", _nat(value, "bvar")]
    raise AuditError(f"unsupported primitive tag: {tag}")


def _declaration_descriptor(row: dict[str, Any], tables: dict[str, dict[int, str]]) -> Any:
    tag = _one_tag(row, DECLARATIONS, "declaration")
    _exact(row, {tag}, tag)
    value = row[tag]
    common = {"name", "levelParams", "type"}
    if tag == "axiom": value = _exact(value, common | {"isUnsafe"}, tag)
    elif tag == "thm": value = _exact(value, common | {"value", "all"}, tag)
    elif tag == "opaque": value = _exact(value, common | {"value", "isUnsafe", "all"}, tag)
    else:
        value = _exact(value, common | {"value", "hints", "safety", "all"}, tag)
        if value["safety"] not in {"unsafe", "safe", "partial"}: raise AuditError("invalid def.safety")
        hint = value["hints"]
        if isinstance(hint, str):
            if hint not in {"opaque", "abbrev"}: raise AuditError("invalid def.hints")
        else:
            hint = _exact(hint, {"regular"}, "def.hints")
            _nat(hint["regular"], "def.hints.regular")
    get = lambda space, index, label: _lookup(tables, space, index, label)
    out = {"tag": tag, "name": get("name", value["name"], f"{tag}.name"),
           "levelParams": [get("name", item, f"{tag}.levelParams") for item in _nats(value["levelParams"], f"{tag}.levelParams")],
           "type": get("expr", value["type"], f"{tag}.type")}
    if "value" in value: out["value"] = get("expr", value["value"], f"{tag}.value")
    if "all" in value: out["all"] = [get("name", item, f"{tag}.all") for item in _nats(value["all"], f"{tag}.all")]
    if "isUnsafe" in value:
        if type(value["isUnsafe"]) is not bool: raise AuditError(f"{tag}.isUnsafe must be boolean")
        out["isUnsafe"] = value["isUnsafe"]
    if tag == "def":
        out["hints"] = value["hints"]
        out["safety"] = value["safety"]
    return out


def decode(data: bytes) -> Decoded:
    rows = _read(data)
    metadata = _meta(rows[0])
    implicit_name = _digest(["name", "anon"])
    implicit_level = _digest(["level", "zero"])
    nodes = {"name": {0: implicit_name}, "level": {0: implicit_level}, "expr": {}}
    descriptors: dict[str, dict[str, Any]] = {"name": {}, "level": {}, "expr": {}}
    record_order: list[str] = []
    assigned: dict[str, tuple[str, int]] = {}
    seen_descriptors: dict[str, set[bytes]] = {"name": set(), "level": set(), "expr": set()}
    expected = dict(START)
    declarations: list[Any] = []
    seen_declaration = False
    for line_no, row in enumerate(rows[1:], 2):
        primitive_tags = set(row).intersection(PRIMITIVE)
        if primitive_tags:
            if seen_declaration: raise AuditError("primitive appears after declaration")
            tag = _one_tag(row, set(PRIMITIVE), f"line {line_no}")
            space, index_key = PRIMITIVE[tag]
            _exact(row, {index_key, tag}, f"line {line_no}")
            index = _nat(row[index_key], f"line {line_no}.{index_key}")
            if index != expected[space]: raise AuditError(f"non-contiguous {space} index {index}, expected {expected[space]}")
            descriptor = _primitive_descriptor(tag, row[tag], nodes)
            canonical = _canon(descriptor)
            if canonical in seen_descriptors[space]: raise AuditError(f"duplicate canonical {space} node")
            digest = _digest(descriptor)
            if digest in assigned: raise AuditError("canonical digest collision or duplicate node")
            nodes[space][index] = digest
            descriptors[space][digest] = descriptor
            seen_descriptors[space].add(canonical)
            assigned[digest] = (space, index)
            record_order.append(digest)
            expected[space] += 1
        else:
            seen_declaration = True
            declarations.append(_declaration_descriptor(row, nodes))
    if not record_order or not declarations: raise AuditError("domain requires primitive prefix and declarations")
    return Decoded(metadata, nodes, descriptors, record_order, assigned, declarations, len(rows))


def audit_bytes(original: bytes, variant: bytes, *, require_nonidentity: bool = True) -> dict[str, Any]:
    left = decode(original)
    right = decode(variant)
    canonical_left = left.canonical()
    canonical_right = right.canonical()
    equivalent = canonical_left == canonical_right
    if set(left.assigned_by_digest) != set(right.assigned_by_digest):
        id_changes = None
    else:
        id_changes = sum(left.assigned_by_digest[digest] != right.assigned_by_digest[digest]
                         for digest in left.assigned_by_digest)
    if len(left.record_order) == len(right.record_order):
        position_changes = sum(a != b for a, b in zip(left.record_order, right.record_order))
    else:
        position_changes = None
    nonidentity = original != variant and (position_changes or 0) >= 2 and (id_changes or 0) >= 1
    eligible = equivalent and (nonidentity or not require_nonidentity)
    return {
        "schema_version": 1,
        "equivalent": equivalent,
        "eligible": eligible,
        "require_nonidentity": require_nonidentity,
        "nonidentity": nonidentity,
        "position_changes": position_changes,
        "identifier_changes": id_changes,
        "original": {
            "sha256": hashlib.sha256(original).hexdigest(),
            "canonical_sha256": _digest(canonical_left),
            "records": left.record_count,
            "nodes": {space: len(left.descriptors[space]) for space in left.descriptors},
            "declarations": len(left.declarations),
        },
        "variant": {
            "sha256": hashlib.sha256(variant).hexdigest(),
            "canonical_sha256": _digest(canonical_right),
            "records": right.record_count,
            "nodes": {space: len(right.descriptors[space]) for space in right.descriptors},
            "declarations": len(right.declarations),
        },
    }


def audit_files(original: Path, variant: Path, *, require_nonidentity: bool = True) -> dict[str, Any]:
    return audit_bytes(original.read_bytes(), variant.read_bytes(), require_nonidentity=require_nonidentity)
