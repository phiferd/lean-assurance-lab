"""Persistent-execution controller for pipeline completeness pilot 2."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

from lib.cvc_prep import bind, committed, require, safe
from lib.cvc_process import atomic, now, sha
from lib.pipeline_completeness import (
    ROOT, _supervise, expected_matrix, file_binding, inventory, load_json,
    omission_fault, process_classification, sentinel, truncation_fault,
    workspace_control_files,
)


ITEM = "PIPELINE-COMPLETENESS-PILOT-2"
BASE = "results/research/pipeline-completeness-pilot-2"
PROTOCOL = BASE + "/protocol.json"
PILOT1_PROTOCOL = "results/research/pipeline-completeness-pilot-1/protocol.json"
EXPECTED = "results/research/pipeline-completeness-pilot-1/expected-module.json"
SOURCE = "corpus/pipeline-completeness-pilot-1/PipelineCompletenessSentinel.lean"
PREFLIGHT = BASE + "/preflight.json"
INPUTS = BASE + "/inputs"
INVENTORY = BASE + "/artifact-inventory.json"
MANIFEST = "config/pipeline-completeness-pilot-2.json"
WORK = BASE + "/work-record.json"
RUN = BASE + "/run-0001"
PLAN = "docs/research/PIPELINE_COMPLETENESS_PILOT_2_PLAN.md"
MODULE = "lib/pipeline_completeness_pilot_2.py"
PREFLIGHT_SCRIPT = "scripts/preflight-pipeline-completeness-pilot-2"
PREPARE_SCRIPT = "scripts/prepare-pipeline-completeness-pilot-2"
ACTIVATE_SCRIPT = "scripts/activate-pipeline-completeness-pilot-2"
EXECUTE_SCRIPT = "scripts/execute-pipeline-completeness-pilot-2"


def _protocols() -> tuple[dict[str, Any], dict[str, Any]]:
    protocol = load_json(ROOT / PROTOCOL)
    inherited = load_json(ROOT / PILOT1_PROTOCOL)
    require(protocol["schema_version"] == 2 and protocol["item_id"] == ITEM,
            "pilot-2 protocol identity differs")
    require(protocol["execution_policy"]["attempt_caps"] == "NONE"
            and protocol["execution_policy"]["engineering_failure"] == "REPAIR_AND_RETRY_WITHIN_ITEM",
            "persistent execution policy differs")
    return protocol, inherited


def _selected(status: str) -> None:
    from lib.research_queue_v3 import load_queue
    queue = load_queue(ROOT, require_ready=True)
    item = next(row for row in queue["items"] if row["id"] == ITEM)
    require(queue["selected_item"] == ITEM and item["status"] == status,
            f"item is not selected {status}")
    require(item["budget"] is None, "unfinished item unexpectedly has an attempt budget")


def _committed_controller() -> None:
    for path in (PLAN, PROTOCOL, PILOT1_PROTOCOL, EXPECTED, SOURCE, MODULE,
                 PREFLIGHT_SCRIPT, PREPARE_SCRIPT, ACTIVATE_SCRIPT, EXECUTE_SCRIPT,
                 "tests/test_pipeline_completeness_pilot_2.py",
                 "tests/test_pipeline_completeness_pilot_2_protocol.py"):
        committed(ROOT, path)


def _environment(inherited: dict[str, Any]) -> tuple[Path, Path, str]:
    arena = ROOT / inherited["arena"]["path"]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=arena, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=arena, text=True)
    require(revision == inherited["arena"]["revision"] and not dirty, "Arena checkout differs")
    producer = ROOT / inherited["producer"]["path"]
    require(producer.is_file() and sha(producer) == inherited["producer"]["sha256"],
            "producer binary differs")
    return arena, producer, revision


def _next_attempt(kind: str) -> tuple[int, Path, Path]:
    index = 1
    while (ROOT / BASE / f"{kind}-run-{index:04d}").exists():
        index += 1
    run_dir = ROOT / BASE / f"{kind}-run-{index:04d}"
    workspace = ROOT / "external" / f"pipeline-completeness-pilot-2-{kind}-{index:04d}"
    require(not workspace.exists(), "fresh workspace path already exists")
    return index, run_dir, workspace


def _materialize_workspace(workspace: Path) -> None:
    workspace.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(ROOT / SOURCE, workspace / "PipelineCompletenessSentinel.lean")
    for name, content in workspace_control_files().items():
        (workspace / name).write_bytes(content)
    require(not (workspace / "lake-manifest.json").exists(),
            "controller must not create lake-manifest.json")


def preflight() -> dict[str, Any]:
    protocol, inherited = _protocols()
    require(protocol["status"] == "READY", "protocol is not READY")
    _selected("READY")
    _committed_controller()
    _, _, revision = _environment(inherited)
    attempt, run_dir, workspace = _next_attempt("preflight")
    _materialize_workspace(workspace)
    safety = protocol["process_safety"]
    env = dict(os.environ)
    env["LANG"] = "C"
    receipt, stdout, stderr = _supervise(
        run_dir / "process", ["lake", "check-build"], workspace, env,
        safety["configuration_preflight_seconds"],
        safety["configuration_preflight_memory_bytes"],
    )
    outcome = process_classification(receipt)
    result = {
        "schema_version": 1, "item_id": ITEM, "attempt": attempt,
        "recorded_at": now(), "outcome": outcome,
        "command": ["lake", "check-build"], "compilation_performed": False,
        "controller_created_manifest": False,
        "workspace_controls": sorted(workspace_control_files()),
        "arena_revision": revision,
        "receipt": file_binding(run_dir / "process/supervisor.json"),
        "stdout": file_binding(run_dir / "process/process.stdout"),
        "stderr": file_binding(run_dir / "process/process.stderr"),
        "stdout_empty": stdout == b"", "stderr_empty": stderr == b"",
    }
    atomic(run_dir / "result.json", result)
    if outcome == "ACCEPT":
        atomic(ROOT / PREFLIGHT, {**result, "attempt_result": file_binding(run_dir / "result.json")})
    require(outcome == "ACCEPT", "configuration preflight failed; repair and retry")
    return load_json(ROOT / PREFLIGHT)


def prepare() -> dict[str, Any]:
    protocol, inherited = _protocols()
    require(protocol["status"] == "READY", "protocol is not READY")
    _selected("READY")
    _committed_controller()
    _, producer, revision = _environment(inherited)
    preflight_record = load_json(ROOT / PREFLIGHT)
    require(preflight_record["outcome"] == "ACCEPT" and not preflight_record["compilation_performed"],
            "passing no-compilation preflight is absent")
    bind(ROOT, preflight_record["attempt_result"])
    committed(ROOT, PREFLIGHT)

    attempt, run_dir, workspace = _next_attempt("producer")
    _materialize_workspace(workspace)
    temporary = run_dir / "baseline.ndjson.tmp"
    command = ('set -eu\nlake build PipelineCompletenessSentinel\n'
               'lake env "$PIPELINE_EXPORTER" PipelineCompletenessSentinel -- PipelineCompleteness.d12 > "$PIPELINE_OUTPUT"')
    env = dict(os.environ)
    env.update({"LANG": "C", "PIPELINE_EXPORTER": str(producer),
                "PIPELINE_OUTPUT": str(temporary)})
    safety = protocol["process_safety"]
    receipt, stdout, _ = _supervise(run_dir / "process", ["/bin/sh", "-c", command],
                                    workspace, env, safety["producer_seconds"],
                                    safety["producer_memory_bytes"])
    process = process_classification(receipt)
    attempt_result = {
        "schema_version": 1, "item_id": ITEM, "attempt": attempt,
        "recorded_at": now(), "process_outcome": process,
        "receipt": file_binding(run_dir / "process/supervisor.json"),
        "stdout": file_binding(run_dir / "process/process.stdout"),
        "stderr": file_binding(run_dir / "process/process.stderr"),
        "temporary_export_exists": temporary.is_file(),
    }
    atomic(run_dir / "result.json", attempt_result)
    require(process == "ACCEPT" and stdout == b"" and temporary.is_file(),
            "producer build failed; repair and retry")

    input_dir = safe(ROOT, INPUTS, exists=False)
    require(not input_dir.exists(), "frozen pilot-2 inputs already exist")
    input_dir.mkdir(parents=True)
    baseline = input_dir / "baseline.ndjson"
    os.replace(temporary, baseline)
    baseline_data = baseline.read_bytes()
    observed = inventory(baseline_data)
    baseline_digest = sha(baseline)
    (input_dir / "omission.ndjson").write_bytes(omission_fault(baseline_data))
    substitution_source = ROOT / "external/lean-kernel-arena/_build/tests/lal-alt-eq-refl.ndjson"
    require(substitution_source.is_file(), "substitution Arena artifact is unavailable")
    shutil.copyfile(substitution_source, input_dir / "substitution.ndjson")
    (input_dir / "truncation.ndjson").write_bytes(truncation_fault(baseline_data))
    expected = {"baseline": "PASS", "omission": "FAIL_MISSING_TARGET",
                "substitution": "FAIL_ARTIFACT_OR_DECLARATION_IDENTITY",
                "truncation": "FAIL_PARSE_OR_DEPENDENCY_CLOSURE"}
    artifacts = {}
    for name, expected_class in expected.items():
        path = input_dir / f"{name}.ndjson"
        result = sentinel(path.read_bytes(), baseline_digest)
        require(result["classification"] == expected_class, f"{name} sentinel differs")
        artifacts[name] = {"binding": file_binding(path), "sentinel": result["classification"]}
    record = {
        "schema_version": 1, "item_id": ITEM, "generated_at": now(),
        "source": file_binding(ROOT / SOURCE), "producer": file_binding(producer),
        "preflight": file_binding(ROOT / PREFLIGHT),
        "producer_attempt": file_binding(run_dir / "result.json"),
        "producer_receipt": file_binding(run_dir / "process/supervisor.json"),
        "substitution_provenance": {"source_path": substitution_source.relative_to(ROOT).as_posix(),
                                    "source_sha256": sha(substitution_source),
                                    "arena_revision": revision},
        "baseline_inventory": observed, "artifacts": artifacts,
    }
    atomic(ROOT / INVENTORY, record)
    result = {"schema_version": 1, "item_id": ITEM, "outcome": "SUCCESS",
              "generated_at": now(), "inventory": file_binding(ROOT / INVENTORY),
              "producer_receipt": file_binding(run_dir / "process/supervisor.json"),
              "artifact_count": 4}
    atomic(ROOT / BASE / "producer-result.json", result)
    return result


def activate() -> dict[str, Any]:
    protocol, inherited = _protocols()
    _selected("READY")
    _committed_controller()
    bind(ROOT, load_json(ROOT / BASE / "producer-result.json")["inventory"])
    inventory_record = load_json(ROOT / INVENTORY)
    work = {
        "schema_version": 1, "item_id": ITEM,
        "frontier_id": "F-DISCOVERY-AND-CONFORMANCE", "owner": "root",
        "status": "ACTIVE", "started_at": now(),
        "plan": PLAN, "execution_policy": protocol["execution_policy"],
        "observations": {"historical_attempts": 1,
                         "pilot_2_preflight_attempts": len(list((ROOT / BASE).glob("preflight-run-*"))),
                         "pilot_2_producer_attempts": len(list((ROOT / BASE).glob("producer-run-*")))},
    }
    atomic(ROOT / WORK, work)
    adapters = []
    for profile in inherited["adapters"]:
        binary = ROOT / profile["binary"]["path"]
        require(binary.is_file() and sha(binary) == profile["binary"]["sha256"],
                f"adapter binary differs for {profile['id']}")
        adapters.append({"id": profile["id"], "binary": file_binding(binary),
                         "arguments_before_artifact": [] if profile["id"] == "official" else ["--import"]})
    manifest = {
        "schema_version": 1, "item_id": ITEM,
        "inputs": [file_binding(ROOT / path) for path in
                   (PLAN, PROTOCOL, PILOT1_PROTOCOL, EXPECTED, SOURCE, PREFLIGHT, INVENTORY)],
        "tooling": [file_binding(ROOT / path) for path in
                    (MODULE, PREFLIGHT_SCRIPT, PREPARE_SCRIPT, ACTIVATE_SCRIPT, EXECUTE_SCRIPT)],
        "artifacts": [inventory_record["artifacts"][name]["binding"]
                      for name in ("baseline", "omission", "substitution", "truncation")],
        "adapter_profiles": adapters,
        "matrix": [{"artifact": artifact, "adapter": adapter,
                    "expected_sentinel": expected}
                   for artifact, adapter, expected in expected_matrix()],
        "work_record": file_binding(ROOT / WORK),
        "execution_policy": protocol["execution_policy"],
    }
    atomic(ROOT / MANIFEST, manifest)
    return manifest


def _validate_execution_manifest() -> dict[str, Any]:
    manifest = load_json(ROOT / MANIFEST)
    require(manifest["schema_version"] == 1 and manifest["item_id"] == ITEM,
            "execution manifest identity differs")
    protocol, inherited = _protocols()
    require(manifest["execution_policy"] == protocol["execution_policy"],
            "execution policy differs")
    for section in ("inputs", "tooling", "artifacts"):
        for row in manifest[section]:
            bind(ROOT, row)
            committed(ROOT, row["path"])
    expected_adapters = {row["id"]: row for row in inherited["adapters"]}
    require({row["id"] for row in manifest["adapter_profiles"]} == set(expected_adapters),
            "adapter profile identities differ")
    for row in manifest["adapter_profiles"]:
        bind(ROOT, row["binary"])
        require(row["binary"]["path"] == expected_adapters[row["id"]]["binary"]["path"],
                f"adapter binary differs for {row['id']}")
    work = load_json(bind(ROOT, manifest["work_record"]))
    require(work["status"] == "ACTIVE" and work["item_id"] == ITEM,
            "work record is not ACTIVE")
    require(manifest["matrix"] == [{"artifact": artifact, "adapter": adapter,
                                     "expected_sentinel": expected}
                                    for artifact, adapter, expected in expected_matrix()],
            "execution matrix differs")
    return manifest


def execute() -> dict[str, Any]:
    manifest = _validate_execution_manifest()
    _selected("ACTIVE")
    for path in (MANIFEST, WORK, PLAN, PROTOCOL, "config/research-queue.json",
                 "docs/RESEARCH_STATUS.md"):
        committed(ROOT, path)
    run_dir = safe(ROOT, RUN, exists=False)
    require(not run_dir.exists(), "refuse execution overwrite")
    run_dir.mkdir(parents=True)
    artifacts = {Path(row["path"]).stem: ROOT / row["path"] for row in manifest["artifacts"]}
    adapters = {row["id"]: row for row in manifest["adapter_profiles"]}
    baseline_digest = sha(artifacts["baseline"])
    safety = load_json(ROOT / PROTOCOL)["process_safety"]
    cells = []
    for artifact_name, adapter_id, expected_sentinel in expected_matrix():
        artifact_path = artifacts[artifact_name]
        sentinel_result = sentinel(artifact_path.read_bytes(), baseline_digest)
        require(sentinel_result["classification"] == expected_sentinel,
                f"sentinel differs before {artifact_name}/{adapter_id}")
        profile = adapters[adapter_id]
        binary = ROOT / profile["binary"]["path"]
        argv = [str(binary), *profile["arguments_before_artifact"], str(artifact_path)]
        directory = run_dir / f"{artifact_name}-{adapter_id}"
        env = {"LANG": "C", "PATH": "/usr/bin:/bin"}
        receipt, _, _ = _supervise(directory, argv, binary.parent, env,
                                    safety["checker_seconds_each"],
                                    safety["checker_memory_bytes_each"])
        receipt.update({"adapter_id": adapter_id, "adapter_binary_sha256": sha(binary),
                        "artifact": file_binding(artifact_path), "sentinel": sentinel_result})
        atomic(directory / "supervisor.json", receipt)
        process = process_classification(receipt)
        require(process not in {"INFRASTRUCTURE_FAILURE", "UNKNOWN"},
                f"process infrastructure failed for {artifact_name}/{adapter_id}; repair and retry")
        if artifact_name == "baseline":
            require(process == "ACCEPT", f"baseline was not accepted by {adapter_id}")
        cells.append({"artifact": artifact_name, "adapter": adapter_id,
                      "sentinel": sentinel_result["classification"],
                      "process_outcome": process,
                      "receipt": file_binding(directory / "supervisor.json"),
                      "stdout": file_binding(directory / "process.stdout"),
                      "stderr": file_binding(directory / "process.stderr")})
    false_reassurance = [{"artifact": row["artifact"], "adapter": row["adapter"]}
                         for row in cells if row["artifact"] != "baseline"
                         and row["process_outcome"] == "ACCEPT"]
    result = {
        "schema_version": 1, "item_id": ITEM, "outcome": "SUCCESS", "generated_at": now(),
        "cells": cells, "false_reassurance_cells": false_reassurance,
        "conclusion": "The checked-object sentinel accepted only the exact intended artifact and rejected all omission, substitution and truncation faults independently of checker exit status.",
        "claim_limit": "This establishes scoped sentinel behavior for one module, producer and two adapters. It does not make checker-correctness or semantic-authority claims.",
    }
    atomic(ROOT / BASE / "result.json", result)
    return result
