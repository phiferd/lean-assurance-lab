"""Pure package tamper checks; Git access is read-only, with no checker launches."""

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from lib.transfer_assessment import PACKAGE, ROOT, validate


class TransferAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="transfer-integrity-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / PACKAGE
        self.manifest = json.loads((ROOT / PACKAGE / "evidence-manifest.json").read_text())
        for binding in self.manifest["files"]:
            target = self.root / binding["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / binding["path"], target)
        self.write("evidence-manifest.json", self.manifest, rebind=False)
        gitdir = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "--absolute-git-dir"], text=True).strip()
        (self.root / ".git").write_text(f"gitdir: {gitdir}\n")
        work = self.read("work-record.json")
        for binding in self.manifest["preserved_inputs"]:
            target = self.root / binding["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(subprocess.check_output(
                ["git", "-C", str(ROOT), "show", f"{work['base_commit']}:{binding['path']}"]))

    def read(self, name):
        return json.loads((self.package / name).read_text())

    def write(self, name, value, rebind=True):
        p = self.package / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value, indent=2) + "\n")
        if rebind:
            self.rebind(p)

    def rebind(self, path):
        relative = path.relative_to(self.root).as_posix()
        row = next(b for b in self.manifest["files"] if b["path"] == relative)
        row.update(bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        self.write("evidence-manifest.json", self.manifest, rebind=False)

    def reject(self, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            validate(self.root)

    def test_historical_and_current_integrity(self):
        result = validate(self.root)
        self.assertEqual(result["scope"], "EVIDENCE_AND_ACCOUNTING_INTEGRITY_ONLY")
        self.assertFalse(result["scientific_eligibility_proved"])
        self.assertTrue(validate(self.root, check_current_preservation=True)["current_preservation_checked"])

    def test_altered_evidence_bytes(self):
        with (self.package / "sources.json").open("a") as stream:
            stream.write(" ")
        self.reject("hash/size mismatch")

    def test_no_go_cannot_be_forged_as_go(self):
        result = self.read("result.json")
        result["gate_decision"] = "GO"
        self.write("result.json", result)
        self.reject("no-go result boundary")

    def test_no_go_cannot_smuggle_design(self):
        result = self.read("result.json")
        result["design"] = {"target": "an invented holdout"}
        self.write("result.json", result)
        self.reject("no-go result boundary")

    def test_invented_launch_rejected_even_if_work_agrees(self):
        for name in ("result.json", "work-record.json"):
            record = self.read(name)
            record["research_counts"]["checker_launches"] = 1
            self.write(name, record)
        self.reject("unauthorized research")

    def test_boolean_zero_is_not_integer_counter(self):
        result = self.read("result.json")
        result["research_counts"]["checker_launches"] = False
        self.write("result.json", result)
        self.reject("unauthorized research")

    def test_nonfinite_budget(self):
        work = self.read("work-record.json")
        work["active_seconds"] = float("nan")
        self.write("work-record.json", work)
        self.reject("nonfinite JSON")

    def test_overflow_budget(self):
        work = self.read("work-record.json")
        work["active_seconds"] = 5401
        self.write("work-record.json", work)
        self.reject("active budget")

    def test_interval_accounting_cannot_be_undercharged(self):
        work = self.read("work-record.json")
        work["active_seconds"] -= 1
        self.write("work-record.json", work)
        self.reject("accounting mismatch")

    def test_open_reservation_rejected(self):
        work = self.read("work-record.json")
        work["source_reviews"][0]["status"] = "RESERVED"
        self.write("work-record.json", work)
        self.reject("unclosed")

    def test_snapshot_cannot_be_rebound_away_from_git(self):
        work = self.read("work-record.json")
        binding = work["entry_bindings"][0]
        snapshot = self.root / binding["snapshot"]
        snapshot.write_bytes(snapshot.read_bytes() + b"\nTampered history.\n")
        binding.update(bytes=snapshot.stat().st_size, sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest())
        self.rebind(snapshot)
        self.write("work-record.json", work)
        self.reject("hash/size mismatch")

    def test_dropped_primary_source(self):
        sources = self.read("sources.json")
        sources["records"].pop()
        self.write("sources.json", sources)
        self.reject("source inventory")

    def test_dropped_candidate_route(self):
        assessment = self.read("target-assessment.json")
        assessment["routes"].pop()
        self.write("target-assessment.json", assessment)
        self.reject("route inventory")

    def test_deleted_manifest_row(self):
        self.manifest["files"].pop()
        self.write("evidence-manifest.json", self.manifest, rebind=False)
        self.reject("package inventory")

    def test_duplicate_json_key(self):
        path = self.package / "result.json"
        raw = path.read_text().replace('"schema_version": 1,', '"schema_version": 1, "schema_version": 1,', 1)
        path.write_text(raw)
        self.rebind(path)
        self.reject("duplicate JSON key")

    def test_unsafe_manifest_path(self):
        self.manifest["files"][0]["path"] = "../outside"
        self.write("evidence-manifest.json", self.manifest, rebind=False)
        self.reject("package inventory|unsafe relative path")

    def test_invalid_local_json_pointer(self):
        local = self.read("local-independence-review.json")
        source = next(s for s in local["sources"] if s.get("json_pointers"))
        source["json_pointers"] = ["/missing~2key"]
        self.write("local-independence-review.json", local)
        self.reject("bad JSON pointer escape")

    def test_future_live_successor_does_not_rewrite_history(self):
        path = self.root / "results/mutants/registry.jsonl"
        path.write_bytes(path.read_bytes() + b"\n")
        self.assertEqual(validate(self.root)["status"], "PASS")
        with self.assertRaisesRegex(ValueError, "hash/size mismatch"):
            validate(self.root, check_current_preservation=True)


if __name__ == "__main__":
    unittest.main()
