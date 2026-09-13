"""Closure gates tested with synthetic outcomes and isolated artifact copies."""
from copy import deepcopy
from datetime import datetime, timedelta
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULE = ModuleType("hsbm_closure_tests")
MODULE.__file__ = str(ROOT / "scripts/validate-hsbm-pilot-closure")
SourceFileLoader(MODULE.__name__, str(ROOT / "scripts/validate-hsbm-pilot-closure")).exec_module(MODULE)


def fixture():
    prefix = ROOT / MODULE.PREFIX
    selection = json.loads((prefix / "selection.json").read_text())
    entry = json.loads((prefix / "work-record.json").read_text())
    requests = json.loads((prefix / "requests.json").read_text())
    ledger = {"item_id": MODULE.ITEM, "rows": [
        {"commit": row["commit"], "arm": row["arm"],
         "boundaries": [{"source_inferred": True}], "decision": "synthetic bounded result"}
        for row in selection["selected"]], "actionable_candidates": []}
    result = {"item_id": MODULE.ITEM, "outcome": "NEGATIVE", "research_counts": {
        "source_setup_requests": requests["charged_source_setup_requests"],
        **{k: 0 for k in ("builds", "checkers", "proofs", "mutations", "new_exports", "external_research_writes")}},
        "next_item": {"id": "SYNTHETIC-SUCCESSOR", "status": "READY", "started": False}}
    work = {"item_id": MODULE.ITEM, "started_at": entry["started_at"],
            "completed_at": (datetime.fromisoformat(entry["started_at"]) + timedelta(seconds=60)).isoformat(),
            "start_monotonic": entry["start_monotonic"],
            "end_monotonic": entry["start_monotonic"] + 60, "active_seconds": 60}
    return selection, ledger, result, work, requests


class HsbmClosureTests(unittest.TestCase):
    def test_retained_fetch_head_bundle_replays_offline(self):
        # This exact bundle advertises no refs/heads branch; clone silently
        # imports no useful history. The gate must import its objects directly.
        bundle = ROOT / MODULE.PREFIX / "nanoda-history.bundle"
        heads = subprocess.check_output(["git", "bundle", "list-heads", str(bundle)]).decode().splitlines()
        self.assertEqual(heads, [MODULE.TIP + " FETCH_HEAD"])
        self.assertTrue(MODULE.reproduce_frozen_selection(ROOT))

    def test_valid_negative_and_two_candidate_success(self):
        data = fixture()
        MODULE.validate_data(*data)
        data[1]["actionable_candidates"] = [
            {"id": f"candidate-{i}", "commit": row["commit"], "fresh_commit_candidate": True}
            for i, row in enumerate(data[0]["selected"][:2])]
        data[2]["outcome"] = "SUCCESS"
        MODULE.validate_data(*data)
        for candidate in data[1]["actionable_candidates"]:
            candidate["fresh_commit_candidate"] = False
        data[2]["outcome"] = "NEGATIVE"
        MODULE.validate_data(*data)

    def test_selection_and_boundary_tampering(self):
        for mutation in ("duplicate", "replace", "arm", "empty", "four_boundaries", "missing_decision"):
            with self.subTest(mutation=mutation):
                data = fixture()
                rows = data[1]["rows"]
                if mutation == "duplicate": rows[1] = deepcopy(rows[0])
                if mutation == "replace": rows[0]["commit"] = "a" * 40
                if mutation == "arm": rows[0]["arm"] = "CONTROL"
                if mutation == "empty": rows[0]["boundaries"] = [{}]
                if mutation == "four_boundaries": rows[0]["boundaries"] *= 4
                if mutation == "missing_decision": rows[0]["decision"] = ""
                with self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_candidate_yield_cannot_be_inflated(self):
        for mutation in ("unsupported_success", "same_commit", "unselected", "too_many", "negative_with_two", "known_as_fresh", "nonboolean_freshness"):
            with self.subTest(mutation=mutation):
                data = fixture()
                candidates = [{"id": f"c{i}", "commit": row["commit"], "fresh_commit_candidate": True}
                              for i, row in enumerate(data[0]["selected"][:2])]
                data[1]["actionable_candidates"] = candidates
                data[2]["outcome"] = "SUCCESS"
                if mutation == "unsupported_success": candidates.pop()
                if mutation == "same_commit": candidates[1]["commit"] = candidates[0]["commit"]
                if mutation == "unselected": candidates[1]["commit"] = "a" * 40
                if mutation == "too_many": candidates.append({"id": "c2", "commit": data[0]["selected"][2]["commit"]})
                if mutation == "negative_with_two": data[2]["outcome"] = "NEGATIVE"
                if mutation == "known_as_fresh": candidates[1]["fresh_commit_candidate"] = False
                if mutation == "nonboolean_freshness": candidates[1]["fresh_commit_candidate"] = "true"
                with self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_clock_and_budget_tampering(self):
        for mutation in ("nan", "negative", "duration", "utc", "over_cap", "naive_utc"):
            with self.subTest(mutation=mutation):
                data = fixture()
                work = data[3]
                if mutation == "nan": work["active_seconds"] = float("nan")
                if mutation == "negative": work["active_seconds"] = -1
                if mutation == "duration": work["active_seconds"] = 1
                if mutation == "utc": work["completed_at"] = work["started_at"]
                if mutation == "over_cap":
                    work["active_seconds"] = 7201
                    work["end_monotonic"] = work["start_monotonic"] + 7201
                if mutation == "naive_utc": work["completed_at"] = "2026-09-13T14:00:00"
                with self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_launch_request_and_successor_gates(self):
        for mutation in ("build", "source_mismatch", "lost_cost", "over_request_cap", "started_successor"):
            with self.subTest(mutation=mutation):
                data = fixture()
                result, requests = data[2], data[4]
                if mutation == "build": result["research_counts"]["builds"] = 1
                if mutation == "source_mismatch": result["research_counts"]["source_setup_requests"] = 0
                if mutation == "lost_cost": requests["requests"] = []
                if mutation == "over_request_cap":
                    requests["requests"].append({"id": 99, "charged_requests": 9})
                    requests["charged_source_setup_requests"] += 9
                    result["research_counts"]["source_setup_requests"] += 9
                if mutation == "started_successor": result["next_item"]["started"] = True
                with self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_isolated_binding_and_frozen_input_tampering(self):
        data = fixture()
        with tempfile.TemporaryDirectory(prefix="hsbm-closure-test-") as temporary:
            root = Path(temporary)
            prefix = root / MODULE.PREFIX
            prefix.mkdir(parents=True)
            (root / "scripts").mkdir()
            for name in ("entry-lock.json", "source-lock.json", "selection.json", "requests.json", "work-record.json", "nanoda-history.bundle"):
                shutil.copyfile(ROOT / MODULE.PREFIX / name, prefix / name)
            shutil.copyfile(ROOT / "scripts/hsbm-pilot", root / "scripts/hsbm-pilot")
            for name, value in zip(("ledger.json", "result.json", "work-closure.json"), data[1:4]):
                (prefix / name).write_text(json.dumps(value))
            names = ("ledger.json", "result.json", "work-closure.json", "requests.json", "nanoda-history.bundle")
            manifest = {"bindings": [{"path": MODULE.PREFIX + name, "sha256": MODULE.digest((prefix / name).read_bytes())} for name in names]}
            (prefix / "artifact-bindings.json").write_text(json.dumps(manifest))
            real_git_bytes = MODULE.git_bytes
            with patch.object(MODULE, "git_bytes", side_effect=lambda _, revision, name: real_git_bytes(ROOT, revision, name)):
                self.assertTrue(MODULE.validate(root))
                ledger = prefix / "ledger.json"
                original = ledger.read_bytes()
                ledger.write_bytes(original + b" ")
                with self.assertRaisesRegex(ValueError, "artifact hash mismatch"):
                    MODULE.validate(root)
                ledger.write_bytes(original)
                selection = prefix / "selection.json"
                selection.write_bytes(selection.read_bytes() + b" ")
                with self.assertRaisesRegex(ValueError, "frozen input changed"):
                    MODULE.validate(root)


if __name__ == "__main__":
    unittest.main()
