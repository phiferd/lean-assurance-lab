"""Frozen tooling and guarded observation for acceptance-impact Stage 2."""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
from typing import Any, Callable, Iterator

from lib.cvc_prep import committed
from lib.metamorphic_pilot_runner import run_supervised
from lib import acceptance_impact_pilot as stage1


ROOT = Path(__file__).resolve().parents[1]
ITEM = stage1.ITEM
BASE = stage1.BASE
ASSUMPTIONS = BASE / "assumption-audit.json"
CONTRACT = BASE / "consequence-contract.json"
TOOLING_MANIFEST = BASE / "stage-2-tooling-manifest.json"
AUDIT_REPORT = BASE / "stage-2-artifact-audit.json"
EXECUTION_MANIFEST = BASE / "stage-2-execution-manifest.json"
RUN_DIR = BASE / "stage-2-run-0001"
RUN_RESULT = RUN_DIR / "result.json"
CANDIDATE = Path("corpus/acceptance-impact-pilot-1/five-app-candidate.ndjson")
CONTROL = Path("corpus/acceptance-impact-pilot-1/five-app-control.ndjson")

MODULE = Path("lib/acceptance_impact_stage2.py")
PRODUCER = Path("lib/acceptance_impact_stage2_producer.py")
AUDITOR = Path("lib/acceptance_impact_stage2_audit.py")
PREPARE_SCRIPT = Path("scripts/prepare-acceptance-impact-stage-2")
GENERATE_SCRIPT = Path("scripts/generate-acceptance-impact-stage-2")
AUDIT_SCRIPT = Path("scripts/audit-acceptance-impact-stage-2")
EXECUTE_SCRIPT = Path("scripts/execute-acceptance-impact-stage-2")
VALIDATE_SCRIPT = Path("scripts/validate-acceptance-impact-stage-2")
TEST = Path("tests/test_acceptance_impact_stage2.py")
PRODUCER_TEST = Path("tests/test_acceptance_impact_stage2_producer.py")
AUDITOR_TEST = Path("tests/test_acceptance_impact_stage2_audit.py")

EXPECTED_CELLS = [
    {"ordinal": 1, "cell_id": "kiota-9fa2c297::control-use", "profile_id": "kiota-9fa2c297", "artifact_id": "control_use"},
    {"ordinal": 2, "cell_id": "kiota-9fa2c297::candidate-use", "profile_id": "kiota-9fa2c297", "artifact_id": "candidate_use"},
    {"ordinal": 3, "cell_id": "official-lean-4.33.0::control-use", "profile_id": "official-lean-4.33.0", "artifact_id": "control_use"},
    {"ordinal": 4, "cell_id": "official-lean-4.33.0::candidate-use", "profile_id": "official-lean-4.33.0", "artifact_id": "candidate_use"},
]
EXPECTED_CONSEQUENTIAL = {
    "kiota-9fa2c297::control-use": "ACCEPT",
    "kiota-9fa2c297::candidate-use": "ACCEPT",
    "official-lean-4.33.0::control-use": "ACCEPT",
    "official-lean-4.33.0::candidate-use": "INTENDED_RECURSOR_REJECT",
}


class Stage2Error(ValueError):
    pass


def _tooling(root: Path) -> list[dict[str, Any]]:
    return [stage1.binding(path, root) for path in (
        MODULE, PRODUCER, AUDITOR, PREPARE_SCRIPT, GENERATE_SCRIPT, AUDIT_SCRIPT,
        EXECUTE_SCRIPT, VALIDATE_SCRIPT, TEST, PRODUCER_TEST, AUDITOR_TEST,
        stage1.MODULE, stage1.SUPERVISOR,
    )]


def _committed_binding(path: Path, root: Path) -> dict[str, Any]:
    committed(root, path.as_posix())
    return stage1.binding(path, root)


def make_tooling_manifest(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    stage1._active(root)
    stage1_result = stage1.validate_stage_1_result(root, require_commit=True)
    if stage1_result["premise_gate"] != {
        "status": "PASS", "expected": stage1.EXPECTED_GATE,
        "observed": stage1.EXPECTED_GATE, "stage_2_authorized": True,
    }:
        raise Stage2Error("committed Stage-1 premise gate is not exact PASS")
    assumptions = stage1.load_json(root / ASSUMPTIONS)
    contract = stage1.load_json(root / CONTRACT)
    if (assumptions.get("status") != "FROZEN_BEFORE_CONSTRUCTION"
            or contract.get("status") != "FROZEN_BEFORE_CONSTRUCTION"
            or contract.get("matrix") != EXPECTED_CELLS
            or contract.get("expected_consequential_matrix") != EXPECTED_CONSEQUENTIAL):
        raise Stage2Error("Stage-2 contract differs from the fixed gate")
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "stage": "STAGE_2_TOOLING_FREEZE",
        "assumption_audit": _committed_binding(ASSUMPTIONS, root),
        "consequence_contract": _committed_binding(CONTRACT, root),
        "stage_1_result": stage1.binding(stage1.RUN_RESULT, root),
        "tooling": _tooling(root),
        "artifact_paths": {"candidate_use": CANDIDATE.as_posix(),
                           "control_use": CONTROL.as_posix()},
        "audit_report_path": AUDIT_REPORT.as_posix(),
        "matrix": EXPECTED_CELLS,
        "expected_consequential_matrix": EXPECTED_CONSEQUENTIAL,
        "maximum_uses": 2,
        "adaptive_search": False,
        "observer_processes_before_artifact_freeze": 0,
    }


def freeze_tooling_manifest(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    value = make_tooling_manifest(root)
    path = root / TOOLING_MANIFEST
    if path.exists():
        if stage1.load_json(path) != value:
            raise Stage2Error("existing Stage-2 tooling manifest differs")
    else:
        stage1._write_json(path, value)
    return value


def validate_tooling_manifest(root: Path = ROOT, *, require_commit: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    actual = stage1.load_json(root / TOOLING_MANIFEST)
    expected = make_tooling_manifest(root)
    if actual != expected:
        raise Stage2Error("Stage-2 tooling manifest is stale")
    if require_commit:
        committed(root, TOOLING_MANIFEST.as_posix())
        for row in actual["tooling"]:
            committed(root, row["path"])
    return actual


def make_execution_manifest(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    tooling = validate_tooling_manifest(root, require_commit=True)
    try:
        from lib import acceptance_impact_stage2_audit as audit
    except ImportError as error:
        raise Stage2Error("independent Stage-2 auditor is unavailable") from error
    report = audit.check(root)
    if report.get("status") != "PASS":
        raise Stage2Error("independent Stage-2 audit is not PASS")
    stage1_manifest = stage1.validate_execution_manifest(root, require_commit=True)
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "stage": "FIXED_FIVE_APPLICATION_CONSEQUENCE",
        "launch_owner": "root",
        "run_directory": RUN_DIR.as_posix(),
        "tooling_manifest": stage1.binding(TOOLING_MANIFEST, root),
        "audit_report": stage1.binding(AUDIT_REPORT, root),
        "artifacts": {"candidate_use": stage1.binding(CANDIDATE, root),
                      "control_use": stage1.binding(CONTROL, root)},
        "profiles": stage1_manifest["profiles"],
        "cells": tooling["matrix"],
        "expected_consequential_matrix": tooling["expected_consequential_matrix"],
        "timeout_seconds_each": 120,
        "memory_bytes_each": 2147483648,
        "environment": stage1_manifest["environment"],
        "adaptive_search": False,
    }


def freeze_execution_manifest(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    value = make_execution_manifest(root)
    path = root / EXECUTION_MANIFEST
    if path.exists():
        if stage1.load_json(path) != value:
            raise Stage2Error("existing Stage-2 execution manifest differs")
    else:
        stage1._write_json(path, value)
    return value


def validate_execution_manifest(root: Path = ROOT, *, require_commit: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    actual = stage1.load_json(root / EXECUTION_MANIFEST)
    expected = make_execution_manifest(root)
    if actual != expected:
        raise Stage2Error("Stage-2 execution manifest is stale")
    if require_commit:
        committed(root, EXECUTION_MANIFEST.as_posix())
        for path in (CANDIDATE, CONTROL, AUDIT_REPORT, TOOLING_MANIFEST):
            committed(root, path.as_posix())
    return actual


@contextmanager
def _launch_lock(root: Path) -> Iterator[None]:
    path = root / BASE / ".stage-2-launch.lock"
    stream = path.open("a+")
    try:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        stream.close()
        raise Stage2Error("another Stage-2 launch owns the lock") from error
    try:
        yield
    finally:
        fcntl.flock(stream, fcntl.LOCK_UN)
        stream.close()
        path.unlink(missing_ok=True)


def _decision(results: list[dict[str, Any]], expected: dict[str, str], root: Path) -> str:
    observed = {row["cell"]["cell_id"]: row["outcome"] for row in results}
    if observed == expected:
        return "CONSEQUENTIAL_WITHIN_FIXED_USE"
    comparison = dict(expected)
    comparison["kiota-9fa2c297::candidate-use"] = "REJECT"
    if observed == comparison:
        candidate = next(row for row in results
                         if row["cell"]["cell_id"] == "kiota-9fa2c297::candidate-use")
        stderr = (root / candidate["receipt"]["raw_stderr_path"]).read_bytes()
        if b"LALNest.rec_1_impact" in stderr:
            return "HARMLESS_WITHIN_TESTED_USE"
    return "CONSTRUCTION_OR_SEMANTIC_BOUNDARY"


def execute(root: Path = ROOT,
            runner: Callable[..., dict[str, Any]] = run_supervised) -> dict[str, Any]:
    root = Path(root).resolve()
    manifest = validate_execution_manifest(root, require_commit=True)
    run_dir = root / RUN_DIR
    if run_dir.exists():
        raise Stage2Error("refuse to overwrite Stage-2 run")
    artifacts = {name: stage1.verify_binding(row, root)
                 for name, row in manifest["artifacts"].items()}
    results: list[dict[str, Any]] = []
    with _launch_lock(root):
        run_dir.mkdir(parents=True)
        for cell in manifest["cells"]:
            profile_id = cell["profile_id"]
            profile = manifest["profiles"][profile_id]
            artifact = artifacts[cell["artifact_id"]]
            binary = stage1.verify_binding(profile["binary"], root)
            raw_prefix = run_dir / "raw" / f"{cell['ordinal']:02d}-{profile_id}-{cell['artifact_id']}"
            receipt = runner(
                argv=[str(binary), str(artifact)], cwd=root, stdin=None,
                env=dict(manifest["environment"]), timeout_seconds=manifest["timeout_seconds_each"],
                memory_bytes=manifest["memory_bytes_each"], raw_prefix=raw_prefix,
            )
            stdout, stderr = stage1._verify_raw(receipt, root)
            outcome, reason = stage1.classify(profile_id, receipt, stdout, stderr)
            row = {"cell": cell, "artifact": manifest["artifacts"][cell["artifact_id"]],
                   "outcome": outcome, "reason": reason, "receipt": receipt}
            results.append(row)
            with (run_dir / "events.jsonl").open("a", encoding="utf-8") as output:
                output.write(json.dumps(row, sort_keys=True) + "\n")
            partial = {"schema_version": 1, "item_id": ITEM,
                       "execution_manifest": stage1.binding(EXECUTION_MANIFEST, root),
                       "cells": results, "status": "RUNNING"}
            stage1._write_json(run_dir / "result.json", partial)
            if outcome == "INFRASTRUCTURE_AUDIT_FAILURE":
                raise Stage2Error(f"cell {cell['cell_id']} infrastructure failure: {reason}")
    observed = {row["cell"]["cell_id"]: row["outcome"] for row in results}
    result = {
        "schema_version": 1,
        "item_id": ITEM,
        "execution_manifest": stage1.binding(EXECUTION_MANIFEST, root),
        "cells": results,
        "checker_attempts": len(results),
        "process_seconds": sum(row["receipt"]["elapsed_seconds"] for row in results),
        "status": "COMPLETE",
        "observed_matrix": observed,
        "decision": _decision(results, manifest["expected_consequential_matrix"], root),
    }
    stage1._write_json(run_dir / "result.json", result)
    return result


def validate_result(root: Path = ROOT, *, require_commit: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    manifest = validate_execution_manifest(root, require_commit=require_commit)
    result = stage1.load_json(root / RUN_RESULT)
    if result.get("status") != "COMPLETE" or result.get("checker_attempts") != 4:
        raise Stage2Error("Stage-2 result is incomplete")
    if [row.get("cell") for row in result.get("cells", [])] != manifest["cells"]:
        raise Stage2Error("Stage-2 cells differ from frozen matrix")
    for row in result["cells"]:
        stage1.verify_binding(row["artifact"], root)
        receipt = row.get("receipt")
        if not isinstance(receipt, dict):
            raise Stage2Error("Stage-2 cell lacks receipt")
        stdout, stderr = stage1._verify_raw(receipt, root)
        if (row.get("outcome"), row.get("reason")) != stage1.classify(
                row["cell"]["profile_id"], receipt, stdout, stderr):
            raise Stage2Error("Stage-2 classification differs")
        if require_commit:
            for kind in ("stdout", "stderr"):
                committed(root, receipt[f"raw_{kind}_path"])
    observed = {row["cell"]["cell_id"]: row["outcome"] for row in result["cells"]}
    if result.get("observed_matrix") != observed \
            or result.get("decision") != _decision(result["cells"],
                                                     manifest["expected_consequential_matrix"], root):
        raise Stage2Error("Stage-2 decision replay differs")
    if require_commit:
        committed(root, RUN_RESULT.as_posix())
        committed(root, (RUN_DIR / "events.jsonl").as_posix())
    return result


def validate_available(root: Path = ROOT, *, require_commit: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    value: dict[str, Any] = {"schema_version": 1, "item_id": ITEM}
    if (root / TOOLING_MANIFEST).exists():
        validate_tooling_manifest(root, require_commit=require_commit)
        value["tooling_manifest"] = "PASS"
    artifact_state = [(root / CANDIDATE).exists(), (root / CONTROL).exists(),
                      (root / AUDIT_REPORT).exists()]
    if any(artifact_state) and not all(artifact_state):
        raise Stage2Error("partial Stage-2 artifact/audit state")
    if all(artifact_state):
        try:
            from lib import acceptance_impact_stage2_audit as audit
            audit.check(root)
        except ImportError as error:
            raise Stage2Error("independent Stage-2 auditor is unavailable") from error
        value["artifact_audit"] = "PASS"
    if (root / EXECUTION_MANIFEST).exists():
        validate_execution_manifest(root, require_commit=require_commit)
        value["execution_manifest"] = "PASS"
    if (root / RUN_RESULT).exists():
        value["result"] = validate_result(root, require_commit=require_commit)["decision"]
    return value
