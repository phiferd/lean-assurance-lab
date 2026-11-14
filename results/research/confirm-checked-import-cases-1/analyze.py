"""Classify one frozen E1 phase from retained raw receipts; never launch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from confirmation_common import (
    HERE, cell_label, load_manifest, require_supervision, sha256,
)


def logs(attempt: Path) -> tuple[dict, str, str]:
    receipt = json.loads((attempt / "receipt.json").read_text())
    stdout = (attempt / "stdout.log").read_text()
    stderr = (attempt / "stderr.log").read_text()
    require_supervision(receipt)
    assert receipt["stdout_sha256"] == sha256(attempt / "stdout.log")
    assert receipt["stderr_sha256"] == sha256(attempt / "stderr.log")
    return receipt, stdout, stderr


def classify(cell: dict, receipt: dict, stdout: str, stderr: str) -> tuple[str, str]:
    family, checker = cell["family"], cell["checker"]
    expected, declaration = cell["expected"], cell["declaration"]
    typ, val = cell["parsed_tree"]["type"], cell["parsed_tree"]["value"]
    if checker == "lean":
        assert f"NAME {declaration}\nPARAMS \n" in stdout
        if family == "expression":
            assert f"TYPE {typ}\nVALUE {val}\n" in stdout
        else:
            assert "TYPE " in stdout and "VALUE " in stdout and "UNEXPECTED-" not in stdout
        if expected == "ACCEPT":
            assert receipt["exit_code"] == 0 and stderr == ""
            assert stdout.endswith("Accepted 1 definition; empty environment; trust level 0.\n")
            return "ACCEPT", "trust-0 empty-environment replay checked the named definition"
        assert receipt["exit_code"] == 1
        assert f"while replaying declaration '{declaration}'" in stderr
        if family == "expression":
            assert "(kernel) application type mismatch" in stderr
            assert "argument has type" in stderr and "but function has type" in stderr
            return "REJECT", "Lean kernel application domain comparison"
        assert "(kernel) type expected" in stderr and "fun _ => Prop" in stderr
        return "REJECT", "Lean kernel declared/value Pi codomain sort inference"

    if expected == "ACCEPT":
        assert receipt["exit_code"] == 0 and stderr == ""
        assert stdout.startswith(f"def {declaration} ")
        assert stdout.endswith("Checked 1 declarations with no errors\n")
        return "ACCEPT", "Nanoda checked and printed the named one-definition input"
    assert receipt["exit_code"] == 101 and stdout == ""
    if family == "expression":
        assert "panicked at src/tc.rs:955:71" in stderr
        assert "assertion failed: self.def_eq(u, v)" in stderr
        return "REJECT", "Nanoda checked application domain equality assertion"
    assert "src/tc.rs:304:18" in stderr
    assert "infer_sort_of could not infer a sort" in stderr
    return "REJECT", "Nanoda Pi codomain infer_sort_of assertion"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("initial", "replay"))
    args = parser.parse_args()
    manifest = load_manifest()
    phase_dir = HERE / args.phase
    execution = json.loads((phase_dir / "execution.json").read_text())
    assert execution["fresh_containers"] == 20 and execution["all_containers_removed"]
    cells = []
    for cell in manifest["cases"]:
        label = cell_label(cell)
        receipt, stdout, stderr = logs(phase_dir / "attempts" / label)
        outcome, attribution = classify(cell, receipt, stdout, stderr)
        assert outcome == cell["expected"]
        post_receipt, post_out, post_err = logs(phase_dir / "attempts" / ("post-" + label))
        assert post_receipt["exit_code"] == 1 and post_out == ""
        assert "No such object" in post_err or "No such container" in post_err
        cells.append({
            "id": cell["id"],
            "family": cell["family"],
            "checker": cell["checker"],
            "input_sha256": cell["input"]["sha256"],
            "expected": cell["expected"],
            "outcome": outcome,
            "declaration": cell["declaration"],
            "attribution": attribution,
            "exit_code": receipt["exit_code"],
            "elapsed_seconds": receipt["elapsed_seconds"],
            "raw_attempt": f"attempts/{label}",
        })
    assert len(cells) == 20
    result = {
        "schema_version": 1,
        "item_id": manifest["item_id"],
        "evidence_class": "E1",
        "phase": args.phase,
        "status": "COMPLETE_EXPECTED",
        "planned_cells": 20,
        "attributable_cells": len(cells),
        "accepted_controls": sum(c["outcome"] == "ACCEPT" for c in cells),
        "rejected_negatives": sum(c["outcome"] == "REJECT" for c in cells),
        "cells": cells,
        "claim_limit": "Known-case finite reproduction on two historical profiles; agreement is not semantic authority or a general correctness claim.",
    }
    (phase_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: {len(cells)} attributable {args.phase} cells; 10 accepts and 10 expected rejections")


if __name__ == "__main__":
    main()
