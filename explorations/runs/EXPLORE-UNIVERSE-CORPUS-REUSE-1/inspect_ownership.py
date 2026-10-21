"""Static parameter-ownership walk; not a parser or a type checker."""
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from lib.real_proof_slices import refs, row_kind

def inspect(raw):
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    tables = {"expr": {}, "level": {}}
    declarations = []
    for line, row in enumerate(rows, 1):
        for field, space in (("ie", "expr"), ("il", "level")):
            if field in row: tables[space][row[field]] = row
        kind = row_kind(row)
        if kind in {"axiom", "def", "thm", "opaque", "quot"}:
            declarations.append((line, row[kind]))
        elif kind == "inductive":
            declarations += [(line, d) for category in ("types", "ctors", "recs") for d in row[kind][category]]
    results = []
    for line, decl in declarations:
        work = [("expr", decl["type"])]
        if "value" in decl: work.append(("expr", decl["value"]))
        work += [("expr", r["rhs"]) for r in decl.get("rules", [])]
        seen, used, unresolved = set(), set(), []
        while work:
            item = work.pop()
            if item in seen or item == ("level", 0): continue
            seen.add(item)
            space, index = item
            node = tables[space].get(index)
            if node is None:
                unresolved.append(item)
                continue
            if row_kind(node) == "param": used.add(node["param"])
            work += [(s, n) for s, n in refs(node) if s in ("expr", "level")]
        results.append(dict(line=line, declaration_name_index=decl["name"],
            owned=decl["levelParams"], used=sorted(used), missing=sorted(used-set(decl["levelParams"])),
            unresolved=unresolved))
    return results

out = {}
for label in ("nanoda", "arena"):
    with tarfile.open(HERE / (label + "-sources.tar.gz")) as t:
        for m in t.getmembers():
            if m.name.endswith(".ndjson") or m.name.endswith("/export"):
                out[label + "/" + m.name] = inspect(t.extractfile(m).read())
fixtures = json.loads((HERE / "fixture-inventory.json").read_text())
for case in fixtures:
    out["lal/" + case["id"]] = inspect((HERE.parents[2] / case["path"]).read_bytes())
for case in fixtures:
    missing = out["lal/" + case["id"]][0]["missing"]
    assert bool(missing) == (case["id"] == "P1-invalid")
(HERE / "ownership-observations.json").write_text(json.dumps(out, indent=2) + "\n")
for name, rows in out.items():
    print(name, "declarations", len(rows), "missing", sum(bool(r["missing"]) for r in rows),
          "unresolved", sum(bool(r["unresolved"]) for r in rows))
