import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
ERRATUM = ROOT / "results/research/arena-let-regression-1/arena-audit-erratum.json"
REPAIR = ROOT / "results/research/arena-let-regression-1/post-closure-repair.json"
REPAIR_SUCCESSOR = ROOT / "results/research/arena-let-regression-1/post-closure-repair-r2.json"
REPAIR_QUEUE_SUCCESSOR = ROOT / "results/research/arena-let-regression-1/post-closure-repair-r3.json"
QUEUE = ROOT / "config/research-queue.json"
STATUS = ROOT / "docs/RESEARCH_STATUS.md"
QUEUE_VALIDATOR = ROOT / "scripts/validate-research-queue"
FIRST_REPAIR_COMMIT = "7aef82e104b04b0f4fbef19f71c11e294d18d092"
SECOND_REPAIR_COMMIT = "0121fc80c9a0aa5d3fcc731c69fa091b64dd1d21"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def committed_bytes(commit, path):
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def blob_bytes(blob):
    return subprocess.check_output(["git", "cat-file", "blob", blob], cwd=ROOT)


class ArenaLetRegressionErratumTests(unittest.TestCase):
    def test_erratum_preserves_and_binds_the_original_closure(self):
        document = json.loads(ERRATUM.read_text(encoding="utf-8"))
        original = document["applies_to"]
        frozen = committed_bytes(original["git_commit"], original["path"])
        self.assertEqual(sha256(frozen), original["sha256"])
        self.assertEqual((ROOT / original["path"]).read_bytes(), frozen)

        attribution, evidence, inventory = document["corrections"]
        for correction, key in ((attribution, "authority"), (evidence, "evidence")):
            binding = correction[key]
            self.assertEqual(
                sha256(committed_bytes(original["git_commit"], binding["path"])),
                binding["sha256"],
            )

        listing = inventory["reproducible_inventory"]["listing"]
        data = (ROOT / listing["path"]).read_bytes()
        self.assertEqual(sha256(data), listing["sha256"])
        self.assertEqual(len(data.splitlines()), listing["line_count"])
        self.assertFalse(document["effect"]["scientific_outcome_changed"])
        self.assertFalse(document["effect"]["historical_artifact_rewritten"])

    def test_status_ready_count_matches_the_canonical_queue(self):
        queue = json.loads(QUEUE.read_text(encoding="utf-8"))
        ready = sum(item["status"] == "READY" for item in queue["items"])
        active = STATUS.read_text(encoding="utf-8").split("### Active", 1)[1]
        active = active.split("### Waiting", 1)[0]
        match = re.search(r"canonical queue retains (\w+) READY items", active)
        self.assertIsNotNone(match)
        words = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10,
        }
        self.assertIn(match.group(1), words)
        self.assertEqual(words[match.group(1)], ready)

    def test_repair_record_binds_successors_without_scientific_change(self):
        repair = json.loads(REPAIR.read_text(encoding="utf-8"))
        self.assertEqual(
            REPAIR.read_bytes(),
            committed_bytes(FIRST_REPAIR_COMMIT, str(REPAIR.relative_to(ROOT))),
        )
        for binding in repair["bindings"]:
            self.assertEqual(
                sha256(committed_bytes(FIRST_REPAIR_COMMIT, binding["path"])),
                binding["sha256"],
            )
        queue = json.loads(committed_bytes(FIRST_REPAIR_COMMIT, "config/research-queue.json"))
        self.assertEqual(queue["selected_item"], "NANODA-CACHE-REGRESSION-1")
        subprocess.run([QUEUE_VALIDATOR, "--require-ready"], cwd=ROOT, check=True, capture_output=True)
        self.assertFalse(repair["scientific_effect"]["arena_closure_outcome_changed"])
        self.assertFalse(repair["scientific_effect"]["catalog_or_authority_changed"])
        self.assertFalse(repair["scientific_effect"]["scientific_inputs_changed"])

    def test_followup_repair_binds_portable_cache_validation(self):
        repair = json.loads(REPAIR_SUCCESSOR.read_text(encoding="utf-8"))
        self.assertEqual(
            REPAIR_SUCCESSOR.read_bytes(),
            committed_bytes(SECOND_REPAIR_COMMIT, str(REPAIR_SUCCESSOR.relative_to(ROOT))),
        )
        predecessor = repair["predecessor"]
        self.assertEqual(predecessor["git_commit"], FIRST_REPAIR_COMMIT)
        self.assertEqual(
            sha256(committed_bytes(FIRST_REPAIR_COMMIT, predecessor["path"])),
            predecessor["sha256"],
        )
        for binding in repair["bindings"]:
            self.assertEqual(
                sha256(committed_bytes(SECOND_REPAIR_COMMIT, binding["path"])),
                binding["sha256"],
            )
        self.assertEqual(repair["github_actions_failure"]["run_id"], 34415285434)
        self.assertFalse(repair["scientific_effect"]["scientific_inputs_changed"])
        self.assertEqual(repair["selected_next_item"], "NANODA-CACHE-REGRESSION-1")

    def test_queue_evolution_repair_preserves_both_historical_repairs(self):
        repair = json.loads(REPAIR_QUEUE_SUCCESSOR.read_text(encoding="utf-8"))
        predecessor = repair["predecessor"]
        self.assertEqual(predecessor["git_commit"], SECOND_REPAIR_COMMIT)
        self.assertEqual(
            sha256(committed_bytes(SECOND_REPAIR_COMMIT, predecessor["path"])),
            predecessor["sha256"],
        )
        test_binding = repair["test_binding"]
        data = blob_bytes(test_binding["git_blob"])
        self.assertEqual(len(data), test_binding["bytes"])
        self.assertEqual(sha256(data), test_binding["sha256"])
        queue = json.loads(committed_bytes(SECOND_REPAIR_COMMIT, "config/research-queue.json"))
        self.assertEqual(queue["selected_item"], "NANODA-CACHE-REGRESSION-1")
        subprocess.run([QUEUE_VALIDATOR, "--require-ready"], cwd=ROOT, check=True, capture_output=True)
        self.assertFalse(repair["scientific_effect"]["arena_closure_outcome_changed"])
        self.assertFalse(repair["scientific_effect"]["scientific_inputs_changed"])


if __name__ == "__main__":
    unittest.main()
