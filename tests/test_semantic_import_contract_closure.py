"""Adversarial checks for source-only claims, accounting and historical closure."""
from copy import deepcopy
from datetime import datetime, timedelta
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULE = ModuleType("semantic_import_contract_closure")
MODULE.__file__ = str(ROOT / "scripts/validate-semantic-import-contract-closure")
SourceFileLoader(MODULE.__name__, MODULE.__file__).exec_module(MODULE)


REPLAY = ModuleType("semantic_import_historical_replay")
REPLAY.__file__ = str(ROOT / MODULE.PREFIX / "replay-historical-evidence.py")
SourceFileLoader(REPLAY.__name__, REPLAY.__file__).exec_module(REPLAY)


def fixture():
    entry = json.loads((ROOT / MODULE.PREFIX / "work-record.json").read_text())
    counts = {"read_only_requests": 8, **{key: 0 for key in MODULE.ZERO_COUNTS}}
    result = {"item_id": MODULE.ITEM, "status": "COMPLETE", "outcome": "SUCCESS",
              "universal_authority": "UNRESOLVED", "current_execution": False, "local_drafts": 1, "catalog_changed": False, "authority_changed": False,
              "entry_commit": MODULE.ENTRY_COMMIT, "freeze_commit": MODULE.FREEZE_COMMIT, "research_counts": counts,
              "next_item": {"id": "SYNTHETIC-NEXT", "status": "READY", "started": False}}
    closure = {"item_id": MODULE.ITEM, "status": "COMPLETE", "outcome": result["outcome"],
               "started_at": entry["started_at"], "start_monotonic": entry["start_monotonic"],
               "completed_at": (datetime.fromisoformat(entry["started_at"]) + timedelta(seconds=60)).isoformat(),
               "end_monotonic": entry["start_monotonic"] + 60, "active_seconds": 60,
               "research_counts": deepcopy(counts), "next_item": "SYNTHETIC-NEXT", "next_item_started": False}
    requests = json.loads((ROOT / MODULE.PREFIX / "requests.json").read_text())
    assessment = {"item_id": MODULE.ITEM, "fields": [{"id": key} for key in sorted(MODULE.FIELD_IDS)],
                  "universal_authority": "UNRESOLVED", "current_execution": False, "local_drafts": 1}
    queue = {"selected_item": "SYNTHETIC-NEXT", "items": [
        {"id": MODULE.ITEM, "status": "COMPLETE", "closure": {"outcome": result["outcome"]}},
        {"id": "SYNTHETIC-NEXT", "status": "READY"}]}
    return result, entry, closure, requests, assessment, queue


class SemanticImportContractClosureTests(unittest.TestCase):
    def test_valid_scoped_closure(self):
        MODULE.validate_data(*fixture())

    def test_inflated_claims_and_launches_refused(self):
        for target, key, value in ((0, "outcome", "NEGATIVE"), (0, "universal_authority", "ESTABLISHED"),
                                   (0, "catalog_changed", True), (0, "authority_changed", True),
                                   (4, "universal_authority", "ESTABLISHED"), (4, "current_execution", True),
                                   (0, "local_drafts", 2), (4, "local_drafts", 0)):
            with self.subTest(key=key):
                data = fixture()
                data[target][key] = value
                with self.assertRaises(ValueError): MODULE.validate_data(*data)
        for mutation in ("replace", "duplicate", "short"):
            data = fixture()
            if mutation == "replace": data[4]["fields"][0]["id"] = "unselected-field"
            if mutation == "duplicate": data[4]["fields"][0] = deepcopy(data[4]["fields"][1])
            if mutation == "short": data[4]["fields"].pop()
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)
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
                closure["active_seconds"] = 7201
                closure["end_monotonic"] = closure["start_monotonic"] + 7201
                closure["completed_at"] = (datetime.fromisoformat(closure["started_at"]) + timedelta(seconds=7201)).isoformat()
            if mutation == "utc": closure["completed_at"] = closure["started_at"]
            if mutation == "naive": closure["completed_at"] = "2026-09-13T19:00:00"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_request_cost_cannot_be_erased_or_exceeded(self):
        for mutation in ("missing", "duplicate", "over_cap", "boolean", "uncharged", "failure"):
            data = fixture()
            requests = data[3]
            if mutation == "failure": requests["requests"][1]["result"] = "SUCCESS"
            if mutation == "missing": requests["requests"] = []
            if mutation == "duplicate": requests["requests"] *= 2
            if mutation == "over_cap":
                requests["requests"][0]["charged_requests"] = requests["charged_requests"] = 9
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

    def test_delivery_accounting_preserves_inclusive_cap_and_handoff(self):
        result, entry, closure, *_ = fixture()
        delivery = {"item_id": MODULE.ITEM, "started_at": entry["started_at"],
                    "start_monotonic": entry["start_monotonic"],
                    "recorded_at": (datetime.fromisoformat(entry["started_at"]) + timedelta(seconds=120)).isoformat(),
                    "end_monotonic": entry["start_monotonic"] + 120,
                    "cumulative_active_seconds": 120, "administrative_seconds_after_work_closure": 60,
                    "remaining_seconds": 7080, "cap_seconds": 7200,
                    "research_counts": deepcopy(result["research_counts"]),
                    "next_item": result["next_item"]["id"], "next_item_started": False}
        MODULE.validate_delivery(delivery, entry, closure, result)
        for mutation in ("reset", "nonfinite", "overcap", "underclosure", "counts", "successor", "utc", "remaining", "admin", "cap"):
            changed = deepcopy(delivery)
            if mutation == "reset": changed["start_monotonic"] += 1
            if mutation == "nonfinite": changed["cumulative_active_seconds"] = float("nan")
            if mutation in ("overcap", "underclosure"):
                active = 7201 if mutation == "overcap" else 59
                changed["cumulative_active_seconds"] = active
                changed["end_monotonic"] = changed["start_monotonic"] + active
                changed["recorded_at"] = (datetime.fromisoformat(entry["started_at"]) + timedelta(seconds=active)).isoformat()
            if mutation == "counts": changed["research_counts"]["read_only_requests"] += 1
            if mutation == "successor": changed["next_item_started"] = True
            if mutation == "utc": changed["recorded_at"] = changed["started_at"]
            if mutation == "remaining": changed["remaining_seconds"] += 1
            if mutation == "admin": changed["administrative_seconds_after_work_closure"] += 1
            if mutation == "cap": changed["cap_seconds"] += 1
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                MODULE.validate_delivery(changed, entry, closure, result)

    def test_artifact_binding_tampering_and_mutable_queue_independence(self):
        data = fixture()
        with tempfile.TemporaryDirectory(prefix="import-closure-test-") as temporary:
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
            for name in MODULE.SOURCE_FROZEN:
                raw = (ROOT / MODULE.PREFIX / name).read_bytes()
                (prefix / name).write_bytes(raw)
                history[(MODULE.FREEZE_COMMIT, MODULE.PREFIX + name)] = raw
            for name, value in (("work-closure.json", data[2]),
                                ("field-assessment.json", data[4]), ("closure-queue.json", data[5])):
                (prefix / name).write_text(json.dumps(value))
            data[0]["output_bindings"] = [{"path": MODULE.PREFIX + name, "sha256": MODULE.digest((prefix / name).read_bytes()),
                                          "bytes": (prefix / name).stat().st_size}
                                         for name in ("source-lock.json", "work-closure.json", "requests.json", "field-assessment.json", "closure-queue.json")]
            result_path = prefix / "result.json"
            result_path.write_text(json.dumps(data[0]))
            with patch.object(MODULE, "git_bytes", side_effect=lambda _, revision, path: history[(revision, path)]):
                # Live queue can advance without invalidating a historical closure.
                (root / "config").mkdir()
                (root / "config/research-queue.json").write_text('{"selected_item":"LATER-ITEM"}')
                self.assertEqual(MODULE.validate(root)["status"], "PASS")
                for name in ("field-assessment.json", "work-record.json", "source-lock.json", "requests.json", "kiota-source.tar.gz", "lean-v4.34.0-rc2-Replay.lean", "request-02.json"):
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
                for mutation in ("bytes", "duplicate", "missing", "escape"):
                    changed = deepcopy(data[0])
                    if mutation == "bytes": changed["output_bindings"][0]["bytes"] += 1
                    if mutation == "duplicate": changed["output_bindings"].append(changed["output_bindings"][0])
                    if mutation == "missing": changed["output_bindings"].pop()
                    if mutation == "escape": changed["output_bindings"][0]["path"] = "../outside"
                    result_path.write_text(json.dumps(changed))
                    with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate(root)
                result_path.write_text(json.dumps(data[0]))

    def test_archive_inventory_replay_rejects_tampering(self):
        source = json.loads((ROOT / MODULE.PREFIX / "source-lock.json").read_text())
        MODULE.validate_sources(ROOT, source)
        for original in source["sources"][:2]:
            for mutation in ("short", "duplicate", "digest", "size", "escape"):
                changed = deepcopy(original)
                if mutation == "short": changed["inventory"].pop()
                if mutation == "duplicate": changed["inventory"][0] = deepcopy(changed["inventory"][1])
                if mutation == "digest": changed["inventory"][0]["sha256"] = "0" * 64
                if mutation == "size": changed["inventory"][0]["bytes"] += 1
                if mutation == "escape": changed["inventory"][0]["path"] = "../outside"
                with self.subTest(source=original["id"], mutation=mutation), self.assertRaises(ValueError):
                    MODULE.validate_archive(ROOT, changed)
        with tempfile.TemporaryDirectory(prefix="import-source-tamper-") as temporary:
            root = Path(temporary)
            original = source["sources"][0]
            archive = root / original["archive"]
            archive.parent.mkdir(parents=True)
            archive.write_bytes((ROOT / original["archive"]).read_bytes() + b"tampered")
            with self.assertRaisesRegex(ValueError, "archive digest mismatch"):
                MODULE.validate_archive(root, original)


class SemanticImportHistoricalReplayTests(unittest.TestCase):
    def test_four_field_replay_preserves_nonrun_and_shared_nodes(self):
        result = REPLAY.generate()
        raw = json.dumps(result, indent=2, sort_keys=True) + "\n"
        self.assertEqual(raw, (ROOT / MODULE.PREFIX / "historical-observations.json").read_text())
        self.assertFalse(result["current_checker_execution"])
        self.assertEqual(result["normative_authority"], "NOT_ESTABLISHED_BY_THIS_AUDIT")
        cases = result["cases"]
        self.assertEqual(len(cases), 4)
        self.assertEqual({row["pair"]["scalar_differences"][0]["pointer"].rsplit("/", 1)[1] for row in cases},
                         {"k", "type", "cidx", "numIndices"})
        self.assertTrue(all(len(row["pair"]["scalar_differences"]) == 1
                            and row["pair"]["name_and_expression_nodes_unchanged"] for row in cases))
        numindices = next(row for row in cases if row["boundary"] == "inductive.numIndices")
        kiota = next(row for row in numindices["cross_validation"]["rows"] if row["checker"] == "kiota")
        self.assertEqual(kiota["compatibility"], "INCOMPATIBLE")
        self.assertIsNone(kiota["candidate_result"])
        self.assertEqual(kiota["control_result"]["normalized_outcome"], "REJECT")
        self.assertIn("non-uniform nested inductive parameter", kiota["control_result"]["stderr_tail"])

    def test_retained_byte_tamper_is_refused_before_pair_or_observer_claims(self):
        result = REPLAY.generate()
        original_read = Path.read_bytes
        candidate = ROOT / result["cases"][0]["pair"]["candidate"]["path"]
        observer = ROOT / result["cases"][0]["cross_validation"]["binding"]["path"]
        for target in (candidate, observer):
            def tampered_read(path):
                raw = original_read(path)
                return raw + b"tampered" if path == target else raw
            with self.subTest(path=str(target)), patch.object(Path, "read_bytes", tampered_read):
                with self.assertRaisesRegex(ValueError, "historical binding differs"):
                    REPLAY.generate()


if __name__ == "__main__":
    unittest.main()
