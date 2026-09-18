"""Adversarial checks for source-only claims, accounting and historical closure."""
from copy import deepcopy
from datetime import datetime, timedelta
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import shutil
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULE = ModuleType("nanoda_native_config_closure")
MODULE.__file__ = str(ROOT / "scripts/validate-nanoda-native-config-closure")
SourceFileLoader(MODULE.__name__, MODULE.__file__).exec_module(MODULE)


def matrix_fixture():
    rows = []
    for nat, string in ((False, False), (False, True), (True, False), (True, True)):
        for presence in ("ABSENT", "PRESENT"):
            typing = lambda flag: "UNREACHED" if not flag else "PANIC_MISSING_NAME" if presence == "ABSENT" else "SYNTACTIC_TYPE_CONST"
            rows.append({"id": f"N{int(nat)}S{int(string)}-{presence}",
                         "nat_extension": nat, "string_extension": string, "prerequisites": presence,
                         "declarations_present": False, "parser_nat": "ADMIT" if nat else "REJECT",
                         "parser_string": "ADMIT" if string else "REJECT", "quick_nat": "SOME" if nat else "NONE",
                         "quick_string": "SOME" if string else "NONE",
                         "nat_reconstruction": "UNREACHED" if not nat else "NONE" if presence == "ABSENT" else "SOME_ZERO_OR_SUCC",
                         "string_reconstruction": "SOME_SHAPE" if nat and string and presence == "PRESENT" else "NONE",
                         "native_typing": {"nat": typing(nat), "string": typing(string)}})
    return {"item_id": MODULE.ITEM, "source_revision": MODULE.TIP, "evidence_kind": "SOURCE_INFERENCE",
            "state_refinement": {"axis": "CACHED_NAME_PRESENCE", "declaration_presence_states": 1,
                                 "declarations_present": False, "reason": "Cached names are not declarations."},
            "rows": rows}


def fixture():
    entry = json.loads((ROOT / MODULE.PREFIX / "work-record.json").read_text())
    counts = {"read_only_requests": 1, **{key: 0 for key in MODULE.ZERO_COUNTS}}
    result = {"item_id": MODULE.ITEM, "status": "COMPLETE", "outcome": "SUCCESS",
              "execution": False, "universal_obligation": False, "current_bug": False,
              "entry_commit": MODULE.ENTRY_COMMIT, "research_counts": counts,
              "next_item": {"id": "SYNTHETIC-NEXT", "status": "READY", "started": False}}
    closure = {"item_id": MODULE.ITEM, "status": "COMPLETE", "outcome": result["outcome"],
               "started_at": entry["started_at"], "start_monotonic": entry["start_monotonic"],
               "completed_at": (datetime.fromisoformat(entry["started_at"]) + timedelta(seconds=60)).isoformat(),
               "end_monotonic": entry["start_monotonic"] + 60, "active_seconds": 60,
               "research_counts": deepcopy(counts), "next_item": "SYNTHETIC-NEXT", "next_item_started": False}
    requests = {"item_id": MODULE.ITEM, "cap": 8, "charged_read_only_requests": 1,
                "requests": [{"id": "source-1", "charged_requests": 1}]}
    assessment = matrix_fixture()
    queue = {"selected_item": "SYNTHETIC-NEXT", "items": [
        {"id": MODULE.ITEM, "status": "COMPLETE", "closure": {"outcome": result["outcome"]}},
        {"id": "SYNTHETIC-NEXT", "status": "READY"}]}
    return result, entry, closure, requests, assessment, queue


class NanodaNativeConfigClosureTests(unittest.TestCase):
    def test_valid_scoped_closure(self):
        MODULE.validate_data(*fixture())

    def test_matrix_requires_exact_unique_flag_and_name_cells(self):
        for mutation in ("missing", "duplicate", "boolean", "declaration", "axis", "third_state"):
            value = matrix_fixture()
            if mutation == "missing": value["rows"].pop()
            if mutation == "duplicate":
                value["rows"][-1] = deepcopy(value["rows"][0])
                value["rows"][-1]["id"] = "unique-name-duplicate-config"
            if mutation == "boolean": value["rows"][0]["nat_extension"] = 0
            if mutation == "declaration": value["rows"][0]["declarations_present"] = True
            if mutation == "axis": value["state_refinement"]["axis"] = "DECLARATION_VALIDITY"
            if mutation == "third_state": value["rows"][0]["prerequisites"] = "PARTIAL"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                MODULE.validate_matrix(value)

    def test_reconstruction_typing_and_admission_cannot_be_conflated(self):
        for index in range(8):
            for key in ("parser_nat", "parser_string", "quick_nat", "quick_string", "nat_reconstruction", "string_reconstruction"):
                value = matrix_fixture()
                value["rows"][index][key] = "SEMANTIC_SUCCESS"
                with self.subTest(cell=index, field=key), self.assertRaisesRegex(ValueError, "source condition"):
                    MODULE.validate_matrix(value)
            for native in ("nat", "string"):
                value = matrix_fixture()
                value["rows"][index]["native_typing"][native] = "VALID_DECLARATION"
                with self.subTest(cell=index, typing=native), self.assertRaisesRegex(ValueError, "typing source condition"):
                    MODULE.validate_matrix(value)
        value = matrix_fixture()
        value["rows"][3]["string_reconstruction"] = "SOME_SHAPE"
        with self.assertRaisesRegex(ValueError, "string_reconstruction"):
            MODULE.validate_matrix(value)

    def test_design_cannot_claim_execution_or_drop_unicode_control(self):
        design = json.loads((ROOT / MODULE.PREFIX / "regression-design.json").read_text())
        for mutation in ("execution", "semantic", "status", "scope", "unicode", "control", "cells", "names", "declarations"):
            value = deepcopy(design)
            if mutation == "execution": value["claims"]["execution"] = True
            if mutation == "semantic": value["claims"]["public_semantic_acceptance"] = True
            if mutation == "status": value["status"] = "EXECUTED"
            if mutation == "scope": value["deliverable_count"] = 2
            if mutation == "unicode": value["payloads"][1]["unicode_scalars"] = [65, 195, 169]
            if mutation == "control": value["payloads"].pop(0)
            if mutation == "cells": value["cells"].pop()
            if mutation == "names": value["fixture"]["present_leaf_paths"].pop()
            if mutation == "declarations": value["fixture"]["declarations_present"] = True
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                MODULE.validate_design(value, matrix_fixture())

    def test_exact_source_inventory_tests_and_excerpt_bindings(self):
        source = json.loads((ROOT / MODULE.PREFIX / "source-lock.json").read_text())
        tests = json.loads((ROOT / MODULE.PREFIX / "test-inventory.json").read_text())
        blobs = MODULE.validate_source(ROOT, source, tests)
        for mutation in ("count", "line", "duplicate", "fixture", "source_bytes"):
            changed_source, changed_tests = deepcopy(source), deepcopy(tests)
            if mutation == "count": changed_tests["count"] = 39
            if mutation == "line": changed_tests["tests"][0]["line"] += 1
            if mutation == "duplicate": changed_tests["tests"][-1] = deepcopy(changed_tests["tests"][0])
            if mutation == "fixture": changed_source["inventory"].pop()
            if mutation == "source_bytes": changed_source["inventory"][0]["bytes"] += 1
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                MODULE.validate_source(ROOT, changed_source, changed_tests)
        assessment = json.loads((ROOT / MODULE.PREFIX / "source-assessment.json").read_text())
        MODULE.validate_excerpts(assessment, blobs)
        for mutation in ("text", "digest", "range", "claim"):
            value = deepcopy(assessment)
            if mutation == "text": value["excerpts"][0]["text"] += "Unsupported source text"
            if mutation == "digest": value["excerpts"][0]["source_sha256"] = "0" * 64
            if mutation == "range": value["excerpts"][0]["start_line"] = 0
            if mutation == "claim": value["current_bug"] = True
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                MODULE.validate_excerpts(value, blobs)

    def test_inflated_claims_and_launches_refused(self):
        for target, key, value in ((0, "outcome", "NEGATIVE"), (0, "execution", True),
                                   (0, "universal_obligation", True), (0, "current_bug", True),
                                   (4, "evidence_kind", "EXECUTED"), (4, "source_revision", "f" * 40)):
            with self.subTest(key=key):
                data = fixture()
                data[target][key] = value
                with self.assertRaises(ValueError): MODULE.validate_data(*data)
        for key in MODULE.ZERO_COUNTS:
            data = fixture()
            data[0]["research_counts"][key] = data[2]["research_counts"][key] = 1
            with self.subTest(launch=key), self.assertRaisesRegex(ValueError, "prohibited launch"):
                MODULE.validate_data(*data)

    def test_clock_reset_nonfinite_and_cap_refused(self):
        for mutation in ("reset", "nan", "over_cap", "utc", "naive"):
            data = fixture()
            closure = data[2]
            if mutation == "reset": closure["start_monotonic"] += 1
            if mutation == "nan": closure["active_seconds"] = float("nan")
            if mutation == "over_cap":
                closure["active_seconds"] = 5401
                closure["end_monotonic"] = closure["start_monotonic"] + 5401
                closure["completed_at"] = (datetime.fromisoformat(closure["started_at"]) + timedelta(seconds=5401)).isoformat()
            if mutation == "utc": closure["completed_at"] = closure["started_at"]
            if mutation == "naive": closure["completed_at"] = "2026-09-13T19:00:00"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_request_cost_cannot_be_erased_or_exceeded(self):
        for mutation in ("missing", "duplicate", "over_cap", "boolean", "uncharged"):
            data = fixture()
            requests = data[3]
            if mutation == "missing": requests["requests"] = []
            if mutation == "duplicate": requests["requests"] *= 2
            if mutation == "over_cap":
                requests["requests"][0]["charged_requests"] = requests["charged_read_only_requests"] = 9
                data[0]["research_counts"]["read_only_requests"] = data[2]["research_counts"]["read_only_requests"] = 9
            if mutation == "boolean": requests["requests"][0]["charged_requests"] = True
            if mutation == "uncharged": requests["requests"].append({"id": "lost-failure", "charged_requests": 0})
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_handoff_and_item_closure_agree(self):
        for mutation in ("started", "active", "wrong_selected", "wrong_outcome", "duplicate"):
            data = fixture()
            if mutation == "started": data[0]["next_item"]["started"] = True
            if mutation == "active": data[5]["items"][1]["status"] = "ACTIVE"
            if mutation == "wrong_selected": data[5]["selected_item"] = MODULE.ITEM
            if mutation == "wrong_outcome": data[5]["items"][0]["closure"]["outcome"] = "NEGATIVE"
            if mutation == "duplicate": data[5]["items"].append(deepcopy(data[5]["items"][1]))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_artifact_binding_tampering_and_mutable_queue_independence(self):
        data = fixture()
        with tempfile.TemporaryDirectory(prefix="native-config-closure-test-") as temporary:
            root = Path(temporary)
            prefix = root / MODULE.PREFIX
            prefix.mkdir(parents=True)
            history = {}
            for name in MODULE.FROZEN:
                raw = (ROOT / MODULE.PREFIX / name).read_bytes()
                (prefix / name).write_bytes(raw)
                history[(data[0]["entry_commit"], MODULE.PREFIX + name)] = raw
            base = data[1]["base_commit"]
            for row in json.loads((prefix / "entry-lock.json").read_text())["bindings"]:
                history[(base, row["path"])] = MODULE.git_bytes(ROOT, base, row["path"])
            history[(base, "config/research-queue.json")] = (prefix / "entry-queue.json").read_bytes()
            bundle = root / MODULE.BUNDLE
            bundle.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / MODULE.BUNDLE, bundle)
            source = json.loads((ROOT / MODULE.PREFIX / "source-lock.json").read_text())
            for name, value in (("work-closure.json", data[2]),
                                ("requests.json", data[3]), ("matrix.json", data[4]), ("closure-queue.json", data[5])):
                (prefix / name).write_text(json.dumps(value))
            for name in ("report.md", "validation-design.json"):
                (prefix / name).write_text("test binding")
            for name in ("regression-design.json", "source-assessment.json"):
                value = json.loads((ROOT / MODULE.PREFIX / name).read_text())
                raw_matrix = (prefix / "matrix.json").read_bytes()
                value["matrix"] = {"path": MODULE.PREFIX + "matrix.json", "bytes": len(raw_matrix), "sha256": MODULE.digest(raw_matrix)}
                (prefix / name).write_text(json.dumps(value))
            for name in ("scripts/validate-nanoda-native-config-closure", "tests/test_nanoda_native_config_closure.py"):
                (root / name).parent.mkdir(exist_ok=True)
                (root / name).write_text("test tooling binding")
            outputs = [MODULE.PREFIX + name for name in
                       ("source-lock.json", "test-inventory.json", "work-closure.json", "requests.json", "matrix.json",
                        "closure-queue.json", "report.md", "regression-design.json", "source-assessment.json", "validation-design.json")]
            outputs += ["scripts/validate-nanoda-native-config-closure", "tests/test_nanoda_native_config_closure.py"]
            data[0]["output_bindings"] = [{"path": name, "sha256": MODULE.digest((root / name).read_bytes()),
                                          "bytes": (root / name).stat().st_size} for name in outputs]
            result_path = prefix / "result.json"
            result_path.write_text(json.dumps(data[0]))
            original_git_bytes = MODULE.git_bytes
            def historical_bytes(repository, revision, path):
                if (revision, path) in history:
                    return history[(revision, path)]
                return original_git_bytes(repository, revision, path)
            with patch.object(MODULE, "git_bytes", side_effect=historical_bytes):
                # Live queue can advance without invalidating a historical closure.
                (root / "config").mkdir()
                (root / "config/research-queue.json").write_text('{"selected_item":"LATER-ITEM"}')
                self.assertEqual(MODULE.validate(root)["status"], "PASS")
                for name in ("matrix.json", *MODULE.FROZEN):
                    path = prefix / name
                    raw = path.read_bytes()
                    path.write_bytes(raw + b" ")
                    with self.subTest(name=name), self.assertRaises(ValueError): MODULE.validate(root)
                    path.write_bytes(raw)
                historical_key = (base, "CONSTITUTION.md")
                historical_raw = history[historical_key]
                history[historical_key] += b"changed historical bytes"
                with self.assertRaisesRegex(ValueError, "historical entry binding mismatch"): MODULE.validate(root)
                history[historical_key] = historical_raw
                for mutation in ("bytes", "duplicate", "missing", "escape", "entry_commit"):
                    changed = deepcopy(data[0])
                    if mutation == "bytes": changed["output_bindings"][0]["bytes"] += 1
                    if mutation == "duplicate": changed["output_bindings"].append(changed["output_bindings"][0])
                    if mutation == "missing": changed["output_bindings"].pop()
                    if mutation == "escape": changed["output_bindings"][0]["path"] = "../outside"
                    if mutation == "entry_commit": changed["entry_commit"] = "f" * 40
                    result_path.write_text(json.dumps(changed))
                    with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate(root)
                result_path.write_text(json.dumps(data[0]))
                with bundle.open("ab") as handle: handle.write(b"tampered")
                with self.assertRaisesRegex(ValueError, "bundle mismatch"): MODULE.validate(root)


if __name__ == "__main__":
    unittest.main()
