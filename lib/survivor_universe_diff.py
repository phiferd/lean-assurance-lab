"""Mechanical checks for the bounded universe diff-zero reachability result."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ASSESSMENT = "results/research/survivor-universe-diff-1/reachability-assessment.json"
RESULT = "results/research/survivor-universe-diff-1/result.json"
WORK_CLOSURE = "results/research/survivor-universe-diff-1/work-closure.json"
FOCUSED_VALIDATION = "results/research/survivor-universe-diff-1/focused-validation.json"
EVIDENCE_MANIFEST = "results/research/survivor-universe-diff-1/evidence-manifest.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordered(text: str, fragments: list[str], label: str) -> None:
    cursor = -1
    for fragment in fragments:
        position = text.find(fragment, cursor + 1)
        require(position >= 0, f"{label}: missing or reordered fragment: {fragment}")
        cursor = position


def json_lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def validate(root: Path) -> dict:
    root = root.resolve()
    assessment_path = root / ASSESSMENT
    assessment = json.loads(assessment_path.read_text(encoding="utf-8"))
    required = {
        "schema_version", "item_id", "mutation_id", "revision", "assessment",
        "question", "existing_artifact", "exact_call_chain", "state_trace",
        "historical_context", "remaining_boundary", "decision",
        "execution_accounting", "evidence_bindings",
    }
    require(set(assessment) == required, "assessment fields changed")
    require(assessment["schema_version"] == 1
            and assessment["item_id"] == "SURVIVOR-UNIVERSE-DIFF-1",
            "wrong assessment identity")
    require(assessment["mutation_id"] == "nanoda-gen-e9648d8c028d"
            and assessment["revision"] == "6ae1f0cd962f081f6c423454c5da729d841236a7",
            "wrong source or mutation identity")
    require(assessment["assessment"]
            == "EXACT_CALL_STATE_REACHABLE_WITHOUT_LOCAL_OUTCOME_DIFFERENCE",
            "wrong reachability assessment")

    bindings = assessment["evidence_bindings"]
    require(isinstance(bindings, list) and len(bindings) == 13,
            "incomplete assessment evidence bindings")
    bound: set[str] = set()
    for row in bindings:
        require(set(row) == {"path", "sha256"} and row["path"] not in bound,
                "malformed or duplicate evidence binding")
        bound.add(row["path"])
        require(sha256(root / row["path"]) == row["sha256"],
                "assessment evidence drift: " + row["path"])

    mutation = json.loads((root / "mutations/nanoda-gen-e9648d8c028d.json").read_text())
    require(mutation["source_file"] == "src/level.rs"
            and mutation["source_span"] == "179"
            and mutation["function"] == "leq_core"
            and mutation["original"] == "diff < 0"
            and mutation["mutated"] == "(diff <= 0)"
            and mutation["replace_occurrence"] == 0,
            "mutation contract drift")
    comparison = json.loads((root / "results/mutants/nanoda-gen-e9648d8c028d/scheduled-comparison.json").read_text())
    require(comparison["status"] == "SURVIVED"
            and comparison["executed_test_count"] == 163
            and comparison["difference_count"] == 0
            and comparison["all_covering_tests_exhausted"] is True,
            "historical comparison drift")

    candidate = json_lines(root / assessment["existing_artifact"]["candidate"]["path"])
    control = json_lines(root / assessment["existing_artifact"]["control"]["path"])
    require(len(candidate) == len(control) == 7, "existing pair record count drift")
    require(candidate[2] == control[2] == {"ie": 0, "sort": 0},
            "existing pair no longer uses Sort Zero")
    require(candidate[-1].get("thm", {}).get("type") == 0
            and control[-1].get("def", {}).get("type") == 0
            and candidate[2:6] == control[2:6],
            "existing theorem/control shape drift")
    observation = json.loads((root / assessment["existing_artifact"]["baseline_observation"]["path"]).read_text())
    require(observation["candidate"]["result"]["normalized_outcome"] == "REJECT"
            and observation["control"]["result"]["normalized_outcome"] == "ACCEPT",
            "baseline theorem/control observation drift")

    pinned = root / "results/research/alt-survivors-2026-09-08/evidence/pinned-nanoda/src"
    util = (pinned / "util.rs").read_text(encoding="utf-8")
    parser = (pinned / "parser.rs").read_text(encoding="utf-8")
    tc = (pinned / "tc.rs").read_text(encoding="utf-8")
    level = (pinned / "level.rs").read_text(encoding="utf-8")
    ordered(util, [
        "pub fn new(config: &Config) -> Self",
        "let _ = out.levels.insert(Level::Zero);",
        "pub(crate) fn zero(&self) -> LevelPtr<'a>",
    ], "implicit Zero")
    ordered(parser, [
        "LevelSucc(u32)", "LevelMax([u32; 2])", "LevelIMax([u32; 2])",
        "LevelParam(u32)", "ExprSort(level)", "let level = self.get_level_ptr(level);",
        "Thm {name, ty, uparams, value}", "let theorem = Declar::Theorem { info, val };",
    ], "export reconstruction")
    ordered(tc, [
        "let inferred_type = self.infer(info.ty, Check);",
        "let sort = self.ensure_sort(inferred_type);",
        "if let Declar::Theorem {..} = d",
        "if !self.ctx.is_zero(sort)",
        "fn infer_sort(&mut self, l: LevelPtr<'t>, flag: InferFlag)",
        "let out = self.ctx.succ(l);",
        "self.ctx.mk_sort(out)",
    ], "theorem sort path")
    ordered(level, [
        "pub fn simplify(&mut self, ptr: LevelPtr<'t>)",
        "fn leq_core(&mut self, l_in: LevelPtr<'t>, r_in: LevelPtr<'t>, diff: isize)",
        "(Zero, _) if diff >= 0 => true",
        "(_, Zero) if diff < 0 => false",
        "(Param(..), Zero) => false",
        "(Succ(s, ..), _) => self.leq_core(s, r_in, diff - 1)",
        "pub fn leq(&mut self, l: LevelPtr<'t>, r: LevelPtr<'t>)",
        "self.leq_core(l_prime, r_prime, 0)",
        "pub fn is_zero(&mut self, level: LevelPtr<'t>)",
        "self.leq(level, zero)",
    ], "comparison path")

    trace = assessment["state_trace"]
    require(trace["entry"] == {"lhs": "Succ Zero", "rhs": "Zero", "diff": 0}
            and trace["baseline"]["result"] is False
            and trace["mutant"]["result"] is False
            and trace["control_flow_difference"] is True
            and trace["local_boolean_difference"] is False,
            "state trace or scoped outcome changed")
    decision = assessment["decision"]
    require(decision["outcome"] == "SUCCESS"
            and decision["call_state_reachable"] is True
            and decision["canonical_classification_change"] is False
            and decision["next_item"] == "SURVIVOR-UNIVERSE-EQUIVALENCE-1"
            and decision["external_action"] == "NO_ACTION_SUPPORTED",
            "decision scope or successor drift")
    require({key: value for key, value in assessment["execution_accounting"].items()
             if key != "active_seconds_charged_conservatively"}.values()
            and all(value == 0 for key, value in assessment["execution_accounting"].items()
                    if key != "active_seconds_charged_conservatively"),
            "source-only assessment consumed a launch")
    require(assessment["execution_accounting"]["active_seconds_charged_conservatively"] <= 3600,
            "source-only active-time bound exceeded")

    result = json.loads((root / RESULT).read_text(encoding="utf-8"))
    require(result["item_id"] == assessment["item_id"]
            and result["outcome"] == "SUCCESS"
            and result["finding"] == assessment["assessment"],
            "result identity or finding drift")
    require(result["assessment"] == {"path": ASSESSMENT, "sha256": sha256(assessment_path)}
            and result["next_item"] == "SURVIVOR-UNIVERSE-EQUIVALENCE-1"
            and result["recommendation"]["external_action"] == "NO_ACTION_SUPPORTED",
            "result binding or recommendation drift")
    closure = json.loads((root / WORK_CLOSURE).read_text(encoding="utf-8"))
    require(closure["item_id"] == assessment["item_id"]
            and closure["status"] == "CLOSED" and closure["outcome"] == "SUCCESS"
            and closure["canonical_classification_changed"] is False
            and closure["next_item_started"] is False,
            "work closure drift")
    require(closure["budget"]["active_seconds_charged_conservatively"]
            <= closure["budget"]["active_seconds_limit"]
            and all(value == 0 for key, value in closure["budget"].items()
                    if key not in {"active_seconds_limit", "active_seconds_charged_conservatively"}),
            "work-closure budget drift")

    focused = json.loads((root / FOCUSED_VALIDATION).read_text(encoding="utf-8"))
    require(focused["item_id"] == assessment["item_id"] and focused["status"] == "PASS"
            and focused["scientific_build_or_checker_launches"] == 0,
            "focused-validation disposition drift")
    for row in focused["tooling"]:
        require(sha256(root / row["path"]) == row["sha256"],
                "focused tooling drift: " + row["path"])

    manifest = json.loads((root / EVIDENCE_MANIFEST).read_text(encoding="utf-8"))
    require(set(manifest) == {"schema_version", "kind", "item_id", "status", "note", "inputs"}
            and manifest["schema_version"] == 1
            and manifest["kind"] == "SURVIVOR_UNIVERSE_DIFF_REACHABILITY_CLOSURE"
            and manifest["item_id"] == assessment["item_id"] and manifest["status"] == "PASS",
            "evidence manifest identity drift")
    manifest_paths: set[str] = set()
    for row in manifest["inputs"]:
        require(set(row) == {"path", "sha256", "bytes"} and row["path"] not in manifest_paths,
                "malformed or duplicate manifest input")
        path = root / row["path"]
        manifest_paths.add(row["path"])
        require(path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"],
                "manifest input drift: " + row["path"])
    require({
        "docs/research/SURVIVOR_UNIVERSE_DIFF_PLAN.md", ASSESSMENT, RESULT,
        "results/research/survivor-universe-diff-1/report.md", WORK_CLOSURE,
        FOCUSED_VALIDATION, "lib/survivor_universe_diff.py",
        "scripts/validate-survivor-universe-diff-closure",
        "tests/test_survivor_universe_diff.py",
        "results/research/survivor-universe-diff-1/historical-transition.json",
        "lib/survivor_universe_diff_historical.py",
        "scripts/validate-survivor-universe-diff-historical",
        "tests/test_survivor_universe_diff_historical.py",
    }.issubset(manifest_paths), "manifest omits closure evidence or tooling")
    return {
        "status": "PASS",
        "item_id": assessment["item_id"],
        "assessment": assessment["assessment"],
        "evidence_bindings": len(bindings),
        "call_state_reachable": True,
        "local_boolean_difference": False,
        "manifest_inputs": len(manifest_paths),
        "scientific_launches": 0,
    }
