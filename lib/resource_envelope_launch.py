"""Sealing, smoke, and fixed-matrix launch controls for the resource pilot."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from lib.resource_envelope_audit import audit_corpus
from lib.resource_envelope_control import (
    BASE, EMPTY_EXPORT, EXECUTION, OFFICIAL_BINARY, NANODA_BINARY, ROOT,
    SCIENCE, GateError, _check_binding, _committed, _read, _write_new,
    binding, require_construction_gate,
)
from lib.resource_envelope_producer import canonical_json, case_id, selected_slots
from lib.resource_envelope_observe import classify
from lib.resource_envelope_supervisor import SupervisedResult, run_direct


CORPUS = BASE / "corpus"
CORPUS_LOCK = BASE / "corpus-lock.json"
CORPUS_REVIEW = BASE / "independent-corpus-review.json"
SMOKE_MANIFEST = BASE / "smoke-manifest.json"
SMOKE_LAUNCH_REVIEW = BASE / "independent-smoke-launch-review.json"
SMOKE_RESULT = BASE / "smoke-result.json"
SMOKE_RESULT_REVIEW = BASE / "independent-smoke-result-review.json"
PRELAUNCH_REVIEW = BASE / "independent-prelaunch-review.json"

EXPECTED = {"official": b"Accepted 1 declarations.\n",
            "nanoda": b"Checked 1 declarations with no errors\n"}
BASELINE_EXPECTED = {"official": b"Accepted 0 declarations.\n",
                     "nanoda": b"Checked 0 declarations with no errors\n"}


def _new_attempt(kind: str) -> Path:
    for number in range(1, 10000):
        path = BASE / f"{kind}-run-{number:04d}"
        try:
            path.mkdir(parents=True, exist_ok=False)
            return path
        except FileExistsError:
            continue
    raise GateError(f"{kind} attempt namespace exhausted")


def _write_raw(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def _write_json(path: Path, row: Any) -> None:
    _write_raw(path, canonical_json(row))


def _append_ledger(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as stream:
        stream.write(canonical_json(row))
        stream.flush()
        os.fsync(stream.fileno())


def _record_process(attempt: Path, label: str, result: SupervisedResult) -> dict[str, Any]:
    base = attempt / "processes" / label
    stdout = base.with_suffix(".stdout")
    stderr = base.with_suffix(".stderr")
    receipt = base.with_suffix(".receipt.json")
    _write_raw(stdout, result.stdout)
    _write_raw(stderr, result.stderr)
    saved = {**result.receipt, "raw_stdout_path": stdout.relative_to(ROOT).as_posix(),
             "raw_stderr_path": stderr.relative_to(ROOT).as_posix()}
    _write_json(receipt, saved)
    return {"stdout": binding(stdout), "stderr": binding(stderr),
            "receipt": binding(receipt)}


def _corpus_files() -> list[Path]:
    if not CORPUS.is_dir() or CORPUS.is_symlink():
        raise GateError("canonical corpus directory absent")
    return sorted(path for path in CORPUS.rglob("*") if path.is_file())


def _construction_result() -> Path:
    candidates = sorted(BASE.glob("construction-run-*/construction-result.json"))
    if len(candidates) != 1:
        raise GateError("expected exactly one successful construction result")
    return candidates[0]


def seal_corpus() -> dict[str, Any]:
    require_construction_gate()
    audited = audit_corpus(CORPUS)
    if audited.get("status") != "PASS" or audited.get("count") != 12:
        raise GateError("canonical corpus independent audit failed")
    construction_result = _construction_result()
    _committed(construction_result)
    _committed(CORPUS_REVIEW)
    for path in _corpus_files():
        _committed(path)
    review = _read(CORPUS_REVIEW)
    if (review.get("verdict") != "PASS_FOR_CORPUS_SEALING"
            or review.get("corpus_index_sha256") != binding(CORPUS / "index.json")["sha256"]
            or review.get("construction_result_sha256") != binding(construction_result)["sha256"]):
        raise GateError("exact independent corpus sealing review absent")
    row = {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
           "status": "SEALED_AFTER_INDEPENDENT_AUDIT",
           "scientific_manifest": binding(SCIENCE),
           "execution_manifest": binding(EXECUTION),
           "construction_result": binding(construction_result),
           "independent_corpus_review": binding(CORPUS_REVIEW),
           "files": [binding(path) for path in _corpus_files()],
           "audit": audited}
    _write_new(CORPUS_LOCK, row)
    return row


def require_corpus_lock() -> dict[str, Any]:
    require_construction_gate()
    _committed(CORPUS_LOCK)
    lock = _read(CORPUS_LOCK)
    if (lock.get("status") != "SEALED_AFTER_INDEPENDENT_AUDIT"
            or lock.get("scientific_manifest") != binding(SCIENCE)
            or lock.get("execution_manifest") != binding(EXECUTION)):
        raise GateError("corpus lock manifest binding differs")
    for row in lock["files"]:
        _check_binding(row, committed=True)
    if {row["path"] for row in lock["files"]} != {path.relative_to(ROOT).as_posix()
                                                  for path in _corpus_files()}:
        raise GateError("corpus file membership differs from lock")
    if audit_corpus(CORPUS) != lock["audit"]:
        raise GateError("corpus independent audit differs from lock")
    for field in ("construction_result", "independent_corpus_review"):
        _check_binding(lock[field], committed=True)
    return lock


def freeze_smoke() -> dict[str, Any]:
    """Create exact two-profile smoke manifest; invokes no observer."""
    _, execution = require_construction_gate()
    fixture = _read(BASE / "smoke-fixture-contract.json")
    _check_binding(fixture["input"], committed=True)
    if execution["smoke_fixture_contract"] != binding(BASE / "smoke-fixture-contract.json"):
        raise GateError("execution smoke fixture binding differs")
    row = {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
           "status": "FROZEN_BEFORE_SMOKE_LAUNCH",
           "scientific_manifest": binding(SCIENCE),
           "execution_manifest": binding(EXECUTION),
           "preflight_review": binding(BASE / "independent-preflight-review.json"),
           "fixture_contract": binding(BASE / "smoke-fixture-contract.json"),
           "input": fixture["input"],
           "profiles": [{"id": profile, "expected_stdout": fixture["expected_outputs"][profile],
                         "expected_stderr": "", "limits": execution["limits"]["checker"],
                         "invocation": execution["invocations"][profile]}
                        for profile in ("official", "nanoda")],
           "excluded_from_scientific_cells": True,
           "excluded_from_baseline_runs": True}
    _write_new(SMOKE_MANIFEST, row)
    return row


def require_smoke_gate() -> tuple[dict[str, Any], dict[str, Any]]:
    _, execution = require_construction_gate()
    _committed(SMOKE_MANIFEST)
    _committed(SMOKE_LAUNCH_REVIEW)
    manifest = _read(SMOKE_MANIFEST)
    fixture = _read(BASE / "smoke-fixture-contract.json")
    if (manifest.get("status") != "FROZEN_BEFORE_SMOKE_LAUNCH"
            or manifest.get("scientific_manifest") != binding(SCIENCE)
            or manifest.get("execution_manifest") != binding(EXECUTION)
            or manifest.get("fixture_contract") != binding(BASE / "smoke-fixture-contract.json")
            or manifest.get("input") != fixture["input"]
            or manifest.get("preflight_review") != binding(BASE / "independent-preflight-review.json")
            or [row.get("id") for row in manifest["profiles"]] != ["official", "nanoda"]):
        raise GateError("smoke manifest differs from exact frozen profiles")
    _check_binding(manifest["input"], committed=True)
    for row in manifest["profiles"]:
        profile = row["id"]
        if (row.get("invocation") != execution["invocations"][profile]
                or row.get("expected_stdout") != fixture["expected_outputs"][profile]
                or row.get("expected_stderr") != ""
                or row.get("limits") != execution["limits"]["checker"]):
            raise GateError("smoke profile contract differs")
    review = _read(SMOKE_LAUNCH_REVIEW)
    if (review.get("verdict") != "PASS_FOR_SMOKE_LAUNCH"
            or review.get("smoke_manifest_sha256") != binding(SMOKE_MANIFEST)["sha256"]
            or review.get("execution_manifest_sha256") != binding(EXECUTION)["sha256"]):
        raise GateError("independent exact smoke launch review absent")
    return manifest, execution


def _profile_run(*, attempt: Path, label: str, profile: str,
                 export_path: Path, expected: bytes,
                 expected_binding: dict[str, Any],
                 execution: dict[str, Any], baseline: bool) -> dict[str, Any]:
    if profile not in ("official", "nanoda"):
        raise GateError("unsupported observer profile")
    def custody_failure(reason: str, *, process: dict[str, Any] | None = None) -> None:
        _write_json(attempt / "processes" / f"{label}.custody-failure.json",
                    {"schema_version": 1, "status": "INPUT_CUSTODY_REPAIR_PAUSE",
                     "label": label, "reason": reason, "expected_input": expected_binding,
                     "process": process})
        raise GateError(f"{label}: input custody differs: {reason}")

    try:
        before = binding(export_path)
        raw = export_path.read_bytes()
    except (OSError, GateError) as exc:
        custody_failure(f"input unavailable before launch: {type(exc).__name__}")
    if before != expected_binding:
        custody_failure("input binding changed before launch")
    if (len(raw) != expected_binding["bytes"]
            or hashlib.sha256(raw).hexdigest() != expected_binding["sha256"]):
        custody_failure("read bytes differ from sealed input")
    if profile == "official":
        argv = [str(ROOT / OFFICIAL_BINARY), str(export_path)]
        stdin = None
    else:
        argv = [str(ROOT / NANODA_BINARY), str(BASE / "nanoda-single-check.json")]
        stdin = raw
    template = execution["invocations"][profile]
    want = [arg.replace("{export_path}", str(export_path)) for arg in template]
    if argv != want:
        raise GateError("profile argv differs from frozen execution template")
    limits = execution["limits"]
    try:
        result = run_direct(argv=argv, cwd=ROOT, env=execution["environment"],
                            stdin_bytes=stdin,
                            timeout_seconds=limits["checker"]["timeout_seconds"],
                            memory_ceiling_bytes=limits["checker"]["memory_ceiling_bytes"],
                            sample_interval_seconds=limits["sample_interval_seconds"],
                            max_trace_gap_seconds=limits["max_trace_gap_seconds"],
                            cleanup_seconds=limits["cleanup_seconds"],
                            ps_timeout_seconds=limits["ps_timeout_seconds"],
                            output_cap_bytes=limits["output_cap_bytes"])
    except Exception as exc:
        _write_json(attempt / "processes" / f"{label}.launch-failure.json",
                    {"schema_version": 1, "status": "OBSERVER_LAUNCH_REPAIR_PAUSE",
                     "label": label, "argv": argv, "cwd": str(ROOT),
                     "environment": execution["environment"],
                     "input": expected_binding, "limits": limits,
                     "error_type": type(exc).__name__, "error": str(exc)})
        raise GateError(f"{label}: observer launch failed; preserve and repair") from exc
    saved = _record_process(attempt, label, result)
    try:
        after = binding(export_path)
    except (OSError, GateError) as exc:
        custody_failure(f"input unavailable after observer execution: {type(exc).__name__}",
                        process=saved)
    if after != expected_binding:
        custody_failure("file binding changed during observer execution", process=saved)
    if profile == "nanoda" and (result.receipt.get("stdin_bytes") != expected_binding["bytes"]
                                or result.receipt.get("stdin_sha256") != expected_binding["sha256"]):
        custody_failure("Nanoda stdin receipt differs from sealed input", process=saved)
    disposition = classify(result.receipt, result.stdout, result.stderr,
                           expected_stdout=expected, baseline=baseline)
    return {"profile": profile, "input": binding(export_path),
            "process": saved, "disposition": disposition,
            "started_monotonic_ns": result.receipt["started_monotonic_ns"]}


def run_smoke() -> dict[str, Any]:
    manifest, execution = require_smoke_gate()
    if SMOKE_RESULT.exists():
        raise GateError("smoke result already exists; preserve and review it")
    if any(BASE.glob("smoke-run-*")):
        raise GateError("prior smoke attempt requires explicit same-item repair review")
    attempt = _new_attempt("smoke")
    progress: list[dict[str, Any]] = []
    current: str | None = None
    try:
        input_path = ROOT / manifest["input"]["path"]
        for profile in ("official", "nanoda"):
            require_smoke_gate()
            current = profile
            row = _profile_run(attempt=attempt, label=profile, profile=profile,
                               export_path=input_path, expected=EXPECTED[profile],
                               expected_binding=manifest["input"],
                               execution=execution, baseline=False)
            progress.append(row)
            _append_ledger(attempt / "ledger.ndjson", row)
            if row["disposition"]["status"] != "ACCEPTED":
                raise GateError(f"smoke {profile} did not complete exact accepted definition")
        outcome = {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
                   "status": "SMOKE_EXACT_ACCEPTANCE_BOTH_PROFILES",
                   "completed_at": datetime.now(timezone.utc).isoformat(),
                   "smoke_manifest": binding(SMOKE_MANIFEST),
                   "profiles": progress,
                   "excluded_from_scientific_cells": True,
                   "excluded_from_baseline_runs": True}
        _write_json(attempt / "smoke-result.json", outcome)
        _write_json(SMOKE_RESULT, {"attempt_result": binding(attempt / "smoke-result.json"),
                                   **outcome})
        return outcome
    except Exception as exc:
        _write_json(attempt / "smoke-failure.json",
                    {"schema_version": 1, "status": "SMOKE_REPAIR_PAUSE",
                     "profile": current, "error_type": type(exc).__name__,
                     "error": str(exc), "completed": progress,
                     "smoke_manifest": binding(SMOKE_MANIFEST)})
        raise


def require_scientific_launch_gate() -> tuple[dict[str, Any], dict[str, Any]]:
    _, execution = require_construction_gate()
    lock = require_corpus_lock()
    smoke_manifest, _ = require_smoke_gate()
    for path in (SMOKE_RESULT, SMOKE_RESULT_REVIEW, PRELAUNCH_REVIEW):
        _committed(path)
    smoke = _read(SMOKE_RESULT)
    if (smoke.get("status") != "SMOKE_EXACT_ACCEPTANCE_BOTH_PROFILES"
            or smoke.get("smoke_manifest") != binding(SMOKE_MANIFEST)
            or [row["profile"] for row in smoke.get("profiles", [])] != ["official", "nanoda"]
            or any(row["disposition"]["status"] != "ACCEPTED" for row in smoke["profiles"])):
        raise GateError("positive two-profile smoke result differs")
    _check_binding(smoke["attempt_result"], committed=True)
    attempt_result = _read(ROOT / smoke["attempt_result"]["path"])
    if attempt_result != {key: value for key, value in smoke.items()
                          if key != "attempt_result"}:
        raise GateError("smoke result and attempt differ")
    if smoke_manifest["input"] != binding(ROOT / smoke_manifest["input"]["path"]):
        raise GateError("smoke input changed after positive acceptance")
    for row in smoke["profiles"]:
        if row.get("input") != smoke_manifest["input"]:
            raise GateError("smoke profile input differs")
        process = row.get("process")
        if type(process) is not dict or set(process) != {"receipt", "stdout", "stderr"}:
            raise GateError("smoke raw process bindings absent")
        for field in ("receipt", "stdout", "stderr"):
            _check_binding(process[field], committed=True)
        receipt = _read(ROOT / process["receipt"]["path"])
        stdout = (ROOT / process["stdout"]["path"]).read_bytes()
        stderr = (ROOT / process["stderr"]["path"]).read_bytes()
        expected_argv = [arg.replace("{export_path}",
                                     str(ROOT / smoke_manifest["input"]["path"]))
                         for arg in execution["invocations"][row["profile"]]]
        limits = execution["limits"]
        expected_limits = {**limits["checker"],
                           **{name: limits[name] for name in (
                               "sample_interval_seconds", "max_trace_gap_seconds",
                               "cleanup_seconds", "ps_timeout_seconds", "output_cap_bytes")}}
        if (receipt.get("raw_stdout_path") != process["stdout"]["path"]
                or receipt.get("raw_stderr_path") != process["stderr"]["path"]
                or receipt.get("argv") != expected_argv or receipt.get("cwd") != str(ROOT)
                or receipt.get("limits") != expected_limits
                or row.get("started_monotonic_ns") != receipt.get("started_monotonic_ns")
                or classify(receipt, stdout, stderr, expected_stdout=EXPECTED[row["profile"]],
                            baseline=False)["status"] != "ACCEPTED"):
            raise GateError("smoke raw result does not replay exact acceptance")
        if row["profile"] == "nanoda" and (
                receipt.get("stdin_bytes") != smoke_manifest["input"]["bytes"]
                or receipt.get("stdin_sha256") != smoke_manifest["input"]["sha256"]):
            raise GateError("smoke Nanoda stdin differs from exact fixture")
        if row["profile"] == "official" and (
                receipt.get("stdin_bytes") is not None or receipt.get("stdin_sha256") is not None):
            raise GateError("smoke official invocation unexpectedly used stdin")
    review = _read(SMOKE_RESULT_REVIEW)
    if (review.get("verdict") != "PASS_EXACT_SMOKE_RESULTS"
            or review.get("smoke_result_sha256") != binding(SMOKE_RESULT)["sha256"]):
        raise GateError("independent smoke result review absent")
    prelaunch = _read(PRELAUNCH_REVIEW)
    if (prelaunch.get("verdict") != "PASS_FOR_SCIENTIFIC_LAUNCH"
            or prelaunch.get("scientific_manifest_sha256") != binding(SCIENCE)["sha256"]
            or prelaunch.get("execution_manifest_sha256") != binding(EXECUTION)["sha256"]
            or prelaunch.get("corpus_lock_sha256") != binding(CORPUS_LOCK)["sha256"]
            or prelaunch.get("smoke_result_sha256") != binding(SMOKE_RESULT)["sha256"]):
        raise GateError("independent exact scientific launch review absent")
    return lock, execution


def _schedule() -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for profile in ("official", "nanoda"):
        for phase in ("before", "after"):
            if phase == "after":
                for family in ("pi", "let"):
                    for size in (16, 32, 64, 128, 256, 512):
                        slots.append({"kind": "science", "profile": profile,
                                      "family": family, "size": size,
                                      "id": f"{profile}-{case_id(family, size)}"})
            for repeat in (1, 2, 3):
                slots.append({"kind": "baseline", "profile": profile,
                              "phase": phase, "repeat": repeat,
                              "id": f"{profile}-{phase}-{repeat:02d}"})
    if len(slots) != 36:
        raise GateError("fixed schedule cardinality differs")
    return slots


def _previous_runs() -> list[Path]:
    return sorted(path for path in BASE.glob("science-run-*") if path.is_dir())


def _verify_prefix_events(events: list[dict[str, Any]], schedule: list[dict[str, Any]],
                          lock: dict[str, Any], execution: dict[str, Any],
                          approved_triggers: dict[str, str], candidate_limit_id: str,
                          *, committed: bool = True) -> None:
    """Reconcile every preserved slot against sealed input and raw observer bytes."""
    locked_files = {row["path"]: row for row in lock["files"]}
    baseline_path = BASE / "baseline-empty.ndjson"
    baseline_ref = {"path": baseline_path.relative_to(ROOT).as_posix(),
                    **execution["empty_export"]}
    if binding(baseline_path) != baseline_ref:
        raise GateError("preserved baseline input changed")
    if type(events) is not list or not events or len(events) > len(schedule):
        raise GateError("preserved event prefix malformed")
    seen_receipts: set[str] = set()
    previous_completed_ns: int | None = None
    for index, event in enumerate(events):
        if type(event) is not dict or set(event) != {"slot", "row"}:
            raise GateError("preserved event schema differs")
        slot, row = event["slot"], event["row"]
        if slot != schedule[index] or type(row) is not dict:
            raise GateError("preserved slot order differs")
        profile = slot["profile"]
        if slot["kind"] == "baseline":
            if (row.get("baseline_id") != slot["id"] or row.get("phase") != slot["phase"]
                    or row.get("profile") != profile):
                raise GateError("preserved baseline identity differs")
            expected_ref = baseline_ref
            expected_stdout = BASELINE_EXPECTED[profile]
        else:
            if (row.get("cell_id") != slot["id"] or row.get("profile") != profile
                    or row.get("family") != slot["family"] or row.get("size") != slot["size"]):
                raise GateError("preserved scientific cell identity differs")
            path = CORPUS / "exports" / f"{case_id(slot['family'], slot['size'])}.ndjson"
            expected_ref = locked_files.get(path.relative_to(ROOT).as_posix())
            if expected_ref is None or binding(path) != expected_ref:
                raise GateError("preserved scientific input differs from corpus lock")
            expected_stdout = EXPECTED[profile]
        if row.get("input") != expected_ref:
            raise GateError("preserved observer input binding differs")
        key = f"{profile}/{slot['family']}" if slot["kind"] == "science" else None
        if row.get("status") == "NOT_RUN_AFTER_LIMIT":
            reviewed_trigger = approved_triggers.get(key)
            preceding = [earlier for earlier in events[:index]
                         if earlier["slot"].get("id") == reviewed_trigger]
            if (key not in approved_triggers
                    or len(preceding) != 1
                    or preceding[0]["slot"].get("profile") != profile
                    or preceding[0]["slot"].get("family") != slot["family"]
                    or preceding[0]["slot"].get("size", 0) >= slot["size"]
                    or preceding[0]["row"].get("status") not in (
                        "OBSERVED_TIME_LIMIT", "OBSERVED_MEMORY_LIMIT",
                        "OBSERVED_OVER_CEILING_AFTER_EXIT")
                    or row != {"cell_id": slot["id"], "profile": profile,
                               "family": slot["family"], "size": slot["size"],
                               "status": "NOT_RUN_AFTER_LIMIT",
                               "trigger_cell_id": reviewed_trigger,
                               "input": expected_ref}):
                raise GateError("unreviewed or malformed skipped cell")
            continue
        fields = ({"baseline_id", "phase", "status", "profile", "input", "process",
                   "disposition", "started_monotonic_ns"} if slot["kind"] == "baseline"
                  else {"cell_id", "profile", "family", "size", "status", "input",
                        "process", "disposition", "started_monotonic_ns"})
        if set(row) != fields:
            raise GateError("preserved executed slot schema differs")
        if key in approved_triggers and slot["id"] != approved_triggers[key]:
            trigger_indices = [position for position, candidate in enumerate(schedule)
                               if candidate["id"] == approved_triggers[key]]
            if len(trigger_indices) != 1 or index > trigger_indices[0]:
                raise GateError("reviewed sequence stop has later executed size")
        process = row.get("process")
        if type(process) is not dict or set(process) != {"receipt", "stdout", "stderr"}:
            raise GateError("preserved executed slot lacks raw process bindings")
        for field in ("receipt", "stdout", "stderr"):
            _check_binding(process[field], committed=committed)
        receipt_path = process["receipt"]["path"]
        if receipt_path in seen_receipts:
            raise GateError("preserved prefix reused a process receipt")
        seen_receipts.add(receipt_path)
        receipt = _read(ROOT / process["receipt"]["path"])
        stdout = (ROOT / process["stdout"]["path"]).read_bytes()
        stderr = (ROOT / process["stderr"]["path"]).read_bytes()
        if (receipt.get("raw_stdout_path") != process["stdout"]["path"]
                or receipt.get("raw_stderr_path") != process["stderr"]["path"]
                or receipt.get("cwd") != str(ROOT)
                or row.get("started_monotonic_ns") != receipt.get("started_monotonic_ns")):
            raise GateError("preserved observer process identity differs")
        started_ns = receipt.get("started_monotonic_ns")
        drained_ns = receipt.get("drained_monotonic_ns")
        if (type(started_ns) is not int or type(drained_ns) is not int
                or drained_ns < started_ns
                or (previous_completed_ns is not None and started_ns < previous_completed_ns)):
            raise GateError("preserved process timestamps contradict slot order")
        previous_completed_ns = drained_ns
        export_path = ROOT / expected_ref["path"]
        wanted_argv = [arg.replace("{export_path}", str(export_path))
                       for arg in execution["invocations"][profile]]
        limits = execution["limits"]
        wanted_limits = {**limits["checker"],
                         **{name: limits[name] for name in (
                             "sample_interval_seconds", "max_trace_gap_seconds",
                             "cleanup_seconds", "ps_timeout_seconds", "output_cap_bytes")}}
        if receipt.get("argv") != wanted_argv or receipt.get("limits") != wanted_limits:
            raise GateError("preserved observer command or limits differ")
        if profile == "nanoda":
            if (receipt.get("stdin_bytes") != expected_ref["bytes"]
                    or receipt.get("stdin_sha256") != expected_ref["sha256"]):
                raise GateError("preserved Nanoda stdin differs")
        elif receipt.get("stdin_bytes") is not None or receipt.get("stdin_sha256") is not None:
            raise GateError("preserved official invocation unexpectedly used stdin")
        observed = classify(receipt, stdout, stderr, expected_stdout=expected_stdout,
                            baseline=slot["kind"] == "baseline")
        if (observed != row.get("disposition") or row.get("status") != observed["status"]
                or (slot["kind"] == "baseline" and observed["status"] != "ACCEPTED")):
            raise GateError("preserved raw observer disposition differs")
        if observed["status"] not in ("ACCEPTED", "OBSERVED_TIME_LIMIT",
                                      "OBSERVED_MEMORY_LIMIT",
                                      "OBSERVED_OVER_CEILING_AFTER_EXIT"):
            raise GateError("preserved repair fault cannot resume as science")
        if slot["kind"] == "science" and observed["status"] in (
                "OBSERVED_TIME_LIMIT", "OBSERVED_MEMORY_LIMIT",
                "OBSERVED_OVER_CEILING_AFTER_EXIT"):
            if slot["id"] != candidate_limit_id and approved_triggers.get(key) != slot["id"]:
                raise GateError("scientific limit lacks independent sequence-stop review")
            if slot["id"] == candidate_limit_id and index != len(events) - 1:
                raise GateError("limit candidate was not an immediate pause")


def _resume_state(path: Path, schedule: list[dict[str, Any]],
                  lock: dict[str, Any], execution: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str], list[dict[str, Any]]]:
    path = path.resolve()
    if path.name != "science-pause.json" or path.parent not in [item.resolve() for item in _previous_runs()[-1:]]:
        raise GateError("resume requires latest preserved science pause")
    review_path = path.parent / "independent-limit-review.json"
    for required in (path, review_path):
        _committed(required)
    pause, review = _read(path), _read(review_path)
    events = pause.get("events")
    start = pause.get("segment_start_index")
    if (pause.get("status") != "AWAITING_INDEPENDENT_LIMIT_DIAGNOSIS"
            or pause.get("scientific_manifest") != binding(SCIENCE)
            or pause.get("execution_manifest") != binding(EXECUTION)
            or pause.get("corpus_lock") != binding(CORPUS_LOCK)
            or type(events) is not list or type(start) is not int
            or not 0 <= start < len(events) <= 36
            or pause.get("next_slot_index") != len(events)
            or [row.get("slot") for row in events] != schedule[:len(events)]):
        raise GateError("preserved science prefix differs from fixed schedule")
    if type(pause.get("approved_triggers")) is not dict:
        raise GateError("preserved approved trigger map malformed")
    _verify_prefix_events(events, schedule, lock, execution,
                          pause["approved_triggers"], pause["trigger_cell_id"])
    _check_binding(pause["ledger"], committed=True)
    ledger = ROOT / pause["ledger"]["path"]
    if ledger.read_bytes() != b"".join(canonical_json(row) for row in events[start:]):
        raise GateError("preserved science ledger differs from prefix")
    last = events[-1]
    if (last["slot"]["kind"] != "science"
            or last["row"]["status"] not in ("OBSERVED_TIME_LIMIT", "OBSERVED_MEMORY_LIMIT",
                                             "OBSERVED_OVER_CEILING_AFTER_EXIT")
            or pause.get("trigger_cell_id") != last["slot"]["id"]):
        raise GateError("preserved limit trigger differs")
    for field in ("receipt", "stdout", "stderr"):
        _check_binding(last["row"]["process"][field], committed=True)
    receipt_binding = last["row"]["process"]["receipt"]
    receipt = _read(ROOT / receipt_binding["path"])
    stdout = (ROOT / last["row"]["process"]["stdout"]["path"]).read_bytes()
    stderr = (ROOT / last["row"]["process"]["stderr"]["path"]).read_bytes()
    observed = classify(receipt, stdout, stderr,
                        expected_stdout=EXPECTED[last["slot"]["profile"]], baseline=False)
    if observed != last["row"]["disposition"]:
        raise GateError("preserved limit raw observation differs")
    if (review.get("verdict") != "PASS_FOR_SEQUENCE_STOP"
            or review.get("science_pause_sha256") != binding(path)["sha256"]
            or review.get("trigger_cell_id") != pause["trigger_cell_id"]
            or review.get("trigger_receipt_sha256") != receipt_binding["sha256"]
            or review.get("ledger_sha256") != pause["ledger"]["sha256"]):
        raise GateError("independent exact limit diagnosis absent")
    triggers = pause.get("approved_triggers")
    history = pause.get("history")
    if type(triggers) is not dict or type(history) is not list or len(history) % 2:
        raise GateError("preserved sequence-stop history malformed")
    reconstructed: dict[str, str] = {}
    previous_events: list[dict[str, Any]] = []
    for offset in range(0, len(history), 2):
        prior_pause_ref, prior_review_ref = history[offset:offset + 2]
        _check_binding(prior_pause_ref, committed=True)
        _check_binding(prior_review_ref, committed=True)
        prior_pause = _read(ROOT / prior_pause_ref["path"])
        prior_review = _read(ROOT / prior_review_ref["path"])
        prior_events = prior_pause.get("events")
        if (type(prior_events) is not list or not prior_events
                or prior_events[:len(previous_events)] != previous_events
                or prior_review.get("verdict") != "PASS_FOR_SEQUENCE_STOP"
                or prior_review.get("science_pause_sha256") != prior_pause_ref["sha256"]
                or prior_review.get("trigger_cell_id") != prior_pause.get("trigger_cell_id")
                or prior_review.get("ledger_sha256") != prior_pause["ledger"]["sha256"]):
            raise GateError("earlier independently reviewed limit chain differs")
        _verify_prefix_events(prior_events, schedule, lock, execution,
                              prior_pause["approved_triggers"], prior_pause["trigger_cell_id"])
        _check_binding(prior_pause["ledger"], committed=True)
        old_start = prior_pause.get("segment_start_index")
        if (type(old_start) is not int or not 0 <= old_start < len(prior_events)
                or (ROOT / prior_pause["ledger"]["path"]).read_bytes()
                != b"".join(canonical_json(row) for row in prior_events[old_start:])):
            raise GateError("earlier limit ledger differs from exact prefix")
        old_last = prior_events[-1]
        old_process = old_last["row"]["process"]
        for field in ("receipt", "stdout", "stderr"):
            _check_binding(old_process[field], committed=True)
        if prior_review.get("trigger_receipt_sha256") != old_process["receipt"]["sha256"]:
            raise GateError("earlier limit receipt review differs")
        old_receipt = _read(ROOT / old_process["receipt"]["path"])
        old_stdout = (ROOT / old_process["stdout"]["path"]).read_bytes()
        old_stderr = (ROOT / old_process["stderr"]["path"]).read_bytes()
        if classify(old_receipt, old_stdout, old_stderr,
                    expected_stdout=EXPECTED[old_last["slot"]["profile"]],
                    baseline=False) != old_last["row"]["disposition"]:
            raise GateError("earlier limit raw observation differs")
        old_key = f"{old_last['slot']['profile']}/{old_last['slot']['family']}"
        reconstructed[old_key] = old_last["slot"]["id"]
        previous_events = prior_events
    if reconstructed != triggers or (history and events[:len(previous_events)] != previous_events):
        raise GateError("approved prior sequence stops differ from replayed history")
    if history and start != len(previous_events):
        raise GateError("resumed segment overlaps or omits prior slots")
    key = f"{last['slot']['profile']}/{last['slot']['family']}"
    if key in triggers:
        raise GateError("duplicate family limit trigger")
    return events, {**triggers, key: last["slot"]["id"]}, [*history, binding(path), binding(review_path)]


def run_science(*, resume_pause: Path | None = None) -> dict[str, Any]:
    lock, execution = require_scientific_launch_gate()
    schedule = _schedule()
    prior = _previous_runs()
    if any((path / "science-result.json").exists() for path in prior):
        raise GateError("completed scientific matrix already exists")
    if resume_pause is None:
        if prior:
            raise GateError("existing science attempt requires explicit reviewed repair/resume")
        events: list[dict[str, Any]] = []
        trigger: dict[str, str] = {}
        history: list[dict[str, Any]] = []
    else:
        events, trigger, history = _resume_state(resume_pause, schedule, lock, execution)
    segment_start = len(events)
    attempt = _new_attempt("science")
    ledger = attempt / "ledger.ndjson"
    current: str | None = None
    try:
        baseline_path = BASE / "baseline-empty.ndjson"
        baseline_binding = {"path": binding(baseline_path)["path"],
                            **execution["empty_export"]}
        if binding(baseline_path) != baseline_binding:
            raise GateError("baseline empty export differs")
        locked_files = {row["path"]: row for row in lock["files"]}
        for slot in schedule[segment_start:]:
            require_scientific_launch_gate()
            current = slot["id"]
            profile = slot["profile"]
            if slot["kind"] == "baseline":
                observed = _profile_run(
                    attempt=attempt, label=current, profile=profile,
                    export_path=baseline_path, expected=BASELINE_EXPECTED[profile],
                    expected_binding=baseline_binding, execution=execution, baseline=True)
                row = {"baseline_id": current, "phase": slot["phase"],
                       "status": observed["disposition"]["status"], **observed}
            else:
                key = f"{profile}/{slot['family']}"
                export_path = CORPUS / "exports" / f"{case_id(slot['family'], slot['size'])}.ndjson"
                frozen = locked_files.get(export_path.relative_to(ROOT).as_posix())
                if frozen is None:
                    raise GateError(f"{current}: sealed input absent")
                if key in trigger:
                    row = {"cell_id": current, "profile": profile,
                           "family": slot["family"], "size": slot["size"],
                           "status": "NOT_RUN_AFTER_LIMIT", "trigger_cell_id": trigger[key],
                           "input": frozen}
                else:
                    observed = _profile_run(
                        attempt=attempt, label=current, profile=profile,
                        export_path=export_path, expected=EXPECTED[profile],
                        expected_binding=frozen, execution=execution, baseline=False)
                    row = {"cell_id": current, "profile": profile,
                           "family": slot["family"], "size": slot["size"],
                           "status": observed["disposition"]["status"], **observed}
            event = {"slot": slot, "row": row}
            events.append(event)
            _append_ledger(ledger, event)
            if row["status"] == "REPAIR_PAUSE":
                raise GateError(f"{current}: observer/control attribution requires repair")
            if slot["kind"] == "science" and row["status"] in (
                    "OBSERVED_TIME_LIMIT", "OBSERVED_MEMORY_LIMIT",
                    "OBSERVED_OVER_CEILING_AFTER_EXIT"):
                pause = {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
                         "status": "AWAITING_INDEPENDENT_LIMIT_DIAGNOSIS",
                         "scientific_manifest": binding(SCIENCE),
                         "execution_manifest": binding(EXECUTION),
                         "corpus_lock": binding(CORPUS_LOCK),
                         "trigger_cell_id": current, "next_slot_index": len(events),
                         "segment_start_index": segment_start, "ledger": binding(ledger),
                         "approved_triggers": trigger, "history": history, "events": events}
                _write_json(attempt / "science-pause.json", pause)
                return pause
            if slot["kind"] == "baseline" and row["status"] != "ACCEPTED":
                raise GateError(f"{current}: baseline repair pause")
        baselines = [event["row"] for event in events if event["slot"]["kind"] == "baseline"]
        cells = [event["row"] for event in events if event["slot"]["kind"] == "science"]
        if len(baselines) != 12 or len(cells) != 24:
            raise GateError("fixed 12 baseline / 24 science ledger incomplete")
        _verify_prefix_events(events, schedule, lock, execution, trigger, "", committed=False)
        result = {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
                  "status": "COMPLETE_FIXED_MATRIX",
                  "completed_at": datetime.now(timezone.utc).isoformat(),
                  "scientific_manifest": binding(SCIENCE),
                  "execution_manifest": binding(EXECUTION),
                  "corpus_lock": binding(CORPUS_LOCK),
                  "smoke_result": binding(SMOKE_RESULT),
                  "independent_prelaunch_review": binding(PRELAUNCH_REVIEW),
                  "baseline_input": baseline_binding,
                  "baselines": baselines, "cells": cells, "events": events,
                  "history": history, "segment_start_index": segment_start,
                  "ledger": binding(ledger)}
        _write_json(attempt / "science-result.json", result)
        return result
    except Exception as exc:
        _write_json(attempt / "science-failure.json",
                    {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
                     "status": "SCIENCE_REPAIR_PAUSE", "current": current,
                     "error_type": type(exc).__name__, "error": str(exc),
                     "scientific_manifest": binding(SCIENCE),
                     "execution_manifest": binding(EXECUTION),
                     "corpus_lock": binding(CORPUS_LOCK),
                     "smoke_result": binding(SMOKE_RESULT),
                     "history": history, "segment_start_index": segment_start,
                     "events": events,
                     "ledger": binding(ledger) if ledger.is_file() else None})
        raise
