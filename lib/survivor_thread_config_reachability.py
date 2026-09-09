"""Validate the public thread-configuration reachability closure."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ITEM = "SURVIVOR-THREAD-CONFIG-REACHABILITY-1"
GE_MUTANT = "nanoda-gen-2bdfe18a9ec2"
NEG_MUTANT = "nanoda-gen-93b21593b0d8"
ENTRY_SNAPSHOT = "336172a83fc6c2c8896aa107637f3a7924bea34a"
BASE = "results/research/survivor-thread-config-reachability-1"
ASSESSMENT = f"{BASE}/dispatch-assessment.json"
RESULT = f"{BASE}/result.json"
WORK_CLOSURE = f"{BASE}/work-closure.json"
FOCUSED_VALIDATION = f"{BASE}/focused-validation.json"
EVIDENCE_MANIFEST = f"{BASE}/evidence-manifest.json"
HISTORICAL_TRANSITION = f"{BASE}/historical-transition.json"
REGISTRY = "results/mutants/registry.jsonl"
INVENTORY = "results/survivors/inventory.jsonl"
NEXT_ITEM = "SURVIVOR-THREAD-CONFIG-REGRESSION-1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return digest(path.read_bytes())


def git_bytes(root: Path, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{ENTRY_SNAPSHOT}:{path}"], cwd=root
    )


def ordered(text: str, fragments: list[str], label: str) -> None:
    cursor = -1
    for fragment in fragments:
        position = text.find(fragment, cursor + 1)
        require(position >= 0, f"{label}: missing or reordered fragment: {fragment}")
        cursor = position


def json_lines(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines()]


def _validate_assessment(root: Path) -> dict:
    assessment = json.loads((root / ASSESSMENT).read_text(encoding="utf-8"))
    fields = {
        "schema_version", "item_id", "mutation_ids", "revision", "finding",
        "question", "scope", "public_configuration_path",
        "dispatch_truth_table", "task_coverage_proof", "checker_isolation",
        "failure_and_stack_boundary", "public_counterexample",
        "mutation_decisions", "supporting_observations", "decision",
        "execution_accounting", "evidence_bindings",
    }
    require(set(assessment) == fields and assessment["schema_version"] == 1,
            "dispatch assessment fields changed")
    require(
        assessment["item_id"] == ITEM
        and assessment["mutation_ids"] == [GE_MUTANT, NEG_MUTANT]
        and assessment["revision"]
        == "6ae1f0cd962f081f6c423454c5da729d841236a7"
        and assessment["finding"]
        == "PUBLIC_ZERO_THREAD_CHECK_ELISION_AND_ONE_THREAD_OPERATIONAL_BOUNDARY",
        "assessment identity or finding changed",
    )
    require(assessment["scope"]["semantic_authority"] is False
            and len(assessment["scope"]["excluded"]) == 4,
            "assessment scope was broadened")
    require([row["step"] for row in assessment["public_configuration_path"]] == [
        "CONFIG_DESERIALIZATION", "CONFIG_VALIDATION", "CONFIG_RETENTION",
        "PUBLIC_DISPATCH",
    ], "public configuration path changed")

    table = assessment["dispatch_truth_table"]
    require([(row["config_class"], row["representative"], row["baseline"],
              row["rel_gt_to_ge_mutant"], row["predicate_negation_mutant"])
             for row in table] == [
        ("ZERO", 0, "SERIAL", "SERIAL", "PARALLEL_ZERO_WORKERS"),
        ("ONE", 1, "SERIAL", "PARALLEL_ONE_WORKER", "PARALLEL_ONE_WORKER"),
        ("MANY", 2, "PARALLEL_N_WORKERS", "PARALLEL_N_WORKERS", "SERIAL"),
    ], "zero/one/many dispatch truth table changed")
    require(table[0]["distinction"] == "EXACT_SEMANTIC_CHECK_ELISION"
            and all("BOUNDARY" in row["distinction"] for row in table[1:]),
            "semantic and operational distinctions were conflated")
    proof = assessment["task_coverage_proof"]
    require("invokes check_declar zero times" in table[0]["declaration_coverage"]
            and "0..num_threads is empty" in proof["parallel_zero"]
            and "fetch_add" in proof["parallel_positive_no_panic"]
            and "conditional" in proof["failure_limit"],
            "task coverage proof is incomplete")
    isolation = assessment["checker_isolation"]
    require("fresh LeanDag/TcCtx" in isolation["fact"]
            and "fresh TcCache" in isolation["fact"],
            "fresh checker isolation was not preserved")
    failure = assessment["failure_and_stack_boundary"]
    require(failure["parallel_stack_bytes"] == 16_777_216
            and "unwraps spawn_scoped" in failure["spawn_failure"]
            and "join().expect" in failure["worker_panic"]
            and "not proved outcome-equivalent" in failure["conclusion"],
            "stack or failure boundary was weakened")
    counterexample = assessment["public_counterexample"]
    require(counterexample["mutation_id"] == NEG_MUTANT
            and counterexample["status"]
            == "SOURCE_LEVEL_PUBLIC_COUNTEREXAMPLE_NOT_EXECUTED_WITH_THIS_MUTANT"
            and "num_threads=0" in counterexample["baseline_path"]
            and "check_all_declars_par(0)" in counterexample["mutant_path"]
            and "No new config" in counterexample["claim_limit"],
            "public zero-thread counterexample drift")

    decisions = {row["mutation_id"]: row for row in assessment["mutation_decisions"]}
    require(set(decisions) == {GE_MUTANT, NEG_MUTANT}, "mutation decision set changed")
    require(decisions[NEG_MUTANT]["registry_classification"] == "MEANINGFUL_SEMANTIC"
            and decisions[NEG_MUTANT]["canonical_classification_change"] is True
            and decisions[NEG_MUTANT]["execution_needed_for_non_equivalence"] is False
            and decisions[NEG_MUTANT]["corpus_kill_claimed"] is False,
            "negated mutation decision changed")
    require(decisions[GE_MUTANT]["registry_classification"]
            == "SURVIVED_WITHOUT_WITNESS"
            and decisions[GE_MUTANT]["canonical_classification_change"] is False
            and decisions[GE_MUTANT]["execution_needed_for_non_equivalence"] is True
            and decisions[GE_MUTANT]["corpus_kill_claimed"] is False,
            "one-thread operational boundary was hidden")
    observations = assessment["supporting_observations"]
    require(len(observations) == 2
            and {row["mutation_id"] for row in observations}
            == {GE_MUTANT, NEG_MUTANT}
            and all(row["executed_tests"] == 187 and row["difference_count"] == 0
                    and "Finite support only" in row["role"] for row in observations),
            "historical observations were promoted or changed")
    decision = assessment["decision"]
    require(decision == {
        "outcome": "SUCCESS", "registry_append_count": 1,
        "appended_mutation_id": NEG_MUTANT,
        "appended_classification": "MEANINGFUL_SEMANTIC",
        "rel_gt_to_ge_classification_unchanged": True,
        "scientific_pair_or_launch_used": False,
        "external_action": "NO_EXTERNAL_ACTION", "next_item": NEXT_ITEM,
    }, "assessment decision changed")
    accounting = assessment["execution_accounting"]
    require(accounting["active_seconds_charged_conservatively"] <= 3600
            and all(value == 0 for key, value in accounting.items()
                    if key != "active_seconds_charged_conservatively"),
            "assessment exceeds budget or records an unauthorized launch")

    bindings = assessment["evidence_bindings"]
    require(len({row["path"] for row in bindings}) == len(bindings),
            "duplicate assessment evidence binding")
    for row in bindings:
        require(set(row) == {"path", "sha256"}
                and sha256(root / row["path"]) == row["sha256"],
                "assessment evidence drift: " + row["path"])

    specs = {
        mutant: json.loads((root / f"mutations/{mutant}.json").read_text())
        for mutant in (GE_MUTANT, NEG_MUTANT)
    }
    require(specs[GE_MUTANT]["function"] == "check_all_declars"
            and specs[GE_MUTANT]["source_span"] == "147"
            and specs[GE_MUTANT]["original"] == "self.config.num_threads > 1"
            and specs[GE_MUTANT]["mutated"] == "(self.config.num_threads >= 1)"
            and specs[NEG_MUTANT]["original"] == "self.config.num_threads > 1"
            and specs[NEG_MUTANT]["mutated"] == "!(self.config.num_threads > 1)",
            "thread mutation contracts drift")
    for mutant in (GE_MUTANT, NEG_MUTANT):
        comparison = json.loads(
            (root / f"results/mutants/{mutant}/scheduled-comparison.json").read_text()
        )
        require(comparison["status"] == "SURVIVED"
                and comparison["executed_test_count"] == 187
                and comparison["difference_count"] == 0
                and comparison["all_covering_tests_exhausted"] is True,
                "historical comparison drift: " + mutant)

    pinned = root / "results/research/alt-survivors-2026-09-08/evidence/pinned-nanoda/src"
    main = (pinned / "main.rs").read_text(encoding="utf-8")
    parser = (pinned / "parser.rs").read_text(encoding="utf-8")
    util = (pinned / "util.rs").read_text(encoding="utf-8")
    tc = (pinned / "tc.rs").read_text(encoding="utf-8")
    lib = (pinned / "lib.rs").read_text(encoding="utf-8")
    env = (pinned / "env.rs").read_text(encoding="utf-8")
    test_util = (pinned / "tests/util.rs").read_text(encoding="utf-8")
    ordered(main, ["Config::try_from(config_path)?", "cfg.to_export_file()?",
                   "export_file.check_all_declars();", "pp_selected_declars",
                   "Checked {} declarations with no errors"], "binary config path")
    ordered(util, ["#[derive(Debug, Clone, Deserialize)]", "pub struct Config",
                   "#[serde(default)]\n    pub num_threads: usize", "impl TryFrom<&Path> for Config",
                   "Ok(config)", "pub fn to_export_file", "parse_export_file"],
            "config reachability")
    try_from = util.split("impl TryFrom<&Path> for Config", 1)[1].split(
        "pub enum PpDestination", 1
    )[0]
    require("num_threads" not in try_from, "Config::try_from gained a thread bound")
    ordered(parser, ["parse_export_file<'p", "config: Config", "Parser::new",
                     "config: parser.config"], "parser config retention")
    ordered(tc, ["check_all_declars_serial", "for declar in self.declars.values()",
                 "self.check_declar(declar)", "check_all_declars_par",
                 "for i in 0..num_threads", ".stack_size(crate::STACK_SIZE)",
                 "task_num.fetch_add(1, Relaxed)", "self.declars.get_index(idx)",
                 "t.join().expect", "pub fn check_all_declars",
                 "if self.config.num_threads > 1", "check_all_declars_par",
                 "check_all_declars_serial"], "declaration dispatch")
    require("pub(crate) const STACK_SIZE: usize = 16_777_216;" in lib,
            "parallel stack size changed")
    require("pub(crate) type DeclarMap<'a> = FxIndexMap" in env,
            "declaration map lost index semantics")
    require("num_threads: 1" in test_util,
            "historical test utility no longer fixes one thread")
    existing = json.loads(
        (root / "results/mutants/nanoda-gen-21ef4d1d32a1/augmented-comparison-v2.json")
        .read_text(encoding="utf-8")
    )
    require(existing["candidate"]["path"] == counterexample["existing_export"]
            and existing["candidate"]["sha256"]
            == sha256(root / counterexample["existing_export"])
            and existing["candidate_outcomes"]["baseline"] == "REJECT",
            "existing parsed rejection evidence drift")
    return assessment


def _validate_registry(root: Path, assessment: dict) -> dict:
    predecessor = git_bytes(root, REGISTRY)
    current = (root / REGISTRY).read_bytes()
    require(digest(predecessor)
            == "9f38a528bec31f358009cf7f3c00f4f8d6779dc07dbd3371271ff3e4801eac10"
            and len(predecessor.splitlines()) == 609,
            "registry entry predecessor drift")
    require(current.startswith(predecessor) and len(current.splitlines()) == 610,
            "registry is not one exact append over the entry snapshot")
    suffix = current[len(predecessor):]
    require(suffix.startswith(b"{") and suffix.count(b"\n") == 1,
            "registry append is not one JSONL record")
    appended = json.loads(suffix.decode("utf-8"))
    fields = {
        "checker", "classification", "classification_scope",
        "config_reachability_assessment", "function", "id",
        "mutation_operator", "notes", "operator_family", "source_file",
        "source_span", "status", "subsystem", "updated_at",
    }
    require(set(appended) == fields and appended["id"] == NEG_MUTANT
            and appended["checker"] == "nanoda" and appended["status"] == "SURVIVED"
            and appended["classification"] == "MEANINGFUL_SEMANTIC"
            and appended["config_reachability_assessment"] == ASSESSMENT
            and appended["function"] == "check_all_declars"
            and appended["mutation_operator"] == "BOOL_NEGATE"
            and appended["operator_family"] == "predicate-negation"
            and appended["source_file"] == "src/tc.rs"
            and appended["source_span"] == "147"
            and appended["subsystem"] == "declaration-validation"
            and "num_threads=0" in appended["classification_scope"]
            and "creates no workers" in appended["notes"],
            "registry append overstates or misidentifies the source distinction")
    latest = {}
    for row in json_lines(current):
        latest[row["id"]] = {**latest.get(row["id"], {}), **row}
    require(latest[NEG_MUTANT]["classification"] == "MEANINGFUL_SEMANTIC"
            and latest[GE_MUTANT]["status"] == "SURVIVED"
            and latest[GE_MUTANT]["classification"] == "SURVIVED_WITHOUT_WITNESS",
            "latest mutation states do not preserve the split decision")
    require((root / INVENTORY).read_bytes() == git_bytes(root, INVENTORY),
            "survivor inventory changed during source classification")
    require(assessment["decision"]["appended_classification"]
            == appended["classification"],
            "assessment and registry append disagree")
    return appended


def validate(root: Path) -> dict:
    root = root.resolve()
    assessment = _validate_assessment(root)
    _validate_registry(root, assessment)
    result = json.loads((root / RESULT).read_text(encoding="utf-8"))
    require(result["item_id"] == ITEM and result["outcome"] == "SUCCESS"
            and result["finding"] == assessment["finding"]
            and result["assessment"] == {"path": ASSESSMENT,
                                           "sha256": sha256(root / ASSESSMENT)}
            and result["registry_transition"] == {
                "path": REGISTRY, "predecessor_lines": 609,
                "successor_lines": 610,
                "predecessor_sha256": digest(git_bytes(root, REGISTRY)),
                "successor_sha256": sha256(root / REGISTRY),
                "appended_mutation_id": NEG_MUTANT,
                "appended_classification": "MEANINGFUL_SEMANTIC",
            }
            and result["assurance_transition"] == {
                "pending_survivors_before": 4, "pending_survivors_after": 3,
                "meaningful_survivors_before": 3,
                "meaningful_survivors_after": 4, "equivalent_mutants": 14,
                "modeled_mutation_score_numerator": 135,
                "modeled_mutation_score_denominator": 142,
            }
            and result["recommendation"]["external_action"]
            == "NO_ACTION_BEFORE_REGRESSION"
            and result["next_item"] == NEXT_ITEM
            and result["next_item_started"] is False,
            "result binding, metrics, or successor drift")
    split = {row["mutation_id"]: row for row in result["mutation_results"]}
    require(split[NEG_MUTANT]["classification"] == "MEANINGFUL_SEMANTIC"
            and split[NEG_MUTANT]["classification_changed"] is True
            and split[GE_MUTANT]["classification"] == "SURVIVED_WITHOUT_WITNESS"
            and split[GE_MUTANT]["classification_changed"] is False
            and all(row["corpus_kill"] is False for row in split.values()),
            "result mutation split changed")
    require(all(value == 0 for key, value in result["execution_accounting"].items()
                if key != "active_seconds_charged_conservatively"),
            "result records an unauthorized launch")

    closure = json.loads((root / WORK_CLOSURE).read_text(encoding="utf-8"))
    require(closure["item_id"] == ITEM and closure["status"] == "CLOSED"
            and closure["outcome"] == "SUCCESS"
            and closure["canonical_classification_changed"] is True
            and closure["appended_mutation_id"] == NEG_MUTANT
            and closure["unchanged_mutation_id"] == GE_MUTANT
            and closure["budget"]["active_seconds_charged_conservatively"]
            <= closure["budget"]["active_seconds_limit"]
            and all(value == 0 for key, value in closure["budget"].items()
                    if key.endswith("_used"))
            and closure["budget"]["new_export_byte_variants"] == 0
            and closure["budget"]["new_mutation_identities"] == 0
            and closure["budget"]["external_actions"] == 0
            and closure["next_item"] == NEXT_ITEM
            and closure["next_item_started"] is False,
            "work closure or budget drift")

    focused = json.loads((root / FOCUSED_VALIDATION).read_text(encoding="utf-8"))
    require(focused["item_id"] == ITEM and focused["status"] == "PASS"
            and focused["scientific_launches"] == 0,
            "focused validation identity or launch count drift")
    for row in focused["tooling"]:
        require(sha256(root / row["path"]) == row["sha256"],
                "focused tooling drift: " + row["path"])

    manifest = json.loads((root / EVIDENCE_MANIFEST).read_text(encoding="utf-8"))
    require(set(manifest) == {"schema_version", "kind", "item_id", "status",
                              "note", "inputs"}
            and manifest["schema_version"] == 1
            and manifest["kind"]
            == "SURVIVOR_THREAD_CONFIG_REACHABILITY_CLOSURE"
            and manifest["item_id"] == ITEM and manifest["status"] == "PASS",
            "evidence manifest identity drift")
    paths: set[str] = set()
    for row in manifest["inputs"]:
        require(set(row) == {"path", "sha256", "bytes"}
                and row["path"] not in paths,
                "malformed or duplicate manifest input")
        paths.add(row["path"])
        path = root / row["path"]
        require(path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"],
                "manifest input drift: " + row["path"])
    require({
        "docs/research/SURVIVOR_THREAD_CONFIG_REACHABILITY_PLAN.md",
        "docs/research/SURVIVOR_THREAD_CONFIG_REGRESSION_PLAN.md",
        ASSESSMENT, RESULT, f"{BASE}/report.md", WORK_CLOSURE,
        HISTORICAL_TRANSITION, FOCUSED_VALIDATION, REGISTRY, INVENTORY,
        "lib/survivor_thread_config_reachability.py",
        "lib/survivor_thread_config_reachability_historical.py",
        "scripts/validate-survivor-thread-config-reachability-closure",
        "scripts/validate-survivor-thread-config-reachability-historical",
        "tests/test_survivor_thread_config_reachability.py",
        "tests/test_survivor_thread_config_reachability_historical.py",
    }.issubset(paths), "manifest omits closure, transition, or tooling evidence")
    return {
        "status": "PASS", "item_id": ITEM,
        "finding": assessment["finding"], "configuration_classes": 3,
        "registry_append_count": 1, "remaining_pending_mutations": [GE_MUTANT],
        "scientific_launches": 0,
    }
