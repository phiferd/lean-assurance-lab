#!/usr/bin/env python3
"""Retain an independent Lean check of the control and candidate reducts."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.resource_envelope_supervisor import run_direct

RUN = Path(__file__).resolve().parent
LEAN = Path("/Users/danphifer/.elan/bin/lean")


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


def check(role: str, source: Path) -> dict[str, object]:
    directory = RUN / "attempts" / f"independent-{role}-r3"
    directory.mkdir(parents=True, exist_ok=False)
    result = run_direct(
        argv=[str(LEAN), str(source)], cwd=ROOT, env=dict(os.environ),
        stdin_bytes=None, timeout_seconds=30, memory_ceiling_bytes=2 * 1024**3,
        sample_interval_seconds=0.1, max_trace_gap_seconds=5,
        cleanup_seconds=5, output_cap_bytes=2 * 1024**2,
    )
    (directory / "stdout.log").write_bytes(result.stdout)
    (directory / "stderr.log").write_bytes(result.stderr)
    save(directory / "receipt.json", result.receipt)
    if supervision_fault(result.receipt):
        raise RuntimeError(f"supervision fault during independent {role} check")
    return {
        "role": role,
        "source": str(source.relative_to(ROOT)),
        "source_sha256": sha(source),
        "exit_code": result.receipt["exit_code"],
        "stdout_sha256": result.receipt["stdout_sha256"],
        "stderr_sha256": result.receipt["stderr_sha256"],
        "attempt": str(directory.relative_to(ROOT)),
    }


def main() -> None:
    if (RUN / "independent-reduct-result.json").exists():
        raise RuntimeError("independent result already exists")
    version = subprocess.run(
        [str(LEAN), "--version"], check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.strip()
    control = check("control", RUN / "independent-control.lean")
    candidate = check("candidate", RUN / "independent-candidate.lean")
    candidate_output = b"".join([
        (ROOT / candidate["attempt"] / "stdout.log").read_bytes(),
        (ROOT / candidate["attempt"] / "stderr.log").read_bytes(),
    ]).decode("utf-8", "replace")
    if control["exit_code"] != 0:
        raise RuntimeError("independent control did not type-check")
    if candidate["exit_code"] == 0 or "LALNest → Sort u" not in candidate_output:
        raise RuntimeError("candidate did not fail at the expected universe mismatch")
    result = {
        "schema_version": 1,
        "checker": "official Lean elaborator and kernel",
        "version": version,
        "control": control,
        "candidate": candidate,
        "observation": "The level-1 control reduct checks. The candidate reduct at free level u is rejected because its level-1 motive is not a motive into Sort u.",
        "separation": "The admission export contains only the ordinary level-1 application; this independent source reifies the predicted reduct and is not imported by Nanoda.",
        "repair": "Retained r1 used theorem for a computational term and was rejected because theorem types must be propositions. Retained r2 used opaque but still reached unsupported code generation for the auxiliary recursor. Revision r3 uses noncomputable definitions so elaboration and kernel checking occur without code generation.",
    }
    save(RUN / "independent-reduct-result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
