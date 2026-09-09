"""Validate the public-export free-variable reachability closure."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ITEM = "SURVIVOR-FVAR-REACHABILITY-1"
MUTANT = "nanoda-gen-399895fa0b72"
ENTRY_SNAPSHOT = "4cea69c0b66487b82596c47c917b1d58af057a45"
BASE = "results/research/survivor-fvar-reachability-1"
ASSESSMENT = f"{BASE}/reachability-assessment.json"
RESULT = f"{BASE}/result.json"
WORK_CLOSURE = f"{BASE}/work-closure.json"
FOCUSED_VALIDATION = f"{BASE}/focused-validation.json"
EVIDENCE_MANIFEST = f"{BASE}/evidence-manifest.json"
HISTORICAL_TRANSITION = f"{BASE}/historical-transition.json"
REGISTRY = "results/mutants/registry.jsonl"
INVENTORY = "results/survivors/inventory.jsonl"


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
        "schema_version", "item_id", "mutation_id", "revision", "finding",
        "classification", "question", "scope", "public_entry_path",
        "structural_exclusion_proof", "internal_boundary",
        "corroborating_existing_evidence", "supporting_observation", "decision",
        "execution_accounting", "evidence_bindings",
    }
    require(set(assessment) == fields and assessment["schema_version"] == 1,
            "reachability assessment fields changed")
    require(assessment["item_id"] == ITEM and assessment["mutation_id"] == MUTANT
            and assessment["revision"]
            == "6ae1f0cd962f081f6c423454c5da729d841236a7"
            and assessment["finding"]
            == "EXCLUDED_ON_PUBLIC_EXPORTED_DECLARATION_PATH"
            and assessment["classification"] == "EQUIVALENT_AT_PUBLIC_EXPORT_PATH",
            "assessment identity or classification changed")
    scope = assessment["scope"]
    require(scope["semantic_authority"] is False
            and scope["guard_role"].startswith("Defense in depth")
            and any("Arbitrary crate-internal" in value for value in scope["excluded"]),
            "assessment overstates public-path scope")

    require([row["step"] for row in assessment["public_entry_path"]] == [
        "CONFIG_INGESTION", "PARSER_SCHEMA", "PARSER_RECONSTRUCTION",
        "DECLARATION_TYPES", "CHECK_DISPATCH",
    ], "public entry-path partition changed")
    proof = assessment["structural_exclusion_proof"]
    require(proof["free_variable_representation"].startswith("Expr::Local")
            and len(proof["base_cases"]) == 2
            and len(proof["inductive_cases"]) == 4
            and "Every expression" in proof["conclusion"],
            "structural parser exclusion proof is incomplete")
    boundary = assessment["internal_boundary"]
    require(boundary["reachable"] is True
            and boundary["status"] == "SOURCE_LEVEL_COUNTEREXAMPLE_NOT_EXECUTED"
            and "synthetic" in boundary["construction"]
            and "No current public parser" in boundary["why_out_of_scope"],
            "internal counterexample or scope was hidden")
    observation = assessment["supporting_observation"]
    require(observation == {
        "executed_tests": 184,
        "difference_count": 0,
        "all_covering_tests_exhausted": True,
        "role": "Consistent finite observation only; not used as the exclusion proof.",
    }, "finite observation was promoted or changed")
    decision = assessment["decision"]
    require(decision == {
        "outcome": "SUCCESS", "registry_classification": "EQUIVALENT",
        "canonical_classification_change": True,
        "public_export_path_equivalence": True,
        "arbitrary_internal_equivalence": False,
        "scientific_pair_or_launch_needed": False,
        "external_action": "NO_ACTION_SUPPORTED",
        "next_item": "SURVIVOR-THREAD-CONFIG-REACHABILITY-1",
    }, "terminal decision or successor drift")
    accounting = assessment["execution_accounting"]
    require(accounting["active_seconds_charged_conservatively"] <= 3600
            and all(value == 0 for key, value in accounting.items()
                    if key != "active_seconds_charged_conservatively"),
            "source-only item exceeded its active-time or launch cap")

    bindings = assessment["evidence_bindings"]
    require(isinstance(bindings, list) and len(bindings) == 12,
            "assessment evidence inventory changed")
    seen: set[str] = set()
    for row in bindings:
        require(set(row) == {"path", "sha256"} and row["path"] not in seen,
                "malformed or duplicate evidence binding")
        seen.add(row["path"])
        require(sha256(root / row["path"]) == row["sha256"],
                "assessment evidence drift: " + row["path"])

    spec = json.loads((root / f"mutations/{MUTANT}.json").read_text())
    require(spec["source_file"] == "src/tc.rs" and spec["source_span"] == "168"
            and spec["function"] == "check_declar_info"
            and spec["original"] == "assert!(!self.ctx.has_fvars(info.ty));"
            and spec["mutated"]
            == "if false { assert!(!self.ctx.has_fvars(info.ty)); }"
            and spec["replace_occurrence"] == 0,
            "mutation contract drift")
    comparison = json.loads(
        (root / f"results/mutants/{MUTANT}/scheduled-comparison.json").read_text()
    )
    require(comparison["status"] == "SURVIVED"
            and comparison["executed_test_count"] == 184
            and comparison["difference_count"] == 0
            and comparison["all_covering_tests_exhausted"] is True,
            "historical finite observation drift")

    pinned = root / "results/research/alt-survivors-2026-09-08/evidence/pinned-nanoda/src"
    main = (pinned / "main.rs").read_text(encoding="utf-8")
    util = (pinned / "util.rs").read_text(encoding="utf-8")
    parser = (pinned / "parser.rs").read_text(encoding="utf-8")
    expr = (pinned / "expr.rs").read_text(encoding="utf-8")
    tc = (pinned / "tc.rs").read_text(encoding="utf-8")
    inductive = (pinned / "inductive.rs").read_text(encoding="utf-8")
    ordered(main, ["cfg.to_export_file()?", "export_file.check_all_declars();"],
            "binary public entry")
    ordered(util, [
        "pub fn with_tc_and_declar", "let mut dag = LeanDag::new(&self.config);",
        "let mut tc = TypeChecker::new", "pub struct TcCtx",
        "pub fn mk_dbj_level", "Expr::Local", "pub fn remake_dbj_level",
        "Expr::Local", "pub fn mk_unique", "Expr::Local",
        "pub fn to_export_file", "crate::parser::parse_export_file",
    ], "persistent versus temporary construction")
    ordered(parser, [
        "enum ExportJsonVal", "ExprMData", "ExprLet", "ExprConst", "ExprApp",
        "ExprPi", "ExprLambda", "ExprProj", "ExprSort", "ExprBVar",
        "fn get_expr_ptr", "assert!((idx as usize) < self.dag.exprs.len());",
        "ExprSort(level)", "ExprMData {..}", "panic!(\"Expr.mdata not supported\")",
        "ExprConst {name, levels}", "ExprApp {fun, arg}",
        "ExprBVar(dbj_idx)", "ExprLambda", "ExprPi", "ExprLet", "ExprProj",
        "Axiom {name, ty", "let ty = self.get_expr_ptr(ty);",
        "Defn {name, ty", "let ty = self.get_expr_ptr(ty);",
        "Thm {name, ty", "let ty = self.get_expr_ptr(ty);",
        "Opaque {name, ty", "let ty = self.get_expr_ptr(ty);",
        "Quot {name, ty", "let ty = self.get_expr_ptr(ty);",
        "Inductive {ind_vals, ctor_vals, rec_vals}",
    ], "parser grammar and declaration types")
    require("Expr::Local" not in parser, "parser gained a Local constructor")
    ordered(expr, [
        "pub enum Expr", "Var {", "Local {", "pub enum FVarId",
        "pub(crate) fn has_fvars(&self)", "Local { .. } => true",
        "Var { .. } | Sort { .. } | Const { .. }", "App { has_fvars, .. }",
    ], "free-variable representation")
    require(tc.count(".check_declar_info(") == 4,
            "ordinary check_declar_info caller inventory changed")
    ordered(tc, [
        "pub fn check_declar", "Axiom { .. }", "tc.check_declar_info(d)",
        "Inductive(..) => self.check_inductive_declar(d)",
        "Quot { .. } =>", "tc.check_declar_info(d)",
        "pub(crate) fn check_declar_info", "let info = d.info();",
        "assert!(!self.ctx.has_fvars(info.ty));", "self.infer(info.ty, Check)",
        "Local { binder_type, .. } => binder_type",
    ], "declaration dispatch and internal counterexample")
    require(inductive.count(".check_declar_info(") == 1,
            "inductive check_declar_info caller inventory changed")
    ordered(inductive, [
        "pub(crate) fn check_inductive_declar", "tc.check_declar_info(d).unwrap();",
        "tc.collect_unmodified_mutuals(ind)", "tc.specialize_nested",
    ], "inductive pre-local guard")

    discovery = json.loads(
        (root / "config/declaration-validation-discovery-closure.json").read_text()
    )
    topic = next(row for row in discovery["topics"]
                 if row["id"] == "TOPIC.FVAR_CLOSURE")
    nanoda = next(row for row in topic["observer_matrix"]
                  if row["observer"] == "NANODA")
    require(nanoda["state"] == "NOT_REPRESENTABLE_IN_INPUT"
            and "export representability" in topic["disposition"],
            "existing representation/enforcement distinction drift")
    return assessment


def _validate_registry(root: Path, assessment: dict) -> dict:
    predecessor = git_bytes(root, REGISTRY)
    current = (root / REGISTRY).read_bytes()
    require(digest(predecessor)
            == "2ba8a9a640d994e4ee90fe78f58896c0735a2bbebce4db75eab8dfcee6a09961"
            and len(predecessor.splitlines()) == 608,
            "registry predecessor drift")
    require(current.startswith(predecessor) and len(current.splitlines()) == 609,
            "registry is not one exact append over the entry snapshot")
    suffix = current[len(predecessor):]
    require(suffix.startswith(b"{") and suffix.count(b"\n") == 1,
            "registry append is not one JSONL record")
    appended = json.loads(suffix.decode("utf-8"))
    fields = {
        "checker", "classification", "classification_scope",
        "equivalence_analysis", "function", "id", "mutation_operator", "notes",
        "operator_family", "source_file", "source_span", "status", "subsystem",
        "updated_at",
    }
    require(set(appended) == fields and appended["id"] == MUTANT
            and appended["checker"] == "nanoda" and appended["status"] == "SURVIVED"
            and appended["classification"] == "EQUIVALENT"
            and appended["equivalence_analysis"] == ASSESSMENT
            and appended["function"] == "check_declar_info"
            and appended["mutation_operator"] == "SKIP_VALIDATION"
            and appended["operator_family"] == "validation-elision"
            and appended["source_file"] == "src/tc.rs"
            and appended["source_span"] == "168"
            and appended["subsystem"] == "declaration-validation"
            and "arbitrary internal" in appended["classification_scope"]
            and "defense in depth" in appended["notes"],
            "registry append overstates or misidentifies equivalence")
    latest = {row["id"]: row for row in json_lines(current)}
    require(latest[MUTANT] == appended, "registry append is not the latest mutant state")
    require((root / INVENTORY).read_bytes() == git_bytes(root, INVENTORY),
            "survivor inventory changed during fvar admission")
    require(assessment["decision"]["registry_classification"]
            == appended["classification"],
            "assessment and registry classification disagree")
    return appended


def validate(root: Path) -> dict:
    root = root.resolve()
    assessment = _validate_assessment(root)
    _validate_registry(root, assessment)
    result = json.loads((root / RESULT).read_text(encoding="utf-8"))
    require(result["item_id"] == ITEM and result["outcome"] == "SUCCESS"
            and result["finding"] == assessment["classification"]
            and result["assessment"] == {"path": ASSESSMENT,
                                           "sha256": sha256(root / ASSESSMENT)}
            and result["registry_transition"] == {
                "path": REGISTRY, "predecessor_lines": 608,
                "successor_lines": 609,
                "predecessor_sha256": digest(git_bytes(root, REGISTRY)),
                "successor_sha256": sha256(root / REGISTRY),
                "appended_classification": "EQUIVALENT",
            }
            and result["scope"]["public_export_path_equivalence"] is True
            and result["scope"]["arbitrary_internal_declaration_equivalence"] is False
            and result["scope"]["guard_retained_as_defense_in_depth"] is True
            and result["recommendation"]["external_action"] == "NO_ACTION_SUPPORTED"
            and result["next_item"] == "SURVIVOR-THREAD-CONFIG-REACHABILITY-1"
            and result["next_item_started"] is False,
            "result binding, scope or successor drift")
    require(all(value == 0 for key, value in result["execution_accounting"].items()
                if key != "active_seconds_charged_conservatively"),
            "result records an unauthorized launch")

    closure = json.loads((root / WORK_CLOSURE).read_text(encoding="utf-8"))
    require(closure["item_id"] == ITEM and closure["status"] == "CLOSED"
            and closure["outcome"] == "SUCCESS"
            and closure["canonical_classification_changed"] is True
            and closure["public_export_path_equivalence"] is True
            and closure["arbitrary_internal_equivalence"] is False
            and closure["budget"]["active_seconds_charged_conservatively"]
            <= closure["budget"]["active_seconds_limit"]
            and all(value == 0 for key, value in closure["budget"].items()
                    if key.endswith("_used"))
            and closure["budget"]["new_export_byte_variants"] == 0
            and closure["budget"]["new_mutation_identities"] == 0
            and closure["budget"]["external_actions"] == 0
            and closure["next_item"] == "SURVIVOR-THREAD-CONFIG-REACHABILITY-1"
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
    require(set(manifest) == {"schema_version", "kind", "item_id", "status", "note", "inputs"}
            and manifest["schema_version"] == 1
            and manifest["kind"] == "SURVIVOR_FVAR_PUBLIC_EXPORT_EQUIVALENCE_CLOSURE"
            and manifest["item_id"] == ITEM and manifest["status"] == "PASS",
            "evidence manifest identity drift")
    paths: set[str] = set()
    for row in manifest["inputs"]:
        require(set(row) == {"path", "sha256", "bytes"} and row["path"] not in paths,
                "malformed or duplicate manifest input")
        paths.add(row["path"])
        path = root / row["path"]
        require(path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"],
                "manifest input drift: " + row["path"])
    require({
        "docs/research/SURVIVOR_FVAR_REACHABILITY_PLAN.md",
        "docs/research/SURVIVOR_THREAD_CONFIG_REACHABILITY_PLAN.md",
        ASSESSMENT, RESULT, f"{BASE}/report.md", WORK_CLOSURE,
        HISTORICAL_TRANSITION, FOCUSED_VALIDATION, REGISTRY, INVENTORY,
        "lib/survivor_fvar_reachability.py",
        "lib/survivor_fvar_reachability_historical.py",
        "scripts/validate-survivor-fvar-reachability-closure",
        "scripts/validate-survivor-fvar-reachability-historical",
        "tests/test_survivor_fvar_reachability.py",
        "tests/test_survivor_fvar_reachability_historical.py",
    }.issubset(paths), "manifest omits closure, transition or tooling evidence")
    return {
        "status": "PASS", "item_id": ITEM,
        "classification": assessment["classification"],
        "public_entry_steps": len(assessment["public_entry_path"]),
        "internal_counterexamples": 1, "registry_append_count": 1,
        "scientific_launches": 0,
    }
