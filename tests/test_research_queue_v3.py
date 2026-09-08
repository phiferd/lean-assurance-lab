import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib.research_queue import validate_queue as validate_v1
from lib.research_queue_v2 import validate_queue as validate_v2
from lib.research_queue_v3 import CATEGORIES, handoff_status, load_queue, queue_digest, validate_queue


class ResearchQueueV3Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / "config").mkdir()
        self.paths = ["CONSTITUTION.md", "docs/RESEARCH_WORKFLOW.md", "docs/plan.md", "evidence.txt"]
        for path in self.paths:
            (self.root / path).write_text(path)
        self.queue = {
            "schema_version": 3, "frontier_id": "F-NEW-LOCAL", "plan": "docs/plan.md",
            "updated_at": "2026-09-08", "selected_item": "one",
            "items": [self.item("one", 1, "ACTIVE"), self.item("two", 2)],
            "handoff": {"status": "EXECUTABLE", "reason": "", "required_decision": "", "evidence_refs": []},
        }
        self.review = {
            "schema_version": 1, "scope": "PROJECT_WIDE", "phase": "ENTRY",
            "reviewed_at": "2026-09-08", "stopped_item": None, "selected_item": "one",
            "queue_sha256": "", "decision": "Local regression has better shared value than maintenance now.",
            "categories": [{"category": name, "assessment": "Compared existing scoped opportunities.",
                            "candidate_ids": ["one", "two"]} for name in sorted(CATEGORIES)],
            "candidates": [{"item_id": name, "disposition": "FEASIBLE", "rationale": "Existing evidence supports bounded work.",
                            "evidence_refs": ["evidence.txt"], "blockers": []} for name in ("one", "two")],
            "evidence_bindings": [{"path": path, "sha256": self.digest(path)} for path in self.paths],
        }
        self.bind()
        self.status()

    def tearDown(self):
        self.temp.cleanup()

    def item(self, name, rank, status="READY"):
        return {"id": name, "priority": rank, "title": name, "target": "local",
                "action": "Construct one fixed regression", "expected_value": "Shared reproducible evidence",
                "rank_rationale": "Higher information value", "entry_gate": "Freeze exact inputs before launch",
                "completion": "Reproducible regression or bounded unresolved evidence", "stop_condition": "One hour",
                "kind": "EXPERIMENT", "status": status, "depends_on": [],
                "budget": {"max_sessions": 1, "session_minutes": 60, "checker_launches": 4},
                "evidence_refs": ["evidence.txt"], "issue_urls": [], "closure": None,
                "blocked_reason": "Requires concrete independent input" if status in {"WAITING", "DEFERRED"} else ""}

    def digest(self, path):
        return hashlib.sha256((self.root / path).read_bytes()).hexdigest()

    def bind(self, *, queue_digest_update=True):
        if queue_digest_update:
            self.review["queue_sha256"] = queue_digest(self.queue)
        (self.root / "review.json").write_text(json.dumps(self.review, indent=2) + "\n")
        self.queue["strategic_review"] = {"path": "review.json", "sha256": self.digest("review.json")}
        (self.root / "config/research-queue.json").write_text(json.dumps(self.queue))

    def status(self):
        (self.root / "docs/RESEARCH_STATUS.md").write_text(
            "## Research Frontier\n### Active\nF-NEW-LOCAL docs/plan.md\n"
            f"Selected next item: `{self.queue['selected_item']}`.\n"
            f"Queue handoff: {self.queue['handoff']['status']}.\n### Waiting\n")

    def fails(self, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            validate_queue(self.queue, self.root)

    def paused(self):
        self.queue["handoff"] = {"status": "PAUSED", "reason": "Independent inputs unavailable",
                                  "required_decision": "Provide independently selected input package",
                                  "evidence_refs": ["evidence.txt"]}
        for item, candidate in zip(self.queue["items"], self.review["candidates"]):
            item["status"] = "WAITING"
            item["blocked_reason"] = "Independent input package unavailable"
            candidate["disposition"] = "BLOCKED"
            candidate["blockers"] = [{"kind": "EXTERNAL_INPUT", "reason": item["blocked_reason"],
                                       "evidence_refs": ["evidence.txt"]}]
        self.closure(successor_status="WAITING")
        self.status()

    def closure(self, successor_status="READY"):
        previous = self.item("previous", 1, "COMPLETE")
        previous["closure"] = {"outcome": "SUCCESS", "evidence_refs": ["evidence.txt"],
                               "recommendation": "Compare all project opportunities, then select one."}
        for item in self.queue["items"]:
            item["priority"] += 1
            if item["id"] == self.queue["selected_item"]:
                item["status"] = successor_status
        self.queue["items"].insert(0, previous)
        self.review.update(phase="CLOSURE", stopped_item="previous")
        self.bind()

    def test_valid_project_wide_local_successor_and_queue_loader(self):
        validate_queue(self.queue, self.root, require_ready=True)
        self.assertEqual(load_queue(self.root), self.queue)
        self.assertEqual(handoff_status(self.queue), "EXECUTABLE")

    def test_closure_records_completed_item_and_leaves_successor_ready(self):
        self.closure()
        validate_queue(self.queue, self.root, require_ready=True)
        self.queue["items"][1]["status"] = "ACTIVE"
        self.bind()
        self.fails("without starting")

    def test_entry_allows_current_active_item_without_claiming_closure(self):
        self.queue["items"][0]["status"] = "ACTIVE"
        self.bind()
        validate_queue(self.queue, self.root)
        self.review["stopped_item"] = "two"
        self.bind()
        self.fails("ENTRY review")

    def test_ready_handoff_cannot_use_entry_to_omit_completion_reassessment(self):
        self.queue["items"][0]["status"] = "READY"
        self.bind()
        self.fails("handoff requires CLOSURE")

    def test_closure_must_reference_a_completed_item(self):
        self.review.update(phase="CLOSURE", stopped_item="two")
        self.bind()
        self.fails("completed stopped item")

    def test_queue_cannot_change_budget_priority_or_action_under_old_review(self):
        for field, value in (("budget", {"max_sessions": 2, "session_minutes": 60, "checker_launches": 4}),
                             ("action", "A different experiment"), ("rank_rationale", "Changed rank rationale")):
            old = copy.deepcopy(self.queue["items"][0][field])
            self.queue["items"][0][field] = value
            with self.subTest(field=field):
                self.fails("queue binding is stale")
            self.queue["items"][0][field] = old

    def test_review_hash_mismatch_is_rejected(self):
        (self.root / "review.json").write_text("{}")
        self.fails("review hash mismatch")

    def test_scientific_evidence_drift_is_rejected(self):
        (self.root / "evidence.txt").write_text("New observations")
        self.fails("evidence hash mismatch")

    def test_constitution_workflow_and_plan_must_be_bound(self):
        for path in self.paths[:3]:
            bindings = self.review["evidence_bindings"]
            self.review["evidence_bindings"] = [row for row in bindings if row["path"] != path]
            self.bind()
            with self.subTest(path=path):
                self.fails("bind constitution, workflow and current plan")
            self.review["evidence_bindings"] = bindings

    def test_review_requires_current_date_selection_and_project_wide_scope(self):
        for field, value, pattern in (("reviewed_at", "2026-09-07", "date does not match"),
                                      ("selected_item", "two", "selected_item disagrees"),
                                      ("scope", "NEXT_MILESTONE", "PROJECT_WIDE")):
            old = self.review[field]
            self.review[field] = value
            self.bind()
            with self.subTest(field=field):
                self.fails(pattern)
            self.review[field] = old

    def test_missing_project_category_is_rejected(self):
        self.review["categories"].pop()
        self.bind()
        self.fails("omits a project-wide category")

    def test_category_can_explain_why_no_candidate_exists_without_filler(self):
        self.review["categories"][0].update(candidate_ids=[], assessment="No useful blocker-removal action remains after the local source audit.")
        self.bind()
        validate_queue(self.queue, self.root)
        self.review["categories"][0]["assessment"] = " "
        self.bind()
        self.fails("assessment must be a nonempty")

    def test_all_runnable_alternatives_must_be_assessed(self):
        self.queue["items"].append(self.item("omitted", 3))
        self.bind()
        self.fails("omits selected or executable")

    def test_feasible_disposition_cannot_relabel_a_blocked_item(self):
        self.queue["items"][1]["status"] = "WAITING"
        self.queue["items"][1]["blocked_reason"] = "No independent input"
        self.bind()
        self.fails("disposition disagrees")

    def test_candidate_evidence_must_be_bound_and_match_queue_evidence(self):
        self.review["candidates"][0]["evidence_refs"] = ["missing.txt"]
        self.bind()
        self.fails("unique bound evidence")
        self.review["candidates"][0]["evidence_refs"] = ["CONSTITUTION.md"]
        self.bind()
        self.fails("bind its queue evidence")

    def test_bounded_item_and_highest_ranked_selection_checks_are_preserved(self):
        self.queue["items"][0]["budget"]["max_sessions"] = 0
        self.bind()
        self.fails("max_sessions is invalid")
        self.queue["items"][0]["budget"]["max_sessions"] = 1
        self.queue["selected_item"] = self.review["selected_item"] = "two"
        self.bind()
        self.status()
        self.fails("selected_item must be one")

    def test_real_pause_validates_integrity_but_refuses_readiness(self):
        self.paused()
        validate_queue(self.queue, self.root)
        self.assertEqual(handoff_status(self.queue), "PAUSED")
        with self.assertRaisesRegex(ValueError, "queue is PAUSED; no executable item"):
            validate_queue(self.queue, self.root, require_ready=True)

    def test_completed_plan_is_not_a_blocker_kind(self):
        self.paused()
        self.review["candidates"][0]["blockers"][0]["kind"] = "PLAN_EXHAUSTED"
        self.bind()
        self.fails("plan exhaustion alone is not a blocker")

    def test_blocked_candidates_require_exact_blocker_evidence(self):
        self.paused()
        self.review["candidates"][0]["blockers"] = []
        self.bind()
        self.fails("require nonempty blockers")

    def test_pause_requires_local_blocker_removal_assessment(self):
        self.paused()
        self.queue["items"][2]["status"] = "DEFERRED"
        self.review["candidates"][1].update(disposition="DEFERRED", blockers=[])
        self.bind()
        self.fails("blockers to local blocker-removal")

    def test_pause_cannot_hide_a_feasible_alternative(self):
        self.paused()
        self.queue["items"][2].update(status="READY", blocked_reason="")
        self.review["candidates"][1].update(disposition="FEASIBLE", blockers=[])
        self.bind()
        self.fails("PAUSED queue must have no READY or ACTIVE")

    def test_duplicate_json_keys_and_nonfinite_review_values_fail_closed(self):
        for payload in ('{"scope":"PROJECT_WIDE","scope":"NEXT_MILESTONE"}', '{"number":NaN}'):
            (self.root / "review.json").write_text(payload)
            self.queue["strategic_review"]["sha256"] = self.digest("review.json")
            with self.subTest(payload=payload):
                self.fails("duplicate JSON key|non-finite JSON")

    def test_queue_duplicate_keys_are_rejected_by_v3_loader(self):
        (self.root / "config/research-queue.json").write_text('{"schema_version":3,"schema_version":3}')
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            load_queue(self.root)

    def test_unsafe_review_binding_cannot_escape_repository(self):
        self.queue["strategic_review"]["path"] = "../review.json"
        self.fails("safe relative path")

    def test_v1_and_v2_historical_semantics_survive_current_successor(self):
        legacy = {key: value for key, value in self.queue.items() if key != "strategic_review"}
        legacy["schema_version"] = 1
        del legacy["handoff"]
        validate_v1(legacy, self.root)
        validate_queue(legacy, self.root)
        self.paused()
        legacy = {key: value for key, value in self.queue.items() if key != "strategic_review"}
        legacy["schema_version"] = 2
        validate_v2(legacy, self.root)
        validate_queue(legacy, self.root)
        # An old pause needs no retroactive project-wide review and v1 still
        # refuses the same blocked state. No historical artifact is rewritten.
        (self.root / "review.json").unlink()
        validate_queue(legacy, self.root)
        legacy["schema_version"] = 1
        del legacy["handoff"]
        with self.assertRaisesRegex(ValueError, "no eligible READY or ACTIVE"):
            validate_queue(legacy, self.root)


if __name__ == "__main__":
    unittest.main()
