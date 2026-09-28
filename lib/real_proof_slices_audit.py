"""Independent, negative-capable audit of retained-source declaration slices.

This module deliberately does not import the slice producer. It streams the
original export, indexes only identifiers and file offsets, derives the least
dependency closure, and reconstructs the expected compact export independently.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SPECS = {
    "init": (324561407, "02a2260b17c8e5be2eb0463c7d3131c35889337b51817f56756faee1241b7b91"),
    "std": (551674936, "0f7993829d6fcc8b07d177a3879024fbbc8908f7c6fd9cb2fa93370e4397e204"),
    "cedar": (829313103, "baff5ac59983ad30481a4d3b2d5f8cbcd665aebad43a3931f833cdac4c840f05"),
}
TAGS = {"meta", "str", "num", "succ", "max", "imax", "param", "bvar", "sort", "const", "app", "lam", "forallE", "letE", "proj", "natVal", "strVal", "mdata", "axiom", "def", "thm", "opaque", "quot", "inductive"}
DECLS = {"axiom", "def", "thm", "opaque", "quot", "inductive"}


class AuditError(ValueError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bound_selection(source: str, slot: int) -> tuple[int, str, dict[str, Any]]:
    base = ROOT / "results/research/real-proof-slices-pilot-1"
    protocol_bytes = (base / "protocol.json").read_bytes()
    protocol = json.loads(protocol_bytes)
    scientific = json.loads((base / "scientific-manifest.json").read_bytes())
    if (protocol.get("schema") != "real-proof-slices-protocol-v1"
            or scientific.get("schema") != "real-proof-slices-scientific-manifest-v1"
            or scientific.get("protocol_sha256") != _sha(protocol_bytes)
            or scientific.get("selection_rule") != protocol.get("selection")):
        raise AuditError("protocol/scientific-manifest binding mismatch")
    selection = protocol["selection"]
    if (selection.get("per_source") != 4 or selection.get("order") != ["init", "std", "cedar"]
            or selection.get("freeze_before_observation") is not True
            or selection.get("replacement_after_outcome") is not False):
        raise AuditError("unexpected fixed selection contract")
    sources = {item["id"]: item for item in protocol["source_contract"]["sources"]}
    science = {item["source"]: item for item in scientific["sources"]}
    if set(sources) != set(SOURCE_SPECS) or set(science) != set(SOURCE_SPECS):
        raise AuditError("source set differs from fixed scientific scope")
    expected_bytes, expected_hash = SOURCE_SPECS[source]
    if (sources[source]["path"] != f"external/lean-kernel-arena/_build/tests/{source}.ndjson"
            or sources[source]["bytes"] != expected_bytes
            or sources[source]["sha256"] != expected_hash
            or science[source]["source_path"] != sources[source]["path"]
            or science[source]["source_bytes"] != expected_bytes
            or science[source]["source_sha256"] != expected_hash
            or len(science[source]["selected"]) != 4):
        raise AuditError("scientific source identity mismatch")
    skip = selection["skip_first_theorem_records"][source]
    prefix = selection["name_prefix"][source]
    if type(skip) is not int or skip < 0 or not isinstance(prefix, str) or not prefix:
        raise AuditError("invalid frozen selection rule")
    return skip, prefix, science[source]["selected"][slot - 1]


def _kind(row: dict[str, Any]) -> str:
    found = TAGS.intersection(row)
    if len(found) != 1:
        raise AuditError(f"expected exactly one format tag, found {sorted(found)}")
    return next(iter(found))


def _names(row: dict[str, Any], kind: str) -> list[int]:
    if kind == "inductive":
        value = row[kind]
        return [x["name"] for section in ("types", "ctors", "recs") for x in value[section]]
    return [row[kind]["name"]] if kind in DECLS else []


def _references(row: dict[str, Any]) -> tuple[list[tuple[str, int]], list[int]]:
    """Return typed table references and declaration-environment references."""
    tag = _kind(row)
    value = row[tag]
    refs: list[tuple[str, int]] = []
    env: list[int] = []

    def one(space: str, index: Any) -> None:
        if type(index) is not int or index < 0:
            raise AuditError(f"bad {space} index {index!r}")
        refs.append((space, index))

    def many(space: str, indexes: Any) -> None:
        if not isinstance(indexes, list):
            raise AuditError(f"bad {space} index list")
        for index in indexes:
            one(space, index)

    def declaration(obj: dict[str, Any], *, body: bool) -> None:
        one("name", obj["name"])
        many("name", obj["levelParams"])
        one("expr", obj["type"])
        if body:
            one("expr", obj["value"])
            many("name", obj["all"])
            env.extend(obj["all"])

    if tag in {"str", "num"}:
        one("name", value["pre"])
    elif tag == "succ":
        one("level", value)
    elif tag in {"max", "imax"}:
        many("level", value)
    elif tag == "param":
        one("name", value)
    elif tag == "sort":
        one("level", value)
    elif tag == "const":
        one("name", value["name"])
        many("level", value["us"])
        env.append(value["name"])
    elif tag == "app":
        one("expr", value["fn"])
        one("expr", value["arg"])
    elif tag in {"lam", "forallE"}:
        one("name", value["name"])
        one("expr", value["type"])
        one("expr", value["body"])
    elif tag == "letE":
        one("name", value["name"])
        for field in ("type", "value", "body"):
            one("expr", value[field])
    elif tag == "proj":
        one("name", value["typeName"])
        one("expr", value["struct"])
        env.append(value["typeName"])
    elif tag == "mdata":
        one("expr", value["expr"])
    elif tag in {"axiom", "quot"}:
        declaration(value, body=False)
    elif tag in {"def", "thm", "opaque"}:
        declaration(value, body=True)
    elif tag == "inductive":
        for item in value["types"]:
            declaration(item, body=False)
            many("name", item["all"])
            many("name", item["ctors"])
            env.extend(item["all"] + item["ctors"])
        for item in value["ctors"]:
            declaration(item, body=False)
            one("name", item["induct"])
            env.append(item["induct"])
        for item in value["recs"]:
            declaration(item, body=False)
            many("name", item["all"])
            env.extend(item["all"])
            for rule in item["rules"]:
                one("name", rule["ctor"])
                one("expr", rule["rhs"])
                env.append(rule["ctor"])
    # meta, bvar, natVal, and strVal have no typed references.
    return refs, env


def _map_row(original: dict[str, Any], mapping: dict[str, dict[int, int]]) -> dict[str, Any]:
    """Translate source table identifiers; preserve all nonreference fields."""
    row = copy.deepcopy(original)
    tag = _kind(row)
    value = row[tag]

    def one(obj: dict[str, Any], field: str, space: str) -> None:
        try:
            obj[field] = mapping[space][obj[field]]
        except KeyError as exc:
            raise AuditError(f"unmapped {space} reference in {field}") from exc

    def many(obj: dict[str, Any], field: str, space: str) -> None:
        obj[field] = [mapping[space][x] for x in obj[field]]

    def declaration(obj: dict[str, Any], *, body: bool) -> None:
        one(obj, "name", "name")
        many(obj, "levelParams", "name")
        one(obj, "type", "expr")
        if body:
            one(obj, "value", "expr")
            many(obj, "all", "name")

    for space, field in (("name", "in"), ("level", "il"), ("expr", "ie")):
        if field in row:
            one(row, field, space)
    if tag in {"str", "num"}:
        one(value, "pre", "name")
    elif tag in {"succ", "param", "sort"}:
        space = "name" if tag == "param" else "level"
        row[tag] = mapping[space][value]
    elif tag in {"max", "imax"}:
        row[tag] = [mapping["level"][x] for x in value]
    elif tag == "const":
        one(value, "name", "name")
        many(value, "us", "level")
    elif tag == "app":
        one(value, "fn", "expr")
        one(value, "arg", "expr")
    elif tag in {"lam", "forallE"}:
        one(value, "name", "name")
        one(value, "type", "expr")
        one(value, "body", "expr")
    elif tag == "letE":
        one(value, "name", "name")
        for field in ("type", "value", "body"):
            one(value, field, "expr")
    elif tag == "proj":
        one(value, "typeName", "name")
        one(value, "struct", "expr")
    elif tag == "mdata":
        one(value, "expr", "expr")
    elif tag in {"axiom", "quot"}:
        declaration(value, body=False)
    elif tag in {"def", "thm", "opaque"}:
        declaration(value, body=True)
    elif tag == "inductive":
        for item in value["types"]:
            declaration(item, body=False)
            many(item, "all", "name")
            many(item, "ctors", "name")
        for item in value["ctors"]:
            declaration(item, body=False)
            one(item, "induct", "name")
        for item in value["recs"]:
            declaration(item, body=False)
            many(item, "all", "name")
            for rule in item["rules"]:
                one(rule, "ctor", "name")
                one(rule, "rhs", "expr")
    return row


def _same_extraction_boundary(receipt: dict[str, Any], error: AuditError) -> bool:
    if (receipt.get("disposition") != "EXTRACTION_FAILURE"
            or receipt.get("error_type") != "SliceError"
            or not isinstance(receipt.get("error"), str)
            or receipt.get("output_path") is not None
            or receipt.get("output_sha256") is not None
            or receipt.get("would_be_bytes") is not None
            or receipt.get("included_rows") != []
            or receipt.get("record_count") != 0):
        return False
    producer = receipt["error"]
    independent = str(error)
    if independent.startswith("unresolved declaration owner "):
        return producer == independent.replace("unresolved declaration owner", "unresolved environment constant")
    if independent.startswith(("unresolved name:", "unresolved level:", "unresolved expr:")):
        return producer.startswith(independent)
    if independent == "incomplete quotient package":
        return producer == independent or producer == "incomplete quotient package in source prefix"
    return False


def audit_case(receipt_path: str | Path) -> dict[str, Any]:
    """Raise AuditError on any provenance, closure, mapping, or output defect."""
    path = Path(receipt_path)
    receipt = json.loads(path.read_bytes())
    if receipt.get("schema") != "real-proof-slice-receipt-v1":
        raise AuditError("wrong receipt schema")
    source = receipt.get("source")
    if source not in SOURCE_SPECS or receipt.get("case") not in {f"{source}-{i:02d}" for i in range(1, 5)}:
        raise AuditError("unrecognized source or case")
    slot = int(receipt["case"].split("-")[-1])
    expected_bytes, expected_hash = SOURCE_SPECS[source]
    skip, prefix, frozen_selected = _bound_selection(source, slot)
    expected_path = f"external/lean-kernel-arena/_build/tests/{source}.ndjson"
    if (receipt.get("source_path") != expected_path or receipt.get("source_sha256") != expected_hash
            or receipt.get("source_bytes") != expected_bytes):
        raise AuditError("source binding mismatch")
    ceiling = 8_000_000
    row_ceiling = 120_000
    if receipt.get("size_ceiling_bytes") != ceiling or receipt.get("record_ceiling") != row_ceiling:
        raise AuditError("size ceiling mismatch")
    source_file = ROOT / expected_path
    table: dict[str, dict[int, int]] = {"name": {}, "level": {}, "expr": {}}
    owners: dict[int, int] = {}
    positions: dict[int, tuple[int, int]] = {}
    quot_lines: list[int] = []
    quot_kinds: list[str] = []
    expr_tag: dict[int, str] = {}
    rendered_names: dict[int, str] = {0: ""}
    selected: list[dict[str, Any]] = []
    theorem_ordinal = 0
    size = 0
    hasher = hashlib.sha256()
    with source_file.open("rb") as stream:
        for line_no, raw in enumerate(stream, 1):
            offset = size
            size += len(raw)
            hasher.update(raw)
            if len(selected) >= slot:
                continue
            row = json.loads(raw)
            tag = _kind(row)
            positions[line_no] = (offset, len(raw))
            for space, field in (("name", "in"), ("level", "il"), ("expr", "ie")):
                if field in row:
                    ident = row[field]
                    if type(ident) is not int or ident < 0 or ident in table[space]:
                        raise AuditError(f"invalid or duplicate source {space} id")
                    table[space][ident] = line_no
            if "ie" in row:
                expr_tag[row["ie"]] = tag
            if "in" in row:
                if tag not in {"str", "num"}:
                    raise AuditError("name table row has wrong kind")
                component = row[tag]
                parent = rendered_names.get(component["pre"])
                if parent is None:
                    raise AuditError("unresolved name parent during selection")
                child = component["str"] if tag == "str" else component["i"]
                rendered_names[row["in"]] = parent + ("." if parent else "") + str(child)
            for name in _names(row, tag):
                if type(name) is not int or name in owners:
                    raise AuditError("invalid or duplicate declaration owner")
                owners[name] = line_no
            if tag == "quot":
                quot_lines.append(line_no)
                quot_kinds.append(row["quot"].get("kind"))
            if tag == "thm":
                theorem_ordinal += 1
                theorem = row["thm"]
                name = rendered_names.get(theorem["name"])
                if name is None:
                    raise AuditError("unresolved theorem name during selection")
                if (theorem_ordinal > skip and name.startswith(prefix)
                        and expr_tag.get(theorem["type"]) == "forallE"
                        and expr_tag.get(theorem["value"]) == "lam"):
                    selected.append({"slot": len(selected) + 1, "theorem_ordinal": theorem_ordinal,
                                     "source_line": line_no, "source_offset": offset,
                                     "name_id": theorem["name"], "name": name,
                                     "source_row_sha256": _sha(raw)})
    if size != expected_bytes or hasher.hexdigest() != expected_hash:
        raise AuditError("retained source bytes changed")
    if len(selected) != slot:
        raise AuditError("selected theorem unavailable")
    if selected[-1] != frozen_selected:
        raise AuditError("selected theorem differs from frozen scientific manifest")
    target_line, target_name = selected[-1]["source_line"], selected[-1]["name_id"]
    if receipt.get("selected_source_line") != target_line or receipt.get("selected_name_id") != target_name:
        raise AuditError("selected theorem changed")

    needed = {1}
    pending = [target_line]
    with source_file.open("rb") as stream:
        def row_at(line_no: int) -> tuple[dict[str, Any], bytes]:
            if line_no not in positions:
                raise AuditError(f"row {line_no} beyond selected source prefix")
            offset, length = positions[line_no]
            stream.seek(offset)
            raw = stream.read(length)
            if len(raw) != length:
                raise AuditError("source row truncated")
            return json.loads(raw), raw

        try:
            while pending:
                line_no = pending.pop()
                if line_no in needed:
                    continue
                needed.add(line_no)
                row, _ = row_at(line_no)
                typed, environment = _references(row)
                for space, ident in typed:
                    if space in {"name", "level"} and ident == 0:
                        continue
                    if ident not in table[space]:
                        raise AuditError(f"unresolved {space}:{ident}")
                    pending.append(table[space][ident])
                for name in environment:
                    if name not in owners:
                        raise AuditError(f"unresolved declaration owner {name}")
                    pending.append(owners[name])
                if _kind(row) == "quot":
                    if len(quot_lines) != 4 or set(quot_kinds) != {"type", "ctor", "lift", "ind"}:
                        raise AuditError("incomplete quotient package")
                    pending.extend(quot_lines)
        except AuditError as error:
            if _same_extraction_boundary(receipt, error):
                return {"case": receipt["case"], "status": "PASS_EXTRACTION_FAILURE",
                        "source_sha256": expected_hash, "boundary": str(error)}
            raise

        ordered = sorted(needed)
        included = []
        source_rows = []
        for line_no in ordered:
            row, raw = row_at(line_no)
            offset, _ = positions[line_no]
            included.append({"source_line": line_no, "offset": offset, "bytes": len(raw), "sha256": _sha(raw)})
            source_rows.append(row)
    if receipt.get("included_rows") != included or receipt.get("record_count") != len(ordered):
        raise AuditError("included-row provenance or dependency closure mismatch")

    mapping: dict[str, dict[int, int]] = {"name": {0: 0}, "level": {0: 0}, "expr": {}}
    for row in source_rows:
        for space, field in (("name", "in"), ("level", "il"), ("expr", "ie")):
            if field in row:
                mapping[space][row[field]] = len(mapping[space])
    expected_output = b"".join(json.dumps(_map_row(row, mapping), ensure_ascii=False,
                                          separators=(",", ":"), allow_nan=False).encode() + b"\n"
                               for row in source_rows)
    if receipt.get("would_be_bytes") != len(expected_output):
        raise AuditError("would-be size mismatch")
    expected_disposition = "READY" if len(expected_output) <= ceiling and len(ordered) <= row_ceiling else "OVERSIZE"
    if receipt.get("disposition") != expected_disposition:
        raise AuditError("disposition mismatch")
    if expected_disposition == "READY":
        output_path = f"corpus/real-proof-slices-pilot-1/{source}-{slot:02d}.ndjson"
        if receipt.get("output_path") != output_path or receipt.get("output_sha256") != _sha(expected_output):
            raise AuditError("output binding mismatch")
        if (ROOT / output_path).read_bytes() != expected_output:
            raise AuditError("slice bytes differ from independent reconstruction")
    elif receipt.get("output_path") is not None or receipt.get("output_sha256") is not None:
        raise AuditError("oversize receipt claims output")
    return {"case": receipt["case"], "status": "PASS", "source_sha256": expected_hash,
            "closure_rows": len(ordered), "output_sha256": _sha(expected_output)}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("receipts", nargs="+", type=Path)
    args = parser.parse_args()
    for receipt in args.receipts:
        print(json.dumps(audit_case(receipt), sort_keys=True))


if __name__ == "__main__":
    main()
