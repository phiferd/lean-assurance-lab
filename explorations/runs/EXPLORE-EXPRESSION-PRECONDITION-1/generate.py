"""Encode the six preselected, closed expression-precondition cases."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.metamorphic_ndjson_audit import decode

HERE = Path(__file__).resolve().parent
META = {"meta": {"exporter": {"name": "LAL hand-encoded precondition screen", "version": "1"},
                 "format": {"version": "3.1.0"},
                 "lean": {"version": "4.34.1", "githash": "5045d0056413266e57c625dcd7c365b10e377c52"}}}


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

    def expr(self, tree):
        tag, *args = tree
        if tag == "sort":
            level = args[0]
            if level == 0: data = 0
            elif level == 1: data = self.put("il", "succ", 0)
            else: raise ValueError(level)
        elif tag == "bvar": data = args[0]
        elif tag == "app": data = {"fn": self.expr(args[0]), "arg": self.expr(args[1])}
        elif tag in ("lam", "forallE"):
            name, typ, body = args
            data = {"name": self.name(name), "type": self.expr(typ),
                    "body": self.expr(body), "binderInfo": "default"}
        else: raise ValueError(tag)
        return self.put("ie", tag, data)

    def declaration(self, name, typ, value):
        name_id = self.name(name)
        type_id, value_id = self.expr(typ), self.expr(value)
        self.rows.append({"def": {"name": name_id, "levelParams": [], "type": type_id,
                                  "value": value_id, "hints": "opaque", "safety": "safe", "all": [name_id]}})
        return self.rows


P = ("sort", 0)
U = ("sort", 1)
FV = ("lam", "_", U, P)
FT = ("lam", "_", U, U)


def encode(rows):
    return ("\n".join(json.dumps(row, separators=(",", ":")) for row in rows) + "\n").encode()


def main():
    (HERE / "inputs").mkdir(exist_ok=True)
    cases = []
    for pair in "VTB":
        name = "LAL_EXPR_" + pair
        app = ("app", FV if pair == "V" else FT, P)
        if pair == "V": typ, value = U, app
        elif pair == "T": typ, value = app, P
        else:
            typ = ("forallE", "x", app, U)
            value = ("lam", "x", U, P)
        control_rows = Encoder().declaration(name, typ, value)
        app_rows = [r for r in control_rows if "app" in r]
        assert len(app_rows) == 1
        app_row = app_rows[0]
        p_row = next(r for r in control_rows if r.get("ie") == app_row["app"]["arg"])
        assert p_row["sort"] == 0
        u_index = next(r["ie"] for r in control_rows if r.get("sort") == 1 and "ie" in r)
        negative_rows = json.loads(json.dumps(control_rows))
        next(r for r in negative_rows if r.get("ie") == app_row["ie"])["app"]["arg"] = u_index
        assert sum(a != b for a, b in zip(control_rows, negative_rows)) == 1
        for suffix, rows, expected in (("-control", control_rows, "ACCEPT"),
                                       ("-negative", negative_rows, "REJECT")):
            ident = pair + suffix
            raw = encode(rows)
            decoded = decode(raw)
            assert len(decoded.declarations) == 1
            path = HERE / "inputs" / (ident + ".ndjson")
            path.write_bytes(raw)
            config = {"export_file_path": "/expression-in/" + path.name,
                      "permitted_axioms": [], "unpermitted_axiom_hard_error": True,
                      "num_threads": 1, "pp_declars": [name], "pp_to_stdout": True,
                      "print_success_message": True, "print_axioms": True}
            cpath = HERE / "inputs" / (ident + ".json")
            cpath.write_text(json.dumps(config, indent=2) + "\n")
            cases.append({"id": ident, "pair": pair, "declaration": name,
                          "expected": expected, "path": str(path.relative_to(ROOT)),
                          "sha256": hashlib.sha256(raw).hexdigest(),
                          "config": str(cpath.relative_to(ROOT)),
                          "config_sha256": hashlib.sha256(cpath.read_bytes()).hexdigest()})
    (HERE / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    print("Generated six raw declarations and Nanoda configs; no checker invoked.")


if __name__ == "__main__":
    main()
