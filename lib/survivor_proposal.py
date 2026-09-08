"""Pure checks for the fixed, unexecuted ALT-SURVIVORS planning artifact.

This validates a proposal, never an execution authorization. Runtime binaries
are metadata-only here; their materialization and derivation are future gates.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from lib.portable_coverage import source_digest

ROOT = Path(__file__).resolve().parents[1]
BASE = "results/research/alt-survivors-2026-09-08"
SELECTED = "nanoda-gen-9face4e6a6f7"
PRIOR = "nanoda-gen-21ef4d1d32a1"
PLANNING_FRONTIER = "F-SURVIVOR-TRIAGE-PROPOSAL"
HISTORICAL_CLASSIFICATION_INPUTS = ["results/mutants/registry.jsonl", "results/survivors/inventory.jsonl"]
LIMITS = {
    "active_seconds": 5400, "interval_seconds": 5400,
    "offline_build_reservations": 2, "per_build_seconds": 120,
    "checker_reservations": 8, "per_checker_seconds": 30, "fixed_pairs": 1,
    "max_scientific_byte_variants": 0, "research_network_requests": 0,
    "proof_launches": 0, "external_research_actions": 0,
}
MATRIX = [
    {"order": 1, "id": "control-baseline", "input": "control", "observer": "baseline"},
    {"order": 2, "id": "control-mutant", "input": "control", "observer": "selected_mutant"},
    {"order": 3, "id": "candidate-baseline", "input": "candidate", "observer": "baseline"},
    {"order": 4, "id": "candidate-mutant", "input": "candidate", "observer": "selected_mutant"},
]
PROPOSAL_FIELDS = set("schema_version kind proposal_id planning_item proposed_item proposed_run "
    "execution_authorized launch_ready approval_scope selected_mutant mutation_spec source_lock "
    "control candidate pair_count baseline selected_binary question hypotheses matrix limits "
    "limit_rationale output_root isolated_build_root configuration build_plan tooling_reuse "
    "prelaunch_gates outcomes attribution stopping_rules historical_constraints closure_requirements "
    "scientific_variant_scope historical_official_result".split())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe(root, name):
    require(isinstance(name, str) and name and not Path(name).is_absolute()
            and ".." not in Path(name).parts, "unsafe evidence path")
    path = Path(root)
    for part in Path(name).parts:
        path /= part
        require(not path.is_symlink(), "symlink evidence refused")
    require(path.is_file(), "missing evidence: " + name)
    return path


def load(root, name):
    return json.loads(safe(root, name).read_text())


def binding(root, row):
    require(isinstance(row, dict) and set(row) == {"path", "bytes", "sha256"},
            "malformed input binding")
    require(type(row["bytes"]) is int and row["bytes"] >= 0, "malformed input size")
    path = safe(root, row["path"])
    payload = path.read_bytes()
    require(len(payload) == row["bytes"] and hashlib.sha256(payload).hexdigest() == row["sha256"],
            "input drift: " + row["path"])
    return path


def _validate(root):
    root = Path(root).resolve()
    read = lambda name: load(root, BASE + "/" + name + ".json")
    inventory, lock, review = (read(n) for n in ("inventory", "source-lock", "source-review"))
    proposal, evidence, entry, work, reuse = (read(n) for n in
        ("execution-proposal", "evidence-manifest", "entry-decision", "work-record", "reuse-assessment"))
    require(set(evidence) == {"schema_version", "item_id", "inputs", "note"}
            and evidence["schema_version"] == 1 and evidence["item_id"] == "ALT-SURVIVORS",
            "wrong evidence manifest")
    bound = {}
    for row in evidence["inputs"]:
        binding(root, row)
        require(row["path"] not in bound, "duplicate evidence binding")
        bound[row["path"]] = row
    require(len(bound) > 0, "empty evidence manifest")
    required_bindings = {"config/authorized-runs/triage.json", "lib/portable_coverage.py",
        *(BASE + "/evidence/historical/" + name for name in HISTORICAL_CLASSIFICATION_INPUTS)}
    require(required_bindings <= set(bound), "required historical/tooling bindings missing")

    snapshot = json.loads(binding(root, inventory["assurance_snapshot"]).read_text())
    pending = snapshot["mutation_testing"]["pending_survivor_triage"]
    require(inventory["pending_ids"] == pending["mutant_ids"] and inventory["count"] == pending["count"] == 7
            and inventory["classification"] == pending["classification"] == "SURVIVED_WITHOUT_WITNESS",
            "pending inventory differs from canonical snapshot")
    rows = inventory["entries"]
    require(len(rows) == 7 and [r["rank"] for r in rows] == list(range(1, 8))
            and sorted(r["mutant_id"] for r in rows) == inventory["pending_ids"],
            "inventory must project all seven distinct pending members")
    require(inventory["selected_mutant"] == SELECTED
            and [r["mutant_id"] for r in rows if r["selected"] is True] == [SELECTED]
            and all(type(r["selected"]) is bool for r in rows), "exact single selection required")
    registry_path = BASE + "/evidence/historical/results/mutants/registry.jsonl"
    registry = {}
    for line in safe(root, registry_path).read_text().splitlines():
        row = json.loads(line)
        registry.setdefault(row["id"], {}).update(row)
    require(sorted(k for k, v in registry.items() if v.get("classification") == "SURVIVED_WITHOUT_WITNESS")
            == inventory["pending_ids"], "historical registry pending membership differs")
    selected_spec = None
    for row in rows:
        spec = json.loads(binding(root, row["spec"]).read_text())
        comparison = json.loads(binding(root, row["comparison"]).read_text())
        require(row["spec"] == bound.get(row["spec"]["path"])
                and row["comparison"] == bound.get(row["comparison"]["path"]), "inventory inputs not locked")
        expected = {"source_file": spec["source_file"], "source_line": int(spec["source_span"]),
            "function": spec["function"], "original": spec["original"], "mutated": spec["mutated"],
            "operator": spec["mutation_operator"], "replace_occurrence": spec["replace_occurrence"],
            "covering_tests_executed": comparison["executed_test_count"],
            "prior_outcome": comparison["status"], "prior_difference_count": comparison["difference_count"]}
        require(all(row[k] == v for k, v in expected.items()), "inventory spec/comparison projection differs")
        require(spec["id"] == comparison["mutant_id"] == row["mutant_id"]
                and comparison["mutation_spec_sha256"] == row["spec"]["sha256"]
                and comparison["source_sha256"] == lock["source_tree_sha256"]
                and comparison["status"] == "SURVIVED" and comparison["difference_count"] == 0,
                "inventory identity or old survivor evidence differs")
        identity = hashlib.sha256("\0".join([spec["source_file"], spec["source_span"],
            str(spec["source_column"]), spec["mutation_operator"], spec["original"], spec["mutated"]]).encode()).hexdigest()
        require(identity == spec["identity"]["sha256"] and spec["id"] == "nanoda-gen-" + identity[:12],
                "mutation identity mismatch")
        if spec["id"] == SELECTED:
            selected_spec = spec

    old_manifest = load(root, "config/authorized-runs/triage.json")
    donors = {r["path"]: r for r in old_manifest["inputs"]}
    paths = []
    for row in lock["files"]:
        path = binding(root, row["binding"])
        require(row["binding"] == bound.get(row["binding"]["path"]), "source binding not locked")
        donor = donors[row["donor"]]
        require(row["binding"]["path"] == BASE + "/evidence/pinned-nanoda/" + row["source_path"]
                and row["donor"] == "external/ecosystem-triage-nanoda/" + row["source_path"]
                and all(row["binding"][k] == donor[k] for k in ("bytes", "sha256")),
                "copied source differs from historical binding")
        paths.append(path.relative_to(root / BASE / "evidence/pinned-nanoda").as_posix())
    tree = root / BASE / "evidence/pinned-nanoda"
    actual = sorted(p.relative_to(tree).as_posix() for p in tree.rglob("*") if p.is_file())
    require(sorted(paths) == actual and len(set(paths)) == len(paths), "source inventory is not exact")
    require(source_digest(tree) == lock["source_tree_sha256"]
            and lock["revision"] == "6ae1f0cd962f081f6c423454c5da729d841236a7"
            and lock["mutation_materialized"] is False, "source digest/revision or materialization differs")

    prior_spec = json.loads(binding(root, review["prior_spec"]).read_text())
    require(review["selected_spec"] == proposal["mutation_spec"]
            and json.loads(binding(root, review["selected_spec"]).read_text()) == selected_spec,
            "selected source review identity differs")
    source = binding(root, review["source"]).read_text()
    require(prior_spec["id"] == PRIOR and review["prior_mutant_id"] == PRIOR
            and all(selected_spec[k] == prior_spec[k] for k in
                ("source_file", "source_span", "source_column", "replace_occurrence", "original"))
            and selected_spec["source_span"] == "649" and selected_spec["replace_occurrence"] == 1
            and selected_spec["original"] == "flag == Check"
            and selected_spec["mutated"] == "!(flag == Check)"
            and prior_spec["mutated"] == "(flag != Check)", "distinct same-site mutation relationship changed")
    locations = [i + 1 for i, line in enumerate(source.splitlines()) if selected_spec["original"] in line]
    require(locations[selected_spec["replace_occurrence"]] == int(selected_spec["source_span"]),
            "mutation occurrence does not locate the bound line")
    require(review["selected_on_reused_pair"] == "NOT_EXECUTED"
            and review["selected_binary"]["status"] == "NOT_RETAINED_OR_ATTRIBUTED", "alias outcome attribution refused")
    old_run = json.loads(binding(root, review["selected_old_run"]).read_text())
    require(old_run["mutant_id"] == SELECTED and review["prior_costs_preserved"] == old_run["steps"],
            "historical selected costs changed")
    observations = json.loads(binding(root, review["prior_observations"]).read_text())
    require(review["prior_complete_result"] == proposal["historical_official_result"],
            "historical official scope binding differs")
    complete_prior = json.loads(binding(root, proposal["historical_official_result"]).read_text())
    require(complete_prior["mutant_id"] == PRIOR
            and complete_prior["official_control"]["outcome"] == "ACCEPT"
            and complete_prior["official_candidate"]["outcome"] == "REJECT", "historical official result changed")
    require(review["prior_outcomes"] == [{"artifact": r["name"], "baseline": r["baseline"]["outcome"],
            "prior_mutant": r["mutant"]["outcome"]} for r in observations], "prior outcomes misreported")
    for role, old in zip(("control", "candidate"), observations):
        path = binding(root, proposal[role])
        require(proposal[role] == bound.get(proposal[role]["path"])
                and path.read_bytes() == binding(root, old["baseline"]["artifact"]).read_bytes()
                == binding(root, old["mutant"]["artifact"]).read_bytes(), "reused pair bytes changed")

    require(set(proposal) == PROPOSAL_FIELDS and proposal["schema_version"] == 1
            and proposal["kind"] == "FIXED_SURVIVOR_EXECUTION_PROPOSAL", "malformed execution proposal")
    require(proposal["execution_authorized"] is False and proposal["launch_ready"] is False
            and proposal["selected_binary"] is None, "proposal must remain nonexecutable and unattributed")
    require(proposal["selected_mutant"] == SELECTED and proposal["planning_item"] == "ALT-SURVIVORS"
            and proposal["proposed_item"] == "SURVIVOR-LET-REUSE-1"
            and proposal["pair_count"] == 1 and proposal["limits"] == LIMITS, "fixed proposal limits/identity changed")
    require(all(type(v) is int for v in proposal["limits"].values()), "noninteger limit")
    variants = proposal["scientific_variant_scope"]
    require(set(variants) == {"max_scientific_byte_variants_means", "fixed_mutant_source_materializations", "source_materialization"}
            and type(variants["fixed_mutant_source_materializations"]) is int
            and variants["fixed_mutant_source_materializations"] == 1,
            "exactly one future fixed mutant source materialization required")
    require(proposal["matrix"] == MATRIX, "fixed controls-first matrix changed")
    require(proposal["hypotheses"] == {"control_baseline": "ACCEPT", "control_selected_mutant": "ACCEPT",
        "candidate_baseline": "TYPECHECK_REFUSAL_AT_LET_VALUE_TYPE", "candidate_selected_mutant": "ACCEPT"},
        "fixed hypotheses changed")
    require(proposal["baseline"] == observations[0]["baseline"]["binary"], "baseline metadata differs")
    require(json.loads(binding(root, proposal["source_lock"]).read_text()) == lock, "source lock differs")
    require([g["id"] for g in proposal["prelaunch_gates"]] == [f"G{i}" for i in range(1, 8)]
            and all(set(g) == {"id", "condition"} and isinstance(g["condition"], str)
                    and g["condition"].strip() for g in proposal["prelaunch_gates"]), "seven prelaunch gates required")
    require(proposal["historical_constraints"] == {"old_runs_terminal": True, "old_budgets_reset": False,
        "prior_unknown_costs_unchanged": True, "cvc_observer_reservations_consumed": 16,
        "semantic_classification_transferred_from_alias": False}, "historical attribution/cost constraint changed")
    config = proposal["configuration"]
    binding(root, config["base"])
    require(config["base"] == bound.get("config/ecosystem-nanoda.json")
            and config["new_config_files_created"] is False and config["preserve_all_other_settings"] is True
            and config["allowed_adapter_changes"] == {"use_stdin": False, "export_file_path":
                "Exact committed absolute path to the selected control or candidate", "print_axioms": False},
            "configuration adapter scope changed")
    build = proposal["build_plan"]
    require(build["command"] == ["cargo", "build", "--release", "--locked", "--offline"]
            and build["network"] == "forbidden" and build["cwd"] == proposal["isolated_build_root"]
            == "external/survivor-let-reuse-0001-nanoda"
            and build["target_dir"] == "external/survivor-let-reuse-0001-target"
            and proposal["output_root"] == "results/research/survivor-let-reuse-1/run-0001", "build/output isolation changed")

    require(work["budget"] == {"max_active_seconds": 5400, "max_interval_seconds": 5400,
        "checker_launches": 0, "proof_builds": 0, "setup_builds": 0,
        "scientific_byte_variants": 0, "research_network_requests": 0}, "planning scope changed")
    for row in work["entry_bindings"]:
        binding(root, {"path": row["snapshot"], "bytes": row["bytes"], "sha256": row["sha256"]})
    before = load(root, entry["before_queue"])
    require(entry["retired_placeholder"] == next(i for i in before["items"] if i["id"] == "CVC-NEXT-AUTHORIZATION")
            and entry["completed_items"] == [] and entry["active_item"] == "ALT-SURVIVORS",
            "owner decision must preserve the unexecuted placeholder")
    require(reuse["decision"] == "REUSE" and reuse["research_network_requests"] == 0
            and reuse["external_action"]["disposition"] == "NO_EXTERNAL_ACTION", "reuse scope changed")
    result = read("result")
    require(result["schema_version"] == 1 and result["item_id"] == "ALT-SURVIVORS"
            and result["outcome"] == "SUCCESS" and result["scientific_status"] == "FIXED_EXECUTION_PROPOSAL_ONLY"
            and result["selected_mutant"] == SELECTED, "result must claim only the fixed planning outcome")
    require(result["research_counts"] == dict.fromkeys(("checker_launches", "proof_builds", "setup_builds",
                "scientific_byte_variants", "research_network_requests", "external_research_actions"), 0)
            and all(type(v) is int for v in result["research_counts"].values()), "planning research counts must be zero")
    require(result["assurance_changes"] == {"new_observations": 0, "classifications_changed": 0,
        "pending_survivors": 7, "modeled_population_changed": False, "normative_source_promotions": 0},
        "planning result cannot promote assurance claims")
    require(result["completed_items"] == ["ALT-SURVIVORS"] and result["next_item_started"] is False
            and result["next_item"] == proposal["proposed_item"] and result["next_item_status"] == "WAITING",
            "planning result cannot complete or start a second item")
    # Check live no-change claims while this planning frontier controls work.
    # Later authorized execution must retain the proposal's historical meaning
    # while legitimately updating the current classification and denominator.
    current_queue = load(root, "config/research-queue.json")
    if current_queue["frontier_id"] == PLANNING_FRONTIER:
        current = load(root, "results/assurance/current.json")
        require(current["mutation_testing"] == snapshot["mutation_testing"], "planning changed canonical mutation classification")
        for name in HISTORICAL_CLASSIFICATION_INPUTS:
            require(safe(root, name).read_bytes() == safe(root, BASE + "/evidence/historical/" + name).read_bytes(),
                    "planning changed live classification input")
    return {"status": "PASS", "item_id": "ALT-SURVIVORS", "pending_survivors": 7,
            "selected_mutant": SELECTED, "execution_authorized": False, "checker_launches": 0}


def validate(root=ROOT):
    """Validate local planning evidence, requiring no ignored runtime payloads."""
    try:
        return _validate(root)
    except (KeyError, TypeError, IndexError, StopIteration) as error:
        raise ValueError("malformed survivor proposal: " + str(error)) from error
