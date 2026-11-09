"""Classify the eight fixed cells from raw supervised receipts and diagnostics."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cases = json.loads((HERE / "cases.json").read_text())
    labels = ["01-mkdir", "02-stage-inputs", "03-stage-importer", "04-stage-hashes"]
    labels += [f"cell-{case['id']}-{checker}" for case in cases for checker in ("lean", "nanoda")]
    labels += [f"post-{case['id']}-{checker}" for case in cases for checker in ("lean", "nanoda")]
    attempts = HERE / "attempts"
    assert {p.name for p in attempts.iterdir() if p.is_dir()} == set(labels)
    receipts = {}
    for label in labels:
        folder = attempts / label
        receipt = json.loads((folder / "receipt.json").read_text())
        command = json.loads((folder / "command.json").read_text())
        assert receipt["argv"] == command["argv"]
        assert receipt["limits"]["timeout_seconds"] == command["timeout_seconds"]
        assert receipt["cleanup_complete"] and receipt["reap_complete"]
        assert receipt["monitor_errors"] == receipt["cleanup_errors"] == receipt["pipe_errors"] == []
        assert receipt["accounting_error"] is None and receipt["stop_reason"] is None
        assert not receipt["trace_gap_fault"]
        assert receipt["stdout_sha256"] == sha(folder / "stdout.log")
        assert receipt["stderr_sha256"] == sha(folder / "stderr.log")
        receipts[label] = receipt
    for label in labels[:4]: assert receipts[label]["exit_code"] == 0
    staged = (attempts / "04-stage-hashes/stdout.log").read_text()
    for case in cases:
        assert case["sha256"] in staged and case["config_sha256"] in staged
        for checker in ("lean", "nanoda"):
            post = attempts / f"post-{case['id']}-{checker}"
            assert receipts[post.name]["exit_code"] == 0
            assert (post / "stdout.log").read_text().split()[0] == case["sha256"]
    cells = []
    for case in cases:
        ident = case["id"]
        for checker in ("lean", "nanoda"):
            label = f"cell-{ident}-{checker}"
            folder = attempts / label
            receipt = receipts[label]
            stdout, stderr = ((folder / name).read_text() for name in ("stdout.log", "stderr.log"))
            if checker == "lean":
                assert f"NAME {case['declaration']}\nPARAMS \n" in stdout
                assert "TYPE " in stdout and "VALUE " in stdout
                assert "UNEXPECTED-" not in stdout
                if case["expected"] == "ACCEPT":
                    assert receipt["exit_code"] == 0 and stderr == ""
                    assert "Accepted 1 definition; empty environment; trust level 0." in stdout
                    outcome, stage = "ACCEPT", "checked ordinary definition admission"
                else:
                    assert receipt["exit_code"] == 1
                    assert f"while replaying declaration '{case['declaration']}'" in stderr
                    assert "(kernel) type expected" in stderr and "fun _ => Prop" in stderr
                    outcome, stage = "REJECT", "checked Pi codomain sort inference"
            else:
                if case["expected"] == "ACCEPT":
                    assert receipt["exit_code"] == 0 and stderr == ""
                    assert f"def {case['declaration']}" in stdout
                    assert "Checked 1 declarations with no errors" in stdout
                    outcome, stage = "ACCEPT", "checked ordinary definition admission"
                else:
                    assert receipt["exit_code"] == 101 and stdout == ""
                    assert "src/tc.rs:304:18" in stderr
                    assert "infer_sort_of could not infer a sort" in stderr
                    outcome, stage = "REJECT", "checked Pi codomain infer_sort_of assertion"
            assert outcome == case["expected"]
            cells.append({"case": ident, "checker": checker, "expected": case["expected"],
                          "outcome": outcome, "first_attributable_stage": stage,
                          "exit_code": receipt["exit_code"], "elapsed_seconds": receipt["elapsed_seconds"],
                          "receipt": str((folder / "receipt.json").relative_to(HERE)),
                          "stdout": str((folder / "stdout.log").relative_to(HERE)),
                          "stderr": str((folder / "stderr.log").relative_to(HERE))})
    result = {"schema_version": 1, "evidence_class": "E0", "trial": "EXPLORE-PI-CODOMAIN-ADMISSION-1",
              "classification": "NO_SIGNAL", "planned_cells": 8, "observed_cells": len(cells),
              "accepted_controls": sum(c["outcome"] == "ACCEPT" for c in cells),
              "rejected_negatives": sum(c["outcome"] == "REJECT" for c in cells),
              "supervised_commands": len(labels),
              "aggregate_host_cell_seconds": round(sum(c["elapsed_seconds"] for c in cells), 6),
              "cells": cells,
              "limits": "Pinned Lean 4.34.1 and Nanoda 3a240721 only; four closed sort-only definitions. Nanoda has no independent runtime AST dump; its source and byte-identical staged input support attribution. Host RSS observes the docker client/process group, not guest checker memory. Agreement is not semantic authority."}
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: {len(cells)} attributed cells; {result['accepted_controls']} accepts, {result['rejected_negatives']} expected rejections; E0 NO_SIGNAL")


if __name__ == "__main__":
    main()
