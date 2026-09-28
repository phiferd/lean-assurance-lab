"""Stream retained lean4export 3.1.0 inputs into dependency-complete slices.

The selection rule and source identities live in the committed protocol. This
module never observes checker results. The separate auditor is deliberately not
imported here.
"""
from __future__ import annotations

import copy
import hashlib
import json
import resource
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "corpus/real-proof-slices-pilot-1"
RECEIPTS = ROOT / "results/research/real-proof-slices-pilot-1/slices"
PROTOCOL_PATH = ROOT / "results/research/real-proof-slices-pilot-1/protocol.json"
SCIENTIFIC_PATH = ROOT / "results/research/real-proof-slices-pilot-1/scientific-manifest.json"
PROTOCOL = json.loads(PROTOCOL_PATH.read_text())
SOURCES = {
    item["id"]: {
        **item,
        "skip_theorems": PROTOCOL["selection"]["skip_first_theorem_records"][item["id"]],
        "name_prefix": PROTOCOL["selection"]["name_prefix"][item["id"]],
    }
    for item in PROTOCOL["source_contract"]["sources"]
}
SOURCE_DIR = ROOT / "external/lean-kernel-arena/_build/tests"
MAX_SLICE_BYTES = PROTOCOL["size_ceiling"]["bytes_per_slice"]
MAX_SLICE_RECORDS = PROTOCOL["size_ceiling"]["records_per_slice"]


class SliceError(ValueError):
    pass


def committed(path: Path) -> None:
    relative = str(path.relative_to(ROOT))
    try:
        content = subprocess.check_output(["git", "show", f"HEAD:{relative}"], cwd=ROOT, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        raise SliceError(f"not committed: {relative}") from exc
    if content != path.read_bytes():
        raise SliceError(f"working file differs from committed bytes: {relative}")


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode() + b"\n"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def row_kind(row: dict[str, Any]) -> str:
    for key in ("meta", "str", "num", "succ", "max", "imax", "param", "bvar", "sort", "const", "app", "lam", "forallE", "letE", "proj", "natVal", "strVal", "mdata", "axiom", "def", "thm", "opaque", "quot", "inductive"):
        if key in row:
            return key
    raise SliceError(f"unsupported record: {list(row)}")


def outputs(row: dict[str, Any]) -> list[int]:
    kind = row_kind(row)
    if kind in {"axiom", "def", "thm", "opaque", "quot"}:
        return [row[kind]["name"]]
    if kind == "inductive":
        val = row[kind]
        return [x["name"] for category in ("types", "ctors", "recs") for x in val[category]]
    return []


def refs(row: dict[str, Any]) -> list[tuple[str, int]]:
    """Enumerate every typed format reference, including redundant metadata."""
    kind = row_kind(row)
    val = row[kind]
    r: list[tuple[str, int]] = []
    def add(space: str, index: int) -> None:
        if type(index) is not int or index < 0:
            raise SliceError(f"invalid {space} reference: {index}")
        r.append((space, index))
    def many(space: str, indexes: list[int]) -> None:
        if not isinstance(indexes, list):
            raise SliceError("expected reference array")
        for index in indexes: add(space, index)
    def decl(v: dict[str, Any], tag: str) -> None:
        add("name", v["name"]); many("name", v["levelParams"]); add("expr", v["type"])
        if tag in {"def", "thm", "opaque"}:
            add("expr", v["value"]); many("name", v["all"])
    if kind == "meta" or kind in {"bvar", "natVal", "strVal"}: pass
    elif kind in {"str", "num"}: add("name", val["pre"])
    elif kind == "succ": add("level", val)
    elif kind in {"max", "imax"}: many("level", val)
    elif kind == "param": add("name", val)
    elif kind == "sort": add("level", val)
    elif kind == "const": add("name", val["name"]); many("level", val["us"])
    elif kind == "app": add("expr", val["fn"]); add("expr", val["arg"])
    elif kind in {"lam", "forallE"}: add("name", val["name"]); add("expr", val["type"]); add("expr", val["body"])
    elif kind == "letE":
        add("name", val["name"])
        for key in ("type", "value", "body"): add("expr", val[key])
    elif kind == "proj": add("name", val["typeName"]); add("expr", val["struct"])
    elif kind == "mdata": add("expr", val["expr"])
    elif kind in {"axiom", "def", "thm", "opaque", "quot"}: decl(val, kind)
    elif kind == "inductive":
        for v in val["types"]:
            decl(v, kind); many("name", v["all"]); many("name", v["ctors"])
        for v in val["ctors"]:
            decl(v, kind); add("name", v["induct"])
        for v in val["recs"]:
            decl(v, kind); many("name", v["all"])
            for rule in v["rules"]: add("name", rule["ctor"]); add("expr", rule["rhs"])
    else: raise SliceError(f"unsupported kind {kind}")
    return r


def environment_refs(row: dict[str, Any]) -> list[int]:
    kind = row_kind(row); val = row[kind]
    if kind == "const": return [val["name"]]
    if kind == "proj": return [val["typeName"]]
    if kind in {"def", "thm", "opaque"}: return val["all"]
    if kind == "inductive":
        return [n for v in val["types"] for n in v["all"]+v["ctors"]] + [v["induct"] for v in val["ctors"]] + [n for v in val["recs"] for n in v["all"]] + [r["ctor"] for v in val["recs"] for r in v["rules"]]
    return []


def remap(row: dict[str, Any], maps: dict[str, dict[int, int]]) -> dict[str, Any]:
    row = copy.deepcopy(row)
    kind = row_kind(row); val = row[kind]
    def one(space: str, old: int) -> int:
        try: return maps[space][old]
        except KeyError as exc: raise SliceError(f"missing remap {space}:{old}") from exc
    def arr(v: dict[str, Any], key: str, space: str) -> None:
        v[key] = [one(space, x) for x in v[key]]
    def field(v: dict[str, Any], key: str, space: str) -> None:
        v[key] = one(space, v[key])
    def decl(v: dict[str, Any], tag: str) -> None:
        field(v,"name","name"); arr(v,"levelParams","name"); field(v,"type","expr")
        if tag in {"def","thm","opaque"}:
            field(v,"value","expr"); arr(v,"all","name")
    if "in" in row: field(row,"in","name")
    if "il" in row: field(row,"il","level")
    if "ie" in row: field(row,"ie","expr")
    if kind in {"str","num"}: field(val,"pre","name")
    elif kind == "succ": row[kind] = one("level",val)
    elif kind in {"max","imax"}: row[kind] = [one("level",x) for x in val]
    elif kind == "param": row[kind] = one("name",val)
    elif kind == "sort": row[kind] = one("level",val)
    elif kind == "const": field(val,"name","name"); arr(val,"us","level")
    elif kind == "app": field(val,"fn","expr"); field(val,"arg","expr")
    elif kind in {"lam","forallE"}: field(val,"name","name"); field(val,"type","expr"); field(val,"body","expr")
    elif kind == "letE":
        field(val,"name","name")
        for key in ("type","value","body"): field(val,key,"expr")
    elif kind == "proj": field(val,"typeName","name"); field(val,"struct","expr")
    elif kind == "mdata": field(val,"expr","expr")
    elif kind in {"axiom","def","thm","opaque","quot"}: decl(val,kind)
    elif kind == "inductive":
        for v in val["types"]:
            decl(v,kind); arr(v,"all","name"); arr(v,"ctors","name")
        for v in val["ctors"]: decl(v,kind); field(v,"induct","name")
        for v in val["recs"]:
            decl(v,kind); arr(v,"all","name")
            for rule in v["rules"]: field(rule,"ctor","name"); field(rule,"rhs","expr")
    return row


def scan_source(source: str) -> tuple[list[dict[str, Any]], list[bytes], list[tuple[int,int]], list[int], str, int]:
    spec = SOURCES[source]
    path = SOURCE_DIR / f"{source}.ndjson"
    rows: list[dict[str, Any]] = []; raw: list[bytes] = []; locations: list[tuple[int,int]] = []
    theorem_count = 0; selected: list[int] = []
    expr_tags: dict[int,str] = {}; names: dict[int,str] = {0:""}
    size = 0; hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for line_no, line in enumerate(stream,1):
            offset = size; size += len(line); hasher.update(line)
            if len(selected) == 4: continue
            row = json.loads(line)
            kind = row_kind(row)
            rows.append(row); raw.append(line); locations.append((line_no,offset))
            if "ie" in row: expr_tags[row["ie"]] = kind
            if "in" in row:
                component = row[kind]
                parent = names[component["pre"]]
                names[row["in"]] = parent + ("." if parent else "") + str(component["str"] if kind == "str" else component["i"])
            if kind == "thm":
                theorem_count += 1
                if (theorem_count > spec["skip_theorems"]
                        and names[row["thm"]["name"]].startswith(spec["name_prefix"])
                        and expr_tags.get(row["thm"]["type"]) == "forallE"
                        and expr_tags.get(row["thm"]["value"]) == "lam"):
                    selected.append(len(rows)-1)
    if size != spec["bytes"] or (spec["sha256"] and hasher.hexdigest() != spec["sha256"]):
        raise SliceError(f"{source} retained source identity mismatch: {size}, {hasher.hexdigest()}")
    if len(selected) != 4: raise SliceError(f"{source}: only {len(selected)} selected theorems")
    return rows,raw,locations,selected,hasher.hexdigest(),size


def inventory_source(source: str) -> dict[str,Any]:
    """Read-only, bounded-memory selection and actual-host RSS preflight."""
    spec=SOURCES[source]
    path=ROOT/spec["path"]
    names={0:""}; expr_tags:dict[int,str]={}; theorem_count=0; selected=[]
    size=0; hasher=hashlib.sha256(); prefix_bytes=None; prefix_rows=None
    max_line=0
    with path.open("rb") as stream:
        for line_no,line in enumerate(stream,1):
            offset=size; size+=len(line); hasher.update(line); max_line=max(max_line,len(line))
            if len(selected)==4: continue
            row=json.loads(line); kind=row_kind(row)
            if "ie" in row: expr_tags[row["ie"]]=kind
            if "in" in row:
                v=row[kind]; parent=names[v["pre"]]
                names[row["in"]]=parent+("." if parent else "")+str(v["str"] if kind=="str" else v["i"])
            if kind=="thm":
                theorem_count+=1; v=row["thm"]; name=names[v["name"]]
                if (theorem_count>spec["skip_theorems"] and name.startswith(spec["name_prefix"])
                    and expr_tags.get(v["type"])=="forallE" and expr_tags.get(v["value"])=="lam"):
                    selected.append({"slot":len(selected)+1,"theorem_ordinal":theorem_count,
                                     "source_line":line_no,"source_offset":offset,
                                     "name_id":v["name"],"name":name,"source_row_sha256":digest(line)})
                    if len(selected)==4: prefix_bytes=size;prefix_rows=line_no
    if size!=spec["bytes"] or hasher.hexdigest()!=spec["sha256"]:
        raise SliceError(f"{source} source identity differs")
    if len(selected)!=4: raise SliceError(f"{source} selected {len(selected)} of four declarations")
    return {"source":source,"source_path":spec["path"],"source_bytes":size,"source_sha256":hasher.hexdigest(),
            "selection_prefix_bytes":prefix_bytes,"selection_prefix_rows":prefix_rows,
            "maximum_line_bytes":max_line,"actual_host_peak_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "selected":selected}


def write_scientific_manifest() -> dict[str,Any]:
    """Freeze twelve identities without constructing or observing a slice."""
    manifest={"schema":"real-proof-slices-scientific-manifest-v1",
              "protocol_sha256":digest(PROTOCOL_PATH.read_bytes()),
              "selection_rule":PROTOCOL["selection"],
              "sources":[inventory_source(source) for source in PROTOCOL["selection"]["order"]]}
    SCIENTIFIC_PATH.parent.mkdir(parents=True,exist_ok=True)
    SCIENTIFIC_PATH.write_bytes(json.dumps(manifest,sort_keys=True,indent=2).encode()+b"\n")
    return manifest


def slice_one(source: str, slot: int, rows: list[dict[str,Any]], raw: list[bytes], locations: list[tuple[int,int]], selected: list[int], source_hash: str, source_size: int) -> dict[str,Any]:
    target = selected[slot-1]
    nodes: dict[str,dict[int,int]] = {"name":{},"level":{},"expr":{}}
    owners: dict[int,int] = {}
    quot_rows: list[int] = []
    for i,row in enumerate(rows[:target+1]):
        for space,key in (("name","in"),("level","il"),("expr","ie")):
            if key in row:
                ident=row[key]
                if ident in nodes[space]: raise SliceError(f"duplicate {space}:{ident}")
                nodes[space][ident]=i
        for name in outputs(row):
            if name in owners: raise SliceError(f"duplicate declaration owner {name}")
            owners[name]=i
        if row_kind(row)=="quot": quot_rows.append(i)
    if quot_rows and len(quot_rows)!=4: raise SliceError("incomplete quotient package in source prefix")
    needed={0}; stack=[target]
    while stack:
        index=stack.pop()
        if index in needed: continue
        needed.add(index)
        row=rows[index]
        for space,ident in refs(row):
            if ident==0 and space in {"name","level"}: continue
            if ident not in nodes[space]: raise SliceError(f"unresolved {space}:{ident} at source row {index}")
            stack.append(nodes[space][ident])
        for name in environment_refs(row):
            if name not in owners: raise SliceError(f"unresolved environment constant {name}")
            stack.append(owners[name])
        if row_kind(row)=="quot": stack.extend(quot_rows)
    ordered=sorted(needed)
    maps={"name":{0:0},"level":{0:0},"expr":{}}
    for index in ordered:
        row=rows[index]
        for space,key in (("name","in"),("level","il"),("expr","ie")):
            if key in row: maps[space][row[key]]=len(maps[space]) if space!="expr" else len(maps[space])
    data=b"".join(canonical(remap(rows[i],maps)) for i in ordered)
    disposition="READY" if len(data)<=MAX_SLICE_BYTES and len(ordered)<=MAX_SLICE_RECORDS else "OVERSIZE"
    case=f"{source}-{slot:02d}"
    output=OUT/f"{case}.ndjson"
    if disposition=="READY":
        output.parent.mkdir(parents=True,exist_ok=True); output.write_bytes(data)
    receipt={
        "schema":"real-proof-slice-receipt-v1","case":case,"source":source,
        "source_path":str((SOURCE_DIR/f"{source}.ndjson").relative_to(ROOT)),"source_sha256":source_hash,"source_bytes":source_size,
        "selected_source_line":locations[target][0],"selected_name_id":rows[target]["thm"]["name"],
        "disposition":disposition,"size_ceiling_bytes":MAX_SLICE_BYTES,"record_ceiling":MAX_SLICE_RECORDS,
        "would_be_bytes":len(data),"record_count":len(ordered),
        "output_path":str(output.relative_to(ROOT)) if disposition=="READY" else None,
        "output_sha256":digest(data) if disposition=="READY" else None,
        "included_rows":[{"source_line":locations[i][0],"offset":locations[i][1],"bytes":len(raw[i]),"sha256":digest(raw[i])} for i in ordered],
    }
    RECEIPTS.mkdir(parents=True,exist_ok=True)
    (RECEIPTS/f"{case}.json").write_bytes(json.dumps(receipt,sort_keys=True,indent=2).encode()+b"\n")
    return {k:receipt[k] for k in ("case","disposition","would_be_bytes","record_count","output_sha256")}


def build() -> list[dict[str,Any]]:
    committed(PROTOCOL_PATH); committed(SCIENTIFIC_PATH)
    scientific=json.loads(SCIENTIFIC_PATH.read_text())
    if scientific["protocol_sha256"]!=digest(PROTOCOL_PATH.read_bytes()):
        raise SliceError("scientific manifest protocol binding differs")
    results=[]
    for source_entry in scientific["sources"]:
        source=source_entry["source"]
        rows,raw,locations,selected,source_hash,source_size=scan_source(source)
        if source_hash!=source_entry["source_sha256"] or source_size!=source_entry["source_bytes"]:
            raise SliceError(f"{source} scientific source identity differs")
        for slot,index in enumerate(selected,1):
            expected=source_entry["selected"][slot-1]
            if (locations[index][0]!=expected["source_line"] or rows[index]["thm"]["name"]!=expected["name_id"]
                    or digest(raw[index])!=expected["source_row_sha256"]):
                raise SliceError(f"{source} selected declaration differs at slot {slot}")
        for slot in range(1,5):
            try:
                results.append(slice_one(source,slot,rows,raw,locations,selected,source_hash,source_size))
            except SliceError as exc:
                index=selected[slot-1];case=f"{source}-{slot:02d}"
                receipt={"schema":"real-proof-slice-receipt-v1","case":case,"source":source,
                         "source_path":str((SOURCE_DIR/f"{source}.ndjson").relative_to(ROOT)),
                         "source_sha256":source_hash,"source_bytes":source_size,
                         "selected_source_line":locations[index][0],"selected_name_id":rows[index]["thm"]["name"],
                         "disposition":"EXTRACTION_FAILURE","error_type":"SliceError","error":str(exc),
                         "size_ceiling_bytes":MAX_SLICE_BYTES,"record_ceiling":MAX_SLICE_RECORDS,
                         "record_count":0,"would_be_bytes":None,"output_path":None,"output_sha256":None,
                         "included_rows":[]}
                RECEIPTS.mkdir(parents=True,exist_ok=True)
                (RECEIPTS/f"{case}.json").write_bytes(json.dumps(receipt,sort_keys=True,indent=2).encode()+b"\n")
                results.append({"case":case,"disposition":"EXTRACTION_FAILURE","error":str(exc)})
    return results
