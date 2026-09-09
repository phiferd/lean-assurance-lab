"""Validate the frozen regression while its maintenance successor advances."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from lib.research_queue_v3 import load_queue
from lib.survivor_thread_config_regression_closure import validate as validate_closure

TRANSITION = Path("results/research/survivor-thread-config-regression-1/historical-transition.json")
CLOSURE = "4b13a40e2ac694d339f419472d3b5c6c1c7672ca"
ENTRY = "b7428e4295b4192d3159cb5fdde13b2e85ca7541"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git_bytes(root: Path, snapshot: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{snapshot}:{path}"], cwd=root)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(root: Path) -> dict:
    root = root.resolve()
    transition = json.loads((root / TRANSITION).read_text(encoding="utf-8"))
    require(transition["closure_snapshot"] == CLOSURE
            and transition["readiness_entry_snapshot"] == ENTRY,
            "historical snapshot identity differs")
    for key, snapshot in (("closure_queue", CLOSURE), ("closure_status", CLOSURE),
                          ("entry_queue", ENTRY), ("entry_status", ENTRY)):
        row = transition[key]
        require(digest(git_bytes(root, snapshot, row["path"])) == row["sha256"],
                "historical binding differs: " + key)
    old_queue = json.loads(git_bytes(root, CLOSURE, "config/research-queue.json"))
    entry_queue = json.loads(git_bytes(root, ENTRY, "config/research-queue.json"))
    require(old_queue["selected_item"] == "NANODA-ZERO-THREAD-UPSTREAM-READINESS-1"
            and next(row for row in old_queue["items"]
                     if row["id"] == "NANODA-ZERO-THREAD-UPSTREAM-READINESS-1")["status"] == "READY"
            and entry_queue["selected_item"] == "NANODA-ZERO-THREAD-UPSTREAM-READINESS-1"
            and next(row for row in entry_queue["items"]
                     if row["id"] == "NANODA-ZERO-THREAD-UPSTREAM-READINESS-1")["status"] == "ACTIVE",
            "historical READY-to-ACTIVE handoff differs")
    closure = validate_closure(root)
    live = load_queue(root, require_ready=True)
    by_id = {row["id"]: row for row in live["items"]}
    expectation = transition["live_expectation"]
    result = json.loads((root / "results/research/nanoda-zero-thread-upstream-readiness-1/result.json").read_text())
    current_selected = live["selected_item"]
    require(by_id[expectation["regression_item"]]["status"] == "COMPLETE"
            and by_id[expectation["completed_readiness_item"]]["status"] == "COMPLETE"
            and by_id[expectation["selected_item"]]["status"] == "COMPLETE"
            and current_selected == "SURVIVOR-THREAD-ONE-DETERMINISM-1"
            and by_id[current_selected]["status"] == "READY"
            and result["outcome"] == expectation["readiness_outcome"]
            and result["gate_decision"] == expectation["readiness_gate_decision"],
            "live maintenance transition differs")
    return {"status": "PASS", "closure_snapshot": CLOSURE,
            "frozen_regression_outcome": closure["outcome"],
            "readiness_outcome": result["outcome"],
            "readiness_gate_decision": result["gate_decision"],
            "selected_item": current_selected}
