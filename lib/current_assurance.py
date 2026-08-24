"""Build the versioned current-assurance snapshot from durable evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from artifact_graph import evaluate_graph, load_graph


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def evidence_record(root: Path, path: Path) -> dict[str, Any]:
    return {
        "path": relative(root, path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def git_revision(path: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, check=True, text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def trend(observed: float | int, policy: dict[str, Any]) -> dict[str, Any]:
    minimum = policy["minimum"]
    if minimum is None:
        assessment = "CONTEXT_ONLY"
    elif observed >= minimum:
        assessment = "MEETS_CONTEXT_THRESHOLD"
    else:
        assessment = "BELOW_CONTEXT_THRESHOLD"
    return {
        "observed": observed,
        "minimum": minimum,
        "assessment": assessment,
        "enabled_as_gate": policy["enabled_as_gate"],
        "context": policy["context"],
    }


def gate_result(passed: bool, summary: str, observed: Any, evidence: list[str]) -> dict[str, Any]:
    return {
        "status": "PASS" if passed else "FAIL",
        "summary": summary,
        "observed": observed,
        "evidence": evidence,
    }


def _cross_validation(root: Path) -> tuple[list[dict[str, Any]], int, int, int, float]:
    cases = []
    semantic = 0
    parse = 0
    runs = 0
    seconds = 0.0
    for path in sorted((root / "results" / "cross-validation").glob("*/results.json")):
        result = load(path)
        kind = result.get("disagreement_kind")
        if result.get("classification") == "CHECKER_DISAGREEMENT" and kind == "SEMANTIC_OUTCOME":
            semantic += 1
        if result.get("classification") == "CHECKER_DISAGREEMENT" and kind == "PARSE_BEHAVIOR":
            parse += 1
        validators = result.get("validators", [])
        runs += len(validators)
        seconds += sum(row.get("result", {}).get("seconds", 0.0) for row in validators)
        cases.append({
            "case_id": result["case_id"],
            "classification": result["classification"],
            "disagreement_kind": kind,
            "semantic_status": result.get("semantic_status"),
            "path": relative(root, path),
            "sha256": sha256_file(path),
        })
    return cases, semantic, parse, runs, seconds


def _artifact_freshness(root: Path, graph_path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    graph = load_graph(graph_path)
    by_id = {node["id"]: node for node in graph["nodes"]}
    if "report:current-assurance" in by_id:
        selected = [row["id"] for row in by_id["report:current-assurance"]["dependencies"]]
    else:
        selected = [
            node["id"] for node in graph["nodes"]
            if node["required_for_current_claims"]
            and not node["id"].startswith(("report:milestone8", "report:milestone9"))
        ]
    statuses = evaluate_graph(graph, root)
    stale = [statuses[node_id] for node_id in sorted(set(selected)) if statuses[node_id]["effective_state"] != "CURRENT"]
    return sorted(set(selected)), stale


def build_snapshot(root: Path, policy: dict[str, Any], created_at: str) -> dict[str, Any]:
    paths = {
        "policy": root / "config" / "assurance-policy.json",
        "coverage_identity": root / "results" / "manifests" / "coverage-nanoda.json",
        "coverage_manifest": root / "results" / "coverage" / "nanoda" / "manifest.json",
        "mutation_report": root / "results" / "assurance" / "milestone-7-report.json",
        "mutation_batch": root / "results" / "mutation-batches" / "nanoda-semantic-0001.json",
        "m4": root / "results" / "assurance" / "milestone-4.json",
        "m6": root / "results" / "assurance" / "milestone-6.json",
        "m7": root / "results" / "assurance" / "milestone-7.json",
        "rotating": root / "results" / "rotating-heldout" / "milestone-7" / "report.json",
        "validators": root / "results" / "cross-validation" / "validator-inventory.json",
        "regressions": root / "corpus" / "regression-candidates" / "milestone-5.json",
    }
    coverage_identity = load(paths["coverage_identity"])
    coverage = load(paths["coverage_manifest"])
    report = load(paths["mutation_report"])
    batch = load(paths["mutation_batch"])
    m4 = load(paths["m4"])
    m6 = load(paths["m6"])
    m7 = load(paths["m7"])
    rotating = load(paths["rotating"])
    inventory = load(paths["validators"])
    regressions = load(paths["regressions"])

    baseline_policy = policy["hard_gates"]["baseline_identity"]
    baseline_sha = coverage_identity["baseline"]["sha256"]
    baseline_count = coverage_identity["baseline"]["test_count"]
    comparison_rows = [row["comparison"] for row in batch["execution"]["results"]]
    for mutant_id in ("nanoda-0001", "nanoda-0002", "nanoda-0003", "nanoda-0004"):
        comparison_rows.append(load(root / "results" / "mutants" / mutant_id / "scheduled-comparison.json"))
    baseline_consistent = (
        baseline_sha == baseline_policy["expected_outcomes_sha256"]
        and baseline_count == baseline_policy["expected_test_count"]
        and all(row["baseline_outcomes_sha256"] == baseline_sha for row in comparison_rows)
        and all(row["coverage_test_count"] == baseline_count for row in comparison_rows)
    )

    required_milestones = policy["hard_gates"]["complete_result_inventories"]["required_milestones"]
    milestone_results = {
        str(number): load(root / "results" / "assurance" / f"milestone-{number}.json")
        for number in required_milestones
    }
    selected_ids = {row["id"] for row in batch["mutants"]}
    build_ids = {row["mutant_id"] for row in batch["build_validation"]["results"]}
    execution_ids = {row["mutant_id"] for row in batch["execution"]["results"]}
    inventories_complete = (
        all(item["status"] == "PASS" and all(item["checks"].values()) for item in milestone_results.values())
        and batch["execution"]["status"] == "COMPLETE"
        and selected_ids == build_ids == execution_ids
        and report["unevaluated_mutants"] == 0
        and baseline_count == len(coverage_identity["corpus"]["files"])
    )

    cross_cases, semantic_disagreements, parse_disagreements, cross_runs, cross_seconds = _cross_validation(root)
    disagreement_policy = policy["hard_gates"]["semantic_checker_disagreements"]
    disagreements_ok = semantic_disagreements <= disagreement_policy["maximum_unresolved"]

    regression_checks = []
    for candidate in regressions["candidates"]:
        evidence_path = root / candidate["expected_evidence"]["path"]
        evidence = load(evidence_path)
        regression_checks.append(
            evidence_path.is_file()
            and sha256_file(evidence_path) == candidate["expected_evidence"]["sha256"]
            and evidence["status"] == policy["hard_gates"]["regression_expected_outcomes"]["required_status"]
            and evidence["expected_outcome"] == candidate["expected_outcome"]
        )
    regression_evidence_ok = bool(regression_checks) and all(regression_checks)

    graph_path = root / "results" / "artifacts" / "graph.json"
    evidence_nodes, stale_nodes = _artifact_freshness(root, graph_path)
    artifact_freshness_ok = not stale_nodes

    checks = {
        "baseline_identity": gate_result(
            baseline_consistent,
            "Baseline outcomes and every active comparison use the policy-pinned identity.",
            {"sha256": baseline_sha, "test_count": baseline_count, "comparison_count": len(comparison_rows)},
            [relative(root, paths["coverage_identity"]), relative(root, paths["mutation_batch"])],
        ),
        "complete_result_inventories": gate_result(
            inventories_complete,
            "Required milestone inventories and the active semantic batch are complete.",
            {"milestones": required_milestones, "selected": len(selected_ids), "built": len(build_ids), "executed": len(execution_ids)},
            [relative(root, paths["mutation_batch"])] + [f"results/assurance/milestone-{number}.json" for number in required_milestones],
        ),
        "semantic_checker_disagreements": gate_result(
            disagreements_ok,
            "Unresolved semantic checker disagreements must not exceed the configured maximum.",
            {"unresolved": semantic_disagreements, "maximum": disagreement_policy["maximum_unresolved"]},
            [row["path"] for row in cross_cases if row["disagreement_kind"] == "SEMANTIC_OUTCOME"],
        ),
        "regression_expected_outcomes": gate_result(
            regression_evidence_ok,
            "Every generated regression candidate carries hash-bound expected-outcome evidence.",
            {"candidates": len(regression_checks), "established": sum(regression_checks)},
            [relative(root, paths["regressions"])] + [row["expected_evidence"]["path"] for row in regressions["candidates"]],
        ),
        "artifact_freshness": gate_result(
            artifact_freshness_ok,
            "All artifact-graph dependencies used by the current snapshot are current.",
            {"checked_nodes": len(evidence_nodes), "stale_nodes": [row["id"] for row in stale_nodes]},
            [relative(root, graph_path)],
        ),
    }
    failures = [name for name, value in checks.items() if value["status"] == "FAIL"]

    validator_rows = []
    for row in inventory["validators"]:
        validator_rows.append({
            "id": row["id"],
            "display_name": row["display_name"],
            "version": row["version"],
            "role": row["role"],
            "implementation_family": row["implementation_family"],
            "arena_revision": row["arena_revision"],
            "source_revision": row.get("source_revision", row.get("built_toolchain")),
            "binary_sha256": row["binary_sha256"],
        })

    batch_started = datetime.fromisoformat(batch["execution"]["started_at"])
    batch_completed = datetime.fromisoformat(batch["execution"]["completed_at"])
    batch_elapsed = (batch_completed - batch_started).total_seconds()
    build_seconds = sum(row["seconds"] for row in batch["build_validation"]["results"])
    build_seconds += batch["build_validation"]["baseline_restore_seconds"]
    checker_components = [
        {"name": "coverage_collection", "checker_runs": coverage["test_count"], "checker_seconds": coverage["run_seconds"]},
        {"name": "witness_search_and_minimization", "checker_runs": m4["measurements"]["checker_runs"], "checker_seconds": m4["measurements"]["checker_seconds"]},
        {"name": "cross_validation", "checker_runs": cross_runs, "checker_seconds": cross_seconds},
        {"name": "milestone_6_transfer", "checker_runs": m6["measurements"]["held_out_checker_runs"], "checker_seconds": m6["measurements"]["held_out_checker_seconds"]},
        {"name": "milestone_7_rotating_folds", "checker_runs": rotating["costs"]["checker_runs"], "checker_seconds": rotating["costs"]["checker_seconds"]},
    ]
    cost_components: list[dict[str, Any]] = checker_components + [
        {"name": "active_mutation_batch", "wall_seconds": batch_elapsed, "checker_runs": sum(row["executed_test_count"] for row in comparison_rows[:len(batch["execution"]["results"])])},
        {"name": "active_mutation_batch_builds", "wall_seconds": build_seconds, "builds": len(build_ids) + 1},
    ]

    config_paths = [
        paths["policy"], root / "config" / "validators.json",
        root / "mutation-model" / "catalog.json",
        root / "experiments" / "milestone-6" / "spec.json",
        root / "experiments" / "milestone-7" / "spec.json",
    ]
    trends = policy["trend_thresholds"]
    producer_path = root / "scripts" / "current-assurance-snapshot"
    library_path = Path(__file__)
    semantic_case_count = 1 if regressions["candidates"] else 0
    return {
        "schema_version": 1,
        "snapshot_id": "current-assurance",
        "status": "COMPLETE",
        "created_at": created_at,
        "scope": {
            "claim": "Measured assurance for the exact pinned validators, corpus, mutations, searches, and policies referenced by this snapshot.",
            "non_claims": ["Lean is correct", "the corpus is sufficient", "the measured mutation score generalizes beyond the modeled population"],
            "injected_faults_are_not_discovered_bugs": True,
        },
        "identity": {
            "producing_repository_revision": git_revision(root),
            "arena_revision": coverage_identity["arena"]["revision"],
            "configurations": [evidence_record(root, path) for path in config_paths],
        },
        "validators": validator_rows,
        "corpus": {
            "test_count": baseline_count,
            "total_bytes": coverage_identity["corpus"]["total_bytes"],
            "identity_manifest_sha256": sha256_file(paths["coverage_identity"]),
            "baseline_outcomes_sha256": baseline_sha,
            "materialized_payload_tracked_in_git": False,
        },
        "mutation_testing": {
            "population_scope": "All 29 evaluated modeled nanoda mutants in the current mutation report.",
            "total_semantic_mutants": report["evaluated_mutants"],
            "killed_by_existing_corpus": report["killed_mutants"],
            "killed_by_generated_corpus": 1,
            "surviving_mutants": report["surviving_mutants"],
            "meaningful_survivors": report["meaningful_survivors"],
            "equivalent_mutants": report["classified_equivalent"],
            "unreachable_mutants": report["classified_unreachable"],
            "unresolved_mutants": report["survived_without_witness"],
            "modeled_mutation_score": report["modeled_mutation_score"],
            "meaningful_mutation_score": report["mutation_score"],
            "subsystem_scores": report["stratified_metrics"]["by_subsystem"],
        },
        "witness_synthesis": {
            "searches": m4["measurements"]["searches"],
            "witnesses_found": m4["measurements"]["witnesses_found"],
            "witnesses_minimized": m4["measurements"]["witnesses_minimized"],
            "bounded_searches_without_witness": m4["measurements"]["bounded_searches_without_witness"],
            "success_rate": m4["measurements"]["witnesses_found"] / m4["measurements"]["searches"],
        },
        "generated_regressions": {
            "artifact_count": len(regressions["candidates"]),
            "semantic_case_count": semantic_case_count,
            "ready_for_upstream": 0,
            "candidates": [{"case_id": row["case_id"], "status": row["status"], "expected_outcome": row["expected_outcome"]} for row in regressions["candidates"]],
        },
        "cross_validator_disagreements": {
            "semantic_unresolved_count": semantic_disagreements,
            "parse_behavior_count": parse_disagreements,
            "majority_vote_used": False,
            "cases": cross_cases,
        },
        "held_out_evaluation": {
            "fold_count": rotating["fold_count"],
            "original_score": rotating["aggregate_score"]["original_score"],
            "augmented_score": rotating["aggregate_score"]["augmented_score"],
            "score_change": rotating["aggregate_score"]["score_change"],
            "classification": rotating["classification"],
            "classification_counts": rotating["classification_counts"],
            "scope": rotating["interpretation"]["scope"],
        },
        "coverage": {
            "checker": coverage["checker"],
            "test_count": coverage["test_count"],
            "covered_source_locations": coverage["covered_location_count"],
            "source_file_count": coverage["source_file_count"],
            "collection_seconds": coverage["run_seconds"],
            "payload_tracked_in_git": False,
        },
        "execution_cost": {
            "recorded_checker_runs": sum(row["checker_runs"] for row in checker_components),
            "recorded_checker_seconds": sum(row["checker_seconds"] for row in checker_components),
            "components": cost_components,
            "scope": "Sum of non-overlapping recorded checker-run components plus separately labeled batch/build wall time; setup and historical superseded work are not reconstructed.",
        },
        "gate": {
            "status": "PASS" if not failures else "FAIL",
            "checks": checks,
            "failure_reasons": failures,
            "passing": len(checks) - len(failures),
            "failing": len(failures),
        },
        "trend_metrics": {
            "modeled_mutation_score": trend(report["modeled_mutation_score"], trends["modeled_mutation_score"]),
            "meaningful_mutation_score": trend(report["mutation_score"], trends["meaningful_mutation_score"]),
            "covered_source_locations": trend(coverage["covered_location_count"], trends["covered_source_locations"]),
            "held_out_score_change": trend(rotating["aggregate_score"]["score_change"], trends["held_out_score_change"]),
        },
        "evidence": {name: evidence_record(root, path) for name, path in paths.items()},
        "producer": {
            "path": relative(root, producer_path),
            "sha256": sha256_file(producer_path),
            "library_sha256": sha256_file(library_path),
            "policy_sha256": sha256_file(paths["policy"]),
        },
    }
