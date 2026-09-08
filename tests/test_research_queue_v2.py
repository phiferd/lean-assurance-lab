import copy
import contextlib
import io
import json
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib.research_queue_v2 import validate_queue


SCRIPT = ROOT / "scripts" / "validate-research-queue"
CLI_MAIN = runpy.run_path(str(SCRIPT))["main"]
RENDER_REVIEW = runpy.run_path(str(ROOT / "scripts" / "build-project-review"))["render"]


class ResearchQueueV2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / "evidence.txt").write_text("evidence")
        (self.root / "docs" / "plan.md").write_text("plan")
        self.queue = self.make_queue()
        self.write_status()

    def tearDown(self):
        self.temp.cleanup()

    def make_item(self, item_id, priority, status="READY", depends_on=None, closure=None):
        return {
            "id": item_id, "priority": priority, "title": item_id, "target": "local",
            "action": "inspect", "expected_value": "bounded result", "rank_rationale": "ranked",
            "entry_gate": "local review", "completion": "evidence", "stop_condition": "one session",
            "kind": "OPERATIONS", "status": status, "depends_on": depends_on or [],
            "budget": {"max_sessions": 1, "session_minutes": 1, "checker_launches": 0},
            "evidence_refs": ["evidence.txt"], "issue_urls": [], "closure": closure,
            "blocked_reason": "blocked" if status in {"WAITING", "DEFERRED"} else "",
        }

    def make_queue(self):
        return {
            "schema_version": 1, "frontier_id": "F-QUEUE", "plan": "docs/plan.md",
            "updated_at": "2026-09-06", "selected_item": "one",
            "items": [self.make_item("one", 1), self.make_item("two", 2)],
        }

    def write_status(self, selected="one", handoff=None):
        marker = f"Queue handoff: {handoff}.\n" if handoff else ""
        self.root.joinpath("docs/RESEARCH_STATUS.md").write_text(
            f"## Research Frontier\n### Active\nF-QUEUE docs/plan.md\n"
            f"Selected next item: `{selected}`.\n{marker}### Waiting\n"
        )

    def paused_queue(self):
        queue = copy.deepcopy(self.queue)
        queue["schema_version"] = 2
        queue["handoff"] = {
            "status": "PAUSED", "reason": "Owner authorization for a new research scope is absent.",
            "required_decision": "Select and authorize the next research scope after reviewing evidence.",
            "evidence_refs": ["evidence.txt"],
        }
        queue["items"] = [self.make_item("one", 1, "WAITING"), self.make_item("two", 2, "DEFERRED")]
        self.write_status(handoff="PAUSED")
        return queue

    def run_cli(self, queue, *arguments):
        (self.root / "config").mkdir(exist_ok=True)
        (self.root / "config/research-queue.json").write_text(json.dumps(queue))
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", [str(SCRIPT), "--root", str(self.root), *arguments]), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = CLI_MAIN()
        return code, stdout.getvalue(), stderr.getvalue()

    def check_fails(self, queue=None):
        with self.assertRaises(ValueError):
            validate_queue(queue or self.queue, self.root)

    def test_paused_handoff_is_valid_but_cli_refuses_operational_readiness(self):
        queue = self.paused_queue()
        validate_queue(queue, self.root)
        code, stdout, stderr = self.run_cli(queue)
        self.assertEqual(code, 0, stderr)
        self.assertIn("PASS (PAUSED:", stdout)
        self.assertIn("no executable item", stdout)
        code, stdout, stderr = self.run_cli(queue, "--require-ready")
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("queue is PAUSED; no executable item", stderr)

    def test_v1_ready_cli_remains_operational(self):
        for arguments in ((), ("--require-ready",)):
            code, stdout, stderr = self.run_cli(self.queue, *arguments)
            self.assertEqual(code, 0, stderr)
            self.assertEqual(stdout.strip(), "PASS")

    def test_paused_handoff_refuses_any_ready_or_active_item(self):
        for status in ("READY", "ACTIVE"):
            queue = self.paused_queue()
            queue["items"][1]["status"] = status
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "no READY or ACTIVE"):
                validate_queue(queue, self.root)

    def test_pause_requires_blocker_decision_and_existing_evidence(self):
        for name, value in (("reason", " "), ("required_decision", ""),
                            ("evidence_refs", []), ("evidence_refs", ["missing.txt"])):
            queue = self.paused_queue()
            queue["handoff"][name] = value
            with self.subTest(field=name, value=value):
                self.check_fails(queue)
        queue = self.paused_queue()
        del queue["handoff"]["reason"]
        self.check_fails(queue)
        queue = self.paused_queue()
        queue["items"][0]["blocked_reason"] = ""
        self.check_fails(queue)

    def test_paused_selection_requires_highest_ranked_blocked_item(self):
        queue = self.paused_queue()
        queue["selected_item"] = "two"
        self.write_status("two", "PAUSED")
        self.check_fails(queue)
        queue = self.paused_queue()
        queue["items"][0]["status"] = "PLANNED"
        self.check_fails(queue)
        queue["selected_item"] = "two"
        self.write_status("two", "PAUSED")
        validate_queue(queue, self.root)
        queue["items"][1]["status"] = "PLANNED"
        self.check_fails(queue)

    def test_handoff_marker_must_match_once(self):
        queue = self.paused_queue()
        for marker in (None, "EXECUTABLE", "UNKNOWN"):
            self.write_status(handoff=marker)
            self.check_fails(queue)
        self.write_status(handoff="PAUSED")
        status = self.root / "docs/RESEARCH_STATUS.md"
        status.write_text(status.read_text().replace("Queue handoff: PAUSED.", "Queue handoff: PAUSED.\nQueue handoff: PAUSED."))
        self.check_fails(queue)

    def test_explicit_schema_successor_preserves_v1_readiness_requirement(self):
        queue = self.paused_queue()
        queue["schema_version"] = 1
        self.check_fails(queue)
        del queue["handoff"]
        with self.assertRaisesRegex(ValueError, "no eligible READY or ACTIVE"):
            validate_queue(queue, self.root)
        queue = copy.deepcopy(self.queue)
        queue["schema_version"] = 2
        self.check_fails(queue)
        queue["handoff"] = {"status": "EXECUTABLE", "reason": "", "required_decision": "", "evidence_refs": []}
        self.write_status(handoff="EXECUTABLE")
        validate_queue(queue, self.root, require_ready=True)
        queue["handoff"]["reason"] = "Old pause"
        self.check_fails(queue)
        queue["handoff"]["reason"] = ""
        for item in queue["items"]:
            item["status"] = "PLANNED"
        with self.assertRaisesRegex(ValueError, "no eligible READY or ACTIVE"):
            validate_queue(queue, self.root)

    def test_project_review_exposes_pause_and_required_decision(self):
        queue = self.paused_queue()
        metrics = dict.fromkeys(("study_outcome", "study_tier", "study_publication_decision", "study_existing_isolated",
            "study_denominator", "study_final_isolated", "assurance_gate", "semantic_disagreement_artifacts",
            "parse_disagreement_artifacts", "pending_survivor_triage", "current_external_actions_pending_review",
            "external_actions_pending_review", "schema_backed_findings_in_selected_registers"), 0)
        review = {"metrics": metrics, "constitutional_assessment": "Scoped fixture", "successor_decision_packet": None,
                  "constitutional_alignment": [], "work_queue": queue, "proposed_next_steps": [],
                  "autonomy_policy": {}, "operational_findings": [], "cost_policy": [], "improvements_completed": []}
        report = RENDER_REVIEW(review)
        self.assertIn("Queue execution is PAUSED; no executable item is selected.", report)
        self.assertIn(queue["handoff"]["reason"], report)
        self.assertIn(queue["handoff"]["required_decision"], report)
        self.assertIn("Selected blocked decision: **one**", report)
        self.assertNotIn("Selected next item: **one**", report)
        review["work_queue"] = self.queue
        report = RENDER_REVIEW(review)
        self.assertIn("Selected next item: **one**", report)
        self.assertNotIn("Queue execution is PAUSED", report)


if __name__ == "__main__":
    unittest.main()
