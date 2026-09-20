"""Bounded typed NDJSON primitive reordering for the representation pilot."""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class TransformError(ValueError):
    pass


SPACE_KEYS = {"in": "name", "il": "level", "ie": "expr"}
SPACE_START = {"name": 1, "level": 1, "expr": 0}
PRIMITIVE_TAGS = {
    "str": "name", "num": "name",
    "succ": "level", "max": "level", "imax": "level", "param": "level",
    "natVal": "expr", "strVal": "expr", "mdata": "expr", "letE": "expr",
    "const": "expr", "app": "expr", "forallE": "expr", "lam": "expr",
    "proj": "expr", "sort": "expr", "bvar": "expr",
}
DECL_TAGS = {"axiom", "def", "thm", "opaque"}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise TransformError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _load(data: bytes) -> list[dict[str, Any]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise TransformError("input is not UTF-8") from error
    if not text.endswith("\n"):
        raise TransformError("input must end in LF")
    rows = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line:
            raise TransformError(f"blank line at {number}")
        try:
            value = json.loads(line, object_pairs_hook=_unique_object)
        except json.JSONDecodeError as error:
            raise TransformError(f"invalid JSON at line {number}: {error}") from error
        if not isinstance(value, dict):
            raise TransformError(f"line {number} is not an object")
        rows.append(value)
    if not rows or set(rows[0]) != {"meta"}:
        raise TransformError("first record must be metadata only")
    return rows


def _exact(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise TransformError(f"{label} fields differ: expected {sorted(keys)}")
    return value


def _integer(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise TransformError(f"{label} must be a nonnegative integer")
    return value


def _integers(value: Any, label: str) -> list[int]:
    if not isinstance(value, list):
        raise TransformError(f"{label} must be an array")
    return [_integer(item, f"{label}[]") for item in value]


def _metadata(row: dict[str, Any]) -> None:
    meta = _exact(row["meta"], {"exporter", "format", "lean"}, "meta")
    exporter = _exact(meta["exporter"], {"name", "version"}, "meta.exporter")
    fmt = _exact(meta["format"], {"version"}, "meta.format")
    lean = _exact(meta["lean"], {"githash", "version"}, "meta.lean")
    for value, label in ((exporter["name"], "exporter.name"),
                         (exporter["version"], "exporter.version"),
                         (fmt["version"], "format.version"),
                         (lean["githash"], "lean.githash"),
                         (lean["version"], "lean.version")):
        if not isinstance(value, str):
            raise TransformError(f"{label} must be a string")
    if fmt["version"] != "3.1.0":
        raise TransformError("only format 3.1.0 is in the frozen domain")


@dataclass(frozen=True)
class Primitive:
    position: int
    row: dict[str, Any]
    tag: str
    space: str
    old_id: int
    references: tuple[tuple[str, int], ...]


def _tag(row: dict[str, Any], candidates: set[str], label: str) -> str:
    tags = set(row).intersection(candidates)
    if len(tags) != 1:
        raise TransformError(f"{label} must contain exactly one known tag")
    return next(iter(tags))


def _primitive(position: int, row: dict[str, Any]) -> Primitive:
    tag = _tag(row, set(PRIMITIVE_TAGS), f"primitive line {position + 1}")
    space = PRIMITIVE_TAGS[tag]
    key = {value: key for key, value in SPACE_KEYS.items()}[space]
    _exact(row, {key, tag}, f"primitive {tag}")
    old_id = _integer(row[key], f"{tag}.{key}")
    value = row[tag]
    refs: list[tuple[str, int]] = []
    if tag == "str":
        value = _exact(value, {"pre", "str"}, tag)
        refs.append(("name", _integer(value["pre"], "str.pre")))
        if not isinstance(value["str"], str): raise TransformError("str.str must be a string")
    elif tag == "num":
        value = _exact(value, {"pre", "i"}, tag)
        refs.append(("name", _integer(value["pre"], "num.pre")))
        _integer(value["i"], "num.i")
    elif tag == "succ":
        refs.append(("level", _integer(value, "succ")))
    elif tag in {"max", "imax"}:
        vals = _integers(value, tag)
        if len(vals) != 2: raise TransformError(f"{tag} needs two operands")
        refs.extend(("level", item) for item in vals)
    elif tag == "param":
        refs.append(("name", _integer(value, "param")))
    elif tag == "natVal":
        if not isinstance(value, str) or not value.isdecimal(): raise TransformError("natVal must be a decimal string")
    elif tag == "strVal":
        if not isinstance(value, str): raise TransformError("strVal must be a string")
    elif tag == "mdata":
        value = _exact(value, {"expr", "data"}, tag)
        refs.append(("expr", _integer(value["expr"], "mdata.expr")))
    elif tag == "letE":
        value = _exact(value, {"name", "type", "value", "body", "nondep"}, tag)
        refs.extend((("name", _integer(value["name"], "letE.name")),
                     ("expr", _integer(value["type"], "letE.type")),
                     ("expr", _integer(value["value"], "letE.value")),
                     ("expr", _integer(value["body"], "letE.body"))))
        if type(value["nondep"]) is not bool: raise TransformError("letE.nondep must be boolean")
    elif tag == "const":
        value = _exact(value, {"name", "us"}, tag)
        refs.append(("name", _integer(value["name"], "const.name")))
        refs.extend(("level", item) for item in _integers(value["us"], "const.us"))
    elif tag == "app":
        value = _exact(value, {"fn", "arg"}, tag)
        refs.extend(("expr", _integer(value[name], f"app.{name}")) for name in ("fn", "arg"))
    elif tag in {"forallE", "lam"}:
        value = _exact(value, {"name", "type", "body", "binderInfo"}, tag)
        refs.extend((("name", _integer(value["name"], f"{tag}.name")),
                     ("expr", _integer(value["type"], f"{tag}.type")),
                     ("expr", _integer(value["body"], f"{tag}.body"))))
        if value["binderInfo"] not in {"default", "implicit", "strictImplicit", "instImplicit"}:
            raise TransformError(f"invalid {tag}.binderInfo")
    elif tag == "proj":
        value = _exact(value, {"typeName", "idx", "struct"}, tag)
        refs.extend((("name", _integer(value["typeName"], "proj.typeName")),
                     ("expr", _integer(value["struct"], "proj.struct"))))
        _integer(value["idx"], "proj.idx")
    elif tag == "sort":
        refs.append(("level", _integer(value, "sort")))
    elif tag == "bvar":
        _integer(value, "bvar")
    return Primitive(position, row, tag, space, old_id, tuple(refs))


def _declaration(row: dict[str, Any], position: int) -> tuple[str, list[tuple[str, int]]]:
    tag = _tag(row, DECL_TAGS, f"declaration line {position + 1}")
    _exact(row, {tag}, f"declaration {tag}")
    value = row[tag]
    common = {"name", "levelParams", "type"}
    if tag == "axiom":
        value = _exact(value, common | {"isUnsafe"}, tag)
    elif tag == "thm":
        value = _exact(value, common | {"value", "all"}, tag)
    elif tag == "opaque":
        value = _exact(value, common | {"value", "isUnsafe", "all"}, tag)
    else:
        value = _exact(value, common | {"value", "hints", "safety", "all"}, tag)
        if value["safety"] not in {"unsafe", "safe", "partial"}: raise TransformError("invalid def.safety")
        hint = value["hints"]
        if isinstance(hint, str):
            if hint not in {"opaque", "abbrev"}: raise TransformError("invalid def.hints")
        else:
            if not isinstance(hint, dict) or set(hint) != {"regular"}: raise TransformError("invalid def.hints")
            _integer(hint["regular"], "def.hints.regular")
    refs = [("name", _integer(value["name"], f"{tag}.name"))]
    refs += [("name", item) for item in _integers(value["levelParams"], f"{tag}.levelParams")]
    refs += [("expr", _integer(value["type"], f"{tag}.type"))]
    if "value" in value: refs.append(("expr", _integer(value["value"], f"{tag}.value")))
    if "all" in value: refs += [("name", item) for item in _integers(value["all"], f"{tag}.all")]
    if "isUnsafe" in value and type(value["isUnsafe"]) is not bool: raise TransformError(f"{tag}.isUnsafe must be boolean")
    return tag, refs


def _parse(data: bytes) -> tuple[list[dict[str, Any]], list[Primitive], list[dict[str, Any]]]:
    rows = _load(data)
    _metadata(rows[0])
    primitives: list[Primitive] = []
    declarations: list[dict[str, Any]] = []
    seen_decl = False
    expected = dict(SPACE_START)
    available = {"name": {0}, "level": {0}, "expr": set()}
    for position, row in enumerate(rows[1:], 1):
        primitive_tags = set(row).intersection(PRIMITIVE_TAGS)
        if primitive_tags:
            if seen_decl: raise TransformError("primitive appears after first declaration")
            item = _primitive(position, row)
            if item.old_id != expected[item.space]:
                raise TransformError(f"non-contiguous {item.space} index {item.old_id}, expected {expected[item.space]}")
            for space, ref in item.references:
                if ref not in available[space]:
                    raise TransformError(f"unresolved or forward {space} reference {ref} at line {position + 1}")
            primitives.append(item)
            available[item.space].add(item.old_id)
            expected[item.space] += 1
        else:
            seen_decl = True
            _, refs = _declaration(row, position)
            for space, ref in refs:
                if ref not in available[space]: raise TransformError(f"unresolved declaration {space} reference {ref}")
            declarations.append(row)
    if not primitives or not declarations:
        raise TransformError("domain requires a nonempty primitive prefix and declarations")
    return rows, primitives, declarations


def _schedule(primitives: list[Primitive], algorithm: str) -> list[Primitive]:
    remaining = list(primitives)
    emitted = {"name": {0}, "level": {0}, "expr": set()}
    order: list[Primitive] = []
    cursor = 0
    spaces = ["name", "level", "expr"]
    while remaining:
        ready = [item for item in remaining if all(ref in emitted[space] for space, ref in item.references)]
        if not ready: raise TransformError("primitive graph has no dependency-respecting schedule")
        if algorithm == "reverse-ready-v1":
            chosen = max(ready, key=lambda item: item.position)
        elif algorithm == "kind-round-robin-v1":
            chosen = None
            for offset in range(3):
                space = spaces[(cursor + offset) % 3]
                candidates = [item for item in ready if item.space == space]
                if candidates:
                    chosen = min(candidates, key=lambda item: item.old_id)
                    cursor = (spaces.index(space) + 1) % 3
                    break
            assert chosen is not None
        else:
            raise TransformError(f"unknown algorithm: {algorithm}")
        order.append(chosen)
        emitted[chosen.space].add(chosen.old_id)
        remaining.remove(chosen)
    return order


def _map_ref(space: str, value: int, mappings: dict[str, dict[int, int]]) -> int:
    if space in {"name", "level"} and value == 0: return 0
    if value not in mappings[space]: raise TransformError(f"unmapped {space} reference {value}")
    return mappings[space][value]


def _rewrite_primitive(item: Primitive, mappings: dict[str, dict[int, int]]) -> dict[str, Any]:
    row = copy.deepcopy(item.row)
    key = {value: key for key, value in SPACE_KEYS.items()}[item.space]
    row[key] = mappings[item.space][item.old_id]
    value = row[item.tag]
    ref = lambda space, old: _map_ref(space, old, mappings)
    if item.tag in {"str", "num"}: value["pre"] = ref("name", value["pre"])
    elif item.tag == "succ": row[item.tag] = ref("level", value)
    elif item.tag in {"max", "imax"}: row[item.tag] = [ref("level", x) for x in value]
    elif item.tag == "param": row[item.tag] = ref("name", value)
    elif item.tag == "mdata": value["expr"] = ref("expr", value["expr"])
    elif item.tag == "letE":
        value["name"] = ref("name", value["name"])
        for name in ("type", "value", "body"): value[name] = ref("expr", value[name])
    elif item.tag == "const":
        value["name"] = ref("name", value["name"])
        value["us"] = [ref("level", x) for x in value["us"]]
    elif item.tag == "app":
        for name in ("fn", "arg"): value[name] = ref("expr", value[name])
    elif item.tag in {"forallE", "lam"}:
        value["name"] = ref("name", value["name"])
        for name in ("type", "body"): value[name] = ref("expr", value[name])
    elif item.tag == "proj":
        value["typeName"] = ref("name", value["typeName"])
        value["struct"] = ref("expr", value["struct"])
    elif item.tag == "sort": row[item.tag] = ref("level", value)
    return row


def _rewrite_declaration(original: dict[str, Any], mappings: dict[str, dict[int, int]]) -> dict[str, Any]:
    row = copy.deepcopy(original)
    tag = next(iter(set(row).intersection(DECL_TAGS)))
    value = row[tag]
    ref = lambda space, old: _map_ref(space, old, mappings)
    value["name"] = ref("name", value["name"])
    value["levelParams"] = [ref("name", x) for x in value["levelParams"]]
    value["type"] = ref("expr", value["type"])
    if "value" in value: value["value"] = ref("expr", value["value"])
    if "all" in value: value["all"] = [ref("name", x) for x in value["all"]]
    return row


def transform_bytes(data: bytes, algorithm: str) -> tuple[bytes, dict[str, Any]]:
    rows, primitives, declarations = _parse(data)
    order = _schedule(primitives, algorithm)
    mappings = {space: {} for space in SPACE_START}
    next_id = dict(SPACE_START)
    for item in order:
        mappings[item.space][item.old_id] = next_id[item.space]
        next_id[item.space] += 1
    out_rows = [copy.deepcopy(rows[0])]
    out_rows += [_rewrite_primitive(item, mappings) for item in order]
    out_rows += [_rewrite_declaration(row, mappings) for row in declarations]
    encoded = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in out_rows) + "\n").encode()
    old_order = [(item.space, item.old_id) for item in primitives]
    new_order = [(item.space, item.old_id) for item in order]
    position_changes = sum(a != b for a, b in zip(old_order, new_order))
    identifier_changes = sum(old != new for space in mappings.values() for old, new in space.items())
    report = {
        "algorithm": algorithm,
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "output_sha256": hashlib.sha256(encoded).hexdigest(),
        "records": len(rows),
        "primitive_records": len(primitives),
        "declarations": len(declarations),
        "old_order": [[space, index] for space, index in old_order],
        "scheduled_old_order": [[space, index] for space, index in new_order],
        "mappings": {space: {str(old): new for old, new in sorted(values.items())} for space, values in mappings.items()},
        "position_changes": position_changes,
        "identifier_changes": identifier_changes,
        "nonidentity": encoded != data and position_changes >= 2 and identifier_changes >= 1,
    }
    return encoded, report


def identity_roundtrip_bytes(data: bytes) -> bytes:
    """Strictly decode and re-encode without changing record order or values."""
    rows, _, _ = _parse(data)
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode()


def transform_file(source: Path, destination: Path, algorithm: str) -> dict[str, Any]:
    encoded, report = transform_bytes(source.read_bytes(), algorithm)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(encoded)
    return report
