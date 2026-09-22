"""Preparation and guarded execution for VALID-DEPENDENT-TERM-PILOT-1.

The checked-object decoder in this module is intentionally independent of the
generator's typing, normalization, shifting, substitution, and category code.
It implements only the frozen lean4export graph-to-AST receipt contract.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Callable, Iterator

from lib.cvc_prep import committed, require, safe
from lib.metamorphic_pilot_runner import classify, run_supervised


ROOT = Path(__file__).resolve().parents[1]
ITEM = "VALID-DEPENDENT-TERM-PILOT-1"
BASE = "results/research/valid-dependent-term-pilot-1"
DESIGN = BASE + "/design.json"
PROTOCOL = BASE + "/protocol.json"
SOURCE_REVIEW = BASE + "/source-reuse-review.json"
WORK = BASE + "/work-record.json"
CORPUS = "corpus/valid-dependent-term-pilot-1"
CORPUS_MANIFEST = BASE + "/corpus-manifest.json"
EXECUTION_MANIFEST = BASE + "/execution-manifest.json"
PLAN = "docs/research/VALID_DEPENDENT_TERM_PILOT_1_PLAN.md"
QUEUE = "config/research-queue.json"
STATUS = "docs/RESEARCH_STATUS.md"
MODULE = "lib/valid_dependent_term_pilot.py"
GENERATOR = "lib/valid_dependent_term_generator.py"
AUDITOR = "lib/valid_dependent_term_audit.py"
PREPARE_SCRIPT = "scripts/prepare-valid-dependent-term-pilot-1"
EXECUTE_SCRIPT = "scripts/execute-valid-dependent-term-pilot-1"
VALIDATE_SCRIPT = "scripts/validate-valid-dependent-term-pilot-1"
GENERATOR_SCRIPT = "scripts/generate-valid-dependent-term-pilot-1"
TEST = "tests/test_valid_dependent_term_pilot.py"
GENERATOR_TEST = "tests/test_valid_dependent_term_generator.py"
AUDITOR_TEST = "tests/test_valid_dependent_term_audit.py"
AUDIT_SCRIPT = "scripts/audit-valid-dependent-term-pilot-1"

REPOSITORY_INPUTS = (PLAN, DESIGN, PROTOCOL, SOURCE_REVIEW, WORK, QUEUE, STATUS)
CONTROLLER_TOOLING = (
    MODULE, GENERATOR, AUDITOR, PREPARE_SCRIPT, EXECUTE_SCRIPT, VALIDATE_SCRIPT,
    GENERATOR_SCRIPT, AUDIT_SCRIPT, TEST, GENERATOR_TEST, AUDITOR_TEST,
    "lib/metamorphic_pilot_runner.py",
)

EXTERNAL_SOURCE_LOCKS = (
    ("external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1/Main.lean",
     "bd8e350903f1382b25fe767f9086dd9882000f01085f7046ea06545e7848842a"),
    ("external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1/Export.lean",
     "1c60d571dc24bfb99e7cbb218d8d489919bbc871238f6db9c76248521fbea998"),
    ("external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1/lakefile.toml",
     "54dde3aba280f32035c882dcd2f2039e738e20ed45ca538337b65cc69c02f7df"),
    ("external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1/lean-toolchain",
     "7dc000621e0046d1aada809e2b7177e64454645cf4c741e9daaf79c99ec2e7a2"),
    ("external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1/lake-manifest.json",
     "f1b9d60d0ebd46f79f48e6833deefeaa835fdee12b4078241635ee14b6a0f07a"),
    ("external/lean-kernel-arena/_build/checkers/official/src/Main.lean",
     "f0c209172f79e2b0b6599f7acc989e15a158f4118a6ddab0a567773b75f333bb"),
    ("external/lean-kernel-arena/_build/checkers/official/src/lean-toolchain",
     "302cd63c54178885b89e669f33b38f12f4dd7ae7e5cac537b3203e3768d8fb2b"),
    ("external/lean-kernel-arena/_build/checkers/official/src/lakefile.toml",
     "e4ef28e6b2a315349e38c35aa2e5a70022d9d5b284f9d4184acadd62cd88cd38"),
    ("external/lean-kernel-arena/_build/checkers/official/src/lake-manifest.json",
     "91cf35681c65b549cfb2e86e2af9d2012f6ddadcc9d7dc9631a2496f6d7ae076"),
    ("external/lean-kernel-arena/_build/checkers/official/src/.lake/packages/lean4export/Export/Parse.lean",
     "1f943b5cc776eece6d528937b976509c8bd57d10bc69a39b1c119bfb6d664286"),
    ("external/lean-kernel-arena/_build/checkers/official/src/.lake/packages/lean4export/format_ndjson.md",
     "f82a21e17e4258a1043895d0653ea4333bef8cb07aad2e3d6c1fc4be52b138e3"),
    ("external/lean-kernel-arena/_build/checkers/nanoda/src/src/parser.rs",
     "251a879b01ec5405d27475c6bea809f72ce51be9501ec61b28a7f965b0855ac4"),
    ("external/lean-kernel-arena/_build/checkers/nanoda/src/src/tc.rs",
     "622b5aaf04b478485ca462b4938f3576c8da20e11bdf53b32f6e8b9021403efc"),
    ("external/lean-kernel-arena/_build/checkers/nanoda/src/src/main.rs",
     "245ceaef34e8925cacaa3c5b99ce096a8c744710ce1f9184423e5a0333e8b35a"),
    ("external/lean-kernel-arena/_build/checkers/nanoda/src/Cargo.toml",
     "04b9d07cfa907f587abc7541b1bf400960e54d6df596d07c0a50c4ce1808d375"),
    ("external/lean-kernel-arena/_build/checkers/nanoda/src/Cargo.lock",
     "5c99446c237555e0d4cda4007cda4d576ea3dbba895b2b0aacde424cb21ad688"),
)

PS_SHA256 = "57b93ca9ccbeb77e261f0792e9722eb44189dd81a81e26a90280a73a2f5a73bb"
LAKE_429_SHA256 = "4b95ad05f8a6d3962d3a95d0a6b699a54a3803a1a3b1b69d70b578e819a46e6a"
LEAN_429_SHA256 = "b48bc5ab229bd8b320a224b87e20fc428dba6fa8a1c054bd4fa6def846e19997"


class PilotError(ValueError):
    pass


class BridgeError(PilotError):
    pass


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PilotError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise PilotError(f"non-finite JSON value: {value}")


def load_json(path: Path | str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"),
                          object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PilotError(f"cannot load JSON {path}: {error}") from error


def canonical_bytes(value: Any, *, newline: bool = False) -> bytes:
    try:
        data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise PilotError(f"value is not canonical JSON: {error}") from error
    return data + (b"\n" if newline else b"")


def object_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _relative(path: Path, root: Path = ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise PilotError(f"path is outside repository: {path}") from error


def file_binding(path: Path, root: Path = ROOT) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise PilotError(f"bound file is absent or a symlink: {path}")
    return {"path": _relative(path, root), "bytes": path.stat().st_size,
            "sha256": file_sha256(path)}


def absolute_binding(path: Path) -> dict[str, Any]:
    path = path.resolve()
    if not path.is_file() or path.is_symlink():
        raise PilotError(f"absolute bound file is absent or a symlink: {path}")
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": file_sha256(path)}


def verify_absolute_binding(row: Any) -> Path:
    if (not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}
            or not isinstance(row["path"], str) or not Path(row["path"]).is_absolute()
            or type(row["bytes"]) is not int or row["bytes"] < 0
            or not isinstance(row["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None):
        raise PilotError("invalid absolute file binding")
    path = Path(row["path"])
    if (not path.is_file() or path.is_symlink() or path.stat().st_size != row["bytes"]
            or file_sha256(path) != row["sha256"]):
        raise PilotError("stale absolute file binding: " + row["path"])
    return path


def verify_binding(row: Any, root: Path = ROOT) -> Path:
    if (not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}
            or type(row["bytes"]) is not int or row["bytes"] < 0
            or not isinstance(row["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None):
        raise PilotError("invalid file binding")
    path = safe(root, row["path"])
    if (not path.is_file() or path.is_symlink() or path.stat().st_size != row["bytes"]
            or file_sha256(path) != row["sha256"]):
        raise PilotError("stale file binding: " + row["path"])
    return path


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if path.is_symlink() or temporary.is_symlink():
        raise PilotError(f"refuse symlink JSON output: {path}")
    with temporary.open("xb") as stream:
        stream.write(canonical_bytes(value, newline=True))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _nat(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise BridgeError(f"{label} must be a nonnegative integer")
    return value


def _exact_object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise BridgeError(f"{label} fields differ")
    return value


class ExportGraph:
    """Strict decoder for the frozen, constant-free scientific fragment."""

    def __init__(self, data: bytes, *, lean_revision: str, expected_name: str):
        if type(data) is not bytes or not data or not data.endswith(b"\n"):
            raise BridgeError("export must be nonempty bytes ending in LF")
        self.rows: list[dict[str, Any]] = []
        for line_number, raw in enumerate(data.splitlines(), 1):
            if not raw:
                raise BridgeError(f"blank export record at line {line_number}")
            try:
                row = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_nonfinite)
            except (UnicodeError, json.JSONDecodeError, PilotError) as error:
                raise BridgeError(f"invalid export record {line_number}: {error}") from error
            if not isinstance(row, dict):
                raise BridgeError(f"export record {line_number} is not an object")
            self.rows.append(row)
        if set(self.rows[0]) != {"meta"}:
            raise BridgeError("first export record must contain only meta")
        self.metadata = _exact_object(self.rows[0]["meta"],
                                      {"exporter", "format", "lean"}, "metadata")
        if self.metadata != {
            "exporter": {"name": "lean4export", "version": "3.1.0"},
            "format": {"version": "3.1.0"},
            "lean": {"githash": lean_revision, "version": "4.29.1"},
        }:
            raise BridgeError("export metadata differs from producer profile")
        self.names: dict[int, str] = {0: ""}
        self.levels: dict[int, int] = {0: 0}
        self.expressions: dict[int, tuple[str, Any]] = {}
        self.declaration: dict[str, Any] | None = None
        self.expected_name = expected_name
        self._parse_records()

    def _parse_records(self) -> None:
        for number, row in enumerate(self.rows[1:], 2):
            if "in" in row:
                self._parse_name(row)
            elif "il" in row:
                self._parse_level(row)
            elif "ie" in row:
                self._parse_expression(row)
            elif "def" in row:
                if self.declaration is not None:
                    raise BridgeError("multiple declaration records")
                self.declaration = self._parse_definition(row)
            else:
                raise BridgeError(f"unknown or forbidden export record at line {number}")
        if self.declaration is None:
            raise BridgeError("exactly one definition record is required")

    def _parse_name(self, row: dict[str, Any]) -> None:
        index = _nat(row.get("in"), "name id")
        if index == 0 or index in self.names:
            raise BridgeError(f"duplicate or reserved name id {index}")
        tags = set(row) - {"in"}
        if tags == {"str"}:
            value = _exact_object(row["str"], {"pre", "str"}, "string name")
            prefix = _nat(value["pre"], "name prefix")
            component = value["str"]
            if not isinstance(component, str) or not component:
                raise BridgeError("name string must be nonempty")
        elif tags == {"num"}:
            value = _exact_object(row["num"], {"pre", "i"}, "numeric name")
            prefix = _nat(value["pre"], "name prefix")
            component = str(_nat(value["i"], "name numeral"))
        else:
            raise BridgeError("name record tag differs")
        if prefix not in self.names:
            raise BridgeError("name prefix is unresolved")
        self.names[index] = component if not self.names[prefix] else self.names[prefix] + "." + component

    def _parse_level(self, row: dict[str, Any]) -> None:
        if set(row) != {"il", "succ"}:
            raise BridgeError("only closed successor levels are admitted")
        index = _nat(row["il"], "level id")
        predecessor = _nat(row["succ"], "successor predecessor")
        if index == 0 or index in self.levels:
            raise BridgeError(f"duplicate or reserved level id {index}")
        if predecessor not in self.levels:
            raise BridgeError("successor predecessor is unresolved")
        self.levels[index] = self.levels[predecessor] + 1

    def _parse_expression(self, row: dict[str, Any]) -> None:
        index = _nat(row.get("ie"), "expression id")
        if index in self.expressions:
            raise BridgeError(f"duplicate expression id {index}")
        tags = set(row) - {"ie"}
        if len(tags) != 1:
            raise BridgeError("expression record must have exactly one tag")
        tag = next(iter(tags))
        if tag not in {"bvar", "sort", "app", "lam", "forallE", "letE"}:
            raise BridgeError(f"forbidden expression tag: {tag}")
        value = row[tag]
        if tag == "bvar":
            value = _nat(value, "bound-variable index")
        elif tag == "sort":
            value = _nat(value, "sort level reference")
            if value not in self.levels:
                raise BridgeError("sort level reference is unresolved")
        elif tag == "app":
            value = _exact_object(value, {"fn", "arg"}, "application")
            _nat(value["fn"], "application function")
            _nat(value["arg"], "application argument")
        elif tag in {"lam", "forallE"}:
            value = _exact_object(value, {"name", "type", "body", "binderInfo"}, tag)
            name = _nat(value["name"], f"{tag} name")
            if name not in self.names:
                raise BridgeError(f"{tag} binder name is unresolved")
            _nat(value["type"], f"{tag} domain")
            _nat(value["body"], f"{tag} body")
            if value["binderInfo"] != "default":
                raise BridgeError(f"{tag} binder info is not default")
        else:
            value = _exact_object(value, {"name", "type", "value", "body", "nondep"}, "let")
            name = _nat(value["name"], "let name")
            if name not in self.names:
                raise BridgeError("let binder name is unresolved")
            _nat(value["type"], "let type")
            _nat(value["value"], "let value")
            _nat(value["body"], "let body")
            if value["nondep"] is not False:
                raise BridgeError("let nondep must be false")
        self.expressions[index] = (tag, value)

    def _parse_definition(self, row: dict[str, Any]) -> dict[str, Any]:
        if set(row) != {"def"}:
            raise BridgeError("definition record fields differ")
        value = _exact_object(row["def"],
                              {"all", "hints", "levelParams", "name", "safety", "type", "value"},
                              "definition")
        name = _nat(value["name"], "definition name")
        if name not in self.names or self.names[name] != self.expected_name:
            raise BridgeError("unexpected definition name")
        if value["levelParams"] != []:
            raise BridgeError("definition level parameters are not empty")
        if value["hints"] != "opaque" or value["safety"] != "safe":
            raise BridgeError("definition hints or safety differ")
        if (not isinstance(value["all"], list)
                or any(type(entry) is not int or entry not in self.names for entry in value["all"])
                or value["all"] != [name]):
            raise BridgeError("definition dependency/name inventory differs")
        _nat(value["type"], "definition type")
        _nat(value["value"], "definition value")
        return value

    def expression(self, root: int) -> dict[str, Any]:
        visiting: set[int] = set()
        memo: dict[int, dict[str, Any]] = {}

        def visit(index: int, depth: int) -> dict[str, Any]:
            index = _nat(index, "expression reference")
            if index in visiting:
                raise BridgeError("cyclic expression graph")
            if index in memo:
                result = memo[index]
                self._closed(result, depth)
                return result
            if index not in self.expressions:
                raise BridgeError(f"unresolved expression reference {index}")
            visiting.add(index)
            tag, value = self.expressions[index]
            if tag == "bvar":
                result = {"tag": "bvar", "index": value}
                if value >= depth:
                    raise BridgeError("loose bound variable")
            elif tag == "sort":
                result = {"tag": "sort", "level": self.levels[value]}
            elif tag == "app":
                result = {"tag": "app", "function": visit(value["fn"], depth),
                          "argument": visit(value["arg"], depth)}
            elif tag in {"lam", "forallE"}:
                result = {"tag": "lam" if tag == "lam" else "pi",
                          "domain": visit(value["type"], depth),
                          "body": visit(value["body"], depth + 1)}
            else:
                result = {"tag": "let", "type": visit(value["type"], depth),
                          "value": visit(value["value"], depth),
                          "body": visit(value["body"], depth + 1)}
            visiting.remove(index)
            memo[index] = result
            return result

        return visit(root, 0)

    def _closed(self, expression: dict[str, Any], depth: int) -> None:
        tag = expression["tag"]
        if tag == "bvar":
            if expression["index"] >= depth:
                raise BridgeError("loose bound variable")
        elif tag == "sort":
            return
        elif tag == "app":
            self._closed(expression["function"], depth)
            self._closed(expression["argument"], depth)
        elif tag in {"lam", "pi"}:
            self._closed(expression["domain"], depth)
            self._closed(expression["body"], depth + 1)
        elif tag == "let":
            self._closed(expression["type"], depth)
            self._closed(expression["value"], depth)
            self._closed(expression["body"], depth + 1)

    def checked_receipt(self, case: dict[str, Any], *, case_binding: dict[str, Any],
                        audit_binding: dict[str, Any], source_binding: dict[str, Any],
                        export_binding: dict[str, Any]) -> dict[str, Any]:
        assert self.declaration is not None
        term = self.expression(self.declaration["value"])
        expected_type = self.expression(self.declaration["type"])
        if term != case.get("term"):
            raise BridgeError("reconstructed declaration value differs from frozen term")
        if expected_type != case.get("expected_type_nf"):
            raise BridgeError("reconstructed declaration type differs from frozen normalized type")
        return {
            "schema_version": 1,
            "item_id": ITEM,
            "case_id": case["case_id"],
            "category": case["category"],
            "category_index": case["category_index"],
            "declaration_name": self.expected_name,
            "case": case_binding,
            "audit": audit_binding,
            "source_module": source_binding,
            "export": export_binding,
            "metadata": self.metadata,
            "term_sha256": object_sha256(term),
            "expected_type_sha256": object_sha256(expected_type),
            "derivation_sha256": object_sha256(case["derivation"]),
            "reconstructed_value_sha256": object_sha256(term),
            "reconstructed_type_sha256": object_sha256(expected_type),
            "fragment_proof": {
                "allowed_expression_tags": ["app", "bvar", "forallE", "lam", "letE", "sort"],
                "binder_info": "default",
                "closed_bound_variables": True,
                "closed_numeric_successor_levels": True,
                "let_nondep": False,
                "level_parameters": [],
                "single_expected_definition": True,
            },
            "record_count": len(self.rows),
        }


def checked_object_receipt(data: bytes, case: dict[str, Any], design: dict[str, Any], *,
                           case_binding: dict[str, Any], audit_binding: dict[str, Any],
                           source_binding: dict[str, Any], export_binding: dict[str, Any]) -> dict[str, Any]:
    declaration = _declaration_name(case, design)
    graph = ExportGraph(data, lean_revision=design["producer_profile"]["lean_revision"],
                        expected_name=declaration)
    return graph.checked_receipt(case, case_binding=case_binding, audit_binding=audit_binding,
                                 source_binding=source_binding, export_binding=export_binding)


def _declaration_name(case: dict[str, Any], design: dict[str, Any]) -> str:
    category = case.get("category")
    index = case.get("category_index")
    if category not in design["case_contract"]["order"] or type(index) is not int or not 1 <= index <= 10:
        raise PilotError("case identity cannot form a declaration name")
    return f"ValidDependentTermPilot1.{category}{index:02d}"


def _case_order(design: dict[str, Any]) -> list[str]:
    return [f"vdtp1-{category}-{index:02d}"
            for category in design["case_contract"]["order"] for index in range(1, 11)]


def _validate_case_shape(case: Any, expected_id: str, design: dict[str, Any]) -> None:
    expected_keys = set(design["case_contract"]["exact_keys"])
    if not isinstance(case, dict) or set(case) != expected_keys:
        raise PilotError(f"case fields differ for {expected_id}")
    if case["case_id"] != expected_id or case["schema_version"] != 1:
        raise PilotError(f"case identity differs for {expected_id}")
    category, index = expected_id.removeprefix("vdtp1-").rsplit("-", 1)
    if (case["category"] != category or type(case["category_index"]) is not int
            or case["category_index"] != int(index)):
        raise PilotError(f"case category/ordinal differs for {expected_id}")
    expected_attempt = design["deterministic_selection"]["expected_selection_attempt"]
    if type(case["selection_attempt"]) is not int or case["selection_attempt"] != expected_attempt:
        raise PilotError(f"case selection attempt differs for {expected_id}")
    if not isinstance(case["case_seed_sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", case["case_seed_sha256"]) is None:
        raise PilotError(f"case seed binding differs for {expected_id}")


def ordered_matrix(design: dict[str, Any], artifacts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    order = _case_order(design)
    if set(artifacts) != set(order):
        raise PilotError("artifact inventory differs from exact 50 cases")
    result = []
    ordinal = 0
    for profile in design["observer_profiles"]:
        for case_id in order:
            ordinal += 1
            result.append({
                "ordinal": ordinal,
                "cell_id": f"{profile['id']}::{case_id}",
                "profile_id": profile["id"],
                "case_id": case_id,
                "artifact": artifacts[case_id],
            })
    if len(result) != 100:
        raise PilotError("matrix is not exactly 100 cells")
    return result


def _validate_design(root: Path = ROOT) -> dict[str, Any]:
    design = load_json(root / DESIGN)
    if (not isinstance(design, dict) or design.get("schema_version") != 1
            or design.get("item_id") != ITEM
            or design.get("design_id") != "valid-dependent-term-pilot-1.design.v1"):
        raise PilotError("design identity differs")
    contract = design.get("case_contract", {})
    if (contract.get("total") != 50 or contract.get("count_per_category") != 10
            or contract.get("order") != ["pi", "lambda", "application", "let", "mixed"]
            or contract.get("distinct_term_hashes") != 50):
        raise PilotError("frozen case contract differs")
    matrix = design.get("matrix", {})
    if matrix != {"adaptive_expansion": False, "artifacts": 50, "complete": True,
                  "observers": 2, "order": "observer profile order, then case order",
                  "ordered_cells": 100}:
        raise PilotError("frozen matrix contract differs")
    if [row.get("id") for row in design.get("observer_profiles", [])] != [
            "official-lean-4.33.0", "nanoda-6ae1f0c"]:
        raise PilotError("observer profile order differs")
    if design.get("process_safety", {}).get("attempt_caps") != "NONE":
        raise PilotError("persistent execution policy differs")
    return design


def _selected_active(root: Path = ROOT) -> None:
    queue = load_json(root / QUEUE)
    row = next((entry for entry in queue.get("items", []) if entry.get("id") == ITEM), None)
    if (queue.get("frontier_id") != "F-DISCOVERY-AND-CONFORMANCE"
            or queue.get("selected_item") != ITEM or not isinstance(row, dict)
            or row.get("status") != "ACTIVE" or row.get("budget") is not None):
        raise PilotError("pilot is not selected ACTIVE under persistent execution")
    work = load_json(root / WORK)
    if (work.get("item_id") != ITEM or work.get("status") != "ACTIVE"
            or work.get("owner") != "root"):
        raise PilotError("work record does not bind the root ACTIVE owner")


def _committed_inputs(root: Path = ROOT, *, include_generated: bool = False) -> None:
    for relative in (*REPOSITORY_INPUTS, *CONTROLLER_TOOLING):
        committed(root, relative)
    if include_generated:
        committed(root, CORPUS_MANIFEST)
        committed(root, EXECUTION_MANIFEST)


def _git_revision(path: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path,
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise PilotError(f"cannot resolve source revision: {path}") from error


def _external_environment(design: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    producer_profile = design["producer_profile"]
    arena = root / "external/lean-kernel-arena"
    exporter_source = arena / "_build/lean4export/leanprover_lean4_v4.29.1"
    nanoda_source = arena / "_build/checkers/nanoda/src"
    official_importer = arena / "_build/checkers/official/src/.lake/packages/lean4export"
    if _git_revision(arena) != producer_profile["arena_revision"]:
        raise PilotError("Arena revision differs")
    if _git_revision(exporter_source) != producer_profile["source_revision"]:
        raise PilotError("lean4export source revision differs")
    nanoda = next(row for row in design["observer_profiles"] if row["id"] == "nanoda-6ae1f0c")
    if _git_revision(nanoda_source) != nanoda["source_revision"]:
        raise PilotError("Nanoda source revision differs")
    if _git_revision(official_importer) != "f297dfe2a8557e8674fe892bb49dffe4bfadc0e9":
        raise PilotError("official importer source revision differs")
    bindings = []
    for relative, digest in EXTERNAL_SOURCE_LOCKS:
        path = root / relative
        if not path.is_file() or file_sha256(path) != digest:
            raise PilotError("producer source lock differs: " + relative)
        bindings.append(file_binding(path, root))
    producer = root / producer_profile["binary"]["path"]
    if not producer.is_file() or file_sha256(producer) != producer_profile["binary"]["sha256"]:
        raise PilotError("producer binary differs")
    profiles = []
    for profile in design["observer_profiles"]:
        locked: dict[str, Any] = {"id": profile["id"]}
        for field in ("definition", "binary", "configuration"):
            if field not in profile:
                continue
            path = root / profile[field]["path"]
            if not path.is_file() or file_sha256(path) != profile[field]["sha256"]:
                raise PilotError(f"{profile['id']} {field} differs")
            locked[field] = file_binding(path, root)
        profiles.append(locked)
    ps = Path("/bin/ps")
    if not ps.is_file() or file_sha256(ps) != PS_SHA256:
        raise PilotError("process-observation binary differs")
    toolchain = Path.home() / ".elan/toolchains/leanprover--lean4---v4.29.1/bin"
    lake, lean = toolchain / "lake", toolchain / "lean"
    if not lake.is_file() or file_sha256(lake) != LAKE_429_SHA256:
        raise PilotError("Lean 4.29.1 Lake binary differs")
    if not lean.is_file() or file_sha256(lean) != LEAN_429_SHA256:
        raise PilotError("Lean 4.29.1 compiler binary differs")
    python = Path(sys.executable)
    lake_command_text = shutil.which("lake")
    if lake_command_text is None:
        raise PilotError("lake command is unavailable")
    lake_command = Path(lake_command_text)
    return {
        "arena_revision": producer_profile["arena_revision"],
        "exporter_source_revision": producer_profile["source_revision"],
        "nanoda_source_revision": nanoda["source_revision"],
        "producer_binary": file_binding(producer, root),
        "source_locks": bindings,
        "observer_profiles": profiles,
        "process_observer": absolute_binding(ps),
        "python": {**absolute_binding(python), "version": sys.version},
        "lake_command": absolute_binding(lake_command),
        "lean_4_29_1_toolchain": {
            "lake": absolute_binding(lake), "lean": absolute_binding(lean),
            "toolchain": "leanprover/lean4:v4.29.1",
        },
    }


def _next_attempt(root: Path, kind: str) -> tuple[int, Path, Path]:
    number = 1
    while (root / BASE / f"{kind}-run-{number:04d}").exists():
        number += 1
    run_dir = root / BASE / f"{kind}-run-{number:04d}"
    workspace = root / "external" / f"valid-dependent-term-pilot-1-{kind}-{number:04d}"
    if workspace.exists():
        raise PilotError("fresh workspace path already exists")
    return number, run_dir, workspace


def _workspace(workspace: Path, source: bytes) -> None:
    workspace.mkdir(parents=True, exist_ok=False)
    (workspace / "ValidDependentTermPilot1.lean").write_bytes(source)
    (workspace / "lakefile.toml").write_text(
        'name = "ValidDependentTermPilot1"\n'
        'defaultTargets = ["ValidDependentTermPilot1"]\n\n'
        '[[lean_lib]]\nname = "ValidDependentTermPilot1"\n', encoding="utf-8")
    (workspace / "lean-toolchain").write_text("leanprover/lean4:v4.29.1\n", encoding="utf-8")
    if (workspace / "lake-manifest.json").exists():
        raise PilotError("controller must not create lake-manifest.json")


def _receipt_safe(receipt: dict[str, Any], label: str) -> None:
    if receipt.get("memory_monitor_error"):
        raise PilotError(f"{label} memory monitor failed; repair before retry")
    if type(receipt.get("memory_monitor_samples")) is not int or receipt["memory_monitor_samples"] <= 0:
        raise PilotError(f"{label} lacks memory samples; repair before retry")
    if type(receipt.get("maximum_observed_rss_bytes")) is not int or receipt["maximum_observed_rss_bytes"] <= 0:
        raise PilotError(f"{label} lacks a positive RSS observation; repair before retry")
    if receipt.get("memory_exceeded"):
        raise PilotError(f"{label} exceeded memory ceiling; diagnose before retry")
    if receipt.get("timed_out"):
        raise PilotError(f"{label} timed out; diagnose before retry")
    if not receipt.get("cleanup_complete"):
        raise PilotError(f"{label} cleanup is incomplete; repair before retry")


def _verify_process_receipt(binding: dict[str, Any], root: Path = ROOT,
                            *, require_commit: bool = False) -> dict[str, Any]:
    receipt_path = verify_binding(binding, root)
    receipt = load_json(receipt_path)
    for kind in ("stdout", "stderr"):
        relative = receipt.get(f"raw_{kind}_path")
        if not isinstance(relative, str):
            raise PilotError(f"process receipt lacks raw {kind} path")
        raw = safe(root, relative)
        if (not raw.is_file() or raw.is_symlink()
                or receipt.get(f"{kind}_bytes") != raw.stat().st_size
                or receipt.get(f"{kind}_sha256") != file_sha256(raw)):
            raise PilotError(f"process receipt raw {kind} binding differs")
        if require_commit:
            committed(root, relative)
    if require_commit:
        committed(root, _relative(receipt_path, root))
    return receipt


def _supervised(*, argv: list[str], cwd: Path, stdin: bytes | None, env: dict[str, str],
                timeout_seconds: int, memory_bytes: int, raw_prefix: Path,
                receipt_path: Path,
                runner: Callable[..., dict[str, Any]] = run_supervised) -> tuple[dict[str, Any], bytes, bytes]:
    receipt = runner(argv=argv, cwd=cwd, stdin=stdin, env=env,
                     timeout_seconds=timeout_seconds, memory_bytes=memory_bytes,
                     raw_prefix=raw_prefix)
    stdout_path = Path(str(raw_prefix) + ".stdout")
    stderr_path = Path(str(raw_prefix) + ".stderr")
    if not stdout_path.is_file() or not stderr_path.is_file():
        raise PilotError("supervisor raw output is missing")
    stdout, stderr = stdout_path.read_bytes(), stderr_path.read_bytes()
    if receipt.get("stdout_sha256") != hashlib.sha256(stdout).hexdigest() or receipt.get("stdout_bytes") != len(stdout):
        raise PilotError("supervisor stdout receipt differs")
    if receipt.get("stderr_sha256") != hashlib.sha256(stderr).hexdigest() or receipt.get("stderr_bytes") != len(stderr):
        raise PilotError("supervisor stderr receipt differs")
    _write_json(receipt_path, receipt)
    _receipt_safe(receipt, "supervised process")
    return receipt, stdout, stderr


def _audit_case(case: dict[str, Any], design: dict[str, Any]) -> dict[str, Any]:
    try:
        from lib.valid_dependent_term_audit import audit_case
    except ImportError as error:
        raise PilotError("independent auditor module is unavailable") from error
    try:
        report = audit_case(case, design)
    except Exception as error:
        raise PilotError(f"independent case audit failed: {type(error).__name__}: {error}") from error
    required = {"case_id", "status", "term_sha256", "expected_type_sha256",
                "derivation_sha256", "metrics_sha256"}
    if not isinstance(report, dict) or set(report) != required or report["status"] != "PASS":
        raise PilotError("independent auditor did not return PASS with required bindings")
    expected = {
        "case_id": case["case_id"],
        "term_sha256": object_sha256(case["term"]),
        "expected_type_sha256": object_sha256(case["expected_type_nf"]),
        "derivation_sha256": object_sha256(case["derivation"]),
        "metrics_sha256": object_sha256(case["metrics"]),
    }
    for key, value in expected.items():
        if report.get(key) != value:
            raise PilotError(f"independent auditor {key} binding differs")
    return report


def validate_preparation(*, root: Path = ROOT, require_commit: bool = True) -> dict[str, Any]:
    design = _validate_design(root)
    _selected_active(root)
    if require_commit:
        _committed_inputs(root)
    environment = _external_environment(design, root)
    result = {"schema_version": 1, "item_id": ITEM, "mode": "VALIDATE_ONLY",
              "design_sha256": file_sha256(root / DESIGN), "environment": environment,
              "scientific_processes_launched": 0}
    if (root / CORPUS_MANIFEST).exists() or (root / EXECUTION_MANIFEST).exists():
        if not ((root / CORPUS_MANIFEST).is_file() and (root / EXECUTION_MANIFEST).is_file()):
            raise PilotError("only one generated manifest exists")
        _validate_manifests(root=root, require_commit=require_commit)
        result["generated_manifests"] = "PASS"
    return result


def prepare(*, root: Path = ROOT,
            runner: Callable[..., dict[str, Any]] = run_supervised) -> dict[str, Any]:
    """Construct, audit, export, and freeze the cohort; never launch an observer."""
    design = _validate_design(root)
    _selected_active(root)
    _committed_inputs(root)
    environment = _external_environment(design, root)
    if (root / CORPUS).exists() or (root / CORPUS_MANIFEST).exists() or (root / EXECUTION_MANIFEST).exists():
        raise PilotError("refuse to overwrite a frozen cohort or manifest")
    number, run_dir, workspace = _next_attempt(root, "prepare")
    run_dir.mkdir(parents=True, exist_ok=False)
    stage = run_dir / "staged"
    stage.mkdir()
    try:
        from lib.valid_dependent_term_generator import generate_all, render_module
        from lib.valid_dependent_term_audit import audit_corpus
        cases = generate_all(design)
        order = _case_order(design)
        if not isinstance(cases, list) or len(cases) != 50:
            raise PilotError("generator did not return exactly 50 cases")
        if [case.get("case_id") if isinstance(case, dict) else None for case in cases] != order:
            raise PilotError("generator case order differs")
        if len({object_sha256(case["term"]) for case in cases}) != 50:
            raise PilotError("generator terms are not pairwise distinct")
        case_paths: dict[str, Path] = {}
        audit_paths: dict[str, Path] = {}
        for case, expected_id in zip(cases, order):
            _validate_case_shape(case, expected_id, design)
            case_path = stage / "cases" / f"{expected_id}.json"
            _write_json(case_path, case)
            report = _audit_case(case, design)
            audit_path = stage / "audits" / f"{expected_id}.json"
            _write_json(audit_path, report)
            case_paths[expected_id], audit_paths[expected_id] = case_path, audit_path
        try:
            staged_corpus_audit = audit_corpus([case_paths[case_id] for case_id in order], design)
        except Exception as error:
            raise PilotError(
                f"independent corpus audit failed: {type(error).__name__}: {error}"
            ) from error
        if staged_corpus_audit.get("status") != "PASS" or staged_corpus_audit.get("case_count") != 50:
            raise PilotError("independent corpus audit did not return exact PASS")
        staged_corpus_audit_path = run_dir / "staged-corpus-audit.json"
        _write_json(staged_corpus_audit_path, staged_corpus_audit)
        rendered = render_module(cases)
        if isinstance(rendered, str):
            source_bytes = rendered.encode("utf-8")
        elif isinstance(rendered, bytes):
            source_bytes = rendered
        else:
            raise PilotError("generator module renderer did not return text or bytes")
        if not source_bytes.endswith(b"\n"):
            raise PilotError("rendered module must end in LF")
        source_path = stage / "ValidDependentTermPilot1.lean"
        source_path.write_bytes(source_bytes)
        _workspace(workspace, source_bytes)
        safety = design["process_safety"]
        env = dict(os.environ)
        env["LANG"] = "C"
        build_prefix = run_dir / "processes/module-build"
        build_receipt_path = run_dir / "processes/module-build.receipt.json"
        lake_command = environment["lake_command"]["path"]
        build_receipt, build_stdout, build_stderr = _supervised(
            argv=[lake_command, "build", "ValidDependentTermPilot1"], cwd=workspace,
            stdin=None, env=env, timeout_seconds=safety["module_build_seconds"],
            memory_bytes=safety["module_build_memory_bytes"], raw_prefix=build_prefix,
            receipt_path=build_receipt_path, runner=runner)
        if build_receipt.get("exit_code") != 0:
            raise PilotError("module build failed; repair and retry")
        producer = root / design["producer_profile"]["binary"]["path"]
        checked_receipts: dict[str, Path] = {}
        artifact_paths: dict[str, Path] = {}
        for case in cases:
            case_id = case["case_id"]
            declaration = _declaration_name(case, design)
            prefix = run_dir / "processes" / f"export-{case_id}"
            process_receipt_path = run_dir / "processes" / f"export-{case_id}.receipt.json"
            process_receipt, stdout, stderr = _supervised(
                argv=[lake_command, "env", str(producer), "ValidDependentTermPilot1", "--", declaration],
                cwd=workspace, stdin=None, env=env,
                timeout_seconds=safety["export_seconds_each"],
                memory_bytes=safety["export_memory_bytes_each"], raw_prefix=prefix,
                receipt_path=process_receipt_path, runner=runner)
            if process_receipt.get("exit_code") != 0 or not stdout:
                raise PilotError(f"export failed for {case_id}; repair and retry")
            if stderr:
                raise PilotError(f"export emitted unexpected stderr for {case_id}")
            export_path = stage / "exports" / f"{case_id}.ndjson"
            export_path.parent.mkdir(parents=True, exist_ok=True)
            export_path.write_bytes(stdout)
            case_binding = file_binding(case_paths[case_id], root)
            audit_binding = file_binding(audit_paths[case_id], root)
            source_binding = file_binding(source_path, root)
            export_binding = file_binding(export_path, root)
            receipt = checked_object_receipt(stdout, case, design,
                                             case_binding=case_binding,
                                             audit_binding=audit_binding,
                                             source_binding=source_binding,
                                             export_binding=export_binding)
            receipt["producer_process"] = file_binding(process_receipt_path, root)
            checked_path = stage / "receipts" / f"{case_id}.json"
            _write_json(checked_path, receipt)
            checked_receipts[case_id], artifact_paths[case_id] = checked_path, export_path
        corpus_dir = root / CORPUS
        shutil.copytree(stage, corpus_dir)
        source_final = corpus_dir / "ValidDependentTermPilot1.lean"
        cases_final = {case_id: corpus_dir / "cases" / f"{case_id}.json" for case_id in order}
        audits_final = {case_id: corpus_dir / "audits" / f"{case_id}.json" for case_id in order}
        exports_final = {case_id: corpus_dir / "exports" / f"{case_id}.ndjson" for case_id in order}
        receipts_final = {case_id: corpus_dir / "receipts" / f"{case_id}.json" for case_id in order}
        # Receipts are rebound after promotion because their staged path bindings are not canonical.
        for case_id in order:
            case = load_json(cases_final[case_id])
            receipt = checked_object_receipt(
                exports_final[case_id].read_bytes(), case, design,
                case_binding=file_binding(cases_final[case_id], root),
                audit_binding=file_binding(audits_final[case_id], root),
                source_binding=file_binding(source_final, root),
                export_binding=file_binding(exports_final[case_id], root))
            receipt["producer_process"] = file_binding(
                run_dir / "processes" / f"export-{case_id}.receipt.json", root)
            _write_json(receipts_final[case_id], receipt)
        try:
            final_corpus_audit = audit_corpus([cases_final[case_id] for case_id in order], design)
        except Exception as error:
            raise PilotError(
                f"promoted independent corpus audit failed: {type(error).__name__}: {error}"
            ) from error
        final_corpus_audit_path = corpus_dir / "audits" / "corpus.json"
        _write_json(final_corpus_audit_path, final_corpus_audit)
        case_rows = []
        artifact_bindings: dict[str, dict[str, Any]] = {}
        for case_id in order:
            case = load_json(cases_final[case_id])
            case_rows.append({
                "case_id": case_id,
                "category": case["category"],
                "category_index": case["category_index"],
                "term_sha256": object_sha256(case["term"]),
                "expected_type_sha256": object_sha256(case["expected_type_nf"]),
                "derivation_sha256": object_sha256(case["derivation"]),
                "case": file_binding(cases_final[case_id], root),
                "audit": file_binding(audits_final[case_id], root),
                "export": file_binding(exports_final[case_id], root),
                "checked_object_receipt": file_binding(receipts_final[case_id], root),
            })
            artifact_bindings[case_id] = file_binding(exports_final[case_id], root)
        corpus_manifest = {
            "schema_version": 1, "item_id": ITEM, "design_id": design["design_id"],
            "generated_at": _now(), "preparation_attempt": number,
            "design": file_binding(root / DESIGN, root),
            "generator": file_binding(root / GENERATOR, root),
            "auditor": file_binding(root / AUDITOR, root),
            "corpus_audit": file_binding(final_corpus_audit_path, root),
            "source_module": file_binding(source_final, root),
            "producer": environment["producer_binary"],
            "module_build": {
                "receipt": file_binding(build_receipt_path, root),
                "stdout_sha256": hashlib.sha256(build_stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(build_stderr).hexdigest(),
            },
            "case_order": order, "case_count": 50, "cases": case_rows,
            "aggregate_sha256": object_sha256(case_rows),
        }
        _write_json(root / CORPUS_MANIFEST, corpus_manifest)
        execution_manifest = {
            "schema_version": 1, "item_id": ITEM, "gate": "PASS",
            "generated_at": _now(),
            "design": file_binding(root / DESIGN, root),
            "corpus_manifest": file_binding(root / CORPUS_MANIFEST, root),
            "repository_inputs": [file_binding(root / path, root) for path in REPOSITORY_INPUTS],
            "tooling": [file_binding(root / path, root) for path in CONTROLLER_TOOLING],
            "external_environment": environment,
            "source_module": file_binding(source_final, root),
            "observer_profiles": design["observer_profiles"],
            "process_safety": design["process_safety"],
            "launch_owner": "root",
            "matrix": ordered_matrix(design, artifact_bindings),
        }
        _write_json(root / EXECUTION_MANIFEST, execution_manifest)
        result = {"schema_version": 1, "item_id": ITEM, "status": "PREPARED",
                  "recorded_at": _now(), "case_count": 50, "matrix_cells": 100,
                  "checker_launches": 0,
                  "corpus_manifest": file_binding(root / CORPUS_MANIFEST, root),
                  "execution_manifest": file_binding(root / EXECUTION_MANIFEST, root)}
        _write_json(run_dir / "result.json", result)
        return result
    except BaseException as error:
        _write_json(run_dir / "failure.json", {
            "schema_version": 1, "item_id": ITEM, "status": "REPAIR_PAUSE",
            "recorded_at": _now(), "error": f"{type(error).__name__}: {error}",
            "checker_launches": 0,
        })
        raise


def _validate_manifests(*, root: Path = ROOT, require_commit: bool) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    design = _validate_design(root)
    corpus = load_json(root / CORPUS_MANIFEST)
    execution = load_json(root / EXECUTION_MANIFEST)
    if (corpus.get("schema_version") != 1 or corpus.get("item_id") != ITEM
            or corpus.get("case_count") != 50 or corpus.get("case_order") != _case_order(design)
            or len(corpus.get("cases", [])) != 50):
        raise PilotError("corpus manifest differs")
    if (execution.get("schema_version") != 1 or execution.get("item_id") != ITEM
            or execution.get("gate") != "PASS" or execution.get("launch_owner") != "root"):
        raise PilotError("execution manifest gate differs")
    verify_binding(execution.get("design"), root)
    verify_binding(execution.get("corpus_manifest"), root)
    verify_binding(corpus.get("design"), root)
    source_path = verify_binding(corpus.get("source_module"), root)
    corpus_audit_path = verify_binding(corpus.get("corpus_audit"), root)
    corpus_audit = load_json(corpus_audit_path)
    if corpus_audit.get("status") != "PASS" or corpus_audit.get("case_count") != 50:
        raise PilotError("independent corpus audit binding differs")
    if execution["corpus_manifest"] != file_binding(root / CORPUS_MANIFEST, root):
        raise PilotError("execution manifest does not bind current corpus manifest")
    if verify_binding(corpus.get("generator"), root) != root / GENERATOR:
        raise PilotError("corpus generator binding differs")
    if verify_binding(corpus.get("auditor"), root) != root / AUDITOR:
        raise PilotError("corpus auditor binding differs")
    for section in ("repository_inputs", "tooling"):
        if not isinstance(execution.get(section), list):
            raise PilotError(f"execution {section} bindings are absent")
        for binding in execution[section]:
            path = verify_binding(binding, root)
            if require_commit:
                committed(root, _relative(path, root))
    case_rows = corpus["cases"]
    artifacts: dict[str, dict[str, Any]] = {}
    seen_terms: set[str] = set()
    for expected_id, row in zip(_case_order(design), case_rows):
        if not isinstance(row, dict) or row.get("case_id") != expected_id:
            raise PilotError("corpus case order differs")
        paths = {key: verify_binding(row.get(key), root)
                 for key in ("case", "audit", "export", "checked_object_receipt")}
        case = load_json(paths["case"])
        audit = load_json(paths["audit"])
        receipt = load_json(paths["checked_object_receipt"])
        _validate_case_shape(case, expected_id, design)
        if (audit != _audit_case(case, design) or receipt.get("case_id") != expected_id):
            raise PilotError("case lacks matching audit/receipt PASS")
        if row.get("term_sha256") != object_sha256(case["term"]):
            raise PilotError("case term hash differs")
        seen_terms.add(row["term_sha256"])
        rebuilt = checked_object_receipt(
            paths["export"].read_bytes(), case, design,
            case_binding=row["case"], audit_binding=row["audit"],
            source_binding=corpus["source_module"], export_binding=row["export"])
        if {key: value for key, value in receipt.items() if key != "producer_process"} != rebuilt:
            raise PilotError("checked-object receipt differs under replay")
        process_receipt = _verify_process_receipt(
            receipt.get("producer_process"), root, require_commit=require_commit)
        _receipt_safe(process_receipt, f"export replay {expected_id}")
        if process_receipt.get("exit_code") != 0:
            raise PilotError("export replay process did not exit successfully")
        raw_stdout = safe(root, process_receipt["raw_stdout_path"])
        raw_stderr = safe(root, process_receipt["raw_stderr_path"])
        if raw_stdout.read_bytes() != paths["export"].read_bytes() or raw_stderr.read_bytes() != b"":
            raise PilotError("export replay raw output differs from frozen artifact")
        artifacts[expected_id] = row["export"]
        if require_commit:
            for path in paths.values():
                committed(root, _relative(path, root))
    if len(seen_terms) != 50 or corpus.get("aggregate_sha256") != object_sha256(case_rows):
        raise PilotError("corpus distinctness or aggregate binding differs")
    try:
        from lib.valid_dependent_term_audit import audit_corpus
        audit_paths = [row["path"] for row in corpus_audit["cases"]]
        expected_paths = [str((root / row["case"]["path"]).resolve()) for row in case_rows]
        if audit_paths != expected_paths:
            raise PilotError("corpus audit case paths differ from frozen cases")
        if audit_corpus(audit_paths, design) != corpus_audit:
            raise PilotError("independent corpus audit differs under replay")
    except PilotError:
        raise
    except Exception as error:
        raise PilotError(
            f"independent corpus audit replay failed: {type(error).__name__}: {error}"
        ) from error
    if execution.get("matrix") != ordered_matrix(design, artifacts):
        raise PilotError("execution matrix differs from frozen order")
    if execution.get("observer_profiles") != design["observer_profiles"]:
        raise PilotError("execution observer profiles differ")
    if execution.get("process_safety") != design["process_safety"]:
        raise PilotError("execution process safety differs")
    current_environment = _external_environment(design, root)
    if execution.get("external_environment") != current_environment:
        raise PilotError("execution environment source/tool bindings differ")
    if corpus.get("producer") != current_environment["producer_binary"]:
        raise PilotError("corpus producer binding differs")
    for key in ("process_observer", "lake_command"):
        verify_absolute_binding(current_environment[key])
    verify_absolute_binding({key: current_environment["python"][key]
                             for key in ("path", "bytes", "sha256")})
    for key in ("lake", "lean"):
        verify_absolute_binding(current_environment["lean_4_29_1_toolchain"][key])
    if require_commit:
        for relative in (CORPUS_MANIFEST, EXECUTION_MANIFEST):
            committed(root, relative)
        for binding in (corpus["source_module"], corpus["corpus_audit"]):
            path = verify_binding(binding, root)
            committed(root, _relative(path, root))
        build_receipt = _verify_process_receipt(
            corpus["module_build"]["receipt"], root, require_commit=True)
        _receipt_safe(build_receipt, "module build replay")
        if build_receipt.get("exit_code") != 0:
            raise PilotError("module build replay did not exit successfully")
    return design, corpus, execution


def validate_execution(*, root: Path = ROOT, require_commit: bool = True) -> dict[str, Any]:
    _selected_active(root)
    if require_commit:
        _committed_inputs(root, include_generated=True)
    design, corpus, execution = _validate_manifests(root=root, require_commit=require_commit)
    return {"schema_version": 1, "item_id": ITEM, "mode": "VALIDATE_ONLY",
            "gate": "PASS", "case_count": corpus["case_count"],
            "matrix_cells": len(execution["matrix"]), "scientific_processes_launched": 0,
            "design_sha256": file_sha256(root / DESIGN)}


@contextmanager
def _launch_lock(root: Path) -> Iterator[None]:
    path = root / BASE / "launch.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise PilotError("symlink launch lock refused")
    stream = path.open("a+")
    try:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise PilotError("another lead owner holds the launch lock") from error
        stream.seek(0)
        stream.truncate()
        stream.write(canonical_bytes({"item_id": ITEM, "owner": "root", "pid": os.getpid()}, newline=True).decode())
        stream.flush()
        os.fsync(stream.fileno())
        yield
    finally:
        try:
            fcntl.flock(stream, fcntl.LOCK_UN)
        finally:
            stream.close()


def execute(*, root: Path = ROOT,
            runner: Callable[..., dict[str, Any]] = run_supervised) -> dict[str, Any]:
    """Run the exact 100-cell frozen matrix after the committed observation gate."""
    _selected_active(root)
    _committed_inputs(root, include_generated=True)
    design, corpus, manifest = _validate_manifests(root=root, require_commit=True)
    with _launch_lock(root):
        number, run_dir, _ = _next_attempt(root, "checker")
        run_dir.mkdir(parents=True, exist_ok=False)
        launch_receipt = run_dir / "launch-owner.lock"
        launch_receipt.write_bytes(canonical_bytes(
            {"item_id": ITEM, "owner": "root", "pid": os.getpid(), "run": number}, newline=True))
        profiles = {row["id"]: row for row in design["observer_profiles"]}
        safety = design["process_safety"]
        results: list[dict[str, Any]] = []
        try:
            for cell in manifest["matrix"]:
                artifact = verify_binding(cell["artifact"], root)
                profile = profiles[cell["profile_id"]]
                raw_prefix = run_dir / "raw" / f"{cell['ordinal']:03d}-{cell['profile_id']}-{cell['case_id']}"
                receipt_path = run_dir / "receipts" / f"{cell['ordinal']:03d}.json"
                env = {key: value for key, value in os.environ.items() if not key.startswith("KIOTA_")}
                env["LANG"] = "C"
                if profile["id"] == "official-lean-4.33.0":
                    binary = root / profile["binary"]["path"]
                    argv, cwd, stdin = [str(binary), str(artifact)], root, None
                elif profile["id"] == "nanoda-6ae1f0c":
                    cwd = root / profile["cwd"]
                    argv = list(profile["invocation"])
                    stdin = artifact.read_bytes()
                    profile_dir = run_dir / "profiles"
                    profile_dir.mkdir(exist_ok=True)
                    env["LLVM_PROFILE_FILE"] = str(profile_dir / "nanoda-%p.profraw")
                else:
                    raise PilotError("unexpected observer profile")
                receipt, stdout, stderr = _supervised(
                    argv=argv, cwd=cwd, stdin=stdin, env=env,
                    timeout_seconds=safety["checker_seconds_each"],
                    memory_bytes=safety["checker_memory_bytes_each"], raw_prefix=raw_prefix,
                    receipt_path=receipt_path, runner=runner)
                outcome, reason = classify(profile["id"], receipt, stdout, stderr)
                if outcome == "INFRASTRUCTURE_AUDIT_FAILURE":
                    raise PilotError(f"cell {cell['cell_id']} infrastructure failure: {reason}")
                row = {
                    "ordinal": cell["ordinal"], "cell_id": cell["cell_id"],
                    "profile_id": cell["profile_id"], "case_id": cell["case_id"],
                    "artifact": cell["artifact"], "outcome": outcome, "reason": reason,
                    "receipt": file_binding(receipt_path, root),
                    "stdout": file_binding(Path(str(raw_prefix) + ".stdout"), root),
                    "stderr": file_binding(Path(str(raw_prefix) + ".stderr"), root),
                }
                results.append(row)
                with (run_dir / "events.jsonl").open("ab") as stream:
                    stream.write(canonical_bytes(row, newline=True))
                    stream.flush()
                    os.fsync(stream.fileno())
            result = {
                "schema_version": 1, "item_id": ITEM, "status": "COMPLETE",
                "generated_at": _now(), "execution_manifest": file_binding(root / EXECUTION_MANIFEST, root),
                "run": number, "owner": "root", "cells": results,
                "checker_attempts": len(results),
                "process_seconds": sum(row_receipt["elapsed_seconds"] for row_receipt in
                                       (load_json(root / row["receipt"]["path"]) for row in results)),
                "outcome_counts": {outcome: sum(row["outcome"] == outcome for row in results)
                                   for outcome in sorted({row["outcome"] for row in results})},
            }
            _write_json(run_dir / "result.json", result)
            return result
        except BaseException as error:
            _write_json(run_dir / "failure.json", {
                "schema_version": 1, "item_id": ITEM, "status": "REPAIR_PAUSE",
                "generated_at": _now(), "completed_cells": len(results),
                "error": f"{type(error).__name__}: {error}",
            })
            raise
        finally:
            launch_receipt.unlink(missing_ok=True)
