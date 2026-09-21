from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from lib.research_queue_v3 import CATEGORIES
from lib.research_queue_v4 import POLICY, load_queue, queue_digest, validate_queue


class ResearchQueueV4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / "config").mkdir()
        self.paths = ["CONSTITUTION.md", "docs/RESEARCH_WORKFLOW.md", "docs/plan.md", "evidence.txt"]
        for path in self.paths:
            (self.root / path).write_text(path)
        self.queue = {
            "schema_version": 4, "frontier_id": "F-NEW-LOCAL", "plan": "docs/plan.md",
            "updated_at": "2026-09-21", "selected_item": "one",
            "items": [self.item("one", 1, "ACTIVE"), self.item("two", 2, "READY")],
            "handoff": {"status": "EXECUTABLE", "reason": "", "required_decision": "", "evidence_refs": []},
            "execution_policy": copy.deepcopy(POLICY),
        }
        self.review = {
            "schema_version": 1, "scope": "PROJECT_WIDE", "phase": "ENTRY",
            "reviewed_at": "2026-09-21", "stopped_item": None, "selected_item": "one",
            "queue_sha256": "", "decision": "Continue the selected scientific work through engineering failures.",
            "categories": [{"category": name, "assessment": "Compared scoped opportunities.",
                            "candidate_ids": ["one", "two"]} for name in sorted(CATEGORIES)],
            "candidates": [{"item_id": name, "disposition": "FEASIBLE", "rationale": "Existing evidence supports the work.",
                            "evidence_refs": ["evidence.txt"], "blockers": []} for name in ("one", "two")],
            "evidence_bindings": [{"path": path, "sha256": self.digest(path)} for path in self.paths],
        }
        self.bind()
        (self.root / "docs/RESEARCH_STATUS.md").write_text(
            "### Active\nF-NEW-LOCAL docs/plan.md\nSelected next item: `one`.\nQueue handoff: EXECUTABLE.\n### Waiting\n")

    def tearDown(self):
        self.temp.cleanup()

    def item(self, name, rank, status):
        return {"id": name, "priority": rank, "title": name, "target": "local",
                "action": "Construct one fixed regression", "expected_value": "Shared evidence",
                "rank_rationale": "Higher information value", "entry_gate": "Freeze exact inputs",
                "completion": "Reproducible result", "stop_condition": "Scientific result or genuine blocker",
                "kind": "EXPERIMENT", "status": status, "depends_on": [], "budget": None,
                "evidence_refs": ["evidence.txt"], "issue_urls": [], "closure": None, "blocked_reason": ""}

    def digest(self, path):
        return hashlib.sha256((self.root / path).read_bytes()).hexdigest()

    def bind(self):
        self.review["queue_sha256"] = queue_digest(self.queue)
        (self.root / "review.json").write_text(json.dumps(self.review) + "\n")
        self.queue["strategic_review"] = {"path": "review.json", "sha256": self.digest("review.json")}
        (self.root / "config/research-queue.json").write_text(json.dumps(self.queue))

    def test_unfinished_work_has_no_terminal_attempt_budget(self):
        validate_queue(self.queue, self.root, require_ready=True)
        self.assertEqual(load_queue(self.root), self.queue)
        self.queue["items"][0]["budget"] = {"max_sessions": 1, "session_minutes": 1, "checker_launches": 1}
        self.bind()
        with self.assertRaisesRegex(ValueError, "must not have an attempt budget"):
            validate_queue(self.queue, self.root)

    def test_execution_policy_is_exact_and_review_bound(self):
        self.queue["execution_policy"]["attempt_caps"] = "ONE"
        self.bind()
        with self.assertRaisesRegex(ValueError, "prohibit terminal attempt budgets"):
            validate_queue(self.queue, self.root)

    def test_completed_historical_item_retains_original_budget(self):
        completed = self.item("done", 3, "COMPLETE")
        completed["budget"] = {"max_sessions": 1, "session_minutes": 60, "checker_launches": 4}
        completed["closure"] = {"outcome": "SUCCESS", "evidence_refs": ["evidence.txt"],
                                "recommendation": "Retain the evidence."}
        self.queue["items"].append(completed)
        self.bind()
        validate_queue(self.queue, self.root)

if __name__ == "__main__":
    unittest.main()
