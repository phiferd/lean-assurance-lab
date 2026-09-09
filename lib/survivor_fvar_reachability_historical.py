"""Validate the fvar admission across its exact entry snapshot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from lib.research_queue_v3 import load_queue


ITEM = "SURVIVOR-FVAR-REACHABILITY-1"
MUTANT = "nanoda-gen-399895fa0b72"
SNAPSHOT = "4cea69c0b66487b82596c47c917b1d58af057a45"
UNIVERSE_CLOSURE_SNAPSHOT = "70de72f54c520fad89ed023204163d1cc3e76c5b"
TRANSITION = f"results/research/survivor-fvar-reachability-1/historical-transition.json"
REGISTRY = "results/mutants/registry.jsonl"
INVENTORY = "results/survivors/inventory.jsonl"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(root: Path, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{SNAPSHOT}:{path}"], cwd=root)


def universe_bytes(root: Path, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{UNIVERSE_CLOSURE_SNAPSHOT}:{path}"], cwd=root
    )


def validate(root: Path) -> dict:
    root = root.resolve()
    transition = json.loads((root / TRANSITION).read_text(encoding="utf-8"))
    fields = {
        "schema_version", "item_id", "transition", "historical_snapshot",
        "historical_queue", "historical_status", "historical_universe_manifest",
        "historical_work_record", "predecessor_registry", "entry_assurance",
        "survivor_inventory", "evolved_live_tooling", "live_expectation", "claim",
    }
    require(set(transition) == fields and transition["schema_version"] == 1
            and transition["item_id"] == ITEM
            and transition["transition"]
            == "PUBLIC_EXPORT_FVAR_EXCLUSION_TO_SCOPED_EQUIVALENT_ADMISSION"
            and transition["historical_snapshot"] in {"4cea69c", SNAPSHOT},
            "historical transition identity drift")
    for key in ("historical_queue", "historical_status",
                "historical_universe_manifest", "historical_work_record"):
        row = transition[key]
        require(set(row) == {"path", "sha256"}
                and digest(git_bytes(root, row["path"])) == row["sha256"],
                "historical snapshot binding drift: " + key)

    old_registry = git_bytes(root, REGISTRY)
    predecessor = transition["predecessor_registry"]
    require(predecessor == {
        "path": REGISTRY, "lines": 608,
        "sha256": "2ba8a9a640d994e4ee90fe78f58896c0735a2bbebce4db75eab8dfcee6a09961",
    } and len(old_registry.splitlines()) == 608
      and digest(old_registry) == predecessor["sha256"],
      "registry predecessor binding drift")
    old_inventory = git_bytes(root, INVENTORY)
    inventory = transition["survivor_inventory"]
    require(inventory == {
        "path": INVENTORY, "lines": 1,
        "sha256": "c7e552e761f128e9911abeb6cc85cf1d4b7c48d6ed03798d574a0ace688f2458",
    } and len(old_inventory.splitlines()) == 1
      and digest(old_inventory) == inventory["sha256"],
      "survivor inventory predecessor drift")

    old_queue = json.loads(git_bytes(root, "config/research-queue.json"))
    old_by_id = {item["id"]: item for item in old_queue["items"]}
    require(old_queue["selected_item"] == ITEM and old_by_id[ITEM]["status"] == "ACTIVE"
            and old_by_id["SURVIVOR-UNIVERSE-EQUIVALENCE-1"]["status"] == "COMPLETE",
            "entry queue was not the committed active state")
    old_assurance = json.loads(git_bytes(root, "results/assurance/current.json"))
    old_pending = old_assurance["mutation_testing"]["pending_survivor_triage"]
    entry = transition["entry_assurance"]
    require(entry["path"] == "results/assurance/current.json"
            and digest(git_bytes(root, entry["path"])) == entry["sha256"]
            and entry["pending_survivors"] == old_pending["count"] == 5
            and entry["equivalent_mutants"]
            == old_assurance["mutation_testing"]["equivalent_mutants"] == 13
            and MUTANT in old_pending["mutant_ids"],
            "entry assurance did not retain the pending fvar survivor")

    old_manifest_row = transition["historical_universe_manifest"]
    old_manifest = json.loads(git_bytes(root, old_manifest_row["path"]))
    require(old_manifest["item_id"] == "SURVIVOR-UNIVERSE-EQUIVALENCE-1"
            and old_manifest["status"] == "PASS", "wrong predecessor manifest")
    old_inputs = {row["path"]: row for row in old_manifest["inputs"]}
    for path, row in old_inputs.items():
        data = universe_bytes(root, path)
        require(len(data) == row["bytes"] and digest(data) == row["sha256"],
                "historical universe-equivalence input drift: " + path)
    evolved = transition["evolved_live_tooling"]
    require(len(evolved) == 9, "evolved tooling inventory drift")
    for row in evolved:
        require(set(row) == {"path", "historical_sha256", "reason"}
                and row["path"] in old_inputs
                and digest(universe_bytes(root, row["path"]))
                == row["historical_sha256"] == old_inputs[row["path"]]["sha256"]
                and isinstance(row["reason"], str) and row["reason"],
                "evolved tooling lacks exact historical binding")

    expectation = transition["live_expectation"]
    require(expectation == {
        "completed_item": ITEM,
        "selected_item": "SURVIVOR-THREAD-CONFIG-REACHABILITY-1",
        "registry_append_count": 1,
        "registry_classification": "EQUIVALENT",
        "pending_survivors_before": 5,
        "pending_survivors_after": 4,
        "equivalent_mutants_before": 13,
        "equivalent_mutants_after": 14,
        "survivor_inventory_changed": False,
    }, "live transition expectation drift")
    current_registry = (root / REGISTRY).read_bytes()
    require(current_registry.startswith(old_registry)
            and len(current_registry.splitlines()) >= 609,
            "current registry no longer preserves the exact fvar append")
    appended = json.loads(
        current_registry[len(old_registry):].splitlines(keepends=True)[0].decode("utf-8")
    )
    require(appended["id"] == MUTANT and appended["status"] == "SURVIVED"
            and appended["classification"] == expectation["registry_classification"],
            "current registry append classification drift")
    require((root / INVENTORY).read_bytes() == old_inventory,
            "current survivor inventory changed")

    current = load_queue(root, require_ready=True)
    current_by_id = {item["id"]: item for item in current["items"]}
    require(current_by_id["SURVIVOR-UNIVERSE-EQUIVALENCE-1"]["closure"]
            == old_by_id["SURVIVOR-UNIVERSE-EQUIVALENCE-1"]["closure"],
            "predecessor queue closure changed")
    require(current_by_id[ITEM]["status"] == "COMPLETE"
            and current_by_id[expectation["selected_item"]]["status"] == "COMPLETE"
            and current_by_id["SURVIVOR-THREAD-CONFIG-REGRESSION-1"]["status"] == "COMPLETE"
            and current_by_id[current["selected_item"]]["status"] in {"READY", "ACTIVE"},
            "current queue does not preserve and advance the fvar successor")
    current_assurance = json.loads((root / "results/assurance/current.json").read_text())
    pending = current_assurance["mutation_testing"]["pending_survivor_triage"]
    require(pending["count"] == 2 and MUTANT not in pending["mutant_ids"]
            and "nanoda-gen-93b21593b0d8" not in pending["mutant_ids"]
            and "nanoda-gen-af1dac9744e9" not in pending["mutant_ids"]
            and current_assurance["mutation_testing"]["equivalent_mutants"] == 14
            and current_assurance["mutation_testing"]["meaningful_survivors"] == 5,
            "current assurance did not admit scoped fvar equivalence")
    report = json.loads(
        (root / "results/assurance/current-mutation-report.json").read_text()
    )
    require(report["classified_equivalent"] == 14
            and report["survived_without_witness"] == 2
            and report["meaningful_survivors"] == 5
            and report["modeled_mutation_score_denominator"] == 142
            and report["modeled_mutation_score"] == 135 / 142,
            "current mutation report metrics disagree with the one-row admission")
    return {
        "status": "PASS", "historical_snapshot": SNAPSHOT,
        "historical_manifest_inputs": len(old_inputs),
        "registry_predecessor_lines": 608,
        "registry_successor_lines": len(current_registry.splitlines()),
        "current_successor": current["selected_item"],
        "current_successor_status": current_by_id[current["selected_item"]]["status"],
        "pending_survivors": pending["count"],
        "equivalent_mutants": current_assurance["mutation_testing"]["equivalent_mutants"],
    }
