import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
ERRATUM = ROOT / "results/research/arena-let-regression-1/arena-audit-erratum.json"
REPAIR = ROOT / "results/research/arena-let-regression-1/post-closure-repair.json"
QUEUE = ROOT / "config/research-queue.json"
STATUS = ROOT / "docs/RESEARCH_STATUS.md"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def committed_bytes(commit, path):
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


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
        for binding in repair["bindings"]:
            self.assertEqual(
                sha256((ROOT / binding["path"]).read_bytes()), binding["sha256"]
            )
        queue = json.loads(QUEUE.read_text(encoding="utf-8"))
        self.assertEqual(queue["selected_item"], "NANODA-CACHE-REGRESSION-1")
        self.assertFalse(repair["scientific_effect"]["arena_closure_outcome_changed"])
        self.assertFalse(repair["scientific_effect"]["catalog_or_authority_changed"])
        self.assertFalse(repair["scientific_effect"]["scientific_inputs_changed"])


if __name__ == "__main__":
    unittest.main()
