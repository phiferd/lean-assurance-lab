"""Preserve static-only claims, exact package bytes, budgets and historical handoff."""
from copy import deepcopy
from datetime import datetime, timedelta
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import shutil
import tempfile
from types import ModuleType
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ModuleType("arena_let_policy_followup_closure")
MODULE.__file__ = str(ROOT / "scripts/validate-arena-let-policy-followup-closure")
SourceFileLoader(MODULE.__name__, MODULE.__file__).exec_module(MODULE)


def read(name):
    return json.loads((ROOT / MODULE.PREFIX / name).read_text())


def fixture():
    entry = read("work-record.json")
    counts = {"read_only_requests": 4, "static_build_test_reservations": 1, **{key: 0 for key in MODULE.ZERO_COUNTS}}
    result = {"item_id": MODULE.ITEM, "status": "COMPLETE", "outcome": "SUCCESS", "candidate_label": "either",
              "current_checker_execution": False, "catalog_changed": False, "authority_changed": False,
              "package_count": 1, "control_included": False, "source_revision": MODULE.SOURCE_REVISION,
              "research_counts": counts, "next_item": {"id": "NANODA-NESTED-REGRESSION-1", "status": "READY", "started": False}}
    closure = {"item_id": MODULE.ITEM, "status": "COMPLETE", "outcome": "SUCCESS", "started_at": entry["started_at"],
               "start_monotonic": entry["start_monotonic"], "end_monotonic": entry["start_monotonic"] + 60,
               "completed_at": (datetime.fromisoformat(entry["started_at"]) + timedelta(seconds=60)).isoformat(),
               "active_seconds": 60, "research_counts": deepcopy(counts), "next_item": "NANODA-NESTED-REGRESSION-1", "next_item_started": False}
    queue = {"selected_item": "NANODA-NESTED-REGRESSION-1", "items": [
        {"id": MODULE.ITEM, "status": "COMPLETE", "closure": {"outcome": "SUCCESS"}},
        {"id": "NANODA-NESTED-REGRESSION-1", "status": "READY"}]}
    return result, entry, closure, read("requests.json"), queue


class ArenaLetPolicyFollowupClosureTests(unittest.TestCase):
    def test_scoped_closure_validates_without_live_queue(self):
        MODULE.validate_data(*fixture())

    def test_strict_label_and_execution_promotion_refused(self):
        for key, value in (("candidate_label", "reject"), ("candidate_label", "accept"), ("current_checker_execution", True),
                           ("catalog_changed", True), ("authority_changed", True), ("package_count", 2), ("control_included", True)):
            data = fixture()
            data[0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                MODULE.validate_data(*data)

    def test_request_and_scientific_charges_cannot_be_erased(self):
        for mutation in ("missing", "uncharged", "duplicate", "boolean", "too_many_builds", *MODULE.ZERO_COUNTS):
            data = fixture()
            if mutation == "missing": data[3]["requests"].pop()
            elif mutation == "uncharged": data[3]["requests"][0]["charged_requests"] = 0
            elif mutation == "duplicate": data[3]["requests"][1]["id"] = 1
            elif mutation == "boolean": data[3]["requests"][0]["charged_requests"] = True
            else:
                key = "static_build_test_reservations" if mutation == "too_many_builds" else mutation
                data[0]["research_counts"][key] = data[2]["research_counts"][key] = 3 if mutation == "too_many_builds" else 1
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_clock_reset_nonfinite_and_cap_refused(self):
        for mutation in ("reset", "nan", "over_cap", "utc"):
            data = fixture()
            closure = data[2]
            if mutation == "reset": closure["start_monotonic"] += 1
            if mutation == "nan": closure["active_seconds"] = float("nan")
            if mutation == "over_cap":
                closure["active_seconds"] = 3601
                closure["end_monotonic"] = closure["start_monotonic"] + 3601
                closure["completed_at"] = (datetime.fromisoformat(closure["started_at"]) + timedelta(seconds=3601)).isoformat()
            if mutation == "utc": closure["completed_at"] = closure["started_at"]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_successor_cannot_be_started_or_snapshot_replaced(self):
        for mutation in ("started", "queue_active", "selected"):
            data = fixture()
            if mutation == "started": data[0]["next_item"]["started"] = True
            if mutation == "queue_active": data[4]["items"][1]["status"] = "ACTIVE"
            if mutation == "selected": data[4]["selected_item"] = MODULE.ITEM
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_complete_archive_inventory_replays_and_omission_fails(self):
        source = read("source-lock.json")
        MODULE.validate_source(ROOT, source)
        source["files"].pop()
        with self.assertRaisesRegex(ValueError, "incomplete source inventory"): MODULE.validate_source(ROOT, source)

    def test_exact_candidate_cannot_be_replaced_even_with_rebound_hash(self):
        manifest = read("execution-manifest.json")
        MODULE.validate_package(ROOT, manifest)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for row in manifest["package"] + [manifest["patch"], manifest["source_lock"], manifest["candidate"]]:
                target = root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], target)
            row = next(row for row in manifest["package"] if row["path"].endswith(".ndjson"))
            target = root / row["path"]
            raw = target.read_bytes().replace(b'"type":1,"value":1', b'"type":2,"value":1')
            target.write_bytes(raw)
            row["sha256"], row["bytes"] = MODULE.digest(raw), len(raw)
            with self.assertRaisesRegex(ValueError, "candidate differs"): MODULE.validate_package(root, manifest)

    def test_static_cleanup_and_statistics_are_verified(self):
        manifest, counts = read("execution-manifest.json"), fixture()[0]["research_counts"]
        MODULE.validate_static(ROOT, manifest, counts)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / MODULE.PREFIX
            target.mkdir(parents=True)
            for name in ("execution-manifest.json", "run-static-build.py"):
                shutil.copyfile(ROOT / MODULE.PREFIX / name, target / name)
            shutil.copytree(ROOT / MODULE.PREFIX / "static-build-01", target / "static-build-01")
            supervisor_path = target / "static-build-01/supervisor.json"
            supervisor = json.loads(supervisor_path.read_text())
            supervisor["cleanup_completed"] = False
            supervisor_path.write_text(json.dumps(supervisor))
            with self.assertRaisesRegex(ValueError, "cleanup"): MODULE.validate_static(root, manifest, counts)
            supervisor["cleanup_completed"] = True
            supervisor_path.write_text(json.dumps(supervisor))
            stats_path = target / "static-build-01/let-value-type-mismatch.stats.json"
            stats = json.loads(stats_path.read_text())
            stats["outcome"] = "accept"
            stats_path.write_text(json.dumps(stats))
            receipt_path = target / "static-build-01/result.json"
            receipt = json.loads(receipt_path.read_text())
            row = next(row for row in receipt["files"] if row["path"].endswith(".stats.json"))
            row["sha256"], row["bytes"] = MODULE.digest(stats_path.read_bytes()), stats_path.stat().st_size
            receipt_path.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, "statistics"): MODULE.validate_static(root, manifest, counts)


if __name__ == "__main__":
    unittest.main()
