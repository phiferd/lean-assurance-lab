"""Mechanical checks for the bounded cache export-reachability boundary."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

BOUNDARY = "results/research/survivor-cache-export-1/construction-boundary.json"
RESULT = "results/research/survivor-cache-export-1/result.json"
WORK_CLOSURE = "results/research/survivor-cache-export-1/work-closure.json"
FOCUSED_VALIDATION = "results/research/survivor-cache-export-1/focused-validation.json"
EVIDENCE_MANIFEST = "results/research/survivor-cache-export-1/evidence-manifest.json"
HISTORICAL_SNAPSHOT = "1778f1de7028e33254d0ab7d5042fe749ed35392"
EVOLVED_TOOLING = {
    "lib/survivor_cache_export_boundary.py",
    "lib/survivor_cache_historical.py",
    "tests/test_survivor_cache_historical.py",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def historical_bytes(root: Path, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{HISTORICAL_SNAPSHOT}:{path}"], cwd=root
    )


def ordered_unique(text: str, fragments: list[str], label: str) -> None:
    cursor = -1
    for fragment in fragments:
        require(text.count(fragment) == 1, f"{label}: fragment is not unique: {fragment}")
        position = text.index(fragment)
        require(position > cursor, f"{label}: source order changed: {fragment}")
        cursor = position


def validate(root: Path) -> dict:
    root = root.resolve()
    boundary_path = root / BOUNDARY
    boundary = json.loads(boundary_path.read_text(encoding="utf-8"))
    required = {
        "schema_version", "item_id", "mutation_id", "revision", "assessment",
        "question", "internal_predecessor", "source_supported_hypothetical_construction",
        "ordinary_export_boundaries", "existing_export_support", "decision",
        "execution_accounting", "evidence_bindings",
    }
    require(set(boundary) == required, "boundary fields changed")
    require(boundary["schema_version"] == 1 and boundary["item_id"] == "SURVIVOR-CACHE-EXPORT-1",
            "wrong boundary identity")
    require(boundary["mutation_id"] == "nanoda-gen-3365809b3c41"
            and boundary["revision"] == "6ae1f0cd962f081f6c423454c5da729d841236a7",
            "wrong source or mutation identity")
    require(boundary["assessment"] == "ORDINARY_K_CARRIER_ORIGIN_AND_POINTER_IDENTITY_BOUNDARY",
            "wrong boundary assessment")

    bindings = boundary["evidence_bindings"]
    require(isinstance(bindings, list) and len(bindings) == 9, "incomplete evidence bindings")
    paths: set[str] = set()
    for row in bindings:
        require(set(row) == {"path", "sha256"} and row["path"] not in paths,
                "malformed or duplicate evidence binding")
        paths.add(row["path"])
        require(sha256(root / row["path"]) == row["sha256"], "evidence drift: " + row["path"])

    spec = json.loads((root / "mutations/nanoda-gen-3365809b3c41.json").read_text())
    require(spec["source_file"] == "src/tc.rs" and spec["source_span"] == "483"
            and spec["original"] == "flag == InferFlag::InferOnly"
            and spec["mutated"] == "(flag != InferFlag::InferOnly)"
            and spec["replace_occurrence"] == 0, "mutation contract drift")
    schedule = json.loads((root / "results/mutants/nanoda-gen-3365809b3c41/scheduled-comparison.json").read_text())
    require(schedule["status"] == "SURVIVED" and schedule["executed_test_count"] == 184
            and schedule["difference_count"] == 0 and schedule["all_scheduled_tests_exhausted"] is True,
            "historical survivor record drift")

    pinned = root / "results/research/alt-survivors-2026-09-08/evidence/pinned-nanoda/src"
    tc = (pinned / "tc.rs").read_text(encoding="utf-8")
    expr = (pinned / "expr.rs").read_text(encoding="utf-8")
    util = (pinned / "util.rs").read_text(encoding="utf-8")
    env = (pinned / "env.rs").read_text(encoding="utf-8")

    ordered_unique(tc, [
        "if flag == InferFlag::InferOnly {",
        "self.tc_cache.infer_cache_no_check.get(&e).copied()",
        "self.tc_cache.infer_cache_no_check.insert(e, r);",
    ], "cache")
    infer_app_start = tc.index("    fn infer_app(&mut self, e: ExprPtr<'t>, flag: InferFlag)")
    infer_app_end = tc.index("    //fn infer_app", infer_app_start)
    live_infer_app = tc[infer_app_start:infer_app_end]
    ordered_unique(live_infer_app, [
        "fn infer_app(&mut self, e: ExprPtr<'t>, flag: InferFlag)",
        "let arg = args.pop().unwrap();",
        "let arg_type = self.infer(arg, flag);",
        "self.assert_def_eq(binder_type, arg_type);",
    ], "application Check order")
    ordered_unique(tc, [
        "fn to_ctor_when_k(",
        "let major_ty = self.infer_then_whnf(major, InferOnly);",
        "fn reduce_rec(",
        "let major = self.to_ctor_when_k(major, rec).unwrap_or(major);",
        "let major = self.whnf(major);",
    ], "K reduction order")
    ordered_unique(tc, [
        "pub fn check_declar(&self, d: &Declar<'p>)",
        "tc.check_declar_info(d).unwrap();",
        "let inferred_type = tc.infer(*val, crate::tc::InferFlag::Check);",
    ], "ordinary declaration order")
    lambda_start = tc.index("    fn infer_lambda(")
    pi_start = tc.index("    fn infer_pi(", lambda_start)
    let_start = tc.index("    fn infer_let(", pi_start)
    let_end = tc.index("    // Not well tested", let_start)
    ordered_unique(tc[lambda_start:pi_start], [
        "fn infer_lambda(",
        "if let Check = flag {",
        "self.infer_sort_of(binder_type, flag);",
        "let infd = self.infer(instd, flag);",
    ], "lambda Check propagation")
    ordered_unique(tc[pi_start:let_start], [
        "fn infer_pi(",
        "let dom_univ = self.infer_sort_of(binder_type, flag);",
        "let mut infd = self.infer_sort_of(instd, flag);",
    ], "Pi Check propagation")
    ordered_unique(tc[let_start:let_end], [
        "fn infer_let(",
        "self.infer_sort_of(binder_type, flag);",
        "let val_ty = self.infer(val, flag);",
        "self.assert_def_eq(val_ty, binder_type);",
        "self.infer(body, flag)",
    ], "let Check propagation")
    subst_start = expr.index("    fn subst_aux(")
    subst_end = expr.index("    pub fn subst_expr_levels", subst_start)
    ordered_unique(expr[subst_start:subst_end], [
        "fn subst_aux(&mut self, e: ExprPtr<'t>, ks: LevelsPtr<'t>, vs: LevelsPtr<'t>)",
        "self.mk_sort(level)",
        "self.mk_const(name, levels)",
        "self.mk_app(fun, arg)",
        "self.mk_pi(binder_name, binder_style, binder_type, body)",
        "self.mk_lambda(binder_name, binder_style, binder_type, body)",
        "self.mk_let(binder_name, binder_type, val, body, nondep)",
    ], "constant type reconstruction")
    require("pub fn subst_expr_levels" in expr[subst_end:], "missing level-substitution entry")
    fresh_start = util.index("    pub fn with_tc_and_declar")
    fresh_end = util.index("    pub fn with_pp", fresh_start)
    ordered_unique(util[fresh_start:fresh_end], [
        "pub fn with_tc_and_declar",
        "let mut dag = LeanDag::new(&self.config);",
        "let mut ctx = TcCtx::new(self, &mut dag);",
        "let mut tc = TypeChecker::new(&mut ctx, &env, Some(d));",
    ], "fresh declaration checker")
    ordered_unique(env, [
        "EnvLimit::ByName(n) => declars.get_index_of(&n).unwrap_or(0)",
        "if idx < self.cutoff",
    ], "prior declaration visibility")

    export_lines = (root / boundary["existing_export_support"]["path"]).read_text().splitlines()
    require(len(export_lines) == 73, "bound Eq export record count changed")
    eq_record = json.loads(export_lines[59])
    require(eq_record["inductive"]["recs"][0]["k"] is True
            and eq_record["inductive"]["recs"][0]["name"] == 10,
            "bound Eq recursor is not K")

    ids = {row["id"] for row in boundary["ordinary_export_boundaries"]}
    require(ids == {"DIRECT_APPLICATION_ORDER", "CARRIER_HEADER_ORIGIN",
                    "FRESH_DECLARATION_CHECKER", "CONSTANT_TYPE_POINTER_REBUILD",
                    "STRUCTURAL_PROPAGATION"}, "boundary inventory changed")
    decision = boundary["decision"]
    require(decision["outcome"] == "BOUNDED_UNRESOLVED" and decision["pair_frozen"] is False
            and decision["canonical_classification_change"] is False
            and decision["external_action"] == "NO_ACTION_SUPPORTED",
            "claim limits or disposition changed")
    require(set(boundary["execution_accounting"].values()) == {0}, "source-only item consumed a launch")

    result = json.loads((root / RESULT).read_text(encoding="utf-8"))
    require(result["item_id"] == boundary["item_id"]
            and result["outcome"] == "BOUNDED_UNRESOLVED"
            and result["finding"] == boundary["assessment"],
            "result identity or finding drift")
    require(result["boundary"] == {"path": BOUNDARY, "sha256": sha256(boundary_path)},
            "result does not bind the validated boundary")
    require(result["next_item"] == "SURVIVOR-UNIVERSE-DIFF-1"
            and result["recommendation"]["external_action"] == "NO_ACTION_SUPPORTED",
            "result successor or external disposition drift")
    require(result["execution_accounting"]["offline_builds"] == 0
            and result["execution_accounting"]["checker_or_scientific_test_launches"] == 0
            and result["execution_accounting"]["scientific_export_pairs"] == 0,
            "result execution accounting drift")

    closure = json.loads((root / WORK_CLOSURE).read_text(encoding="utf-8"))
    require(closure["item_id"] == boundary["item_id"] and closure["status"] == "CLOSED"
            and closure["outcome"] == "BOUNDED_UNRESOLVED"
            and closure["next_item_started"] is False,
            "work closure drift")
    require(closure["budget"]["active_seconds_charged_conservatively"]
            <= closure["budget"]["active_seconds_limit"]
            and closure["budget"]["build_launches_used"] == 0
            and closure["budget"]["checker_launches_used"] == 0
            and closure["budget"]["scientific_pairs_frozen"] == 0,
            "work closure budget drift")

    focused = json.loads((root / FOCUSED_VALIDATION).read_text(encoding="utf-8"))
    require(focused["item_id"] == boundary["item_id"] and focused["status"] == "PASS"
            and focused["scientific_build_or_checker_launches"] == 0,
            "focused-validation disposition drift")
    for row in focused["tooling"]:
        digest = hashlib.sha256(
            historical_bytes(root, row["path"])
            if row["path"] in EVOLVED_TOOLING else (root / row["path"]).read_bytes()
        ).hexdigest()
        require(digest == row["sha256"],
                "focused tooling drift: " + row["path"])

    manifest = json.loads((root / EVIDENCE_MANIFEST).read_text(encoding="utf-8"))
    require(set(manifest) == {"schema_version", "kind", "item_id", "status", "note", "inputs"}
            and manifest["schema_version"] == 1
            and manifest["kind"] == "SURVIVOR_CACHE_EXPORT_BOUNDARY_CLOSURE"
            and manifest["item_id"] == boundary["item_id"] and manifest["status"] == "PASS",
            "evidence manifest identity drift")
    manifest_paths: set[str] = set()
    for row in manifest["inputs"]:
        require(set(row) == {"path", "sha256", "bytes"} and row["path"] not in manifest_paths,
                "malformed or duplicate manifest input")
        manifest_paths.add(row["path"])
        data = (historical_bytes(root, row["path"])
                if row["path"] in EVOLVED_TOOLING else (root / row["path"]).read_bytes())
        require(len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"],
                "manifest input drift: " + row["path"])
    require({
        "docs/research/SURVIVOR_CACHE_EXPORT_PLAN.md", BOUNDARY, RESULT,
        "results/research/survivor-cache-export-1/report.md", WORK_CLOSURE,
        "results/research/survivor-cache-export-1/validator-repair.json", FOCUSED_VALIDATION,
        "lib/survivor_cache_export_boundary.py",
        "scripts/validate-survivor-cache-export-closure",
        "tests/test_survivor_cache_export_boundary.py",
        "lib/survivor_cache_historical.py",
        "scripts/validate-survivor-cache-historical",
        "tests/test_survivor_cache_historical.py",
    }.issubset(manifest_paths), "manifest omits closure evidence or tooling")
    return {
        "status": "PASS",
        "item_id": boundary["item_id"],
        "assessment": boundary["assessment"],
        "evidence_bindings": len(bindings),
        "ordinary_boundaries": len(ids),
        "manifest_inputs": len(manifest_paths),
        "scientific_launches": 0,
    }
