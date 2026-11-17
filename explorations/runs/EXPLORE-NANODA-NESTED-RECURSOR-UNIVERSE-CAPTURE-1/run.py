#!/usr/bin/env python3
"""Run the two frozen Nanoda cells after the prospective ledger start exists."""
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


def supervision_fault(receipt: dict[str, object]) -> bool:
    return bool(
        receipt["accounting_error"] or receipt["monitor_errors"]
        or receipt["pipe_errors"] or receipt["cleanup_errors"]
        or receipt["trace_gap_fault"] or not receipt["reap_complete"]
        or not receipt["cleanup_complete"]
    )


def require_started() -> None:
    events = [json.loads(line) for line in (ROOT / "explorations/ledger.jsonl").read_text().splitlines()]
    ours = [row for row in events if row["id"] == IDENT]
    if len(ours) != 1 or ours[0]["event"] != "start":
        raise RuntimeError("exactly one open prospective start event is required before launch")


def validate_gates(protocol: dict[str, object]) -> None:
    checker = protocol["checker"]
    if sha(ROOT / checker["binary"]) != checker["binary_sha256"]:
        raise RuntimeError("checker binary identity changed")
    if sha(ROOT / checker["config"]) != checker["config_sha256"]:
        raise RuntimeError("checker config identity changed")
    for cell in protocol["scientific_runs"]:
        if sha(ROOT / cell["input"]) != cell["sha256"]:
            raise RuntimeError(f"{cell['role']} input identity changed")
    audit = json.loads((RUN / "fixture-audit.json").read_text())
    if not (
        audit["target"]["numNested"] == 1
        and audit["target"]["declared_universes"] == ["v"]
        and audit["target"]["control_rule_levels"] == [2]
        and audit["target"]["candidate_rule_levels"] == [3]
        and audit["target"]["candidate_rule_free_universe"] == "u"
        and audit["observer"]["declared_universes"] == []
        and audit["observer"]["abstract_motives_and_minors"]
        and audit["observer"]["neutral_children"]
        and audit["pair_differences"] == [{
            "candidate": 117,
            "control": 80,
            "pointer": "/143/inductive/recs/1/rules/0/rhs",
        }]
    ):
        raise RuntimeError("fixture semantic audit no longer satisfies the launch gate")
    reduct = json.loads((RUN / "independent-reduct-result.json").read_text())
    if not (
        reduct["control"]["exit_code"] == 0
        and reduct["candidate"]["exit_code"] == 1
        and "level-1 motive is not a motive into Sort u" in reduct["observation"]
    ):
        raise RuntimeError("independent reduct gate no longer satisfies the protocol")


def classify_exit(exit_code: int, output: str) -> tuple[str, str]:
    if exit_code == 0:
        return "ACCEPT", "checker completed successfully"
    lowered = output.lower()
    parser_markers = ("parser", "parse error", "failed to parse", "unexpected token")
    semantic_markers = ("src/tc.rs", "src/inductive.rs", "assertion", "def_eq", "typecheck")
    if any(marker in lowered for marker in parser_markers):
        return "PARSER_OR_ADAPTER_FAILURE", "diagnostic contains a parser marker"
    if any(marker in lowered for marker in semantic_markers):
        return "REJECT", "diagnostic reaches a checker or inductive semantic assertion"
    return "UNATTRIBUTED_NONZERO", "nonzero exit lacks a retained semantic source marker"


def run_cell(protocol: dict[str, object], cell: dict[str, object]) -> dict[str, object]:
    role = cell["role"]
    attempt = RUN / "attempts" / f"checker-{role}-r1"
    attempt.mkdir(parents=True, exist_ok=False)
    checker = protocol["checker"]
    source = ROOT / cell["input"]
    if sha(source) != cell["sha256"]:
        raise RuntimeError(f"{role} changed immediately before launch")
    environment = dict(os.environ)
    environment["RUST_BACKTRACE"] = "1"
    result = run_direct(
        argv=[str(ROOT / checker["binary"]), str(ROOT / checker["config"])],
        cwd=ROOT,
        env=environment,
        stdin_bytes=source.read_bytes(),
        timeout_seconds=30,
        memory_ceiling_bytes=2 * 1024**3,
        sample_interval_seconds=0.1,
        max_trace_gap_seconds=5,
        cleanup_seconds=5,
        output_cap_bytes=20 * 1024**2,
    )
    (attempt / "stdout.log").write_bytes(result.stdout)
    (attempt / "stderr.log").write_bytes(result.stderr)
    save(attempt / "receipt.json", result.receipt)
    if supervision_fault(result.receipt):
        raise RuntimeError(f"supervision fault during {role}; preserve and repair before continuing")
    output = (result.stdout + b"\n" + result.stderr).decode("utf-8", "replace")
    verdict, basis = classify_exit(result.receipt["exit_code"], output)
    row = {
        "role": role,
        "input": cell["input"],
        "input_sha256": cell["sha256"],
        "attempt": str(attempt.relative_to(ROOT)),
        "exit_code": result.receipt["exit_code"],
        "verdict": verdict,
        "verdict_basis": basis,
        "elapsed_seconds": result.receipt["elapsed_seconds"],
        "child_peak_rss_bytes": result.receipt["child_peak_rss_bytes"],
        "stdout_sha256": result.receipt["stdout_sha256"],
        "stderr_sha256": result.receipt["stderr_sha256"],
    }
    save(attempt / "outcome.json", row)
    return row


def main() -> None:
    if (RUN / "result.json").exists() or (RUN / "outcomes.jsonl").exists():
        raise RuntimeError("final scientific output already exists")
    require_started()
    protocol = json.loads((RUN / "protocol.json").read_text())
    validate_gates(protocol)
    rows = []
    for cell in protocol["scientific_runs"]:
        rows.append(run_cell(protocol, cell))
        print(json.dumps(rows[-1], sort_keys=True), flush=True)
    (RUN / "outcomes.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    verdicts = {row["role"]: row["verdict"] for row in rows}
    if verdicts == {"control": "ACCEPT", "candidate": "ACCEPT"}:
        outcome = "SIGNAL"
        signal_count = 1
        explanation = (
            "Nanoda admitted the candidate after accepting the control, while the independently "
            "checked candidate reduct retains free universe u and is ill-typed at the fixed level-1 motives."
        )
    elif verdicts["control"] == "ACCEPT" and verdicts["candidate"] == "REJECT":
        outcome = "NO_SIGNAL"
        signal_count = 0
        explanation = "Nanoda accepted the control and rejected the candidate in semantic checking."
    else:
        outcome = "INCONCLUSIVE"
        signal_count = 0
        explanation = "The two-cell observation did not satisfy either the signal or bounded no-signal rule."
    result = {
        "schema_version": 1,
        "evidence_class": "E0",
        "id": IDENT,
        "outcome": outcome,
        "signal_count": signal_count,
        "measurement_complete": True,
        "engineering_failures_unresolved": False,
        "completed_runs": len(rows),
        "planned_runs": len(protocol["scientific_runs"]),
        "verdicts": verdicts,
        "observation": explanation,
        "independent_reduct_result": "explorations/runs/EXPLORE-NANODA-NESTED-RECURSOR-UNIVERSE-CAPTURE-1/independent-reduct-result.json",
        "fixture_audit": "explorations/runs/EXPLORE-NANODA-NESTED-RECURSOR-UNIVERSE-CAPTURE-1/fixture-audit.json",
        "cells": rows,
        "limitations": [
            "One constructed nested inductive and one exact Nanoda revision were screened.",
            "Nanoda was not instrumented to print its internal reduct; the reduct typing check is independent.",
            "E0 does not confirm a defect, general unsoundness, a proof of False, or cross-checker transfer."
        ]
    }
    save(RUN / "result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
