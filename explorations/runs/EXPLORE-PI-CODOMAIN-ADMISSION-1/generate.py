"""Encode the four fixed Pi-codomain E0 inputs; no checker is invoked."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
META = {"meta": {"exporter": {"name": "LAL hand-encoded Pi codomain screen", "version": "1"},
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
            level = 0
            for _ in range(args[0]):
                level = self.put("il", "succ", level)
            return self.put("ie", "sort", level)
        if tag in ("lam", "forallE"):
            name, typ, body = args
            return self.put("ie", tag, {"name": self.name(name), "type": self.expr(typ),
                                        "body": self.expr(body), "binderInfo": "default"})
        raise ValueError(tag)

    def declaration(self, name, typ, value):
        name_id = self.name(name)
        type_id, value_id = self.expr(typ), self.expr(value)
        self.rows.append({"def": {"name": name_id, "levelParams": [], "type": type_id,
                                  "value": value_id, "hints": "opaque", "safety": "safe", "all": [name_id]}})
        return self.rows


S0, S1, S2 = ("sort", 0), ("sort", 1), ("sort", 2)
F = ("lam", "_", S1, S0)
G = ("forallE", "_", S1, S1)
N = ("forallE", "_", S1, F)


def encode(rows):
    return ("\n".join(json.dumps(row, separators=(",", ":")) for row in rows) + "\n").encode()


def main():
    inputs = HERE / "inputs"
    inputs.mkdir(exist_ok=True)
    cases = []
    for pair in "AB":
        name = "LAL_PI_" + pair
        for suffix in ("control", "negative"):
            ident = pair + "-" + suffix
            pi = G if suffix == "control" else N
            typ, val = (pi, F) if pair == "A" else (S2, pi)
            raw = encode(Encoder().declaration(name, typ, val))
            path = inputs / (ident + ".ndjson")
            path.write_bytes(raw)
            config = {"export_file_path": "/pi-in/" + path.name,
                      "permitted_axioms": [], "unpermitted_axiom_hard_error": True,
                      "num_threads": 1, "pp_declars": [name], "pp_to_stdout": True,
                      "print_success_message": True, "print_axioms": True}
            cpath = inputs / (ident + ".json")
            cpath.write_text(json.dumps(config, indent=2) + "\n")
            cases.append({"id": ident, "pair": pair, "declaration": name,
                          "expected": "ACCEPT" if suffix == "control" else "REJECT",
                          "path": str(path.relative_to(ROOT)),
                          "sha256": hashlib.sha256(raw).hexdigest(),
                          "config": str(cpath.relative_to(ROOT)),
                          "config_sha256": hashlib.sha256(cpath.read_bytes()).hexdigest()})
    (HERE / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    print("Generated four fixed raw declarations and configs; no checker invoked.")


if __name__ == "__main__":
    main()
