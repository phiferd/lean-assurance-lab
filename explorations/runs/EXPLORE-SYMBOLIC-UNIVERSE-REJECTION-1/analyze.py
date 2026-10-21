"""Validate this fixed E0 matrix from retained bytes; never launch checkers."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def hashes(path):
    return {parts[1]: parts[0] for line in path.read_text().splitlines()
            if len(parts := line.split()) == 2 and re.fullmatch("[0-9a-f]{64}", parts[0])}

def main():
    cases = json.loads((HERE / "cases.json").read_text())
    executions = json.loads((HERE / "observations/executions.json").read_text())
    assert len(cases) == 6 and len(executions) == 12
    assert {(r["case"], r["checker"]) for r in executions} == {
        (c["id"], k) for c in cases for k in ("lean", "nanoda")}
    start = next(json.loads(line) for line in (ROOT / "explorations/ledger.jsonl").read_text().splitlines()
                 if json.loads(line)["id"] == HERE.name and json.loads(line)["event"] == "start")
    for path, digest in start["data"]["input_sha256"].items():
        assert sha(ROOT / path) == digest, path
    bound = json.loads((HERE / "protocol.json").read_text())["observed_sha256"]
    post = hashes(HERE / "attempts/postflight/stdout.log")
    for path, digest in post.items():
        assert bound[path] == digest, path
    expected_post = {p for p in bound if not p.startswith("/opt/nanoda/src/")}
    assert set(post) == expected_post
    assert "Running=false Status=exited" in (HERE / "attempts/final-container-state/stdout.log").read_text()
    assert "OOMKilled=false" in (HERE / "attempts/final-container-state/stdout.log").read_text()
    cells = []
    nanoda_valid = {
        "P1": "def LAL_P1.{u} : Type u := Sort u\n\nChecked 1 declarations with no errors\n",
        "M1": "def LAL_M1.{u v} : Sort (max (u+1) (v+1)) := Sort (max u v)\n\nChecked 1 declarations with no errors\n",
        "I1": "def LAL_I1.{u} : Sort (imax (u+1) u) := forall (X : Sort u), X\n\nChecked 1 declarations with no errors\n",
    }
    for case in cases:
        ident = case["id"]
        assert sha(HERE / "inputs" / (ident + ".ndjson")) == case["sha256"]
        for checker in ("lean", "nanoda"):
            row = next(r for r in executions if r["case"] == ident and r["checker"] == checker)
            directory = HERE / "observations" / (ident + "-" + checker)
            assert json.loads((directory / "execution.json").read_text()) == row
            assert row["input_sha256"] == case["sha256"]
            stdout = (directory / "stdout.log").read_text()
            stderr = (directory / "stderr.log").read_text()
            expected = case["expected"]
            assert row["exit_code"] == (0 if expected == "ACCEPT" else 1 if checker == "lean" else 101)
            if checker == "lean":
                lines = ["NAME " + case["declaration"], "PARAMS " + ",".join(case["params"]),
                         "TYPE " + case["type"], "VALUE " + case["value"]]
                if expected == "ACCEPT":
                    lines += ["Accepted 1 declaration; empty environment; trust level 0."]
                    assert not stderr
                else:
                    prefix = f"uncaught exception: while replaying declaration '{case['declaration']}':\n(kernel) "
                    assert stderr.startswith(prefix)
                    if case["pair"] == "P1":
                        assert stderr == prefix + "invalid reference to undefined universe level parameter 'u'\n"
                    else:
                        assert "declaration type mismatch, '" + case["declaration"] + "' has type\n" in stderr
                        assert "but it is expected to have type\n" in stderr
                        assert "(max u v)" in stderr if case["pair"] == "M1" else "imax (u + 1) u" in stderr and "max (u + 1) u" in stderr
                assert stdout.splitlines() == lines, (ident, stdout, lines)
                transport = "SUCCESS" if expected == "ACCEPT" else "KERNEL_EXCEPTION"
            elif expected == "ACCEPT":
                assert not stderr and stdout == nanoda_valid[ident]
                transport = "SUCCESS"
            else:
                assert not stdout
                source, assertion = (
                    ("554:13", "self.ctx.all_uparams_defined(l, declar_info.uparams)")
                    if case["pair"] == "P1" else ("955:71", "self.def_eq(u, v)"))
                pattern = (r"\nthread 'main' \(\d+\) panicked at src/tc.rs:" + re.escape(source)
                           + r":\nassertion failed: " + re.escape(assertion)
                           + "\nnote: run with `RUST_BACKTRACE=1` environment variable to display a backtrace\n")
                assert re.fullmatch(pattern, stderr), (ident, stderr)
                transport = "EXPECTED_CHECKER_ASSERTION_PANIC"
            cells.append({"case": ident, "checker": checker, "outcome": expected,
                          "transport": transport, "expected_matched": True,
                          "demand_evidence": "EXACT_PARSED_AST" if checker == "lean" else "BOUND_RAW_PARSER_SOURCE_AND_INPUT",
                          "stdout_sha256": sha(directory / "stdout.log"),
                          "stderr_sha256": sha(directory / "stderr.log"),
                          "execution": str(directory.relative_to(HERE) / "execution.json")})
    receipts = [json.loads(p.read_text()) for p in sorted((HERE / "attempts").glob("*/receipt.json"))]
    assert all(r["cleanup_complete"] and not r["monitor_errors"] and
               r["exit_code"] == 0 and r["stop_reason"] is None for r in receipts)
    result = {
        "evidence_class": "E0", "outcome": "NO_SIGNAL", "completed_runs": 12,
        "signal_count": 0, "measurement_complete": True, "engineering_failures_unresolved": False,
        "accepts": 6, "rejections": 6, "expected_assertion_panics": 3,
        "diagnostic_crashes": 0, "unsupported_or_parser_failures": 0, "timeouts": 0,
        "cases": cells, "observed_cell_seconds": sum(r["elapsed_seconds"] for r in executions),
        "supervised_attempts": len(receipts), "supervised_seconds": sum(r["elapsed_seconds"] for r in receipts),
        "preparation_failures": 0, "scientific_retries": 0,
        "analysis_sha256": sha(Path(__file__)),
        "model_usage": "Task-level model/token accounting unavailable; independent input and result review retained. No cost estimate.",
        "recommendation": "Retain the exact three invalid/valid pairs as a normal-priority local boundary corpus. No defect, confirmation experiment, production checker change or external action follows from expected behavior in this fixed E0 sample.",
        "limitations": "Two pinned profiles, three constructed boundaries, no fault-detection rate, general soundness, fresh holdout, runtime Nanoda AST dump or branch-coverage claim. Host supervisor RSS is not guest checker memory."
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))

if __name__ == "__main__":
    main()
