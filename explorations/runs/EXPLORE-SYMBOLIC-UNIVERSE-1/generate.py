"""Encode the six prospectively selected raw declarations, without elaboration."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.metamorphic_ndjson_audit import decode

HERE = Path(__file__).resolve().parent
META = {"meta": {"exporter": {"name": "LAL hand-encoded rule cases", "version": "1"},
    "format": {"version": "3.1.0"}, "lean": {"version": "4.34.1",
    "githash": "5045d0056413266e57c625dcd7c365b10e377c52"}}}

class Encoder:
    def __init__(self):
        self.rows = [META]
        self.tables = {"in": {}, "il": {}, "ie": {}}

    def put(self, space, tag, value):
        key = json.dumps([tag, value], sort_keys=True)
        table = self.tables[space]
        if key not in table:
            table[key] = len(table) + (0 if space == "ie" else 1)
            self.rows.append({space: table[key], tag: value})
        return table[key]

    def name(self, value):
        return self.put("in", "str", {"pre": 0, "str": value})

    def level(self, tree):
        if tree == "0": return 0
        if isinstance(tree, str): return self.put("il", "param", self.name(tree))
        tag, *args = tree
        levels = [self.level(a) for a in args]
        return self.put("il", tag, levels[0] if tag == "succ" else levels)

    def expr(self, tree):
        tag, *args = tree
        if tag == "sort": data = self.level(args[0])
        elif tag == "bvar": data = args[0]
        elif tag == "forallE":
            name, typ, body = args
            data = {"name": self.name(name), "type": self.expr(typ),
                    "body": self.expr(body), "binderInfo": "default"}
        elif tag == "letE":
            name, typ, value, body = args
            data = {"name": self.name(name), "type": self.expr(typ),
                    "value": self.expr(value), "body": self.expr(body), "nondep": False}
        else: raise ValueError(tag)
        return self.put("ie", tag, data)

    def declaration(self, name, params, typ, value):
        name = self.name(name)
        params = [self.name(p) for p in params]
        typ, value = self.expr(typ), self.expr(value)
        self.rows.append({"def": {"name": name, "levelParams": params,
            "type": typ, "value": value, "hints": "opaque", "safety": "safe", "all": [name]}})
        raw = ("\n".join(json.dumps(r, separators=(",", ":")) for r in self.rows) + "\n").encode()
        assert len(decode(raw).declarations) == 1
        return raw

su = ("succ", "u")
one = ("succ", "0")
sortu = ("sort", "u")
pi = ("forallE", "X", sortu, ("bvar", 0))
cases = [
    ("P1", ["u"], ("sort", su), sortu,
     "Sort u has type Sort (succ u), with u explicitly declared."),
    ("P2", ["u"], ("sort", su), ("letE", "X", ("sort", su), sortu, ("bvar", 0)),
     "The let-bound X has type Sort (succ u); zeta reduction returns Sort u."),
    ("M1", ["u", "v"], ("sort", ("max", su, ("succ", "v"))), ("sort", ("max", "u", "v")),
     "Sort(max u v) infers Sort(succ(max u v)); successor distributes over max."),
    ("M2", ["u", "v"], ("sort", ("succ", ("max", "v", "u"))), ("sort", ("max", "u", "v")),
     "Same value; max commutes, so succ(max v u) equals succ(max u v)."),
    ("I1", ["u"], ("sort", ("imax", su, "u")), pi,
     "Pi X:Sort u, X has domain sort succ u and codomain sort u; Pi formation yields imax(succ u,u)."),
    ("I2", ["u"], ("sort", ("imax", ("max", su, one), "u")), pi,
     "Same Pi; max(succ u,1)=succ u. The raw imax right operand remains the parameter u; no claim of demanding a particular imax case-split branch."),
]

def text(tree):
    if isinstance(tree, (str, int)): return str(tree)
    return "(" + " ".join(text(x) for x in tree) + ")"

def main():
    out = []
    (HERE / "inputs").mkdir(exist_ok=True)
    for ident, params, typ, value, reason in cases:
        raw = Encoder().declaration("LAL_" + ident, params, typ, value)
        path = HERE / "inputs" / (ident + ".ndjson")
        path.write_bytes(raw)
        config = {"export_file_path": "/universe-in/" + path.name,
            "permitted_axioms": [], "unpermitted_axiom_hard_error": True,
            "num_threads": 1, "pp_declars": ["LAL_" + ident], "pp_to_stdout": True,
            "print_success_message": True, "print_axioms": True}
        (HERE / "inputs" / (ident + ".json")).write_text(json.dumps(config, indent=2) + "\n")
        out.append({"id": ident, "declaration": "LAL_" + ident, "params": params,
            "type": text(typ), "value": text(value), "expected": "ACCEPT",
            "reason": reason, "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(raw).hexdigest(), "structural_audit": "PASS"})
    (HERE / "cases.json").write_text(json.dumps(out, indent=2) + "\n")
    print("Encoded and structurally audited six cases; no checker invoked.")

if __name__ == "__main__": main()
