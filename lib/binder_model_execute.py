"""Supervised exact API observations for BINDER-MODEL-PILOT-1."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

from lib.binder_model_control import (
    BASE, CORPUS_LOCK, EXECUTION, ROOT, SCIENCE, GateError, binding,
    check_corpus_lock, check_frozen_inputs, committed, read_json, sha, write_new,
)
from lib.metamorphic_pilot_runner_v3 import run_supervised

PREFLIGHT = BASE / "rss-preflight.json"
SMOKE_MANIFEST = BASE / "smoke/manifest.json"
SMOKE_RESULT = BASE / "smoke/result.json"
PRELAUNCH_REVIEW = BASE / "independent-prelaunch-review.json"
RUNS = BASE / "runs"
LEAN = Path("/Users/danphifer/.elan/toolchains/leanprover--lean4---v4.33.0/bin/lean")
LEAN_SOURCE = BASE / "BinderObserver.lean"
KIOTA = BASE / "bin/kiota-observer"
ENV = {"LANG": "C", "PATH": "/usr/bin:/bin"}


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, val in pairs:
        if key in obj:
            raise GateError(f"duplicate JSON key: {key}")
        obj[key] = val
    return obj


def _bad_constant(value: str) -> Any:
    raise GateError(f"nonfinite JSON constant: {value}")


def _parse_lines(data: bytes, *, count: int) -> list[dict[str, Any]]:
    try:
        raw = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GateError("non-UTF8 observation") from exc
    if not raw.endswith("\n"):
        raise GateError("observation missing final newline")
    lines = raw.splitlines()
    if len(lines) != count or any(not line for line in lines):
        raise GateError(f"observation row count differs: {len(lines)} vs {count}")
    rows = []
    for line in lines:
        try:
            value = json.loads(line, object_pairs_hook=_pairs, parse_constant=_bad_constant)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            raise GateError(f"malformed observer JSON: {exc}") from exc
        if type(value) is not dict or set(value) != {"id", "outputs"}:
            raise GateError("observation record schema differs")
        if type(value["id"]) is not str or type(value["outputs"]) is not list:
            raise GateError("observation ID/output type differs")
        rows.append(value)
    return rows


def _tree(term: Any, *, depth: int = 0) -> None:
    if type(term) is not list or not term or type(term[0]) is not str or depth > 32:
        raise GateError("malformed observed expression")
    tag = term[0]
    if tag == "b" and len(term) == 2 and type(term[1]) is int and term[1] >= 0:
        return
    if tag == "s" and len(term) == 1:
        return
    if tag == "a" and len(term) == 3:
        _tree(term[1], depth=depth + 1)
        _tree(term[2], depth=depth + 1)
        return
    if tag == "l" and len(term) == 3:
        _tree(term[1], depth=depth + 1)
        _tree(term[2], depth=depth + 1)
        return
    if tag == "t" and len(term) == 4:
        for sub in term[1:]:
            _tree(sub, depth=depth + 1)
        return
    raise GateError("unexpected observed constructor/index")


def compare(input_bytes: bytes, output_bytes: bytes, *, expected_bytes: bytes | None = None) -> dict[str, Any]:
    try:
        inputs = [json.loads(line, object_pairs_hook=_pairs, parse_constant=_bad_constant)
                  for line in input_bytes.decode("utf-8").splitlines()]
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        raise GateError(f"malformed bound input JSON: {exc}") from exc
    if expected_bytes is None:
        expected = [{"id": item["id"], "outputs": item["expected"]} for item in inputs]
    else:
        expected = _parse_lines(expected_bytes, count=len(inputs))
    observed = _parse_lines(output_bytes, count=len(inputs))
    mismatches: list[dict[str, Any]] = []
    stages = 0
    for index, (want, got) in enumerate(zip(expected, observed)):
        if got["id"] != want["id"] or got["id"] != inputs[index]["id"]:
            raise GateError(f"observation ID/order differs at row {index}")
        if len(got["outputs"]) != len(want["outputs"]):
            raise GateError(f"observation stage count differs at row {index}")
        for stage, (w, g) in enumerate(zip(want["outputs"], got["outputs"])):
            _tree(g)
            _tree(w)
            stages += 1
            if g != w:
                mismatches.append({"id": got["id"], "stage": stage + 1,
                                   "expected": w, "observed": g})
    return {"status": "MATCH" if not mismatches else "DISTINGUISHING",
            "vectors": len(inputs), "stage_outputs": stages, "mismatches": mismatches}


def _profile_argv(profile: str, input_path: Path) -> list[str]:
    if profile == "official-lean-4.33.0":
        return [str(LEAN), "--run", str(LEAN_SOURCE), str(input_path)]
    if profile == "kiota-2d2a9fa":
        return [str(KIOTA), str(input_path)]
    raise GateError("unexpected profile")


def _safety(receipt: dict[str, Any]) -> None:
    if (receipt["exit_code"] != 0 or receipt["timed_out"] or receipt["memory_exceeded"]
            or receipt["memory_monitor_error"] or receipt["memory_monitor_samples"] <= 0
            or receipt["maximum_observed_rss_bytes"] <= 0 or not receipt["cleanup_complete"]):
        raise GateError("supervised process failed or safety evidence incomplete")
    if receipt["stderr_bytes"] != 0:
        raise GateError("observer emitted unexpected stderr")


def freeze_smoke() -> dict[str, Any]:
    execution = check_frozen_inputs()
    for row in execution["tooling"]:
        if row["path"].startswith("results/research/binder-model-pilot-1/smoke/"):
            committed(ROOT / row["path"])
    rows = [binding(BASE / f"smoke/{name}") for name in ("inputs.ndjson", "expected.ndjson", "contexts.json")]
    result = {"schema_version": 1, "item_id": "BINDER-MODEL-PILOT-1",
              "role": "pre-registered capability smoke outside 10000 scientific vectors",
              "scientific_manifest_sha256": sha(SCIENCE),
              "execution_manifest_sha256": sha(EXECUTION),
              "profiles": execution["profiles"], "case_count": 5, "stage_outputs": 7,
              "fixtures": rows, "runtime": execution["runtime"]}
    write_new(SMOKE_MANIFEST, result)
    return result


def _check_smoke_manifest() -> dict[str, Any]:
    committed(SMOKE_MANIFEST)
    row = read_json(SMOKE_MANIFEST)
    if row["scientific_manifest_sha256"] != sha(SCIENCE) or row["execution_manifest_sha256"] != sha(EXECUTION):
        raise GateError("smoke manifest binding differs")
    from lib.binder_model_control import check_bindings
    check_bindings(row["fixtures"])
    check_bindings(row["runtime"], require_committed=False)
    if row["case_count"] != 5 or row["stage_outputs"] != 7:
        raise GateError("smoke scope differs")
    return row


def rss_preflight() -> dict[str, Any]:
    execution = check_frozen_inputs()
    _check_smoke_manifest()
    safety = execution["process_safety"]
    attempts = BASE / "preflight"
    attempts.mkdir(exist_ok=True)
    index = len(list(attempts.glob("attempt-[0-9][0-9][0-9][0-9]"))) + 1
    outdir = attempts / f"attempt-{index:04d}"
    outdir.mkdir(exist_ok=False)
    raw = outdir / "process"
    try:
        receipt = run_supervised(
            argv=[sys.executable, "-c", "import time; time.sleep(0.1)"], cwd=ROOT,
            stdin=None, env=ENV, timeout_seconds=5,
            memory_bytes=safety["rss_ceiling_bytes"], raw_prefix=raw)
    except Exception as exc:
        write_new(outdir / "result.json", {"schema_version": 1, "attempt": index,
                  "status": "FAILED", "error_type": type(exc).__name__, "error": str(exc),
                  "execution_manifest_sha256": sha(EXECUTION),
                  "smoke_manifest_sha256": sha(SMOKE_MANIFEST)})
        raise
    result = {"schema_version": 1, "attempt": index, "status": "FAILED", "receipt": receipt,
              "execution_manifest_sha256": sha(EXECUTION),
              "smoke_manifest_sha256": sha(SMOKE_MANIFEST)}
    try:
        _safety(receipt)
    except GateError:
        write_new(outdir / "result.json", result)
        raise
    result["status"] = "PASS"
    write_new(outdir / "result.json", result)
    write_new(PREFLIGHT, result)
    return result


def _check_preflight() -> None:
    committed(PREFLIGHT)
    row = read_json(PREFLIGHT)
    if (row["status"] != "PASS" or row["execution_manifest_sha256"] != sha(EXECUTION)
            or row["smoke_manifest_sha256"] != sha(SMOKE_MANIFEST)):
        raise GateError("actual-host RSS preflight missing or differs")
    _safety(row["receipt"])


def run_smoke() -> dict[str, Any]:
    execution = check_frozen_inputs()
    _check_smoke_manifest()
    _check_preflight()
    input_path = BASE / "smoke/inputs.ndjson"
    input_bytes = input_path.read_bytes()
    expected_bytes = (BASE / "smoke/expected.ndjson").read_bytes()
    attempts = BASE / "smoke/attempts"
    attempts.mkdir(exist_ok=True)
    index = len(list(attempts.glob("attempt-[0-9][0-9][0-9][0-9]"))) + 1
    outdir = attempts / f"attempt-{index:04d}"
    outdir.mkdir(exist_ok=False)
    out: dict[str, Any] = {"schema_version": 1, "attempt": index, "status": "RUNNING", "profiles": {},
                           "execution_manifest_sha256": sha(EXECUTION),
                           "smoke_manifest_sha256": sha(SMOKE_MANIFEST),
                           "rss_preflight_sha256": sha(PREFLIGHT)}
    for profile in execution["profiles"]:
        raw = outdir / profile / "process"
        try:
            receipt = run_supervised(argv=_profile_argv(profile, input_path), cwd=ROOT,
                                     stdin=None, env=ENV,
                                     timeout_seconds=execution["process_safety"]["timeout_seconds"],
                                     memory_bytes=execution["process_safety"]["rss_ceiling_bytes"],
                                     raw_prefix=raw)
        except Exception as exc:
            out["status"] = "FAILED"
            out["error_type"] = type(exc).__name__
            out["error"] = str(exc)
            write_new(outdir / "result.json", out)
            raise
        out["profiles"][profile] = {"receipt": receipt}
        try:
            _safety(receipt)
            comparison = compare(input_bytes, (ROOT / receipt["raw_stdout_path"]).read_bytes(),
                                 expected_bytes=expected_bytes)
            out["profiles"][profile]["comparison"] = comparison
            if comparison["status"] != "MATCH" or comparison["stage_outputs"] != 7:
                raise GateError("smoke semantic comparison differs")
        except GateError as exc:
            out["status"] = "FAILED"
            out["error"] = str(exc)
            write_new(outdir / "result.json", out)
            raise
    out["status"] = "PASS"
    write_new(outdir / "result.json", out)
    write_new(SMOKE_RESULT, out)
    return out


def _launch_gate() -> dict[str, Any]:
    execution = check_frozen_inputs()
    lock = check_corpus_lock()
    _check_smoke_manifest()
    _check_preflight()
    committed(SMOKE_RESULT)
    smoke = read_json(SMOKE_RESULT)
    if smoke["status"] != "PASS" or smoke["execution_manifest_sha256"] != sha(EXECUTION):
        raise GateError("smoke gate differs")
    committed(PRELAUNCH_REVIEW)
    review = read_json(PRELAUNCH_REVIEW)
    if (review.get("verdict") != "PASS_FOR_SCIENTIFIC_LAUNCH"
            or review.get("scientific_manifest_sha256") != sha(SCIENCE)
            or review.get("execution_manifest_sha256") != sha(EXECUTION)
            or review.get("corpus_lock_sha256") != sha(CORPUS_LOCK)
            or review.get("smoke_result_sha256") != sha(SMOKE_RESULT)):
        raise GateError("independent prelaunch gate absent or differs")
    return {"execution": execution, "corpus_lock": lock}


def run_science() -> dict[str, Any]:
    gate = _launch_gate()
    execution = gate["execution"]
    RUNS.mkdir(exist_ok=True)
    index = len(list(RUNS.glob("attempt-[0-9][0-9][0-9][0-9]"))) + 1
    outdir = RUNS / f"attempt-{index:04d}"
    outdir.mkdir(exist_ok=False)
    result: dict[str, Any] = {"schema_version": 1, "item_id": "BINDER-MODEL-PILOT-1",
                              "attempt": index, "status": "RUNNING", "cells": [],
                              "scientific_manifest_sha256": sha(SCIENCE),
                              "execution_manifest_sha256": sha(EXECUTION),
                              "corpus_lock_sha256": sha(CORPUS_LOCK),
                              "prelaunch_review_sha256": sha(PRELAUNCH_REVIEW)}
    (outdir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    for profile in execution["profiles"]:
        for batch in range(execution["batch_count"]):
            input_path = BASE / f"corpus/batch-{batch:02d}.ndjson"
            cell_dir = outdir / profile / f"batch-{batch:02d}"
            cell_dir.mkdir(parents=True, exist_ok=False)
            try:
                receipt = run_supervised(
                    argv=_profile_argv(profile, input_path), cwd=ROOT, stdin=None, env=ENV,
                    timeout_seconds=execution["process_safety"]["timeout_seconds"],
                    memory_bytes=execution["process_safety"]["rss_ceiling_bytes"],
                    raw_prefix=cell_dir / "process")
            except Exception as exc:
                result["status"] = "PAUSED_FOR_REPAIR"
                result["error_type"] = type(exc).__name__
                result["error"] = str(exc)
                (outdir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
                raise
            (cell_dir / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            cell: dict[str, Any] = {"profile": profile, "batch": batch,
                                    "input": binding(input_path),
                                    "receipt": binding(cell_dir / "receipt.json")}
            result["cells"].append(cell)
            try:
                _safety(receipt)
                comparison = compare(input_path.read_bytes(),
                                     (ROOT / receipt["raw_stdout_path"]).read_bytes())
                cell["comparison"] = comparison
                (cell_dir / "comparison.json").write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n")
            except GateError as exc:
                result["status"] = "PAUSED_FOR_REPAIR"
                result["error"] = str(exc)
                (outdir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
                raise
            (outdir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    comparisons = [cell["comparison"] for cell in result["cells"]]
    result["vector_observations"] = sum(c["vectors"] for c in comparisons)
    result["stage_outputs"] = sum(c["stage_outputs"] for c in comparisons)
    result["mismatches"] = [dict(profile=cell["profile"], batch=cell["batch"], **m)
                            for cell in result["cells"] for m in cell["comparison"]["mismatches"]]
    if result["vector_observations"] != 20000 or result["stage_outputs"] != 30000:
        result["status"] = "PAUSED_FOR_REPAIR"
        result["error"] = "observation accounting differs"
    else:
        result["status"] = "COMPLETE_WITH_DIFFERENCES" if result["mismatches"] else "COMPLETE_MATCH"
    (outdir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result
