"""Independent read-only audit of the fixed raw sample; never invokes a checker."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.metamorphic_ndjson_audit import decode

HERE = Path(__file__).resolve().parent


def tree(decoded, digest):
    d = decoded.descriptors["expr"][digest]
    if d[1] == "sort":
        level = decoded.descriptors["level"].get(d[2])
        if level is None: return ["sort", 0]
        assert level[1] == "succ" and level[2] == decoded.nodes["level"][0]
        return ["sort", 1]
    if d[1] == "app": return ["app", tree(decoded, d[2]), tree(decoded, d[3])]
    if d[1] in ("lam", "forallE"):
        name = decoded.descriptors["name"][d[2]]
        assert name[1] == "str" and name[2] == decoded.nodes["name"][0]
        assert d[5] == "default"
        return [d[1], name[3], tree(decoded, d[3]), tree(decoded, d[4])]
    raise AssertionError(d[1])


def main():
    cases = json.loads((HERE / "cases.json").read_text())
    assert [c["id"] for c in cases] == [f"{p}-{s}" for p in "VTB" for s in ("control", "negative")]
    P, U = ["sort", 0], ["sort", 1]
    fv, ft = ["lam", "_", U, P], ["lam", "_", U, U]
    for pair in "VTB":
        records = []
        for suffix in ("control", "negative"):
            ident = f"{pair}-{suffix}"
            case = next(c for c in cases if c["id"] == ident)
            raw = (ROOT / case["path"]).read_bytes()
            config = (ROOT / case["config"]).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == case["sha256"]
            assert hashlib.sha256(config).hexdigest() == case["config_sha256"]
            obj = json.loads(config)
            assert obj == {"export_file_path": "/expression-in/" + ident + ".ndjson",
                           "permitted_axioms": [], "unpermitted_axiom_hard_error": True,
                           "num_threads": 1, "pp_declars": ["LAL_EXPR_" + pair],
                           "pp_to_stdout": True, "print_success_message": True, "print_axioms": True}
            decoded = decode(raw)
            assert len(decoded.declarations) == 1
            decl = decoded.declarations[0]
            assert decl["tag"] == "def" and decl["levelParams"] == []
            assert decl["hints"] == "opaque" and decl["safety"] == "safe"
            name = decoded.descriptors["name"][decl["name"]]
            assert name[3] == "LAL_EXPR_" + pair
            assert decl["all"] == [decl["name"]]
            arg = P if suffix == "control" else U
            app = ["app", fv if pair == "V" else ft, arg]
            if pair == "V": expected = (U, app)
            elif pair == "T": expected = (app, P)
            else: expected = (["forallE", "x", app, U], ["lam", "x", U, P])
            actual = (tree(decoded, decl["type"]), tree(decoded, decl["value"]))
            assert actual == expected, (ident, actual, expected)
            records.append([json.loads(line) for line in raw.splitlines()])
        left, right = records
        assert len(left) == len(right)
        differences = [(a, b) for a, b in zip(left, right) if a != b]
        assert len(differences) == 1
        a, b = differences[0]
        assert a.keys() == b.keys() == {"ie", "app"}
        assert a["ie"] == b["ie"] and a["app"]["fn"] == b["app"]["fn"]
        assert a["app"]["arg"] != b["app"]["arg"]
        assert all(row.keys().isdisjoint({"axiom", "thm", "opaque", "inductive", "quot", "const", "mvar"})
                   for row in left + right)
    print("PASS: six exact closed trees, three one-field arg edits, six configurations; no checker invoked.")


if __name__ == "__main__":
    main()
