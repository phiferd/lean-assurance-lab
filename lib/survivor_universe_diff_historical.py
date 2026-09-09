"""Validate the universe reachability closure across frozen predecessor state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from lib.research_queue_v3 import load_queue

TRANSITION = "results/research/survivor-universe-diff-1/historical-transition.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(root: Path, snapshot: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{snapshot}:{path}"], cwd=root)


def validate(root: Path) -> dict:
    root = root.resolve()
    transition = json.loads((root / TRANSITION).read_text(encoding="utf-8"))
    required = {
        "schema_version", "item_id", "transition", "historical_snapshot",
        "historical_queue", "historical_status", "historical_cache_export_manifest",
        "evolved_live_tooling", "live_expectation", "claim",
    }
    require(set(transition) == required and transition["schema_version"] == 1
            and transition["item_id"] == "SURVIVOR-UNIVERSE-DIFF-1",
            "historical transition identity drift")
    snapshot = transition["historical_snapshot"]
    for key in ("historical_queue", "historical_status", "historical_cache_export_manifest"):
        row = transition[key]
        require(set(row) == {"path", "sha256"}
                and digest(git_bytes(root, snapshot, row["path"])) == row["sha256"],
                "historical snapshot binding drift: " + key)

    old_manifest_row = transition["historical_cache_export_manifest"]
    old_manifest = json.loads(git_bytes(root, snapshot, old_manifest_row["path"]))
    require(old_manifest["item_id"] == "SURVIVOR-CACHE-EXPORT-1"
            and old_manifest["status"] == "PASS", "wrong predecessor manifest")
    old_inputs = {row["path"]: row for row in old_manifest["inputs"]}
    for path, row in old_inputs.items():
        data = git_bytes(root, snapshot, path)
        require(len(data) == row["bytes"] and digest(data) == row["sha256"],
                "historical cache-export input drift: " + path)

    evolved = transition["evolved_live_tooling"]
    require(isinstance(evolved, list) and len(evolved) == 3, "evolved tooling inventory drift")
    for row in evolved:
        require(set(row) == {"path", "historical_sha256", "reason"}
                and row["path"] in old_inputs
                and digest(git_bytes(root, snapshot, row["path"])) == row["historical_sha256"]
                == old_inputs[row["path"]]["sha256"]
                and isinstance(row["reason"], str) and row["reason"],
                "evolved tooling lacks exact historical binding")

    old_queue = json.loads(git_bytes(root, snapshot, "config/research-queue.json"))
    old_by_id = {item["id"]: item for item in old_queue["items"]}
    require(old_queue["selected_item"] == "SURVIVOR-UNIVERSE-DIFF-1"
            and old_by_id["SURVIVOR-CACHE-EXPORT-1"]["status"] == "COMPLETE",
            "historical predecessor queue drift")
    current = load_queue(root, require_ready=True)
    current_by_id = {item["id"]: item for item in current["items"]}
    expectation = transition["live_expectation"]
    require(expectation == {
        "completed_item": "SURVIVOR-UNIVERSE-DIFF-1",
        "selected_item": "SURVIVOR-UNIVERSE-EQUIVALENCE-1",
        "canonical_classification_changed": False,
    }, "live transition expectation drift")
    require(current_by_id["SURVIVOR-CACHE-EXPORT-1"]["closure"]
            == old_by_id["SURVIVOR-CACHE-EXPORT-1"]["closure"],
            "completed cache-export queue record changed")
    require(current_by_id[expectation["completed_item"]]["status"] == "COMPLETE"
            and current_by_id[expectation["selected_item"]]["status"] == "COMPLETE"
            and current_by_id["SURVIVOR-FVAR-REACHABILITY-1"]["status"] == "COMPLETE"
            and current_by_id["SURVIVOR-THREAD-CONFIG-REACHABILITY-1"]["status"] == "COMPLETE"
            and current_by_id["SURVIVOR-THREAD-CONFIG-REGRESSION-1"]["status"] == "COMPLETE"
            and current_by_id[current["selected_item"]]["status"] in {"READY", "ACTIVE"},
            "live universe successor transition drift")
    current_assurance = json.loads((root / "results/assurance/current.json").read_text())
    pending = current_assurance["mutation_testing"]["pending_survivor_triage"]["mutant_ids"]
    require("nanoda-gen-e9648d8c028d" not in pending
            and "nanoda-gen-399895fa0b72" not in pending
            and "nanoda-gen-93b21593b0d8" not in pending
            and current_assurance["mutation_testing"]["equivalent_mutants"] == 14,
            "scoped equivalence successor was not admitted")
    return {
        "status": "PASS",
        "historical_snapshot": snapshot,
        "historical_manifest_inputs": len(old_inputs),
        "completed_item": expectation["completed_item"],
        "current_successor": current["selected_item"],
        "current_successor_status": current_by_id[current["selected_item"]]["status"],
        "canonical_classification_changed": True,
    }
