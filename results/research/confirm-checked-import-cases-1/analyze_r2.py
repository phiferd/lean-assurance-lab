"""Tooling revision 2: classify Docker absence output without changing cells."""

from __future__ import annotations

import argparse
import json

from analyze import classify, logs
from confirmation_common import HERE, cell_label, load_manifest


def absence_proven(receipt: dict, stdout: str, stderr: str) -> bool:
    return (
        receipt["exit_code"] == 1
        and stdout in ("", "[]\n")
        and ("No such object" in stderr or "No such container" in stderr)
    )


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
        assert absence_proven(post_receipt, post_out, post_err)
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
        "analyzer_revision": "analyze_r2.py",
        "claim_limit": "Known-case finite reproduction on two historical profiles; agreement is not semantic authority or a general correctness claim.",
    }
    (phase_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: {len(cells)} attributable {args.phase} cells; 10 accepts and 10 expected rejections")


if __name__ == "__main__":
    main()
