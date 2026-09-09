"""Validate the completed cache result across a later queue transition."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from lib.research_queue_v3 import load_queue
from lib.survivor_cache_runner import evidence

ITEM = "SURVIVOR-CACHE-1"
SNAPSHOT = "1194f3ef59d85196af40bf9c2703b41cc9f8d386"
BASE = "results/research/survivor-cache-1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(root: Path, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{SNAPSHOT}:{path}"], cwd=root)


def validate(root: Path) -> dict:
    root = root.resolve()
    manifest = json.loads((root / BASE / "evidence-manifest.json").read_text())
    require(manifest["item_id"] == ITEM and manifest["status"] == "PASS",
            "historical manifest identity drift")

    state = evidence(root)
    observed = [attempt["terminal"].get("classification") for attempt in state["attempts"]
                if attempt["reservation"]["phase"] == "checker"]
    require(observed == ["TEST_PASS", "TEST_PASS", "TEST_PASS", "REGRESSION_FAILURE"],
            "historical scientific cell pattern differs")
    require(state["next_action"] in (("DONE", None), ["DONE", None]),
            "historical execution is not complete")

    for name in ("execution_ledger", "manifest", "result", "report", "work_closure",
                 "source_review", "strategic_review", "validation", "closure_validator"):
        row = manifest[name]
        require(sha256((root / row["path"]).read_bytes()) == row["sha256"],
                "historical closure evidence drift: " + row["path"])
    for row in manifest["durable_state"]:
        require(sha256(git_bytes(root, row["path"])) == row["sha256"],
                "historical durable-state snapshot drift: " + row["path"])

    old_queue = json.loads(git_bytes(root, "config/research-queue.json"))
    old_by_id = {item["id"]: item for item in old_queue["items"]}
    result = json.loads((root / BASE / "result.json").read_text())
    require(old_queue["selected_item"] == result["next_item"] == "SURVIVOR-CACHE-EXPORT-1"
            and old_by_id[ITEM]["status"] == "COMPLETE",
            "historical queue closure or successor drift")

    current = load_queue(root, require_ready=True)
    current_by_id = {item["id"]: item for item in current["items"]}
    require(current_by_id[ITEM]["closure"] == old_by_id[ITEM]["closure"],
            "completed cache queue record changed")
    require(current_by_id["SURVIVOR-CACHE-EXPORT-1"]["status"] == "COMPLETE"
            and current_by_id["SURVIVOR-UNIVERSE-DIFF-1"]["status"] == "COMPLETE"
            and current["selected_item"] == "SURVIVOR-UNIVERSE-EQUIVALENCE-1",
            "current transition does not preserve and advance the cache successor")
    return {
        "status": "PASS",
        "historical_item": ITEM,
        "snapshot": SNAPSHOT,
        "scientific_cells": len(observed),
        "historical_successor": result["next_item"],
        "current_successor": current["selected_item"],
    }
