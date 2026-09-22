"""Validate the KIOTA-RECURSOR-TYPE-DESIGN-1 source-bound design package."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from lib.research_queue_v4 import queue_digest


ROOT = Path(__file__).resolve().parents[1]
ITEM = "KIOTA-RECURSOR-TYPE-DESIGN-1"
SUCCESSOR = "KIOTA-RECURSOR-TYPE-REPAIR-1"
BASE = Path("results/research/kiota-recursor-type-design-1")
SOURCE = BASE / "source-inventory.json"
DESIGN = BASE / "construction-design.json"
FIXTURES = BASE / "acceptance-fixtures.json"
AUDIT = BASE / "design-audit.json"
RESULT = BASE / "result.json"
CLOSURE = BASE / "closure.json"
REPORT = BASE / "report.md"
PROTOCOL = BASE / "protocol.json"
WORK = BASE / "work-record.json"
QUEUE = Path("config/research-queue.json")
REVIEW = Path("results/research/queue-reviews/2026-09-22-kiota-recursor-type-design-1-closure.json")

SOURCE_BINDINGS = {
    "kiota_archive": ("results/research/semantic-import-contract-1/kiota-source.tar.gz", 4587521,
                      "dacbc7bdb92471f2df8fbd4a31b6b6b07c1a0d3f435bfab9e9b093ddad06aaa8"),
    "kiota_parser": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/src/parser.rs", 46528,
                     "537d94a883cfdceafd20299502a954c9680e177b6ffb20252fa733bc83383f7e"),
    "kiota_environment": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/src/env.rs", 4057,
                          "b8665c8b96f770ffffe6d6ff50e05bd4a468edfb835c665ce98485b1bac0107b"),
    "kiota_type_checker": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/src/tc.rs", 545983,
                           "c5ea600b20ab058f2de4be555391e63b6ae44e38b42a6895946779e6b61b8e3b"),
    "kiota_expression": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/src/expr.rs", 30728,
                         "264c6063e5dd0f2deb5481881907d0bd1702bdfe9575cc405fc2936930abac02"),
    "kiota_level": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/src/level.rs", 7771,
                    "af5a1a5a18b1224130140296b4f5c811f11f28d244e7e9dcfcd6f4892c6f82ed"),
    "kiota_export_tests": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/tests/exports.rs", 49582,
                           "db3b6313093d4d31830b32699b01a818b86620e968c42465668ac67d35304b8a"),
    "lean_4_33_inductive_kernel": ("results/research/evidence/proof-parameter-contract-review/lean4-v4.33.0-inductive.cpp", 63881,
                                   "3f7a71c8f5081b41a9a8e625ca555d6dd41b0451c8d6671b828679fd533dc78b"),
    "lean_4_33_inductive_provenance": ("results/research/evidence/proof-parameter-contract-review/lean4-v4.33.0-inductive.json", 88880,
                                       "fccf15a9f4776d55996112cdcb5a2dfb140d180f106f302e1732635923118fa1"),
}

FINDINGS = {
    "KIOTA_SUPPLIED_TYPE_IS_ONLY_SHAPE_CHECKED": ("kiota_parser", [[484, 579]],
                                                   ("let typ = self.require_expr", "pi_telescope_len(&typ)", "ConstantInfo::Recursor")),
    "KIOTA_REDUCTION_CONSUMES_DECLARED_TYPE_METADATA": ("kiota_type_checker", [[4273, 5251]],
                                                          ("fn try_iota", "fn nested_rec_for_type", "fn minor_index_from_type", "fn mk_rec_call")),
    "KIOTA_HAS_REQUIRED_TERM_OPERATIONS": ("kiota_expression", [[130, 160], [415, 653]],
                                            ("loose_bvar_range", "pub fn shift", "pub fn instantiate", "pub fn pi")),
    "KIOTA_HAS_REQUIRED_TYPING_RELATION": ("kiota_type_checker", [[1740, 1946], [3747, 4022]],
                                            ("fn ensure_pi", "pub fn infer_type", "pub fn is_def_eq", "ExprData::Pi(_, t1, b1)")),
    "KIOTA_HAS_REQUIRED_UNIVERSE_OPERATIONS": ("kiota_level", [[14, 153], [225, 250]],
                                                ("pub fn zero", "pub fn param", "pub fn subst_map", "pub fn is_def_eq")),
    "LEAN_SOURCE_DEFINES_COMPLETE_BASE_CONSTRUCTION": ("lean_4_33_inductive_kernel", [[478, 790]],
                                                        ("init_elim_level", "mk_rec_infos", "declare_recursors", "mk_pi(minors")),
    "LEAN_SOURCE_DEFINES_COMPLETE_NESTED_CONSTRUCTION": ("lean_4_33_inductive_kernel", [[887, 1090], [1093, 1259]],
                                                          ("elim_nested_inductive_fn", "replace_if_nested", "mk_aux_rec_name_map", "restore_nested")),
}

FIXTURE_BINDINGS = {
    "ORDINARY_INDEXED_EQ": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/tests/fixtures/067_eqRec.accept.ndjson", 3369,
                            "693007cd24f0763cc6c7776840bdc05539645a0e35897af2688bde984f2551e2",
                            {"blocks": 1, "multi_type_blocks": 0, "nested_blocks": 0, "max_motives": 1, "max_minors": 1, "max_rule_count": 1}),
    "NESTED_TWO_SAME_CONTAINER_SPECIALIZATIONS": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/tests/fixtures/lean-value-two-list-specializations.accept.ndjson", 550476,
                                                  "a7df00d85687467150799db404d7069763370823b2c12a8748ca1ba0ebe23ce1",
                                                  {"blocks": 41, "multi_type_blocks": 0, "nested_blocks": 1, "max_motives": 4, "max_minors": 8, "max_rule_count": 3}),
    "PARAMETRIC_DEEP_NESTED": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/tests/fixtures/lean-doc-block-nested-rec-param-shift.accept.ndjson", 796409,
                               "a7ad63de1347bc87000d0c84e769681b217dfbd162ddfec4569b2f43d2219702",
                               {"blocks": 45, "multi_type_blocks": 0, "nested_blocks": 2, "max_motives": 9, "max_minors": 19, "max_rule_count": 11}),
    "MUTUAL_AND_NESTED_LCNF": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/tests/fixtures/lean-compiler-lcnf-code-ctorelim.accept.ndjson", 905093,
                               "04e2d1d4de32bdc3501f9e2c29989121728f2e0f20c94a51177be76093a4f152",
                               {"blocks": 67, "multi_type_blocks": 1, "nested_blocks": 2, "max_motives": 6, "max_minors": 19, "max_rule_count": 15}),
}

PAIR_BINDINGS = {
    "pair_audit": ("results/research/acceptance-impact-pilot-1/pair-audit.json", 6097,
                   "bc3e9f48fd17f3c6ebcf96efa8d7b98133f88fc6a7b09f9b1699a8e549379007"),
    "contract": ("results/research/recursor-type-trust-boundary-1/regression-contract.json", 3219,
                 "eb14c51345b43ad5898344c183dfd651f805e08e6ec0e5fbb84e296be1fb8c2b"),
    "candidate": ("corpus/generated/nanoda-gen-7b603be7dc87-valid-aux-type.ndjson", 6332,
                  "13900d3c26371111800a6c85ba8a9cc3d472beb384cf2c5fde574b8a9e7f36bd"),
    "control": ("corpus/generated/nanoda-gen-7b603be7dc87-valid-control.ndjson", 6332,
                "3b66763082822a74a203fb4dda773ff473e853e73077b8f564c603b56e9610ae"),
}


class DesignError(ValueError):
    """The design package or its durable closure state is invalid."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DesignError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda token: (_ for _ in ()).throw(
                               DesignError(f"non-finite JSON value: {token}")))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DesignError(f"cannot load {path}: {error}") from error
    if not isinstance(value, dict):
        raise DesignError(f"JSON root is not an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe(root: Path, relative: Any) -> Path:
    if (not isinstance(relative, str) or not relative or Path(relative).is_absolute()
            or ".." in Path(relative).parts):
        raise DesignError("path must be repository-relative")
    root = root.resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise DesignError(f"path escapes repository: {relative}") from error
    return path


def _expected_binding(expected: tuple[str, int, str] | tuple[str, int, str, dict[str, int]]) -> dict[str, Any]:
    return {"path": expected[0], "bytes": expected[1], "sha256": expected[2]}


def _verify_binding(root: Path, row: Any,
                    expected: tuple[str, int, str] | tuple[str, int, str, dict[str, int]]) -> Path:
    wanted = _expected_binding(expected)
    if row != wanted:
        raise DesignError(f"binding differs: {row!r}")
    path = _safe(root, wanted["path"])
    if (not path.is_file() or path.is_symlink() or path.stat().st_size != wanted["bytes"]
            or sha256(path) != wanted["sha256"]):
        raise DesignError(f"bound file differs: {wanted['path']}")
    return path


def _range_text(path: Path, ranges: list[list[int]]) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    chunks = []
    for start, end in ranges:
        if start < 1 or end < start or end > len(lines):
            raise DesignError(f"invalid source line range: {path}:{start}-{end}")
        chunks.append("\n".join(lines[start - 1:end]))
    return "\n".join(chunks)


def validate_source_value(source: dict[str, Any], root: Path = ROOT) -> None:
    if (source.get("schema_version") != 1 or source.get("item_id") != ITEM
            or source.get("status") != "COMPLETE"
            or source.get("target_revision") != "9fa2c297dd700fe8fd1712a86bdbb258e1c01c42"):
        raise DesignError("source inventory identity differs")
    bindings = source.get("source_bindings")
    if not isinstance(bindings, dict) or set(bindings) != set(SOURCE_BINDINGS):
        raise DesignError("source binding roles differ")
    paths = {role: _verify_binding(root, bindings[role], expected)
             for role, expected in SOURCE_BINDINGS.items()}
    provenance = load_json(paths["lean_4_33_inductive_provenance"])
    if (provenance.get("path") != "src/kernel/inductive.cpp"
            or provenance.get("sha") != "118ed7badeb3940a4a2dc1dd6c2e11ca5a50c664"
            or provenance.get("size") != 63881):
        raise DesignError("official kernel source provenance differs")
    findings = source.get("source_findings")
    if not isinstance(findings, list) or len(findings) != len(FINDINGS):
        raise DesignError("source findings differ")
    by_id = {row.get("id"): row for row in findings if isinstance(row, dict)}
    if set(by_id) != set(FINDINGS):
        raise DesignError("source finding identities differ")
    for finding_id, (role, ranges, tokens) in FINDINGS.items():
        row = by_id[finding_id]
        if (row.get("binding_role") != role or row.get("line_ranges") != ranges
                or not row.get("finding")):
            raise DesignError(f"source finding differs: {finding_id}")
        text = _range_text(paths[role], ranges)
        for token in tokens:
            if token not in text:
                raise DesignError(f"source locator omits {token}: {finding_id}")
    conclusion = source.get("conclusion", {})
    if (conclusion.get("complete_design_supported") is not True
            or conclusion.get("authority_class") != "PINNED_REFERENCE_ALGORITHM_FOR_LOCAL_KIOTA_IMPORT_POLICY"
            or source.get("kiota_native_capability_map", {}).get("missing_source_or_authority") != []):
        raise DesignError("source conclusion differs")
    if source.get("observations") != {
        "local_source_files_inspected": 9, "checker_attempts": 0, "builds": 0,
        "production_edits": 0, "generated_scientific_bytes": 0,
        "network_requests": 0, "external_actions": 0,
    }:
        raise DesignError("source observations differ")


def validate_design_value(design: dict[str, Any]) -> None:
    if (design.get("schema_version") != 1 or design.get("item_id") != ITEM
            or design.get("status") != "COMPLETE"
            or design.get("outcome") != "VALIDATED_COMPLETE_KIOTA_DESIGN"):
        raise DesignError("construction design identity differs")
    authority = design.get("authority", {})
    if (authority.get("class") != "SOURCE_BOUND_LOCAL_IMPORT_POLICY"
            or "not a universal" not in authority.get("claim", "")):
        raise DesignError("construction authority boundary differs")
    input_contract = design.get("input_contract", {})
    stage = input_contract.get("stage", "")
    if "before any recursor record" not in stage:
        raise DesignError("construction input stage permits circular recursor trust")
    if "serialized recursor type" not in input_contract.get("untrusted_inputs", []):
        raise DesignError("construction trusts the serialized type")
    base = design.get("base_construction", {})
    base_ids = [row.get("id") for row in base.get("steps", []) if isinstance(row, dict)]
    if base.get("source_lines") != [[478, 790]] or base_ids != [
        "B1_ELIMINATION_LEVEL", "B2_MOTIVES", "B3_CONSTRUCTOR_FIELDS",
        "B4_RECURSIVE_HYPOTHESES", "B5_MINORS", "B6_TARGET_RECURSOR_TYPES",
        "B7_DERIVED_METADATA",
    ]:
        raise DesignError("base construction stages differ")
    base_text = " ".join(row.get("rule", "") for row in base["steps"])
    for token in ("[elim, declaration...]", "Motive order", "Append all fields first",
                  "Pi params", "Do not use serialized counts"):
        if token not in base_text:
            raise DesignError(f"base construction omits {token}")
    nested = design.get("nested_construction", {})
    nested_ids = [row.get("id") for row in nested.get("steps", []) if isinstance(row, dict)]
    if nested.get("source_lines") != [[887, 1090], [1093, 1259]] or nested_ids != [
        "N1_DISCOVER", "N2_SPECIALIZE", "N3_CLOSE_WORKLIST", "N4_BUILD",
        "N5_RESTORE", "N6_RECHECK",
    ]:
        raise DesignError("nested construction stages differ")
    nested_text = " ".join(row.get("rule", "") for row in nested["steps"])
    for token in ("breadth-first", "copy every J member", "discovery order",
                  ".rec_1", "never falls back"):
        if token not in nested_text:
            raise DesignError(f"nested construction omits {token}")
    adjudication = design.get("comparison_adjudication", {})
    selected = adjudication.get("definitional_equality_then_replacement", {})
    if (adjudication.get("structural_equality", {}).get("selected") is not False
            or adjudication.get("normalized_structural_equality", {}).get("selected") is not False
            or selected.get("selected") is not True):
        raise DesignError("comparison selection differs")
    rule = selected.get("rule", "")
    for token in ("no current-block recursors", "Alpha-normalize", "Checker::is_def_eq",
                  "False is REJECT", "fail-closed", "only the reconstructed type"):
        if token not in rule:
            raise DesignError(f"comparison rule omits {token}")
    order = " ".join(design.get("transactional_import_order", []))
    for token in ("uncommitted block", "without exposing supplied", "fail closed",
                  "reconstructed types"):
        if token not in order:
            raise DesignError(f"transactional import order omits {token}")
    if design.get("regression_effect", {}).get("candidate", {}).get("expected") != "REJECT" \
            or design.get("regression_effect", {}).get("control", {}).get("expected") != "ACCEPT":
        raise DesignError("design regression effect differs")


def _fixture_profile(path: Path) -> dict[str, int]:
    blocks = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            value = json.loads(line)
            if "inductive" in value:
                blocks.append(value["inductive"])
    return {
        "blocks": len(blocks),
        "multi_type_blocks": sum(len(block.get("types", [])) > 1 for block in blocks),
        "nested_blocks": sum(len(block.get("recs", [])) > len(block.get("types", [])) for block in blocks),
        "max_motives": max(rec["numMotives"] for block in blocks for rec in block.get("recs", [])),
        "max_minors": max(rec["numMinors"] for block in blocks for rec in block.get("recs", [])),
        "max_rule_count": max(len(rec.get("rules", [])) for block in blocks for rec in block.get("recs", [])),
    }


def validate_fixtures_value(fixtures: dict[str, Any], root: Path = ROOT) -> None:
    if (fixtures.get("schema_version") != 1 or fixtures.get("item_id") != ITEM
            or fixtures.get("status") != "FROZEN_FOR_LATER_IMPLEMENTATION"):
        raise DesignError("fixture manifest identity differs")
    rows = fixtures.get("accepted_fixture_bindings")
    if not isinstance(rows, list) or len(rows) != len(FIXTURE_BINDINGS):
        raise DesignError("accepted fixture set differs")
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    if set(by_id) != set(FIXTURE_BINDINGS):
        raise DesignError("accepted fixture identities differ")
    for fixture_id, expected in FIXTURE_BINDINGS.items():
        row = by_id[fixture_id]
        path = _verify_binding(root, {key: row.get(key) for key in ("path", "bytes", "sha256")}, expected)
        if row.get("expected_after_repair") != "ACCEPT" or row.get("static_profile") != expected[3]:
            raise DesignError(f"fixture expectation or profile differs: {fixture_id}")
        if _fixture_profile(path) != expected[3]:
            raise DesignError(f"fixture bytes no longer have the frozen profile: {fixture_id}")
    inherited = fixtures.get("inherited_regression", {})
    for role, expected in PAIR_BINDINGS.items():
        row = inherited.get(role, {})
        _verify_binding(root, {key: row.get(key) for key in ("path", "bytes", "sha256")}, expected)
    if (inherited.get("candidate", {}).get("expected_after_repair") != "REJECT"
            or inherited.get("control", {}).get("expected_after_repair") != "ACCEPT"
            or inherited.get("only_scalar_difference") != {
                "pointer": "/104/inductive/recs/0/type", "candidate": 68, "control": 49}
            or inherited.get("same_manifest_pi_arity") != 5
            or inherited.get("candidate_fifth_domain") != "LALNest"
            or inherited.get("control_fifth_domain") != "LALWrap LALNest"):
        raise DesignError("inherited regression contract differs")
    audit = load_json(root / PAIR_BINDINGS["pair_audit"][0]).get("pair", {})
    if audit.get("scalar_differences") != [{"candidate": 68, "control": 49,
                                             "pointer": "/104/inductive/recs/0/type"}]:
        raise DesignError("pair audit no longer proves the exact scalar delta")
    if fixtures.get("observations") != {
        "fixture_bytes_generated": 0, "checker_attempts": 0, "builds": 0,
        "network_requests": 0, "external_actions": 0,
    }:
        raise DesignError("fixture observations differ")


def validate_audit_value(audit: dict[str, Any]) -> None:
    if (audit.get("schema_version") != 1 or audit.get("item_id") != ITEM
            or audit.get("status") != "PASS"
            or audit.get("audit_class") != "INDEPENDENT_MECHANICAL_AND_ADVERSARIAL_DESIGN_AUDIT"):
        raise DesignError("design audit identity differs")
    expected = {
        "SOURCE_IDENTITY", "BASE_CONSTRUCTION_COMPLETENESS", "NESTED_CONSTRUCTION_COMPLETENESS",
        "NO_CIRCULAR_TYPE_TRUST", "COMPARISON_RELATION", "BINDERINFO_BOUNDARY",
        "REGRESSION_DISCRIMINATION", "ACCEPTANCE_PRESERVATION_COVERAGE", "ACTION_BOUNDARY",
    }
    checks = audit.get("checks")
    by_id = {row.get("id"): row for row in checks if isinstance(row, dict)} if isinstance(checks, list) else {}
    if set(by_id) != expected or any(row.get("result") != "PASS" for row in by_id.values()):
        raise DesignError("design audit checks differ")
    verdict = audit.get("verdict", {})
    if (verdict.get("complete_design") is not True
            or verdict.get("implementation_item_ready") is not True
            or verdict.get("production_edit_authorized_by_this_item") is not False
            or verdict.get("remaining_design_boundary") is not None):
        raise DesignError("design audit verdict differs")


def validate_result_value(result: dict[str, Any]) -> None:
    if (result.get("schema_version") != 1 or result.get("item_id") != ITEM
            or result.get("status") != "COMPLETE"
            or result.get("outcome") != "VALIDATED_COMPLETE_KIOTA_DESIGN"
            or result.get("selected_relation") != "POSITIONAL_LEVEL_ALPHA_NORMALIZATION_THEN_DEFINITIONAL_EQUALITY_THEN_REPLACEMENT"):
        raise DesignError("result identity or selected relation differs")
    boundary = result.get("implementation_boundary", {})
    if (boundary.get("implementation_item_ready") is not True
            or boundary.get("production_edit_authorized_by_this_item") is not False
            or SUCCESSOR not in boundary.get("required_next_gate", "")):
        raise DesignError("result implementation boundary differs")
    if result.get("regression_requirement") != {
        "candidate": "REJECT", "control": "ACCEPT", "accepted_fixture_count": 4,
        "pair_replacement": "FORBIDDEN", "completed_attempt_reuse_as_new_result": "FORBIDDEN",
    }:
        raise DesignError("result regression requirement differs")
    limits = " ".join(result.get("claim_limits", []))
    for token in ("not a universal", "does not establish a checker defect", "No declaration-validation", "No external action"):
        if token not in limits:
            raise DesignError(f"result claim limits omit {token}")
    observations = result.get("observations", {})
    if observations != {
        "local_source_files_inspected": 9, "checker_attempts": 0, "builds": 0,
        "production_edits": 0, "generated_scientific_bytes": 0,
        "network_requests": 0, "external_actions": 0,
    }:
        raise DesignError("result observations differ")


def validate_package(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    validate_source_value(load_json(root / SOURCE), root)
    validate_design_value(load_json(root / DESIGN))
    validate_fixtures_value(load_json(root / FIXTURES), root)
    validate_audit_value(load_json(root / AUDIT))
    validate_result_value(load_json(root / RESULT))
    closure = load_json(root / CLOSURE)
    if (closure.get("item_id") != ITEM or closure.get("status") != "COMPLETE"
            or closure.get("outcome") != "VALIDATED_COMPLETE_KIOTA_DESIGN"
            or closure.get("successor") != SUCCESSOR
            or closure.get("implementation_item_ready") is not True
            or closure.get("production_edit_authorized_by_this_item") is not False
            or any(closure.get("observations", {}).values())):
        raise DesignError("closure differs")
    report = (root / REPORT).read_text(encoding="utf-8")
    for token in ("VALIDATED_COMPLETE_KIOTA_DESIGN", "ordinary, mutual and nested",
                  "definitional equality", "installs only the reconstructed", "candidate reject",
                  "No checker was launched", SUCCESSOR):
        if token.lower() not in report.lower():
            raise DesignError(f"report omits {token}")
    return {"status": "PASS", "item_id": ITEM, "outcome": "VALIDATED_COMPLETE_KIOTA_DESIGN"}


def _validate_final_state(root: Path) -> None:
    work = load_json(root / WORK)
    if (work.get("item_id") != ITEM or work.get("status") != "COMPLETE"
            or work.get("current_phase") != "COMPLETE"
            or work.get("result", {}).get("outcome") != "VALIDATED_COMPLETE_KIOTA_DESIGN"
            or work.get("result", {}).get("successor") != SUCCESSOR):
        raise DesignError("final work record differs")
    observations = work.get("observations", {})
    if observations != {
        "local_source_files_inspected": 9, "checker_attempts": 0, "builds": 0,
        "production_edits": 0, "generated_scientific_bytes": 0,
        "network_requests": 0, "external_actions": 0,
    }:
        raise DesignError("final work observations differ")
    protocol = load_json(root / PROTOCOL)
    if (protocol.get("item_id") != ITEM or protocol.get("status") != "COMPLETE"
            or protocol.get("current_phase") != "COMPLETE"
            or protocol.get("result", {}).get("outcome") != "VALIDATED_COMPLETE_KIOTA_DESIGN"
            or protocol.get("result", {}).get("successor") != SUCCESSOR):
        raise DesignError("final protocol differs")
    queue = load_json(root / QUEUE)
    if queue.get("selected_item") != SUCCESSOR or queue.get("handoff", {}).get("status") != "EXECUTABLE":
        raise DesignError("final queue selection differs")
    items = {row.get("id"): row for row in queue.get("items", []) if isinstance(row, dict)}
    current, successor = items.get(ITEM), items.get(SUCCESSOR)
    if (not isinstance(current, dict) or current.get("status") != "COMPLETE"
            or current.get("closure", {}).get("outcome") != "SUCCESS"
            or not isinstance(successor, dict) or successor.get("status") != "READY"
            or successor.get("budget") is not None or successor.get("closure") is not None
            or any(row.get("status") == "ACTIVE" for row in items.values())):
        raise DesignError("final queue item states differ")
    review_binding = queue.get("strategic_review", {})
    if (review_binding.get("path") != REVIEW.as_posix()
            or sha256(root / REVIEW) != review_binding.get("sha256")):
        raise DesignError("closure strategic review binding differs")
    review = load_json(root / REVIEW)
    if (review.get("phase") != "CLOSURE" or review.get("stopped_item") != ITEM
            or review.get("selected_item") != SUCCESSOR
            or review.get("queue_sha256") != queue_digest(queue)):
        raise DesignError("closure strategic review differs")


def validate(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    result = validate_package(root)
    _validate_final_state(root)
    result["successor"] = SUCCESSOR
    result["checker_attempts"] = 0
    result["production_edits"] = 0
    result["external_actions"] = 0
    return result
