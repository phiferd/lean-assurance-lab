"""Structural extraction for the CVC-2 single sort-definition fragment.

This is a deliberately restricted decoder, not a checker, semantic evaluator,
or general lean4export importer. It preserves level syntax without comparing or
normalizing it and exposes no artifact execution interface. Lean metadata is
provenance only. Every parameter in every level record, including unused level
records, must be owned by the final declaration's explicit levelParams list.

Names are flat nonempty strings; name 0 is implicitly anonymous, level 0 is
implicitly zero, and expression 0 may be explicitly defined. References must
already exist in their own namespace. Only one final safe opaque definition,
with sort nodes as its type and value, is supported.
"""

import json


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value):
    raise ValueError(f"non-JSON constant: {value}")


def _fields(value, expected, context):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{context}: expected exactly {sorted(expected)}")


def _id(value, context):
    if type(value) is not int or value < 0:
        raise ValueError(f"{context}: expected a nonnegative integer ID")
    return value


def _string(value, context):
    if type(value) is not str or not value:
        raise ValueError(f"{context}: expected a nonempty string")
    return value


def _reference(value, namespace, context):
    key = _id(value, context)
    if key not in namespace:
        raise ValueError(f"{context}: unresolved or forward reference {key}")
    return namespace[key]


def _new_id(value, namespace, context):
    key = _id(value, context)
    if key in namespace:
        raise ValueError(f"{context}: duplicate namespace ID {key}")
    return key


def _name(value, names, context):
    return _string(_reference(value, names, context), context)


def _header(record):
    _fields(record, {"meta"}, "header")
    meta = record["meta"]
    _fields(meta, {"exporter", "format", "lean"}, "meta")
    _fields(meta["exporter"], {"name", "version"}, "exporter")
    _fields(meta["format"], {"version"}, "format")
    _fields(meta["lean"], {"githash", "version"}, "lean provenance")
    if meta["exporter"] != {"name": "lean4export", "version": "3.1.0"}:
        raise ValueError("unsupported exporter: expected lean4export 3.1.0")
    if meta["format"]["version"] != "3.1.0":
        raise ValueError("unsupported format: expected 3.1.0")
    for key, value in meta["lean"].items():
        _string(value, f"lean provenance {key}")


def _tree(node):
    # Expand shared input references into plain tree data, retaining all tags.
    return [_tree(child) if isinstance(child, tuple) else child for child in node]


def decode_sort_definition(raw: bytes) -> dict:
    """Extract name, params, value_level and type_level from exact input bytes.

    AST nodes are ['zero'], ['succ', child], ['max'/'imax', left, right], or
    ['param', name]. Malformed or unsupported input raises ValueError. A
    successful decode establishes only membership in this structural subset;
    it does not establish semantic validity or validator acceptance.
    """
    if type(raw) is not bytes:
        raise ValueError("input must be bytes")
    try:
        lines = raw.decode("utf-8").split("\n")
    except UnicodeDecodeError as error:
        raise ValueError("input must be UTF-8") from error
    if lines[-1] == "":
        lines.pop()
    if not lines:
        raise ValueError("missing header and definition")
    records = []
    for index, line in enumerate(lines, 1):
        try:
            records.append(json.loads(line, object_pairs_hook=_object,
                                      parse_constant=_constant))
        except ValueError as error:
            raise ValueError(f"line {index}: {error}") from error
    _header(records[0])
    names = {0: None}
    levels = {0: ("zero",)}
    expressions = {}
    used_params = set()
    definition = None

    for index, record in enumerate(records[1:], 1):
        if not isinstance(record, dict):
            raise ValueError(f"record {index + 1}: expected an object")
        if "in" in record:
            _fields(record, {"in", "str"}, "name record")
            key = _new_id(record["in"], names, "name ID")
            _fields(record["str"], {"pre", "str"}, "flat name")
            if _id(record["str"]["pre"], "name prefix") != 0:
                raise ValueError("only flat names with prefix 0 are supported")
            names[key] = _string(record["str"]["str"], "name string")
        elif "il" in record:
            kinds = set(record) - {"il"}
            if len(kinds) != 1 or not kinds <= {"param", "succ", "max", "imax"}:
                raise ValueError("unsupported level record fields")
            key = _new_id(record["il"], levels, "level ID")
            kind = next(iter(kinds))
            value = record[kind]
            if kind == "param":
                param = _name(value, names, "level parameter")
                used_params.add(param)
                node = (kind, param)
            elif kind == "succ":
                node = (kind, _reference(value, levels, "successor level"))
            else:
                if not isinstance(value, list) or len(value) != 2:
                    raise ValueError(f"{kind}: expected two level references")
                node = (kind, *(_reference(child, levels, f"{kind} level")
                                for child in value))
            levels[key] = node
        elif "ie" in record:
            _fields(record, {"ie", "sort"}, "sort expression record")
            key = _new_id(record["ie"], expressions, "expression ID")
            expressions[key] = _reference(record["sort"], levels, "sort level")
        elif "def" in record:
            _fields(record, {"def"}, "definition record")
            if index != len(records) - 1:
                raise ValueError("the single definition must be the final record")
            definition = record["def"]
        else:
            raise ValueError("unsupported record form")

    if definition is None:
        raise ValueError("missing final definition")
    _fields(definition, {"all", "hints", "levelParams", "name", "safety",
                         "type", "value"}, "definition")
    if definition["safety"] != "safe" or definition["hints"] != "opaque":
        raise ValueError("only safe definitions with opaque hints are supported")
    name_id = _id(definition["name"], "definition name")
    name = _name(name_id, names, "definition name")
    all_names = definition["all"]
    if not isinstance(all_names, list) or len(all_names) != 1:
        raise ValueError("definition all must contain exactly its name ID")
    if _id(all_names[0], "definition all") != name_id:
        raise ValueError("definition all must contain exactly its name ID")
    param_ids = definition["levelParams"]
    if not isinstance(param_ids, list):
        raise ValueError("levelParams must be an explicit list")
    params = [_name(key, names, "declared level parameter") for key in param_ids]
    if len(params) != len(set(params)):
        raise ValueError("declared level parameters must be distinct names")
    if not used_params <= set(params):
        raise ValueError("unowned universe parameter in a level record")
    type_level = _reference(definition["type"], expressions, "definition type")
    value_level = _reference(definition["value"], expressions, "definition value")
    return {"name": name, "params": params,
            "value_level": _tree(value_level), "type_level": _tree(type_level)}
