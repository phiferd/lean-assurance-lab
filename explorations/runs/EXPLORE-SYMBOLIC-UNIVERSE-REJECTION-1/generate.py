"""Derive exactly three invalid variants; preserve valid controls byte-for-byte."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from lib.metamorphic_ndjson_audit import decode

OLD = HERE.with_name("EXPLORE-SYMBOLIC-UNIVERSE-1")
old_cases = {c["id"]: c for c in json.loads((OLD / "cases.json").read_text())}
reasons = {
    "P1": "Sort u uses u but the declaration owns no universe parameter; Lean checks parameter membership during sort inference.",
    "M1": "Sort(max u v) infers Sort(succ(max u v)), which is not Sort(max u v); at u=v=0 these levels are 1 and 0.",
    "I1": "Pi X:Sort u, X infers Sort(imax(succ u,u)); at u=0 this is Sort 0, whereas max(succ u,u)=1. The symbolic types cannot be definitionally equal.",
}

def main():
    (HERE / "inputs").mkdir(exist_ok=True)
    cases = []
    for base in ("P1", "M1", "I1"):
        control = (OLD / "inputs" / f"{base}.ndjson").read_bytes()
        assert hashlib.sha256(control).hexdigest() == old_cases[base]["sha256"]
        rows = [json.loads(line) for line in control.splitlines()]
        declaration = rows[-1]["def"]
        if base == "P1":
            declaration["levelParams"] = []
        elif base == "M1":
            declaration["type"] = declaration["value"]
        else:
            type_row = next(r for r in rows if r.get("ie") == declaration["type"])
            level_row = next(r for r in rows if r.get("il") == type_row["sort"])
            level_row["max"] = level_row.pop("imax")
        invalid = ("\n".join(json.dumps(r, separators=(",", ":")) for r in rows) + "\n").encode()
        original_rows = [json.loads(line) for line in control.splitlines()]
        assert sum(a != b for a, b in zip(original_rows, rows)) == 1
        for suffix, raw in (("", control), ("-invalid", invalid)):
            ident = base + suffix
            assert len(decode(raw).declarations) == 1
            case = dict(old_cases[base])
            case.update(id=ident, pair=base, expected="REJECT" if suffix else "ACCEPT",
                        path=str((HERE / "inputs" / f"{ident}.ndjson").relative_to(ROOT)),
                        sha256=hashlib.sha256(raw).hexdigest())
            if suffix:
                case["reason"] = reasons[base]
                if base == "P1":
                    case["params"] = []
                if base == "M1":
                    case["type"] = "(sort (max u v))"
                if base == "I1":
                    case["type"] = "(sort (max (succ u) u))"
            (HERE / "inputs" / f"{ident}.ndjson").write_bytes(raw)
            config = json.loads((OLD / "inputs" / f"{base}.json").read_text())
            config["export_file_path"] = f"/universe-rejection-in/{ident}.ndjson"
            (HERE / "inputs" / f"{ident}.json").write_text(json.dumps(config, indent=2) + "\n")
            cases.append(case)
    (HERE / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    print("Six cases structurally audited; controls unchanged, one JSON row changed per invalid candidate. No checker invoked.")

if __name__ == "__main__":
    main()
