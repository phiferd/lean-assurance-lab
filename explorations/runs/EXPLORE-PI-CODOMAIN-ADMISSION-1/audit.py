"""Read-only raw-input and elementary typing audit; no checker calls."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from lib.metamorphic_ndjson_audit import decode


def tree(decoded, digest):
    d = decoded.descriptors["expr"][digest]
    if d[1] == "sort":
        level = d[2]
        n = 0
        while level != decoded.nodes["level"][0]:
            level_d = decoded.descriptors["level"][level]
            assert level_d[1] == "succ"
            level = level_d[2]
            n += 1
            assert n <= 2
        return ("sort", n)
    if d[1] in ("lam", "forallE"):
        name = decoded.descriptors["name"][d[2]]
        assert name[1] == "str" and name[2] == decoded.nodes["name"][0]
        assert name[3] == "_" and d[5] == "default"
        return (d[1], tree(decoded, d[3]), tree(decoded, d[4]))
    raise AssertionError("unexpected expression tag: " + d[1])


def infer(expr):
    tag = expr[0]
    if tag == "sort": return ("sort", expr[1] + 1)
    if tag == "lam":
        domain, body = expr[1:]
        assert infer(domain)[0] == "sort"
        return ("forallE", domain, infer(body))
    if tag == "forallE":
        domain, body = expr[1:]
        dom_ty, cod_ty = infer(domain), infer(body)
        assert dom_ty[0] == "sort"
        if cod_ty[0] != "sort":
            raise TypeError("Pi codomain does not infer a sort")
        return ("sort", max(dom_ty[1], cod_ty[1]))
    raise AssertionError(tag)


def main():
    cases = json.loads((HERE / "cases.json").read_text())
    assert [c["id"] for c in cases] == [f"{pair}-{suffix}" for pair in "AB"
                                            for suffix in ("control", "negative")]
    s0, s1, s2 = ("sort", 0), ("sort", 1), ("sort", 2)
    f = ("lam", s1, s0)
    g = ("forallE", s1, s1)
    n = ("forallE", s1, f)
    assert infer(s0) == s1 and infer(s1) == s2
    assert infer(f) == g and infer(g) == s2
    try: infer(n)
    except TypeError as error: assert str(error) == "Pi codomain does not infer a sort"
    else: raise AssertionError("negative Pi unexpectedly formed in independent model")
    for pair in "AB":
        observed = []
        for suffix in ("control", "negative"):
            ident = pair + "-" + suffix
            case = next(c for c in cases if c["id"] == ident)
            assert case["pair"] == pair and case["declaration"] == "LAL_PI_" + pair
            assert case["expected"] == ("ACCEPT" if suffix == "control" else "REJECT")
            raw = (ROOT / case["path"]).read_bytes()
            config = (ROOT / case["config"]).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == case["sha256"]
            assert hashlib.sha256(config).hexdigest() == case["config_sha256"]
            assert json.loads(config) == {
                "export_file_path": "/pi-in/" + ident + ".ndjson",
                "permitted_axioms": [], "unpermitted_axiom_hard_error": True,
                "num_threads": 1, "pp_declars": ["LAL_PI_" + pair],
                "pp_to_stdout": True, "print_success_message": True, "print_axioms": True}
            decoded = decode(raw)
            assert decoded.metadata["format"]["version"] == "3.1.0"
            assert len(decoded.declarations) == 1
            decl = decoded.declarations[0]
            assert decl["tag"] == "def" and decl["levelParams"] == []
            assert decl["hints"] == "opaque" and decl["safety"] == "safe"
            assert decl["all"] == [decl["name"]]
            name = decoded.descriptors["name"][decl["name"]]
            assert name[1] == "str" and name[3] == "LAL_PI_" + pair
            actual = (tree(decoded, decl["type"]), tree(decoded, decl["value"]))
            pi = g if suffix == "control" else n
            expected = (pi, f) if pair == "A" else (s2, pi)
            assert actual == expected, (ident, actual, expected)
            observed.append(actual)
            assert all(row.keys().isdisjoint({"axiom", "thm", "opaque", "inductive", "quot", "const", "mvar", "app", "letE", "bvar"})
                       for row in (json.loads(line) for line in raw.splitlines()))
            if suffix == "control":
                typ, val = actual
                assert infer(typ)[0] == "sort" and infer(val) == typ
            else:
                try: infer(actual[0] if pair == "A" else actual[1])
                except TypeError as error: assert str(error) == "Pi codomain does not infer a sort"
                else: raise AssertionError("negative lacked primary Pi failure")
        left, right = observed
        assert left[0 if pair == "A" else 1][1] == right[0 if pair == "A" else 1][1] == s1
        assert left[0 if pair == "A" else 1][2] == s1
        assert right[0 if pair == "A" else 1][2] == f
        assert left[1 if pair == "A" else 0] == right[1 if pair == "A" else 0]
    print("PASS: four exact closed trees, two codomain-only replacements, four configs and independent typing check; no checker invoked.")


if __name__ == "__main__":
    main()
