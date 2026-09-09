"""Validate the universe equivalence admission across its entry snapshot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from lib.research_queue_v3 import load_queue

ITEM = "SURVIVOR-UNIVERSE-EQUIVALENCE-1"
MUTANT = "nanoda-gen-e9648d8c028d"
TRANSITION = "results/research/survivor-universe-equivalence-1/historical-transition.json"
REGISTRY = "results/mutants/registry.jsonl"
INVENTORY = "results/survivors/inventory.jsonl"
POST_CLOSURE_SNAPSHOT = "9d764b4d46b16aa898f229d60d4fe74714555597"


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
    fields = {
        "schema_version", "item_id", "transition", "historical_snapshot",
        "historical_queue", "historical_status", "historical_diff_manifest",
        "predecessor_registry", "survivor_inventory", "evolved_live_tooling",
        "live_expectation", "claim",
    }
    require(set(transition) == fields and transition["schema_version"] == 1
            and transition["item_id"] == ITEM
            and transition["transition"]
            == "UNIVERSE_DIFF_REACHABILITY_TO_SCOPED_EQUIVALENT_ADMISSION",
            "historical transition identity drift")
    snapshot = transition["historical_snapshot"]
    require(snapshot == "a4580dcd2d74f8156b4151d7439ca1e048a9735c",
            "wrong entry snapshot")
    for key in ("historical_queue", "historical_status", "historical_diff_manifest"):
        row = transition[key]
        require(set(row) == {"path", "sha256"}
                and digest(git_bytes(root, snapshot, row["path"])) == row["sha256"],
                "historical snapshot binding drift: " + key)

    registry_row = transition["predecessor_registry"]
    old_registry = git_bytes(root, snapshot, registry_row["path"])
    require(registry_row == {
        "path": REGISTRY, "lines": 607,
        "sha256": "99b5867b1437b25af3bb5ab440875a616756e7c0bd75047f0dcdd745f4f4a572",
    } and len(old_registry.splitlines()) == 607 and digest(old_registry) == registry_row["sha256"],
            "registry predecessor binding drift")
    inventory_row = transition["survivor_inventory"]
    old_inventory = git_bytes(root, snapshot, inventory_row["path"])
    require(inventory_row == {
        "path": INVENTORY, "lines": 1,
        "sha256": "c7e552e761f128e9911abeb6cc85cf1d4b7c48d6ed03798d574a0ace688f2458",
    } and len(old_inventory.splitlines()) == 1 and digest(old_inventory) == inventory_row["sha256"],
            "survivor inventory predecessor drift")

    manifest_row = transition["historical_diff_manifest"]
    old_manifest = json.loads(git_bytes(root, snapshot, manifest_row["path"]))
    require(old_manifest["item_id"] == "SURVIVOR-UNIVERSE-DIFF-1"
            and old_manifest["status"] == "PASS", "wrong predecessor manifest")
    old_inputs = {row["path"]: row for row in old_manifest["inputs"]}
    for path, row in old_inputs.items():
        data = git_bytes(root, snapshot, path)
        require(len(data) == row["bytes"] and digest(data) == row["sha256"],
                "historical universe-diff input drift: " + path)
    evolved = transition["evolved_live_tooling"]
    require([row["path"] for row in evolved] == [
        "lib/survivor_universe_diff.py",
        "lib/survivor_universe_diff_historical.py",
        "tests/test_survivor_universe_diff_historical.py",
        "lib/survivor_cache_historical.py",
        "tests/test_survivor_cache_historical.py",
    ], "evolved predecessor tooling inventory drift")
    for row in evolved:
        require(set(row) == {"path", "historical_sha256", "reason"}
                and row["path"] in old_inputs
                and digest(git_bytes(root, snapshot, row["path"]))
                == row["historical_sha256"] == old_inputs[row["path"]]["sha256"]
                and isinstance(row["reason"], str) and row["reason"],
                "evolved tooling lacks exact historical binding")

    old_queue = json.loads(git_bytes(root, snapshot, "config/research-queue.json"))
    old_by_id = {item["id"]: item for item in old_queue["items"]}
    require(old_queue["selected_item"] == ITEM and old_by_id[ITEM]["status"] == "ACTIVE"
            and old_by_id["SURVIVOR-UNIVERSE-DIFF-1"]["status"] == "COMPLETE",
            "entry queue was not the committed active state")
    old_assurance = json.loads(git_bytes(root, snapshot, "results/assurance/current.json"))
    old_pending = old_assurance["mutation_testing"]["pending_survivor_triage"]
    require(old_pending["count"] == 6 and MUTANT in old_pending["mutant_ids"]
            and old_assurance["mutation_testing"]["equivalent_mutants"] == 12,
            "entry assurance did not retain the pending survivor")

    expectation = transition["live_expectation"]
    require(expectation == {
        "completed_item": ITEM,
        "selected_item": "SURVIVOR-FVAR-REACHABILITY-1",
        "registry_append_count": 1,
        "registry_classification": "EQUIVALENT",
        "pending_survivors_before": 6,
        "pending_survivors_after": 5,
        "survivor_inventory_changed": False,
    }, "live transition expectation drift")
    post_registry = git_bytes(root, POST_CLOSURE_SNAPSHOT, REGISTRY)
    require(post_registry.startswith(old_registry) and len(post_registry.splitlines()) == 608,
            "universe post-closure registry is not the exact one-row successor")
    appended = json.loads(post_registry[len(old_registry):].decode("utf-8"))
    require(appended["id"] == MUTANT and appended["status"] == "SURVIVED"
            and appended["classification"] == expectation["registry_classification"],
            "current registry append classification drift")
    require(git_bytes(root, POST_CLOSURE_SNAPSHOT, INVENTORY) == old_inventory
            and (root / INVENTORY).read_bytes() == old_inventory,
            "current survivor inventory changed")

    post_queue = json.loads(git_bytes(root, POST_CLOSURE_SNAPSHOT, "config/research-queue.json"))
    post_by_id = {item["id"]: item for item in post_queue["items"]}
    require(post_queue["selected_item"] == expectation["selected_item"]
            and post_by_id[expectation["selected_item"]]["status"] == "READY",
            "universe post-closure successor state drift")
    post_assurance = json.loads(
        git_bytes(root, POST_CLOSURE_SNAPSHOT, "results/assurance/current.json")
    )
    post_pending = post_assurance["mutation_testing"]["pending_survivor_triage"]
    require(post_pending["count"] == 5 and MUTANT not in post_pending["mutant_ids"]
            and post_assurance["mutation_testing"]["equivalent_mutants"] == 13,
            "universe post-closure assurance drift")

    current = load_queue(root, require_ready=True)
    current_by_id = {item["id"]: item for item in current["items"]}
    require(current_by_id["SURVIVOR-UNIVERSE-DIFF-1"]["closure"]
            == old_by_id["SURVIVOR-UNIVERSE-DIFF-1"]["closure"],
            "predecessor queue closure changed")
    require(current_by_id[ITEM]["status"] == "COMPLETE"
            and current_by_id[expectation["selected_item"]]["status"] == "COMPLETE"
            and current_by_id["SURVIVOR-THREAD-CONFIG-REACHABILITY-1"]["status"] == "COMPLETE"
            and current_by_id["SURVIVOR-THREAD-CONFIG-REGRESSION-1"]["status"] == "COMPLETE"
            and current_by_id[current["selected_item"]]["status"] in {"READY", "ACTIVE"},
            "current queue does not preserve the universe successor transition")
    current_assurance = json.loads((root / "results/assurance/current.json").read_text())
    pending = current_assurance["mutation_testing"]["pending_survivor_triage"]
    require(pending["count"] == 2 and MUTANT not in pending["mutant_ids"]
            and "nanoda-gen-399895fa0b72" not in pending["mutant_ids"]
            and "nanoda-gen-93b21593b0d8" not in pending["mutant_ids"]
            and "nanoda-gen-af1dac9744e9" not in pending["mutant_ids"]
            and current_assurance["mutation_testing"]["equivalent_mutants"] == 14
            and current_assurance["mutation_testing"]["meaningful_survivors"] == 5,
            "current assurance did not preserve and advance scoped equivalence")
    report = json.loads((root / "results/assurance/current-mutation-report.json").read_text())
    require(report["classified_equivalent"] == 14
            and report["survived_without_witness"] == 2
            and report["meaningful_survivors"] == 5
            and report["modeled_mutation_score_denominator"] == 142
            and report["modeled_mutation_score"] == 135 / 142,
            "current mutation report metrics disagree with later scoped admissions")
    return {
        "status": "PASS",
        "historical_snapshot": snapshot,
        "historical_manifest_inputs": len(old_inputs),
        "registry_predecessor_lines": 607,
        "registry_successor_lines": len((root / REGISTRY).read_bytes().splitlines()),
        "current_successor": current["selected_item"],
        "current_successor_status": current_by_id[current["selected_item"]]["status"],
        "pending_survivors": pending["count"],
        "equivalent_mutants": current_assurance["mutation_testing"]["equivalent_mutants"],
    }
