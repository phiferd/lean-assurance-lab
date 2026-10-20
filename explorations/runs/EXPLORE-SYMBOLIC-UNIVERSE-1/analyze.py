"""Check retained observations against the prospectively declared six cases."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
cases = json.loads((HERE / "cases.json").read_text())
executions = json.loads((HERE / "observations/executions.json").read_text())
assert len(executions) == 12
assert {(r["case"], r["checker"]) for r in executions} == {(c["id"], k) for c in cases for k in ("lean", "nanoda")}
raw_nanoda = {"P1": "Sort u", "P2": "let X", "M1": "Sort (max (u+1) (v+1))",
              "M2": "Type (max v u)", "I1": "imax (u+1) u", "I2": "imax (max (u+1) 1) u"}
cells = []
for case in cases:
    assert hashlib.sha256((HERE / "inputs" / (case["id"] + ".ndjson")).read_bytes()).hexdigest() == case["sha256"]
    for checker in ("lean", "nanoda"):
        row = next(r for r in executions if r["case"] == case["id"] and r["checker"] == checker)
        cell = HERE / "observations" / (case["id"] + "-" + checker)
        stdout, stderr = (cell / "stdout.log").read_text(), (cell / "stderr.log").read_text()
        assert row["input_sha256"] == case["sha256"] and row["exit_code"] == 0
        assert not stderr, (case["id"], checker, stderr)
        if checker == "lean":
            expected = ["NAME " + case["declaration"], "PARAMS " + ",".join(case["params"]),
                "TYPE " + case["type"], "VALUE " + case["value"],
                "Accepted 1 declaration; empty environment; trust level 0."]
            assert stdout.splitlines() == expected, (stdout, expected)
        else:
            assert stdout.startswith("def " + case["declaration"] + ".{")
            assert "Checked 1 declarations with no errors" in stdout
            assert raw_nanoda[case["id"]] in stdout
        cells.append({"case": case["id"], "checker": checker, "outcome": "ACCEPT",
            "demand_check": "PASS", "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
            "execution": str(cell.relative_to(HERE) / "execution.json")})
receipts = [json.loads(p.read_text()) for p in sorted((HERE / "attempts").glob("*/receipt.json"))]
assert all(r["cleanup_complete"] and not r["monitor_errors"] for r in receipts)
result = {"evidence_class": "E0", "outcome": "NO_SIGNAL", "completed_runs": 12,
    "signal_count": 0, "measurement_complete": True, "engineering_failures_unresolved": False,
    "cases": cells, "accepts": 12, "rejections": 0, "crashes": 0, "unsupported": 0,
    "observed_cell_seconds": sum(r["elapsed_seconds"] for r in executions),
    "supervised_attempts": len(receipts), "preparation_failures": sum(r["exit_code"] != 0 for r in receipts),
    "supervised_seconds": sum(r["elapsed_seconds"] for r in receipts),
    "model_usage": "Task-level model/token accounting unavailable; one bounded source-review delegate; no private conversation exported.",
    "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "recommendation": "Retain six tiny symbolic-universe fixtures as a normal-priority local conformance corpus. No defect, automatic confirmation, model formalization or external action follows. Separately select a three-boundary invalid/valid-control E0 screen to address rejection behavior, which this all-positive sample did not measure."}
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))
