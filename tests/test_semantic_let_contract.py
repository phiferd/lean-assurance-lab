"""Tamper regressions for retained-source evidence, budget, and claim boundaries."""
import copy
import json
from pathlib import Path
import subprocess
import unittest

from lib.semantic_let_contract import BASE, validate

ROOT = Path(__file__).resolve().parents[1]


class SemanticLetContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.git_cache = {}

    def check(self, overrides=None):
        overrides = overrides or {}

        def read(path):
            return overrides[path] if path in overrides else (ROOT / path).read_bytes()

        def git_read(rev, path):
            key = (rev, path)
            if key not in self.git_cache:
                self.git_cache[key] = subprocess.check_output(
                    ["git", "show", f"{rev}:{path}"], cwd=ROOT)
            return self.git_cache[key]

        return validate(ROOT, read=read, git_read=git_read)

    def altered_json(self, name, mutate):
        path = BASE + name + ".json"
        doc = json.loads((ROOT / path).read_bytes())
        mutate(doc)
        return {path: json.dumps(doc).encode()}

    def test_current_closure_and_later_queue_selection(self):
        self.assertTrue(self.check()["valid"])
        queue = json.loads((ROOT / "config/research-queue.json").read_bytes())
        queue["selected_item"] = "A-LATER-ITEM"
        for row in queue["items"]:
            if row["id"] == "HSBM-PILOT-1":
                row["status"] = "COMPLETE"
        self.assertTrue(self.check({"config/research-queue.json": json.dumps(queue).encode()})["valid"])

    def test_extra_request_is_not_hidden_by_unchanged_counters(self):
        def mutate(doc):
            extra = copy.deepcopy(doc["requests"][-1])
            extra["ordinal"] = 8
            doc["requests"].append(extra)
        with self.assertRaisesRegex(ValueError, "seven charged requests"):
            self.check(self.altered_json("source-assessment", mutate))

    def test_mutated_source_and_out_of_bounds_excerpt(self):
        path = BASE + "sources/l4l-translation.lean"
        with self.assertRaisesRegex(ValueError, "content binding"):
            self.check({path: (ROOT / path).read_bytes() + b"\n"})
        def mutate(doc):
            doc["sources"][0]["excerpts"][0]["start_line"] = 0
        with self.assertRaisesRegex(ValueError, "excerpt bounds"):
            self.check(self.altered_json("source-assessment", mutate))

    def test_authority_promotion_and_semantic_resolution_refused(self):
        for key, value, message in (("authority_changed", True, "authority promotion"),
                                    ("policy_status", "RESOLVED", "policy resolution")):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, message):
                self.check(self.altered_json("result", lambda doc: doc.update({key: value})))

    def test_clock_disagreement_and_prohibited_launch_refused(self):
        def mutate(doc):
            doc["intervals"][0]["end_monotonic"] += 90
        with self.assertRaisesRegex(ValueError, "UTC/monotonic"):
            self.check(self.altered_json("work-closure", mutate))
        def launch(doc):
            doc["research_counts"]["proofs"] = 1
        with self.assertRaisesRegex(ValueError, "zero prohibited count"):
            self.check(self.altered_json("result", launch))


if __name__ == "__main__":
    unittest.main()
