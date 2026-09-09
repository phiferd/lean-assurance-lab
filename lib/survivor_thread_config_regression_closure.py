"""Closure validator for the executed zero-thread fixed-pair regression."""
from __future__ import annotations

import json
from pathlib import Path

from lib.cvc_prep import bind, require
from lib.cvc_process import sha
from lib.survivor_thread_config_regression import evidence

BASE = "results/research/survivor-thread-config-regression-1"
RESULT = BASE + "/result.json"
WORK = BASE + "/work-record.json"
CLOSURE = BASE + "/work-closure.json"
PRESERVATION = BASE + "/canonical-state-preservation.json"
EVIDENCE = BASE + "/evidence-manifest.json"
REPAIR = BASE + "/validator-repair.json"
LEDGER = BASE + "/run-0001/execution/events.jsonl"
TAIL = "4a93c2e67d721d8606b12f5d100be7dbfa95c2e5349614bae0a654c324a32c5b"
PROCESS_SECONDS = 30.361877125003957


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_state(state):
    require(state["next_action"] == ("DONE", None) and not state["repairs"]
            and len(state["attempts"]) == 6, "fixed execution is not complete")
    expected = [
        ("build", "baseline", None), ("build", "mutant", None),
        ("checker", 0, "ACCEPT"), ("checker", 1, "ACCEPT"),
        ("checker", 2, "TYPECHECK_REFUSAL"), ("checker", 3, "ACCEPT"),
    ]
    for attempt, (phase, cell, classification) in zip(state["attempts"], expected):
        reservation, terminal = attempt["reservation"], attempt["terminal"]
        require(reservation["phase"] == phase and reservation["cell"] == cell
                and terminal["cleanup_completed"] is True
                and terminal["engineering_pause"] is False, "attempt sequence or cleanup differs")
        if phase == "build":
            require(terminal["status"] == "COMPLETE" and terminal["returncode"] == 0
                    and terminal.get("binary"), "build did not complete exactly")
        else:
            require(terminal["classification"] == classification, "fixed-pair outcome differs")
    require(abs(state["charged_seconds"] - PROCESS_SECONDS) < 1e-9,
            "scientific process accounting differs")
    return state


def validate(root):
    root = Path(root).resolve()
    state = validate_state(evidence(root))
    result = load(root / RESULT)
    require(result["item_id"] == "SURVIVOR-THREAD-CONFIG-REGRESSION-1"
            and result["outcome"] == "SUCCESS"
            and result["finding"] == "EXECUTED_PUBLIC_ZERO_THREAD_DECLARATION_CHECK_ELISION"
            and result["ledger"] == {"path": LEDGER,
                "sha256": "060545675671e50137f8e257397b6c1578930b917c60485a3a56eadd8ab2e5cd",
                "event_count": 13, "tail_sha256": TAIL}, "result or ledger binding differs")
    require(result["fixed_pair"] == [
        {"cell": "control-baseline", "expected": "ACCEPT", "observed": "ACCEPT", "returncode": 0, "attempt": 3},
        {"cell": "control-mutant", "expected": "ACCEPT", "observed": "ACCEPT", "returncode": 0, "attempt": 4},
        {"cell": "candidate-baseline", "expected": "TYPECHECK_REFUSAL", "observed": "TYPECHECK_REFUSAL", "returncode": 101, "attempt": 5},
        {"cell": "candidate-mutant", "expected": "ACCEPT", "observed": "ACCEPT", "returncode": 0, "attempt": 6},
    ], "reported fixed pair differs")
    require(result["binaries"]["baseline"] == state["attempts"][0]["terminal"]["binary"]
            and result["binaries"]["mutant"] == state["attempts"][1]["terminal"]["binary"],
            "reported binary identities differ")
    accounting = result["execution_accounting"]
    require(accounting["offline_build_launches"] == 2 and accounting["checker_launches"] == 4
            and accounting["scientific_process_seconds"] == PROCESS_SECONDS
            and accounting["research_network_requests"] == 0
            and accounting["lean_proof_launches"] == 0
            and accounting["new_export_byte_variants"] == 0
            and accounting["new_mutation_identities"] == 0
            and accounting["external_actions"] == 0
            and accounting["total_active_seconds_charged_conservatively"] <= 7200,
            "result accounting differs or exceeds cap")
    work, closure = load(root / WORK), load(root / CLOSURE)
    require(work["status"] == closure["status"] == "COMPLETE"
            and work["outcome"] == closure["outcome"] == "SUCCESS"
            and work["research_counts"]["offline_build_launches"] == 2
            and work["research_counts"]["checker_launches"] == 4
            and closure["ledger_tail_sha256"] == TAIL
            and closure["next_item"] == result["recommendation"]["next_item"]
            == "NANODA-ZERO-THREAD-UPSTREAM-READINESS-1"
            and not work["next_item_started"] and not closure["next_item_started"]
            and not result["next_item_started"], "work closure differs")
    preservation = load(root / PRESERVATION)
    require(preservation["status"] == "MUTATION_STATE_UNCHANGED_DERIVED_SNAPSHOT_REFRESHED",
            "canonical mutation state is not preserved")
    for row in preservation["artifacts"]:
        path = root / row["path"]
        require(row["after_sha256"] == sha(path)
                and len(path.read_text(encoding="utf-8").splitlines()) == row["lines"],
                "canonical state drift: " + row["path"])
        if row["path"] != "results/assurance/current.json":
            require(row["before_sha256"] == row["after_sha256"],
                    "canonical mutation input changed: " + row["path"])
    repair = load(root / REPAIR)
    require(repair["item_id"] == result["item_id"]
            and repair["status"] == "REPAIRED"
            and repair["classification"]
            == "ENGINEERING_HISTORICAL_SUCCESSOR_VALIDATOR_STALENESS"
            and repair["scientific_evidence_changed"] is False
            and repair["scientific_launches_added"] == 0
            and repair["focused_repair_validation"]["survivor_status"] == "PASS"
            and repair["full_suite_revalidation"]["current_suite_status"] == "PASS"
            and repair["full_suite_revalidation"]["frozen_publication_status"] == "PASS",
            "validator repair record differs or changes scientific evidence")
    manifest = load(root / EVIDENCE)
    require(manifest["item_id"] == result["item_id"] and manifest["status"] == "PASS"
            and manifest["ledger_tail_sha256"] == TAIL, "evidence manifest differs")
    required = {RESULT, WORK, CLOSURE, PRESERVATION, REPAIR, LEDGER,
                "config/survivor-thread-config-regression-0001.json",
                "docs/research/NANODA_ZERO_THREAD_UPSTREAM_READINESS_PLAN.md",
                "results/research/queue-reviews/2026-09-08-survivor-thread-config-regression-closure-strategic.json"}
    paths = {row["path"] for row in manifest["artifacts"]}
    require(required <= paths and len(paths) == len(manifest["artifacts"]),
            "evidence manifest missing required or duplicate paths")
    for row in manifest["artifacts"]:
        path = bind(root, {"path": row["path"], "sha256": row["sha256"]})
        require(path.stat().st_size == row["bytes"], "evidence byte count differs")
    attempts_root = root / BASE / "run-0001/attempts"
    for number in range(1, 7):
        directory = attempts_root / f"{number:02d}"
        require({path.name for path in directory.iterdir()} ==
                {"process.json", "request.json", "supervisor.json", "stdout", "stderr"},
                "raw attempt inventory differs")
        process = load(directory / "process.json")
        request = load(directory / "request.json")
        require(process["request_sha256"] == request["request_sha256"]
                and type(process["pid"]) is int and type(process["supervisor_pid"]) is int,
                "process identity receipt differs")
    from lib.research_queue_v3 import load_queue
    queue = load_queue(root, require_ready=True)
    current = next(row for row in queue["items"] if row["id"] == result["item_id"])
    successor = next(row for row in queue["items"]
                     if row["id"] == "NANODA-ZERO-THREAD-UPSTREAM-READINESS-1")
    require(queue["frontier_id"] == "F-NANODA-ZERO-THREAD-UPSTREAM-READINESS"
            and queue["selected_item"] == successor["id"]
            and current["status"] == "COMPLETE" and successor["status"] == "READY"
            and not any(row["status"] == "ACTIVE" for row in queue["items"]),
            "queue handoff differs")
    return {"status": "PASS", "outcome": result["outcome"],
            "fixed_pair": [row["observed"] for row in result["fixed_pair"]],
            "scientific_process_seconds": state["charged_seconds"],
            "selected_item": queue["selected_item"]}
