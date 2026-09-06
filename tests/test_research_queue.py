import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from research_queue import validate_queue


SCRIPT = ROOT / "scripts" / "validate-research-queue"


class ResearchQueueTests(unittest.TestCase):
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

    def write_status(self, selected="one"):
        self.root.joinpath("docs/RESEARCH_STATUS.md").write_text(
            f"## Research Frontier\n### Active\nF-QUEUE docs/plan.md\n"
            f"Selected next item: `{selected}`.\n### Waiting\n"
        )

    def check_fails(self, queue=None):
        with self.assertRaises(ValueError):
            validate_queue(queue or self.queue, self.root)

    def test_valid_queue_and_cli(self):
        validate_queue(self.queue, self.root)
        (self.root / "config").mkdir()
        (self.root / "config/research-queue.json").write_text(json.dumps(self.queue))
        result = subprocess.run(
            ["python3", str(SCRIPT), "--root", str(self.root)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "PASS")

    def test_duplicate_id_or_rank_is_refused(self):
        queue = copy.deepcopy(self.queue)
        queue["items"][1]["id"] = "one"
        self.check_fails(queue)
        queue = copy.deepcopy(self.queue)
        queue["items"][1]["priority"] = 1
        self.check_fails(queue)

    def test_cycle_and_unsatisfied_dependency_are_refused(self):
        queue = copy.deepcopy(self.queue)
        queue["items"][0]["depends_on"] = ["two"]
        queue["items"][1]["depends_on"] = ["one"]
        self.check_fails(queue)
        queue = copy.deepcopy(self.queue)
        queue["items"][0]["depends_on"] = ["two"]
        queue["items"][1]["status"] = "WAITING"
        queue["items"][1]["blocked_reason"] = "awaiting review"
        self.check_fails(queue)

    def test_no_ready_item_is_refused(self):
        queue = copy.deepcopy(self.queue)
        queue["items"][0]["status"] = "PLANNED"
        queue["items"][1]["status"] = "WAITING"
        queue["items"][1]["blocked_reason"] = "awaiting review"
        self.check_fails(queue)

    def test_non_success_completion_cannot_unlock_dependency(self):
        closure = {"outcome": "BOUNDED_UNRESOLVED", "evidence_refs": ["evidence.txt"], "recommendation": "choose successor"}
        queue = copy.deepcopy(self.queue)
        queue["items"][0] = self.make_item("one", 1, "COMPLETE", closure=closure)
        queue["items"][1]["depends_on"] = ["one"]
        queue["selected_item"] = "two"
        self.check_fails(queue)

    def test_selection_uses_lowest_ready_and_active_sticks(self):
        queue = copy.deepcopy(self.queue)
        queue["selected_item"] = "two"
        self.check_fails(queue)
        queue = copy.deepcopy(self.queue)
        queue["items"][1]["status"] = "ACTIVE"
        queue["selected_item"] = "two"
        self.write_status("two")
        validate_queue(queue, self.root)

    def test_two_active_items_are_refused(self):
        queue = copy.deepcopy(self.queue)
        queue["items"][0]["status"] = "ACTIVE"
        queue["items"][1]["status"] = "ACTIVE"
        self.check_fails(queue)

    def test_successful_completion_unlocks_dependency(self):
        closure = {"outcome": "SUCCESS", "evidence_refs": ["evidence.txt"], "recommendation": "continue"}
        queue = copy.deepcopy(self.queue)
        queue["items"][0] = self.make_item("one", 1, "COMPLETE", closure=closure)
        queue["items"][1]["depends_on"] = ["one"]
        queue["selected_item"] = "two"
        self.write_status("two")
        validate_queue(queue, self.root)

    def test_budget_closure_and_status_binding_are_required(self):
        queue = copy.deepcopy(self.queue)
        del queue["items"][0]["budget"]["max_sessions"]
        self.check_fails(queue)
        queue = copy.deepcopy(self.queue)
        queue["items"][0]["status"] = "COMPLETE"
        self.check_fails(queue)
        queue = copy.deepcopy(self.queue)
        queue["items"][0]["budget"]["max_sessions"] = True
        self.check_fails(queue)
        self.root.joinpath("docs/RESEARCH_STATUS.md").write_text("### Active\nF-OTHER\n")
        self.check_fails()

    def test_path_and_malformed_values_are_refused(self):
        queue = copy.deepcopy(self.queue)
        queue["items"][0]["evidence_refs"] = ["../evidence.txt"]
        self.check_fails(queue)
        queue = copy.deepcopy(self.queue)
        queue["items"][0]["evidence_refs"] = ["missing.txt"]
        self.check_fails(queue)
        queue = copy.deepcopy(self.queue)
        queue["items"][0]["evidence_refs"] = [{}]
        self.check_fails(queue)
        queue = copy.deepcopy(self.queue)
        queue["items"][0]["kind"] = []
        self.check_fails(queue)
        queue = copy.deepcopy(self.queue)
        queue["schema_version"] = True
        self.check_fails(queue)


if __name__ == "__main__":
    unittest.main()
