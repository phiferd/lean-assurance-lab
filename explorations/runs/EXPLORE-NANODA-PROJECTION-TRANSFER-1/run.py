#!/usr/bin/env python3
"""Run one fixed historical affected/fixed pair over the frozen compact sample."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.resource_envelope_supervisor import run_direct

RUN = Path(__file__).resolve().parent
TRIAL = json.loads((RUN / "trial.json").read_text())
SELECTION = json.loads((ROOT / TRIAL["selection_path"]).read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def normalize_exit(code: int | None) -> str:
    if code is None:
        return "TIMEOUT"
    if code == 0:
        return "ACCEPT"
    if code == 2:
        return "DECLINE"
    if code < 0:
        return "CRASH"
    return "REJECT"


def diagnostic_class(outcome: str, stdout: bytes, stderr: bytes) -> str:
    if outcome != "REJECT":
        return outcome
    text = (stdout + b"\n" + stderr).decode("utf-8", "replace").lower()
    parser_patterns = (
        r"json[^\n]*(parse|syntax|deserialize)",
        r"(parse|parser|deserialize|serde)[^\n]*(error|fail|invalid)",
        r"expected (a |an )?(json|object|array|value)",
        r"invalid json",
    )
    return "PARSER_OR_ADAPTER_FAILURE" if any(
        re.search(pattern, text) for pattern in parser_patterns
    ) else "REJECT"


def supervision_fault(receipt: dict[str, object]) -> bool:
    return bool(
        receipt["accounting_error"]
        or receipt["monitor_errors"]
        or receipt["pipe_errors"]
        or receipt["cleanup_errors"]
        or receipt["trace_gap_fault"]
        or not receipt["reap_complete"]
        or not receipt["cleanup_complete"]
    )


def attempt(role: str, index: int, item: dict[str, object]) -> dict[str, object]:
    profile = TRIAL["binaries"][role]
    directory = RUN / "attempts" / f"{role}-{index:03d}"
    directory.mkdir(parents=True, exist_ok=False)
    binary = ROOT / profile["path"]
    artifact = ROOT / item["path"]
    if TRIAL["invocation"] == "path":
        argv = [str(binary), str(artifact)]
        stdin = None
    elif TRIAL["invocation"] == "stdin":
        argv = [str(binary), str(RUN / TRIAL["config_path"])]
        stdin = artifact.read_bytes()
    else:
        raise RuntimeError("unknown invocation mode")
    save(directory / "command.json", {
        "argv": argv,
        "cwd": str(ROOT),
        "stdin_sha256": None if stdin is None else hashlib.sha256(stdin).hexdigest(),
        "artifact": item,
    })
    result = run_direct(
        argv=argv,
        cwd=ROOT,
        env=dict(os.environ),
        stdin_bytes=stdin,
        timeout_seconds=30,
        memory_ceiling_bytes=2 * 1024**3,
        sample_interval_seconds=3,
        max_trace_gap_seconds=10,
        cleanup_seconds=10,
        output_cap_bytes=20 * 1024**2,
    )
    (directory / "stdout").write_bytes(result.stdout)
    (directory / "stderr").write_bytes(result.stderr)
    save(directory / "receipt.json", result.receipt)
    category = normalize_exit(result.receipt["exit_code"])
    row = {
        "role": role,
        "index": index,
        "path": item["path"],
        "sha256": item["sha256"],
        "normalized_outcome": category,
        "diagnostic_class": diagnostic_class(category, result.stdout, result.stderr),
        "exit_code": result.receipt["exit_code"],
        "elapsed_seconds": result.receipt["elapsed_seconds"],
        "stdout_sha256": result.receipt["stdout_sha256"],
        "stderr_sha256": result.receipt["stderr_sha256"],
        "attempt": str(directory.relative_to(ROOT)),
    }
    with (RUN / "outcomes.jsonl").open("a") as output:
        output.write(json.dumps(row, sort_keys=True) + "\n")
    if supervision_fault(result.receipt):
        raise RuntimeError(f"supervision fault in {directory.name}")
    return row


def main() -> None:
    if (RUN / "attempts").exists() or (RUN / "outcomes.jsonl").exists():
        raise RuntimeError("trial output already exists; preserve it and use a linked repair")
    selected = SELECTION["selected"]
    if len(selected) != 90 or SELECTION["augmented"] == []:
        raise RuntimeError("unexpected frozen selection")
    if any("collatz" in item["path"].lower() or "EXPLORE-NANODA-CONGRUENCE" in item["path"]
           for item in selected):
        raise RuntimeError("excluded witness entered fixed selection")
    for item in selected:
        path = ROOT / item["path"]
        if path.stat().st_size != item["bytes"] or digest(path) != item["sha256"]:
            raise RuntimeError("stale selected input: " + item["path"])
    for profile in TRIAL["binaries"].values():
        path = ROOT / profile["path"]
        if path.stat().st_size != profile["bytes"] or digest(path) != profile["sha256"]:
            raise RuntimeError("stale binary: " + profile["path"])
    if TRIAL["invocation"] == "stdin":
        config = RUN / TRIAL["config_path"]
        if digest(config) != TRIAL["config_sha256"]:
            raise RuntimeError("stale retained config")

    save(RUN / "execution-preflight.json", {
        "trial_id": TRIAL["trial_id"],
        "activation_commit": TRIAL["activation_commit"],
        "selection_files": len(selected),
        "selection_bytes": sum(item["bytes"] for item in selected),
        "binary_sha256": {role: item["sha256"] for role, item in TRIAL["binaries"].items()},
        "excluded_collatz_holdout_and_targeted_pair": True,
    })
    rows: list[dict[str, object]] = []
    for role in ("affected", "fixed"):
        for index, item in enumerate(selected):
            rows.append(attempt(role, index, item))
            if (index + 1) % 15 == 0:
                print(role, index + 1, "of", len(selected), flush=True)

    by_key = {(row["role"], row["path"]): row for row in rows}
    comparisons = []
    for item in selected:
        affected = by_key[("affected", item["path"])]
        fixed = by_key[("fixed", item["path"])]
        comparable = (
            affected["diagnostic_class"] != "PARSER_OR_ADAPTER_FAILURE"
            and fixed["diagnostic_class"] != "PARSER_OR_ADAPTER_FAILURE"
            and affected["normalized_outcome"] not in {"TIMEOUT", "CRASH", "DECLINE"}
            and fixed["normalized_outcome"] not in {"TIMEOUT", "CRASH", "DECLINE"}
        )
        comparisons.append({
            "path": item["path"],
            "sha256": item["sha256"],
            "affected_outcome": affected["normalized_outcome"],
            "fixed_outcome": fixed["normalized_outcome"],
            "affected_diagnostic_class": affected["diagnostic_class"],
            "fixed_diagnostic_class": fixed["diagnostic_class"],
            "comparable": comparable,
            "different": affected["normalized_outcome"] != fixed["normalized_outcome"],
        })
    with (RUN / "comparisons.jsonl").open("w") as output:
        for row in comparisons:
            output.write(json.dumps(row, sort_keys=True) + "\n")
    signals = [row for row in comparisons if row["comparable"] and row["different"]]
    boundaries = [row for row in comparisons if not row["comparable"]]
    exceptional = [row for row in rows if row["normalized_outcome"] in {"TIMEOUT", "CRASH", "DECLINE"}]
    result = {
        "schema_version": 1,
        "evidence_class": "E0",
        "trial_id": TRIAL["trial_id"],
        "historical_fault": TRIAL["historical_fault"],
        "sample_files": len(selected),
        "attempts": len(rows),
        "comparable_inputs": sum(row["comparable"] for row in comparisons),
        "compatibility_boundaries": len(boundaries),
        "exceptional_observations": len(exceptional),
        "signal_count": len(signals),
        "signals": signals,
        "boundary_rows": boundaries,
        "binary_sha256": {role: item["sha256"] for role, item in TRIAL["binaries"].items()},
        "total_process_seconds": sum(float(row["elapsed_seconds"]) for row in rows),
        "measurement_complete": len(rows) == 180 and not exceptional,
    }
    save(RUN / "result.json", result)
    (RUN / "summary.md").write_text(
        "# Historical-fault transfer E0 result\n\n"
        f"**What did we find?** The fixed 90-file sample produced {len(signals)} "
        f"comparable affected/fixed verdict difference(s) for {TRIAL['historical_fault']}. "
        f"{len(boundaries)} input(s) had a parser/adapter or other compatibility boundary.\n\n"
        f"**Is it interesting?** {'Yes; the differing rows require causal review.' if signals else 'No transfer signal was observed in this fixed sample.'}\n\n"
        f"**Does it require more work?** {'Review the exact differing diagnostics and source boundary before any contribution decision.' if signals else 'No fault-specific follow-up follows from this trial.'}\n\n"
        "This is E0 screening evidence over exact retained binaries. It is not a defect-prevalence, "
        "implementation-quality, conformance or correctness claim.\n"
    )
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
