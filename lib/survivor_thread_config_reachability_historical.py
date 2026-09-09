"""Validate thread-config classification across its exact entry snapshot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from lib.research_queue_v3 import load_queue


ITEM = "SURVIVOR-THREAD-CONFIG-REACHABILITY-1"
GE_MUTANT = "nanoda-gen-2bdfe18a9ec2"
NEG_MUTANT = "nanoda-gen-93b21593b0d8"
SNAPSHOT = "336172a83fc6c2c8896aa107637f3a7924bea34a"
FVAR_CLOSURE_SNAPSHOT = "87eadcc83e89439388b17997af50a207936ebe5a"
TRANSITION = f"results/research/survivor-thread-config-reachability-1/historical-transition.json"
REGISTRY = "results/mutants/registry.jsonl"
INVENTORY = "results/survivors/inventory.jsonl"
NEXT_ITEM = "SURVIVOR-THREAD-CONFIG-REGRESSION-1"


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
        "historical_queue", "historical_status", "historical_fvar_manifest",
        "historical_work_record", "historical_entry_decision",
        "predecessor_registry", "entry_assurance", "survivor_inventory",
        "evolved_live_tooling", "live_expectation", "claim",
    }
    require(set(transition) == fields and transition["schema_version"] == 1
            and transition["item_id"] == ITEM
            and transition["transition"]
            == "PUBLIC_THREAD_CONFIG_TRACE_TO_SCOPED_MEANINGFUL_ADMISSION"
            and transition["historical_snapshot"] in {"336172a", SNAPSHOT},
            "historical transition identity drift")
    for key in ("historical_queue", "historical_status",
                "historical_fvar_manifest", "historical_work_record",
                "historical_entry_decision"):
        row = transition[key]
        require(set(row) == {"path", "sha256"}
                and digest(git_bytes(root, SNAPSHOT, row["path"])) == row["sha256"],
                "historical entry binding drift: " + key)

    old_registry = git_bytes(root, SNAPSHOT, REGISTRY)
    predecessor = transition["predecessor_registry"]
    require(predecessor == {
        "path": REGISTRY, "lines": 609,
        "sha256": "9f38a528bec31f358009cf7f3c00f4f8d6779dc07dbd3371271ff3e4801eac10",
    } and len(old_registry.splitlines()) == 609
      and digest(old_registry) == predecessor["sha256"],
      "registry predecessor binding drift")
    old_inventory = git_bytes(root, SNAPSHOT, INVENTORY)
    inventory = transition["survivor_inventory"]
    require(inventory == {
        "path": INVENTORY, "lines": 1,
        "sha256": "c7e552e761f128e9911abeb6cc85cf1d4b7c48d6ed03798d574a0ace688f2458",
    } and len(old_inventory.splitlines()) == 1
      and digest(old_inventory) == inventory["sha256"],
      "survivor inventory predecessor drift")

    old_queue = json.loads(git_bytes(root, SNAPSHOT, "config/research-queue.json"))
    old_by_id = {item["id"]: item for item in old_queue["items"]}
    require(old_queue["selected_item"] == ITEM
            and old_by_id[ITEM]["status"] == "ACTIVE"
            and old_by_id["SURVIVOR-FVAR-REACHABILITY-1"]["status"] == "COMPLETE",
            "entry queue was not the committed active state")
    old_assurance = json.loads(
        git_bytes(root, SNAPSHOT, "results/assurance/current.json")
    )
    old_pending = old_assurance["mutation_testing"]["pending_survivor_triage"]
    entry = transition["entry_assurance"]
    require(entry["path"] == "results/assurance/current.json"
            and digest(git_bytes(root, SNAPSHOT, entry["path"])) == entry["sha256"]
            and entry["pending_survivors"] == old_pending["count"] == 4
            and entry["meaningful_survivors"]
            == old_assurance["mutation_testing"]["meaningful_survivors"] == 3
            and entry["equivalent_mutants"]
            == old_assurance["mutation_testing"]["equivalent_mutants"] == 14
            and GE_MUTANT in old_pending["mutant_ids"]
            and NEG_MUTANT in old_pending["mutant_ids"],
            "entry assurance did not retain both pending thread survivors")

    manifest_row = transition["historical_fvar_manifest"]
    manifest = json.loads(git_bytes(root, SNAPSHOT, manifest_row["path"]))
    require(manifest["item_id"] == "SURVIVOR-FVAR-REACHABILITY-1"
            and manifest["status"] == "PASS", "wrong historical fvar manifest")
    old_inputs = {row["path"]: row for row in manifest["inputs"]}
    for path, row in old_inputs.items():
        data = git_bytes(root, FVAR_CLOSURE_SNAPSHOT, path)
        require(len(data) == row["bytes"] and digest(data) == row["sha256"],
                "historical fvar closure input drift: " + path)
    evolved = transition["evolved_live_tooling"]
    require(len(evolved) == 11, "evolved tooling inventory drift")
    for row in evolved:
        require(set(row) == {"path", "historical_sha256", "reason"}
                and digest(git_bytes(root, SNAPSHOT, row["path"]))
                == row["historical_sha256"]
                and isinstance(row["reason"], str) and row["reason"],
                "evolved tooling lacks exact entry binding")

    expectation = transition["live_expectation"]
    require(expectation == {
        "completed_item": ITEM, "selected_item": NEXT_ITEM,
        "registry_append_count": 1, "registry_mutation_id": NEG_MUTANT,
        "registry_classification": "MEANINGFUL_SEMANTIC",
        "pending_survivors_before": 4, "pending_survivors_after": 3,
        "meaningful_survivors_before": 3, "meaningful_survivors_after": 4,
        "equivalent_mutants": 14, "survivor_inventory_changed": False,
    }, "live transition expectation drift")
    current_registry = (root / REGISTRY).read_bytes()
    require(current_registry.startswith(old_registry)
            and len(current_registry.splitlines()) == 610,
            "current registry is not the exact one-row successor")
    appended = json.loads(current_registry[len(old_registry):].decode("utf-8"))
    require(appended["id"] == NEG_MUTANT and appended["status"] == "SURVIVED"
            and appended["classification"] == expectation["registry_classification"],
            "current registry append classification drift")
    latest = {}
    for line in current_registry.decode("utf-8").splitlines():
        row = json.loads(line)
        latest[row["id"]] = {**latest.get(row["id"], {}), **row}
    require(latest[GE_MUTANT]["classification"] == "SURVIVED_WITHOUT_WITNESS"
            and latest[NEG_MUTANT]["classification"] == "MEANINGFUL_SEMANTIC",
            "live registry lost the split thread classification")
    require((root / INVENTORY).read_bytes() == old_inventory,
            "current survivor inventory changed")

    current = load_queue(root, require_ready=True)
    current_by_id = {item["id"]: item for item in current["items"]}
    require(current_by_id["SURVIVOR-FVAR-REACHABILITY-1"]["closure"]
            == old_by_id["SURVIVOR-FVAR-REACHABILITY-1"]["closure"],
            "predecessor fvar queue closure changed")
    require(current_by_id[ITEM]["status"] == "COMPLETE"
            and current["selected_item"] == NEXT_ITEM
            and current_by_id[NEXT_ITEM]["status"] == "READY",
            "current queue does not close this item and select its successor")
    current_assurance = json.loads((root / "results/assurance/current.json").read_text())
    pending = current_assurance["mutation_testing"]["pending_survivor_triage"]
    require(pending["count"] == 3 and GE_MUTANT in pending["mutant_ids"]
            and NEG_MUTANT not in pending["mutant_ids"]
            and current_assurance["mutation_testing"]["meaningful_survivors"] == 4
            and current_assurance["mutation_testing"]["equivalent_mutants"] == 14,
            "current assurance did not apply the split thread classification")
    report = json.loads(
        (root / "results/assurance/current-mutation-report.json").read_text()
    )
    require(report["classified_equivalent"] == 14
            and report["survived_without_witness"] == 3
            and report["meaningful_survivors"] == 4
            and report["modeled_mutation_score_denominator"] == 142
            and report["modeled_mutation_score"] == 135 / 142,
            "current mutation metrics disagree with the scoped admission")
    return {
        "status": "PASS", "historical_snapshot": SNAPSHOT,
        "historical_manifest_inputs": len(old_inputs),
        "registry_predecessor_lines": 609, "registry_successor_lines": 610,
        "current_successor": current["selected_item"],
        "pending_survivors": pending["count"],
        "meaningful_survivors": current_assurance["mutation_testing"]["meaningful_survivors"],
        "equivalent_mutants": current_assurance["mutation_testing"]["equivalent_mutants"],
    }
