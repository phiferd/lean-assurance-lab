"""Validate the scoped public-entrypoint equivalence admission for e964."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ITEM = "SURVIVOR-UNIVERSE-EQUIVALENCE-1"
MUTANT = "nanoda-gen-e9648d8c028d"
SNAPSHOT = "a4580dcd2d74f8156b4151d7439ca1e048a9735c"
TOOLING_SNAPSHOT = "4cea69c0b66487b82596c47c917b1d58af057a45"
CLOSURE_SNAPSHOT = "70de72f54c520fad89ed023204163d1cc3e76c5b"
BASE = "results/research/survivor-universe-equivalence-1"
ANALYSIS = f"{BASE}/equivalence-analysis.json"
RESULT = f"{BASE}/result.json"
WORK_CLOSURE = f"{BASE}/work-closure.json"
FOCUSED_VALIDATION = f"{BASE}/focused-validation.json"
EVIDENCE_MANIFEST = f"{BASE}/evidence-manifest.json"
HISTORICAL_TRANSITION = f"{BASE}/historical-transition.json"
REGISTRY = "results/mutants/registry.jsonl"
INVENTORY = "results/survivors/inventory.jsonl"
EVOLVED_TOOLING = {
    "lib/survivor_universe_equivalence.py",
    "lib/survivor_universe_equivalence_historical.py",
    "tests/test_survivor_universe_equivalence_historical.py",
    "lib/survivor_universe_diff_historical.py",
    "tests/test_survivor_universe_diff_historical.py",
    "lib/survivor_cache_historical.py",
    "tests/test_survivor_cache_historical.py",
    "tests/test_current_assurance.py",
    "scripts/build-artifact-graph",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return digest(path.read_bytes())


def git_bytes(root: Path, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{SNAPSHOT}:{path}"], cwd=root)


def tooling_bytes(root: Path, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{TOOLING_SNAPSHOT}:{path}"], cwd=root
    )


def closure_bytes(root: Path, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{CLOSURE_SNAPSHOT}:{path}"], cwd=root
    )


def ordered(text: str, fragments: list[str], label: str) -> None:
    cursor = -1
    for fragment in fragments:
        position = text.find(fragment, cursor + 1)
        require(position >= 0, f"{label}: missing or reordered fragment: {fragment}")
        cursor = position


def json_lines(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines()]


def _validate_analysis(root: Path) -> dict:
    analysis_path = root / ANALYSIS
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    fields = {
        "schema_version", "item_id", "mutation_id", "revision", "classification",
        "scope", "changed_domain", "private_counterexamples", "mutual_induction",
        "normal_form", "baseline_changed_state_cases", "recursive_closure",
        "public_callers", "supporting_observation", "decision", "execution_accounting",
        "evidence_bindings",
    }
    require(set(analysis) == fields and analysis["schema_version"] == 1,
            "equivalence analysis fields changed")
    require(analysis["item_id"] == ITEM and analysis["mutation_id"] == MUTANT
            and analysis["revision"] == "6ae1f0cd962f081f6c423454c5da729d841236a7"
            and analysis["classification"] == "EQUIVALENT_AT_PUBLIC_LEVEL_COMPARISON_ENTRYPOINTS",
            "analysis identity or scope changed")
    scope = analysis["scope"]
    require(scope["semantic_authority"] is False
            and "private leq_core" in scope["excluded"]
            and "public TcCtx::leq" in scope["included"],
            "analysis overstates its scope")

    disputed = analysis["changed_domain"]["only_disputed_state"]
    require(disputed == {
        "lhs": "non-Zero", "rhs": "Zero", "diff": 0,
        "mutant_result": False,
        "baseline_obligation": "Every such state in the public recursive closure returns false in the baseline.",
    }, "changed-domain partition drift")
    require(len(analysis["changed_domain"]["predicate_partition"]) == 3
            and analysis["changed_domain"]["preceding_arm"]
            == "(Zero, _) if diff >= 0 => true", "incomplete predicate partition")

    counterexamples = analysis["private_counterexamples"]
    require(len(counterexamples) == 2
            and counterexamples[0]["state"] == "leq_core(Max(Zero, Zero), Zero, 0)"
            and counterexamples[0]["baseline_result"] is True
            and counterexamples[0]["mutant_result"] is False
            and counterexamples[1]["baseline_result"] is True
            and counterexamples[1]["mutant_result"] is False,
            "private non-equivalence counterexample was hidden or changed")

    induction = analysis["mutual_induction"]
    require(set(induction) == {"measure", "normalization_claim", "zero_reflection_claim",
                               "recursive_equivalence_claim"}
            and "true exactly when N is syntactic Zero" in induction["zero_reflection_claim"],
            "mutual induction obligations are incomplete")
    require([row["id"] for row in analysis["normal_form"]["source_cases"]]
            == ["ZERO_OR_PARAM", "SUCCESSOR", "MAX_COMBINING", "IMAX_ELIMINATION"],
            "normal-form case partition changed")
    require([row["id"] for row in analysis["baseline_changed_state_cases"]] == [
        "PARAM", "SUCC", "RETAINED_MAX", "IMAX_PARAM_TAIL",
        "IMAX_MAX_TAIL", "IMAX_IMAX_TAIL",
    ] and all(row["result"] is False for row in analysis["baseline_changed_state_cases"]),
            "baseline changed-state proof is not exhaustive")
    require([row["id"] for row in analysis["recursive_closure"]] == [
        "SUCCESSOR_PEELING", "MAX_SPLITTING", "SUBSTITUTION_CASES",
        "LEFT_IMAX_REWRITES", "RIGHT_IMAX_REWRITES",
    ], "recursive closure partition changed")
    require(len(analysis["public_callers"]) == 8, "public caller inventory changed")
    require(analysis["supporting_observation"] == {
        "executed_tests": 163,
        "difference_count": 0,
        "role": "Consistent finite observation only; not used as the equivalence proof.",
    }, "finite observation was promoted or changed")
    decision = analysis["decision"]
    require(decision == {
        "outcome": "SUCCESS", "registry_classification": "EQUIVALENT",
        "canonical_classification_change": True, "private_function_equivalence": False,
        "public_entrypoint_equivalence": True, "external_action": "NO_ACTION_SUPPORTED",
        "next_item": "SURVIVOR-FVAR-REACHABILITY-1",
    }, "terminal decision or scoped classification drift")

    accounting = analysis["execution_accounting"]
    require(accounting["active_seconds_charged_conservatively"] <= 5400
            and all(value == 0 for key, value in accounting.items()
                    if key != "active_seconds_charged_conservatively"),
            "equivalence item exceeded its launch or active-time cap")
    bindings = analysis["evidence_bindings"]
    require(isinstance(bindings, list) and len(bindings) == 15,
            "equivalence analysis evidence inventory changed")
    seen: set[str] = set()
    for row in bindings:
        require(set(row) == {"path", "sha256"} and row["path"] not in seen,
                "malformed or duplicate evidence binding")
        seen.add(row["path"])
        data = git_bytes(root, row["path"]) if row["path"] == REGISTRY else (root / row["path"]).read_bytes()
        require(digest(data) == row["sha256"], "analysis evidence drift: " + row["path"])

    spec = json.loads((root / f"mutations/{MUTANT}.json").read_text())
    require(spec["source_file"] == "src/level.rs" and spec["source_span"] == "179"
            and spec["function"] == "leq_core" and spec["original"] == "diff < 0"
            and spec["mutated"] == "(diff <= 0)" and spec["replace_occurrence"] == 0,
            "mutation contract drift")
    comparison = json.loads((root / f"results/mutants/{MUTANT}/scheduled-comparison.json").read_text())
    require(comparison["status"] == "SURVIVED" and comparison["executed_test_count"] == 163
            and comparison["difference_count"] == 0
            and comparison["all_covering_tests_exhausted"] is True,
            "historical finite observation drift")

    pinned = root / "results/research/alt-survivors-2026-09-08/evidence/pinned-nanoda/src"
    level = (pinned / "level.rs").read_text(encoding="utf-8")
    util = (pinned / "util.rs").read_text(encoding="utf-8")
    parser = (pinned / "parser.rs").read_text(encoding="utf-8")
    tc = (pinned / "tc.rs").read_text(encoding="utf-8")
    inductive = (pinned / "inductive.rs").read_text(encoding="utf-8")
    ordered(util, [
        "pub fn succ(&mut self, l: LevelPtr<'t>)", "self.alloc_level(Level::Succ(l, hash))",
        "pub fn max(&mut self, l: LevelPtr<'t>, r: LevelPtr<'t>)",
        "self.alloc_level(Level::Max(l, r, hash))",
        "pub fn imax(&mut self, l: LevelPtr<'t>, r: LevelPtr<'t>)",
        "self.alloc_level(Level::IMax(l, r, hash))",
    ], "raw level constructors")
    ordered(parser, ["LevelSucc(l)", "LevelMax([l, r])", "LevelIMax([l, r])", "LevelParam(var_idx)"],
            "export level reconstruction")
    ordered(level, [
        "fn combining(&mut self, l: LevelPtr<'t>, r: LevelPtr<'t>)",
        "(Zero, _) => r", "(_, Zero) => l", "(Succ(l, ..), Succ(r, ..))",
        "pub fn simplify(&mut self, ptr: LevelPtr<'t>)",
        "if self.is_zero(l_simp) || self.is_one(l_simp)",
        "Zero => r_simp", "Succ(..) => self.combining(l_simp, r_simp)",
        "fn leq_imax_by_cases", "let lhs_0 = self.subst_simp", "let lhs_s = self.subst_simp",
        "self.leq_core(lhs_0, rhs_0, diff) && self.leq_core(lhs_s, rhs_s, diff)",
        "fn leq_core", "(Zero, _) if diff >= 0 => true", "(_, Zero) if diff < 0 => false",
        "(Param(..), Zero) => false", "(Succ(s, ..), _) => self.leq_core(s, r_in, diff - 1)",
        "(Max(a, b, ..), _) => self.leq_core(a, r_in, diff) && self.leq_core(b, r_in, diff)",
        "(IMax(_, b, _), _) if self.is_param(b) => self.leq_imax_by_cases",
        "let new_lhs = self.imax(a, y);", "let new_rhs = self.imax(x, y);",
        "let new_max = self.max(new_lhs, new_rhs);", "self.leq_core(new_max, r_in, diff)",
        "let new_max = self.simplify(new_max);", "self.leq_core(new_max, r_in, diff)",
        "pub fn leq(&mut self, l: LevelPtr<'t>, r: LevelPtr<'t>)",
        "let l_prime = self.simplify(l);", "let r_prime = self.simplify(r);",
        "self.leq_core(l_prime, r_prime, 0)",
        "pub fn eq_antisymm", "pub fn eq_antisymm_many", "pub fn is_zero", "self.leq(level, zero)",
        "pub fn is_nonzero", "self.leq(one, level)",
    ], "normalization and comparison proof path")
    require(level.count("fn leq_core") == 1 and "pub fn leq_core" not in level,
            "leq_core is no longer a single private entry")
    ordered(tc, [
        "if !self.ctx.is_zero(sort)", "self.ctx.eq_antisymm_many(x_levels, y_levels)",
        "Some(self.ctx.eq_antisymm(l, r))", "self.ctx.eq_antisymm_many(l_levels, r_levels)",
        "Sort { level, .. } => (self.ctx.is_zero(level), ty)",
    ], "type-checker public consumers")
    ordered(inductive, [
        "let is_nonzero = self.ctx.is_nonzero(block_codom);",
        "let is_zero = self.ctx.is_zero(block_codom);",
        "assert!(self.ctx.eq_antisymm(codom_level, st.block_codom.unwrap()));",
        "if !self.ctx.eq_antisymm(lhs[i], rhs[i])",
        "self.ctx.leq(s, st.block_codom.unwrap())",
        "if !self.ctx.is_zero(binder_type_level)",
    ], "inductive-checker public consumers")
    return analysis


def _validate_registry(root: Path, analysis: dict) -> dict:
    predecessor = git_bytes(root, REGISTRY)
    current = (root / REGISTRY).read_bytes()
    require(digest(predecessor) == "99b5867b1437b25af3bb5ab440875a616756e7c0bd75047f0dcdd745f4f4a572"
            and len(predecessor.splitlines()) == 607, "registry predecessor drift")
    require(current.startswith(predecessor) and len(current.splitlines()) >= 608,
            "registry no longer preserves the universe predecessor and append")
    suffix = current[len(predecessor):]
    first_line = suffix.splitlines(keepends=True)[0]
    require(first_line.startswith(b"{") and first_line.count(b"\n") == 1,
            "universe registry append is not one JSONL record")
    appended = json.loads(first_line.decode("utf-8"))
    fields = {
        "checker", "classification", "classification_scope", "equivalence_analysis",
        "function", "id", "mutation_operator", "notes", "operator_family", "source_file",
        "source_span", "status", "subsystem", "updated_at",
    }
    require(set(appended) == fields and appended["id"] == MUTANT
            and appended["checker"] == "nanoda" and appended["status"] == "SURVIVED"
            and appended["classification"] == "EQUIVALENT"
            and appended["equivalence_analysis"] == ANALYSIS
            and appended["function"] == "leq_core"
            and appended["mutation_operator"] == "REL_LT_TO_LE"
            and appended["operator_family"] == "relational-boundary"
            and appended["source_file"] == "src/level.rs" and appended["source_span"] == "179"
            and appended["subsystem"] == "universes"
            and "private leq_core" in appended["classification_scope"]
            and "Raw Max(Zero,Zero)" in appended["notes"],
            "registry append overstates or misidentifies equivalence")
    rows = json_lines(current)
    latest = {row["id"]: row for row in rows}
    require(latest[MUTANT] == appended, "registry append is not the latest mutant state")
    require((root / INVENTORY).read_bytes() == git_bytes(root, INVENTORY),
            "survivor inventory changed during equivalence admission")
    require(analysis["decision"]["registry_classification"] == appended["classification"],
            "analysis and registry classification disagree")
    return appended


def validate(root: Path) -> dict:
    root = root.resolve()
    analysis = _validate_analysis(root)
    _validate_registry(root, analysis)

    result = json.loads((root / RESULT).read_text(encoding="utf-8"))
    predecessor_registry = git_bytes(root, REGISTRY)
    first_append = (root / REGISTRY).read_bytes()[len(predecessor_registry):].splitlines(keepends=True)[0]
    historical_successor_registry = predecessor_registry + first_append
    require(result["item_id"] == ITEM and result["outcome"] == "SUCCESS"
            and result["finding"] == analysis["classification"]
            and result["analysis"] == {"path": ANALYSIS, "sha256": sha256(root / ANALYSIS)}
            and result["registry_transition"]["predecessor_lines"] == 607
            and result["registry_transition"]["successor_lines"] == 608
            and result["registry_transition"]["predecessor_sha256"] == digest(git_bytes(root, REGISTRY))
            and result["registry_transition"]["successor_sha256"]
            == digest(historical_successor_registry)
            and result["scope"]["public_entrypoint_equivalence"] is True
            and result["scope"]["arbitrary_private_leq_core_equivalence"] is False
            and result["recommendation"]["external_action"] == "NO_ACTION_SUPPORTED"
            and result["next_item"] == "SURVIVOR-FVAR-REACHABILITY-1"
            and result["next_item_started"] is False,
            "result binding, scope or successor drift")
    require(all(value == 0 for key, value in result["execution_accounting"].items()
                if key != "active_seconds_charged_conservatively"),
            "result records an unauthorized launch")

    closure = json.loads((root / WORK_CLOSURE).read_text(encoding="utf-8"))
    require(closure["item_id"] == ITEM and closure["status"] == "CLOSED"
            and closure["outcome"] == "SUCCESS"
            and closure["canonical_classification_changed"] is True
            and closure["private_function_equivalence"] is False
            and closure["public_entrypoint_equivalence"] is True
            and closure["budget"]["active_seconds_charged_conservatively"]
            <= closure["budget"]["active_seconds_limit"]
            and all(value == 0 for key, value in closure["budget"].items()
                    if key.endswith("_used"))
            and closure["budget"]["new_export_byte_variants"] == 0
            and closure["budget"]["new_mutation_identities"] == 0
            and closure["budget"]["external_actions"] == 0
            and closure["next_item"] == "SURVIVOR-FVAR-REACHABILITY-1"
            and closure["next_item_started"] is False,
            "work closure or budget drift")

    focused = json.loads((root / FOCUSED_VALIDATION).read_text(encoding="utf-8"))
    require(focused["item_id"] == ITEM and focused["status"] == "PASS"
            and focused["scientific_launches"] == 0,
            "focused-validation identity or launch count drift")
    for row in focused["tooling"]:
        data = closure_bytes(root, row["path"])
        require(digest(data) == row["sha256"],
                "focused tooling drift: " + row["path"])

    manifest = json.loads((root / EVIDENCE_MANIFEST).read_text(encoding="utf-8"))
    require(set(manifest) == {"schema_version", "kind", "item_id", "status", "note", "inputs"}
            and manifest["schema_version"] == 1
            and manifest["kind"] == "SURVIVOR_UNIVERSE_PUBLIC_EQUIVALENCE_CLOSURE"
            and manifest["item_id"] == ITEM and manifest["status"] == "PASS",
            "evidence manifest identity drift")
    paths: set[str] = set()
    for row in manifest["inputs"]:
        require(set(row) == {"path", "sha256", "bytes"} and row["path"] not in paths,
                "malformed or duplicate manifest input")
        paths.add(row["path"])
        data = closure_bytes(root, row["path"])
        require(len(data) == row["bytes"] and digest(data) == row["sha256"],
                "manifest input drift: " + row["path"])
    require({
        "docs/research/SURVIVOR_UNIVERSE_EQUIVALENCE_PLAN.md",
        "docs/research/SURVIVOR_FVAR_REACHABILITY_PLAN.md",
        ANALYSIS, RESULT, f"{BASE}/report.md", WORK_CLOSURE, HISTORICAL_TRANSITION,
        FOCUSED_VALIDATION, REGISTRY, INVENTORY,
        "lib/survivor_universe_equivalence.py",
        "lib/survivor_universe_equivalence_historical.py",
        "scripts/validate-survivor-universe-equivalence-closure",
        "scripts/validate-survivor-universe-equivalence-historical",
        "tests/test_survivor_universe_equivalence.py",
        "tests/test_survivor_universe_equivalence_historical.py",
    }.issubset(paths), "manifest omits closure, transition or tooling evidence")
    return {
        "status": "PASS",
        "item_id": ITEM,
        "classification": analysis["classification"],
        "private_counterexamples": len(analysis["private_counterexamples"]),
        "normal_form_cases": len(analysis["normal_form"]["source_cases"]),
        "changed_state_cases": len(analysis["baseline_changed_state_cases"]),
        "registry_append_count": 1,
        "scientific_launches": 0,
    }
