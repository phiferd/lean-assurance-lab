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
MODULE = ModuleType("arena_inductive_isolation_closure")
MODULE.__file__ = str(ROOT / "scripts/validate-arena-inductive-isolation-closure")
SourceFileLoader(MODULE.__name__, MODULE.__file__).exec_module(MODULE)

REPLAY = ModuleType("arena_inductive_static_audit")
REPLAY.__file__ = str(ROOT / MODULE.PREFIX / "replay-static-audit.py")
SourceFileLoader(REPLAY.__name__, REPLAY.__file__).exec_module(REPLAY)


def fixture():
    entry = json.loads((ROOT / MODULE.PREFIX / "work-record.json").read_text())
    counts = {"read_only_requests": 1, **{key: 0 for key in MODULE.ZERO_COUNTS}}
    result = {"item_id": MODULE.ITEM, "status": "COMPLETE", "outcome": "NEGATIVE",
              "nominated_packages": 0, "catalog_changed": False, "authority_changed": False,
              "entry_commit": MODULE.ENTRY_COMMIT, "freeze_commit": MODULE.FREEZE_COMMIT, "research_counts": counts,
              "next_item": {"id": "SYNTHETIC-NEXT", "status": "READY", "started": False}}
    closure = {"item_id": MODULE.ITEM, "status": "COMPLETE", "outcome": result["outcome"],
               "started_at": entry["started_at"], "start_monotonic": entry["start_monotonic"],
               "completed_at": (datetime.fromisoformat(entry["started_at"]) + timedelta(seconds=60)).isoformat(),
               "end_monotonic": entry["start_monotonic"] + 60, "active_seconds": 60,
               "research_counts": deepcopy(counts), "next_item": "SYNTHETIC-NEXT", "next_item_started": False}
    requests = {"item_id": MODULE.ITEM, "cap": 8, "charged_requests": 1,
                "requests": [{"id": "source-1", "charged_requests": 1}]}
    selection = json.loads((ROOT / MODULE.PREFIX / "selection.json").read_text())
    assessment = {"item_id": MODULE.ITEM, "cases": deepcopy(selection["cases"]), "nominated_packages": 0}
    queue = {"selected_item": "SYNTHETIC-NEXT", "items": [
        {"id": MODULE.ITEM, "status": "COMPLETE", "closure": {"outcome": result["outcome"]}},
        {"id": "SYNTHETIC-NEXT", "status": "READY"}]}
    return result, entry, closure, requests, assessment, queue, selection


class ArenaInductiveIsolationClosureTests(unittest.TestCase):
    def test_valid_scoped_closure(self):
        MODULE.validate_data(*fixture())

    def test_inflated_claims_and_launches_refused(self):
        for target, key, value in ((0, "outcome", "SUCCESS"), (0, "nominated_packages", 1),
                                   (0, "catalog_changed", True), (0, "authority_changed", True),
                                   (4, "nominated_packages", 1), (6, "replacement_allowed", True)):
            with self.subTest(key=key):
                data = fixture()
                data[target][key] = value
                with self.assertRaises(ValueError): MODULE.validate_data(*data)
        for target in (4, 6):
            for mutation in ("replace", "duplicate", "short"):
                data = fixture()
                if mutation == "replace": data[target]["cases"][0]["id"] = "unselected-case"
                if mutation == "duplicate": data[target]["cases"][0] = deepcopy(data[target]["cases"][1])
                if mutation == "short": data[target]["cases"].pop()
                with self.subTest(target=target, mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)
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
            if mutation == "wrong_outcome": data[5]["items"][0]["closure"]["outcome"] = "SUCCESS"
            if mutation == "duplicate": data[5]["items"].append(deepcopy(data[5]["items"][1]))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): MODULE.validate_data(*data)

    def test_delivery_accounting_preserves_inclusive_cap_and_handoff(self):
        result, entry, closure, *_ = fixture()
        delivery = {"item_id": MODULE.ITEM, "started_at": entry["started_at"],
                    "start_monotonic": entry["start_monotonic"],
                    "recorded_at": (datetime.fromisoformat(entry["started_at"]) + timedelta(seconds=120)).isoformat(),
                    "end_monotonic": entry["start_monotonic"] + 120,
                    "cumulative_active_seconds": 120, "administrative_seconds_after_work_closure": 60,
                    "remaining_seconds": 5280, "cap_seconds": 5400,
                    "research_counts": deepcopy(result["research_counts"]),
                    "next_item": result["next_item"]["id"], "next_item_started": False}
        MODULE.validate_delivery(delivery, entry, closure, result)
        for mutation in ("reset", "nonfinite", "overcap", "underclosure", "counts", "successor", "utc", "remaining", "admin", "cap"):
            changed = deepcopy(delivery)
            if mutation == "reset": changed["start_monotonic"] += 1
            if mutation == "nonfinite": changed["cumulative_active_seconds"] = float("nan")
            if mutation in ("overcap", "underclosure"):
                active = 5401 if mutation == "overcap" else 59
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
        with tempfile.TemporaryDirectory(prefix="inductive-closure-test-") as temporary:
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
            for name in ("source-lock.json", "selection.json", "arena-source.tar.gz"):
                raw = (ROOT / MODULE.PREFIX / name).read_bytes()
                (prefix / name).write_bytes(raw)
                history[(MODULE.FREEZE_COMMIT, MODULE.PREFIX + name)] = raw
            for name, value in (("work-closure.json", data[2]), ("requests.json", data[3]),
                                ("case-assessment.json", data[4]), ("closure-queue.json", data[5])):
                (prefix / name).write_text(json.dumps(value))
            data[0]["output_bindings"] = [{"path": MODULE.PREFIX + name, "sha256": MODULE.digest((prefix / name).read_bytes()),
                                          "bytes": (prefix / name).stat().st_size}
                                         for name in ("source-lock.json", "selection.json", "work-closure.json", "requests.json", "case-assessment.json", "closure-queue.json")]
            result_path = prefix / "result.json"
            result_path.write_text(json.dumps(data[0]))
            with patch.object(MODULE, "git_bytes", side_effect=lambda _, revision, path: history[(revision, path)]):
                # Live queue can advance without invalidating a historical closure.
                (root / "config").mkdir()
                (root / "config/research-queue.json").write_text('{"selected_item":"LATER-ITEM"}')
                self.assertEqual(MODULE.validate(root)["status"], "PASS")
                for name in ("case-assessment.json", "work-record.json", "selection.json", "source-lock.json", "arena-source.tar.gz"):
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
                source = json.loads((prefix / "source-lock.json").read_text())
                for mutation in ("short", "duplicate", "digest", "size", "escape"):
                    changed = deepcopy(source)
                    if mutation == "short": changed["inventory"].pop()
                    if mutation == "duplicate": changed["inventory"][0] = deepcopy(changed["inventory"][1])
                    if mutation == "digest": changed["inventory"][0]["sha256"] = "0" * 64
                    if mutation == "size": changed["inventory"][0]["bytes"] += 1
                    if mutation == "escape": changed["inventory"][0]["path"] = "../outside"
                    with self.subTest(inventory=mutation), self.assertRaises(ValueError): MODULE.validate_archive(root, changed)
                archive = prefix / "arena-source.tar.gz"
                with archive.open("ab") as handle: handle.write(b"tampered")
                with self.assertRaisesRegex(ValueError, "archive digest mismatch"): MODULE.validate_archive(root, source)



class ArenaInductiveStaticAuditTests(unittest.TestCase):
    def test_generated_audit_replays_and_complete_reuse_is_exact(self):
        result = REPLAY.replay()
        self.assertEqual(REPLAY.encoded(result), (ROOT / MODULE.PREFIX / "static-audit.json").read_bytes())
        self.assertEqual(result["archive_file_count"], 232)
        self.assertEqual(len(result["cases"]), 4)
        self.assertTrue(all(comparison["byte_identical"]
                            for row in result["existing_complete_artifact_comparisons"]
                            for comparison in row["retained_comparisons"]))

    def test_copied_evidence_tampering_is_rejected(self):
        original_read = REPLAY.read
        review_path = MODULE.PREFIX + "independent-case-review.json"
        review = json.loads(original_read(ROOT, review_path))
        for mutation in ("candidate", "control", "source", "diagnostic", "identity", "recursor", "pointer", "case"):
            changed = deepcopy(review)
            case = changed["cases"][0]
            if mutation == "candidate": case["existing_candidate"]["sha256"] = "0" * 64
            if mutation == "control": case["existing_control"]["sha256"] = "0" * 64
            if mutation == "source": changed["sources"][0]["sha256"] = "0" * 64
            if mutation == "diagnostic": case["historical_observations"]["validators"][0]["diagnostic"] = "invented"
            if mutation == "identity": case["historical_observations"]["validators"][0]["identity"]["version"] = "current"
            if mutation == "recursor": case["existing_candidate"]["recursor_records"][0][0]["numMotives"] = 1
            if mutation == "pointer": case["historical_observations"]["validators"][0]["json_pointer"] = "/validators/1/result"
            if mutation == "case": case["id"] = "replacement-case"
            def read_changed(root, path):
                return REPLAY.encoded(changed) if path == review_path else original_read(root, path)
            with self.subTest(mutation=mutation), patch.object(REPLAY, "read", side_effect=read_changed):
                with self.assertRaises(ValueError): REPLAY.replay()


if __name__ == "__main__":
    unittest.main()
