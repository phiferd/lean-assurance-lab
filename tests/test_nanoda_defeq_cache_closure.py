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
MODULE = ModuleType("nanoda_defeq_cache_closure")
MODULE.__file__ = str(ROOT / "scripts/validate-nanoda-defeq-cache-closure")
SourceFileLoader(MODULE.__name__, MODULE.__file__).exec_module(MODULE)


def fixture():
    entry = json.loads((ROOT / MODULE.PREFIX / "work-record.json").read_text())
    counts = {"read_only_requests": 1, **{key: 0 for key in MODULE.ZERO_COUNTS}}
    result = {"item_id": MODULE.ITEM, "status": "COMPLETE", "outcome": "BOUNDED_UNRESOLVED",
              "mode_outcome_witness_established": False, "global_mode_equivalence_established": False,
              "entry_commit": "a" * 40, "research_counts": counts,
              "next_item": {"id": "SYNTHETIC-NEXT", "status": "READY", "started": False}}
    closure = {"item_id": MODULE.ITEM, "status": "COMPLETE", "outcome": result["outcome"],
               "started_at": entry["started_at"], "start_monotonic": entry["start_monotonic"],
               "completed_at": (datetime.fromisoformat(entry["started_at"]) + timedelta(seconds=60)).isoformat(),
               "end_monotonic": entry["start_monotonic"] + 60, "active_seconds": 60,
               "research_counts": deepcopy(counts), "next_item": "SYNTHETIC-NEXT", "next_item_started": False}
    requests = {"item_id": MODULE.ITEM, "cap": 8, "charged_read_only_requests": 1,
                "requests": [{"id": "source-1", "charged_requests": 1}]}
    assessment = {"item_id": MODULE.ITEM, "mode_outcome_witness_established": False,
                  "global_mode_equivalence_established": False}
    queue = {"selected_item": "SYNTHETIC-NEXT", "items": [
        {"id": MODULE.ITEM, "status": "COMPLETE", "closure": {"outcome": result["outcome"]}},
        {"id": "SYNTHETIC-NEXT", "status": "READY"}]}
    return result, entry, closure, requests, assessment, queue


class NanodaDefeqCacheClosureTests(unittest.TestCase):
    def test_valid_scoped_closure(self):
        MODULE.validate_data(*fixture())

    def test_inflated_claims_and_launches_refused(self):
        for target, key, value in ((0, "outcome", "SUCCESS"), (0, "mode_outcome_witness_established", True),
                                   (0, "global_mode_equivalence_established", True), (4, "mode_outcome_witness_established", True),
                                   (4, "global_mode_equivalence_established", True)):
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
            if mutation == "wrong_outcome": data[5]["items"][0]["closure"]["outcome"] = "SUCCESS"
            if mutation == "duplicate": data[5]["items"].append(deepcopy(data[5]["items"][1]))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_artifact_binding_tampering_and_mutable_queue_independence(self):
        data = fixture()
        with tempfile.TemporaryDirectory(prefix="defeq-closure-test-") as temporary:
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
            source = {"item_id": MODULE.ITEM, "tip": MODULE.TIP,
                      "history_bundle": MODULE.BUNDLE, "history_bundle_sha256": MODULE.BUNDLE_SHA}
            for name, value in (("source-lock.json", source), ("work-closure.json", data[2]),
                                ("requests.json", data[3]), ("source-assessment.json", data[4]), ("closure-queue.json", data[5])):
                (prefix / name).write_text(json.dumps(value))
            data[0]["output_bindings"] = [{"path": MODULE.PREFIX + name, "sha256": MODULE.digest((prefix / name).read_bytes()),
                                          "bytes": (prefix / name).stat().st_size}
                                         for name in ("source-lock.json", "work-closure.json", "requests.json", "source-assessment.json", "closure-queue.json")]
            result_path = prefix / "result.json"
            result_path.write_text(json.dumps(data[0]))
            with patch.object(MODULE, "git_bytes", side_effect=lambda _, revision, path: history[(revision, path)]):
                # Live queue can advance without invalidating a historical closure.
                (root / "config").mkdir()
                (root / "config/research-queue.json").write_text('{"selected_item":"LATER-ITEM"}')
                self.assertEqual(MODULE.validate(root)["status"], "PASS")
                for name in ("source-assessment.json", "work-record.json"):
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
                with bundle.open("ab") as handle: handle.write(b"tampered")
                with self.assertRaisesRegex(ValueError, "bundle mismatch"): MODULE.validate(root)


if __name__ == "__main__":
    unittest.main()
