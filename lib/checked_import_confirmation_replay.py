"""Portable, nonexecuting replay of the checked-import E1 evidence package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


BASE = Path("results/research/confirm-checked-import-cases-1")


class ReplayError(ValueError):
    pass


def _json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ReplayError(f"invalid JSON evidence: {path}: {error}") from error


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slug(text: str) -> str:
    return text.lower().replace("/", "-").replace("_", "-")


def _label(cell: dict) -> str:
    return f"cell-{cell['ordinal']:02d}-{_slug(cell['id'])}"


def _receipt(attempt: Path) -> tuple[dict, str, str]:
    receipt = _json(attempt / "receipt.json")
    try:
        stdout = (attempt / "stdout.log").read_bytes()
        stderr = (attempt / "stderr.log").read_bytes()
    except OSError as error:
        raise ReplayError(f"missing raw stream: {attempt}: {error}") from error
    if (receipt.get("stdout_sha256") != _sha(stdout)
            or receipt.get("stderr_sha256") != _sha(stderr)
            or receipt.get("stdout_bytes") != len(stdout)
            or receipt.get("stderr_bytes") != len(stderr)):
        raise ReplayError(f"raw stream binding differs: {attempt}")
    if (not receipt.get("cleanup_complete") or not receipt.get("reap_complete")
            or receipt.get("monitor_errors") != [] or receipt.get("cleanup_errors") != []
            or receipt.get("pipe_errors") != [] or receipt.get("accounting_error") is not None
            or receipt.get("trace_gap_fault")):
        raise ReplayError(f"supervision fault: {attempt}")
    return receipt, stdout.decode(), stderr.decode()


def _classify(cell: dict, receipt: dict, stdout: str, stderr: str) -> tuple[str, str]:
    family, checker = cell["family"], cell["checker"]
    expected, declaration = cell["expected"], cell["declaration"]
    if receipt.get("stop_reason") is not None:
        raise ReplayError(f"scientific cell stopped: {cell['id']}")
    if checker == "lean":
        if f"NAME {declaration}\nPARAMS \n" not in stdout:
            raise ReplayError(f"missing Lean declaration identity: {cell['id']}")
        if expected == "ACCEPT":
            if (receipt["exit_code"] != 0 or stderr != ""
                    or not stdout.endswith("Accepted 1 definition; empty environment; trust level 0.\n")):
                raise ReplayError(f"invalid Lean accept: {cell['id']}")
            return "ACCEPT", "trust-0 empty-environment replay checked the named definition"
        if receipt["exit_code"] != 1 or f"while replaying declaration '{declaration}'" not in stderr:
            raise ReplayError(f"invalid Lean reject: {cell['id']}")
        if family == "expression":
            if "(kernel) application type mismatch" not in stderr:
                raise ReplayError(f"unattributed Lean application reject: {cell['id']}")
            return "REJECT", "Lean kernel application domain comparison"
        if "(kernel) type expected" not in stderr or "fun _ => Prop" not in stderr:
            raise ReplayError(f"unattributed Lean Pi reject: {cell['id']}")
        return "REJECT", "Lean kernel declared/value Pi codomain sort inference"
    if expected == "ACCEPT":
        if (receipt["exit_code"] != 0 or stderr != ""
                or not stdout.startswith(f"def {declaration} ")
                or not stdout.endswith("Checked 1 declarations with no errors\n")):
            raise ReplayError(f"invalid Nanoda accept: {cell['id']}")
        return "ACCEPT", "Nanoda checked and printed the named one-definition input"
    if receipt["exit_code"] != 101 or stdout != "":
        raise ReplayError(f"invalid Nanoda reject: {cell['id']}")
    if family == "expression":
        if ("panicked at src/tc.rs:955:71" not in stderr
                or "assertion failed: self.def_eq(u, v)" not in stderr):
            raise ReplayError(f"unattributed Nanoda application reject: {cell['id']}")
        return "REJECT", "Nanoda checked application domain equality assertion"
    if "src/tc.rs:304:18" not in stderr or "infer_sort_of could not infer a sort" not in stderr:
        raise ReplayError(f"unattributed Nanoda Pi reject: {cell['id']}")
    return "REJECT", "Nanoda Pi codomain infer_sort_of assertion"


def replay(root: Path) -> dict:
    root = Path(root).resolve()
    base = root / BASE
    manifest = _json(base / "execution-manifest.json")
    final = _json(base / "result.json")
    if (manifest.get("item_id") != "CONFIRM-CHECKED-IMPORT-CASES-1"
            or manifest.get("cells_per_phase") != 20
            or final.get("status") != "SUCCESS"):
        raise ReplayError("invalid manifest or final result envelope")
    receipt_paths = sorted(base.rglob("receipt.json"))
    for path in receipt_paths:
        receipt, _, _ = _receipt(path.parent)
        allowed_stop = path.as_posix().endswith(
            "preflight-r2/attempts/05-intentional-timeout/receipt.json")
        if receipt.get("stop_reason") != ("OBSERVED_TIME_LIMIT" if allowed_stop else None):
            raise ReplayError(f"unexpected stop classification: {path}")
    classified = {}
    for phase in ("initial", "replay"):
        result = _json(base / phase / "result.json")
        if result.get("status") != "COMPLETE_EXPECTED" or result.get("attributable_cells") != 20:
            raise ReplayError(f"incomplete phase result: {phase}")
        recorded = {row["id"]: row for row in result["cells"]}
        for cell in manifest["cases"]:
            receipt, stdout, stderr = _receipt(base / phase / "attempts" / _label(cell))
            outcome, attribution = _classify(cell, receipt, stdout, stderr)
            row = recorded.get(cell["id"])
            if (row is None or row.get("outcome") != outcome
                    or row.get("attribution") != attribution
                    or row.get("input_sha256") != cell["input"]["sha256"]):
                raise ReplayError(f"phase result differs from raw evidence: {phase}/{cell['id']}")
            classified[(phase, cell["id"])] = outcome
    if len(classified) != 40 or final.get("attributable_cells") != 40:
        raise ReplayError("final cell count differs")
    for cell in manifest["cases"]:
        if classified[("initial", cell["id"])] != classified[("replay", cell["id"])]:
            raise ReplayError(f"replay differs: {cell['id']}")
    return {
        "status": "PASS",
        "process_receipts": len(receipt_paths),
        "scientific_cells": len(classified),
        "reproduced_cell_identities": len(manifest["cases"]),
        "host_launches": 0,
    }
