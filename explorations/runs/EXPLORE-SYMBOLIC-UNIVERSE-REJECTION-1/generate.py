"""Retain three byte-identical controls; change one field in each invalid twin."""
import copy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from lib.metamorphic_ndjson_audit import decode

OLD = HERE.parent / "EXPLORE-SYMBOLIC-UNIVERSE-1"
inputs = HERE / "inputs"
inputs.mkdir(exist_ok=True)
cases = []
for control in json.loads((OLD / "cases.json").read_text()):
    ident = control["id"]
    if ident not in ("P1", "M1", "I1"): continue
    original = (OLD / "inputs" / (ident + ".ndjson")).read_bytes()
    assert hashlib.sha256(original).hexdigest() == control["sha256"]
    for invalid in (False, True):
        case = copy.deepcopy(control)
        case["id"] = ident[0] + "bad" if invalid else ident
        case["pair"] = ident
        case["expected"] = "REJECT" if invalid else "ACCEPT"
        rows = [json.loads(line) for line in original.splitlines()]
        before = copy.deepcopy(rows)
        if invalid:
            if ident == "P1":
                rows[-1]["def"]["levelParams"] = []
                case["params"] = []
                case["reason"] = "The type and value still use u, but u is absent from levelParams. Both validators require every used universe parameter to be declared."
            elif ident == "M1":
                rows[-1]["def"]["type"] = rows[-1]["def"]["value"]
                case["type"] = "(sort (max u v))"
                case["reason"] = "Sort(max u v) has type Sort(succ(max u v)), not Sort(max u v). At u=v=0 the levels are 1 and 0. Noncumulative sort conversion must reject this lower ascription."
            else:
                node = next(r for r in rows if "imax" in r)
                node["max"] = node.pop("imax")
                case["type"] = "(sort (max (succ u) u))"
                case["reason"] = "Pi X:Sort u, X infers Sort(imax(succ u,u)). At u=0 this is Sort0, whereas the max replacement is Sort1. The two symbolic levels are not equivalent."
            assert sum(a != b for a, b in zip(rows, before)) == 1
            raw = ("\n".join(json.dumps(r, separators=(",", ":")) for r in rows) + "\n").encode()
        else:
            raw = original
        assert len(decode(raw).declarations) == 1
        path = inputs / (case["id"] + ".ndjson")
        path.write_bytes(raw)
        cfg = json.loads((OLD / "inputs" / (ident + ".json")).read_text())
        cfg["export_file_path"] = "/universe-rejection-in/" + path.name
        (inputs / (case["id"] + ".json")).write_text(json.dumps(cfg, indent=2) + "\n")
        case.update(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(raw).hexdigest(),
                    control_sha256=control["sha256"], changed_records=int(invalid))
        cases.append(case)
(HERE / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
print("Six exact files structurally audited; three byte-identical controls, three single-record alterations; no checker invoked.")
