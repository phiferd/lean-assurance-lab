#!/usr/bin/env python3
"""Run the exact repaired, canonicalized pair under the open E0 start."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.resource_envelope_supervisor import run_direct

RUN = Path(__file__).resolve().parent
IDENT = "EXPLORE-NANODA-NESTED-RECURSOR-UNIVERSE-CAPTURE-1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fault(receipt: dict[str, object]) -> bool:
    return bool(receipt["accounting_error"] or receipt["monitor_errors"]
                or receipt["pipe_errors"] or receipt["cleanup_errors"]
                or receipt["trace_gap_fault"] or not receipt["reap_complete"]
                or not receipt["cleanup_complete"])


def preflight(manifest: dict[str, object]) -> None:
    events = [json.loads(line) for line in (ROOT / "explorations/ledger.jsonl").read_text().splitlines()]
    ours = [row for row in events if row["id"] == IDENT]
    if len(ours) != 1 or ours[0]["event"] != "start":
        raise RuntimeError("the original prospective E0 start must remain open")
    for identity in manifest["identities"]:
        if sha(ROOT / identity["path"]) != identity["sha256"]:
            raise RuntimeError(f"repair identity changed: {identity['path']}")
    audit = json.loads((RUN / "fixture-audit-r2.json").read_text())
    if not (audit["nanoda_parser_constraints"] == {
        "continuous_expression_ids": True, "unique_expressions": True,
    } and audit["target"]["numNested"] == 1
            and audit["target"]["declared_universes"] == ["v"]
            and audit["target"]["control_rule_levels"] == [2]
            and audit["target"]["candidate_rule_levels"] == [3]
            and audit["observer"]["declared_universes"] == []
            and len(audit["pair_differences"]) == 1):
        raise RuntimeError("revision-2 adapter audit failed")
    independent = json.loads((RUN / "independent-reduct-result.json").read_text())
    if independent["control"]["exit_code"] != 0 or independent["candidate"]["exit_code"] != 1:
        raise RuntimeError("independent reduct boundary changed")


def verdict(exit_code: int, output: str) -> tuple[str, str]:
    if exit_code == 0:
        return "ACCEPT", "checker completed successfully"
    lowered = output.lower()
    if any(marker in lowered for marker in ("attempted to insert duplicate", "declined:", "parse error")):
        return "PARSER_OR_ADAPTER_FAILURE", "diagnostic identifies parser or back-reference handling"
    if any(marker in lowered for marker in ("src/tc.rs", "src/inductive.rs", "assertion", "def_eq", "typecheck")):
        return "REJECT", "diagnostic reaches checker or inductive semantic code"
    return "UNATTRIBUTED_NONZERO", "nonzero exit lacks a retained semantic source marker"


def run_cell(role: str, input_path: str, expected_sha: str) -> dict[str, object]:
    attempt = RUN / "attempts" / f"checker-{role}-r2"
    attempt.mkdir(parents=True, exist_ok=False)
    source = ROOT / input_path
    if sha(source) != expected_sha:
        raise RuntimeError(f"{role} repair input changed immediately before launch")
    environment = dict(os.environ)
    environment["RUST_BACKTRACE"] = "1"
    result = run_direct(
        argv=[str(RUN / "nanoda.bin"), str(RUN / "config.json")], cwd=ROOT,
        env=environment, stdin_bytes=source.read_bytes(), timeout_seconds=30,
        memory_ceiling_bytes=2 * 1024**3, sample_interval_seconds=0.1,
        max_trace_gap_seconds=5, cleanup_seconds=5, output_cap_bytes=20 * 1024**2,
    )
    (attempt / "stdout.log").write_bytes(result.stdout)
    (attempt / "stderr.log").write_bytes(result.stderr)
    save(attempt / "receipt.json", result.receipt)
    if fault(result.receipt):
        raise RuntimeError(f"supervision fault during repaired {role} run")
    classified, basis = verdict(
        result.receipt["exit_code"],
        (result.stdout + b"\n" + result.stderr).decode("utf-8", "replace"),
    )
    row = {
        "role": role, "input": input_path, "input_sha256": expected_sha,
        "attempt": str(attempt.relative_to(ROOT)), "exit_code": result.receipt["exit_code"],
        "verdict": classified, "verdict_basis": basis,
        "elapsed_seconds": result.receipt["elapsed_seconds"],
        "child_peak_rss_bytes": result.receipt["child_peak_rss_bytes"],
        "stdout_sha256": result.receipt["stdout_sha256"],
        "stderr_sha256": result.receipt["stderr_sha256"],
    }
    save(attempt / "outcome.json", row)
    return row


def main() -> None:
    if (RUN / "result-r2.json").exists() or (RUN / "outcomes-r2.jsonl").exists():
        raise RuntimeError("revision-2 final output already exists")
    manifest = json.loads((RUN / "execution-manifest-r2.json").read_text())
    preflight(manifest)
    rows = [run_cell(cell["role"], cell["input"], cell["sha256"])
            for cell in manifest["scientific_runs"]]
    (RUN / "outcomes-r2.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    verdicts = {row["role"]: row["verdict"] for row in rows}
    if verdicts == {"control": "ACCEPT", "candidate": "ACCEPT"}:
        outcome, signal_count = "SIGNAL", 1
        observation = ("Nanoda admitted the repaired candidate after accepting its control. "
                       "The separately frozen Lean check rejects the predicted candidate reduct because free universe u survives at level-1 motives.")
    elif verdicts["control"] == "ACCEPT" and verdicts["candidate"] == "REJECT":
        outcome, signal_count = "NO_SIGNAL", 0
        observation = "Nanoda accepted the repaired control and rejected the repaired candidate in semantic checking."
    else:
        outcome, signal_count = "INCONCLUSIVE", 0
        observation = "The repaired two-cell observation still did not reach a classified comparison."
    result = {
        "schema_version": 1, "evidence_class": "E0", "id": IDENT,
        "outcome": outcome, "signal_count": signal_count,
        "measurement_complete": True, "engineering_failures_unresolved": False,
        "planned_runs": 2, "completed_runs": len(rows), "verdicts": verdicts,
        "observation": observation, "cells": rows,
        "repair": {
            "prior_attempt": "explorations/runs/EXPLORE-NANODA-NESTED-RECURSOR-UNIVERSE-CAPTURE-1/result.json",
            "manifest": "explorations/runs/EXPLORE-NANODA-NESTED-RECURSOR-UNIVERSE-CAPTURE-1/execution-manifest-r2.json",
            "reason": "Revision 1 retained structurally duplicate dormant expression rows; Nanoda requires a unique continuous DAG. Revision 2 canonicalizes duplicates to existing pointers without changing the semantic pair."
        },
        "independent_reduct_result": "explorations/runs/EXPLORE-NANODA-NESTED-RECURSOR-UNIVERSE-CAPTURE-1/independent-reduct-result.json",
        "limitations": [
            "One constructed nested inductive and one exact Nanoda revision were screened.",
            "Nanoda was not instrumented to print its internal reduct; the reduct typing check is independent.",
            "E0 does not confirm a defect, general unsoundness, a proof of False, or cross-checker transfer."
        ]
    }
    save(RUN / "result-r2.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
