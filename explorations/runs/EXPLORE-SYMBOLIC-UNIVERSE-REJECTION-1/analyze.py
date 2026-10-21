"""Classify retained outcomes by exact parsed inputs and source-attributed errors."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
cases = json.loads((HERE / "cases.json").read_text())
executions = json.loads((HERE / "observations/executions.json").read_text())
assert len(executions) == 12
assert {(r["case"], r["checker"]) for r in executions} == {(c["id"], k) for c in cases for k in ("lean", "nanoda")}
cells = []
for case in cases:
    assert hashlib.sha256((HERE / "inputs" / (case["id"] + ".ndjson")).read_bytes()).hexdigest() == case["sha256"]
    for checker in ("lean", "nanoda"):
        row = next(r for r in executions if r["case"] == case["id"] and r["checker"] == checker)
        path = HERE / "observations" / (case["id"] + "-" + checker)
        stdout, stderr = (path / "stdout.log").read_text(), (path / "stderr.log").read_text()
        assert row["input_sha256"] == case["sha256"]
        valid = case["expected"] == "ACCEPT"
        mechanism = "completed_one_declaration"
        if checker == "lean":
            prefix = ["NAME " + case["declaration"], "PARAMS " + ",".join(case["params"]),
                "TYPE " + case["type"], "VALUE " + case["value"]]
            assert stdout.splitlines()[:4] == prefix
            if valid:
                assert row["exit_code"] == 0 and not stderr
                assert stdout.splitlines()[4:] == ["Accepted 1 declaration; empty environment; trust level 0."]
            else:
                assert row["exit_code"] == 1 and "Accepted 1 declaration" not in stdout
                assert "while replaying declaration '" + case["declaration"] + "'" in stderr
                mechanism = "undefined_universe_parameter" if case["id"] == "Pbad" else "declaration_type_mismatch"
                assert ("invalid reference to undefined universe level parameter 'u'" if case["id"] == "Pbad" else "declaration type mismatch") in stderr
        elif valid:
            assert row["exit_code"] == 0 and not stderr
            assert stdout.startswith("def " + case["declaration"] + ".{")
            assert "Checked 1 declarations with no errors" in stdout
        else:
            assert row["exit_code"] == 101 and not stdout
            mechanism = "parameter_guard_assertion" if case["id"] == "Pbad" else "type_conversion_assertion"
            assert ("src/tc.rs:554:13" if case["id"] == "Pbad" else "src/tc.rs:955:71") in stderr
            assert ("assertion failed: self.ctx.all_uparams_defined(l, declar_info.uparams)" if case["id"] == "Pbad" else "assertion failed: self.def_eq(u, v)") in stderr
        cells.append({"case": case["id"], "checker": checker, "verdict": case["expected"],
            "expected_match": True, "mechanism": mechanism, "exit_code": row["exit_code"],
            "parsed_object_or_guard_attribution": "PASS", "execution": str(path.relative_to(HERE) / "execution.json")})
receipts = [json.loads(f.read_text()) for f in sorted((HERE / "attempts").glob("*/receipt.json"))]
assert all(r["cleanup_complete"] and not r["monitor_errors"] for r in receipts)
result = {"evidence_class": "E0", "outcome": "NO_SIGNAL", "completed_runs": 12,
    "signal_count": 0, "measurement_complete": True, "engineering_failures_unresolved": False,
    "cells": cells, "accepts": 6, "rejections": 6, "expected_assertion_rejections": 3,
    "unexpected_crashes": 0, "unsupported": 0, "scientific_retries": 0,
    "checker_invocation_seconds": sum(r["elapsed_seconds"] for r in executions),
    "supervised_attempts": len(receipts), "preparation_failures": sum(r["exit_code"] != 0 for r in receipts),
    "supervised_seconds": sum(r["elapsed_seconds"] for r in receipts),
    "model_usage": "Task token/cost accounting unavailable. No delegate or model calls in execution/analysis loops.",
    "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "recommendation": "Retain three single-record invalid variants with the existing byte-identical controls as a normal-priority local universe-boundary corpus. No defect, automatic confirmation, production change or upstream action follows. Select a bounded source-only corpus-reuse assessment before proposing more universe cases or any upstream contribution; determine whether these fixtures add coverage beyond existing Nanoda/Arena tests."}
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k:v for k,v in result.items() if k != "cells"}, indent=2))
