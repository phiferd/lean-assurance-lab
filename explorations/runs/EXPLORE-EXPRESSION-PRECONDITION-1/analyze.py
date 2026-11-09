"""Classify retained cells; do not launch or alter a checker."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def receipt(label):
    directory = HERE / "attempts" / label
    r = json.loads((directory / "receipt.json").read_text())
    assert r["cleanup_complete"] and not r["monitor_errors"] and r["stop_reason"] is None, label
    return r, (directory / "stdout.log").read_text(), (directory / "stderr.log").read_text()


def main():
    cases = json.loads((HERE / "cases.json").read_text())
    assert len(cases) == 6
    assert len(list((HERE / "attempts").iterdir())) == 28
    for label in ("01-mkdir", "02-stage-inputs", "03-stage-importer", "04-stage-hashes"):
        assert receipt(label)[0]["exit_code"] == 0
    results = []
    for case in cases:
        ident = case["id"]
        pair = case["pair"]
        bad = case["expected"] == "REJECT"
        arg = "(sort (succ 0))" if bad else "(sort 0)"
        fn = "(lam _ (sort (succ 0)) " + ("(sort 0)" if pair == "V" else "(sort (succ 0))") + ")"
        app = f"(app {fn} {arg})"
        expected_type = ("(sort (succ 0))" if pair == "V" else app if pair == "T" else
                         f"(forallE x {app} (sort (succ 0)))")
        expected_value = (app if pair == "V" else "(sort 0)" if pair == "T" else
                          "(lam x (sort (succ 0)) (sort 0))")
        for checker in ("lean", "nanoda"):
            label = f"cell-{ident}-{checker}"
            r, out, err = receipt(label)
            expected_exit = (1 if checker == "lean" else 101) if bad else 0
            assert r["exit_code"] == expected_exit, label
            if checker == "lean":
                assert out.splitlines() == ["NAME LAL_EXPR_" + pair, "PARAMS ",
                                            "TYPE " + expected_type, "VALUE " + expected_value] + (
                                                [] if bad else ["Accepted 1 definition; empty environment; trust level 0."]), label
                if bad:
                    assert "while replaying declaration 'LAL_EXPR_" + pair + "'" in err
                    assert "(kernel) application type mismatch" in err
                    assert "argument has type" in err and "Type 1" in err
                    assert "but function has type" in err
                else: assert not err
            else:
                if bad:
                    assert not out and "panicked at src/tc.rs:955:71" in err
                    assert "assertion failed: self.def_eq(u, v)" in err
                else:
                    assert not err and out.startswith("def LAL_EXPR_" + pair + " ")
                    assert out.endswith("Checked 1 declarations with no errors\n")
            post, hash_out, hash_err = receipt(f"post-{ident}-{checker}")
            assert post["exit_code"] == 0 and not hash_err
            assert hash_out == case["sha256"] + "  /expression-in/" + ident + ".ndjson\n"
            results.append({"case": ident, "checker": checker, "expected": case["expected"],
                            "observed": "REJECT" if bad else "ACCEPT",
                            "exit_code": r["exit_code"], "elapsed_seconds": r["elapsed_seconds"],
                            "raw_attempt": "attempts/" + label})
    assert len(results) == 12
    result = {"evidence_class": "E0", "trial": "EXPLORE-EXPRESSION-PRECONDITION-1",
              "outcome": "NO_SIGNAL", "completed_runs": 12, "signal_count": 0,
              "observations": "Six ordinary checked definitions accepted as controls and six paired negatives rejected. Lean parsed all six exact shapes and reported three application type mismatches. Nanoda accepted three controls and raised its retained checked equality assertion for three negatives; source path and one-app input support application-domain attribution. All 28 supervised setup, cell and post-check processes had complete cleanup without monitor error; post-cell input hashes matched.",
              "limitations": "This is an E0 screen of six closed sort-only definitions on two pinned checker versions. Nanoda has no independent runtime AST trace, and host docker-client RSS does not measure guest checker memory. A passing screen does not prove general checker soundness or absence of other defects. No fresh Nat import or alternative version was tested.",
              "cell_seconds": sum(x["elapsed_seconds"] for x in results), "cells": results}
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: 12 attributable cells, six accepts and six expected rejections; NO_SIGNAL")


if __name__ == "__main__":
    main()
