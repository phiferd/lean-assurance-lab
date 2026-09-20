import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate-kiota-ctor-index-test-closure"
LOADER = importlib.machinery.SourceFileLoader("kiota_test_closure", str(VALIDATOR))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
validator = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(validator)
from lib.research_queue_v3 import CATEGORIES


class KiotaCtorIndexTestClosureTest(unittest.TestCase):
    def history(self, path: str) -> bytes:
        return validator.historical_bytes(ROOT, path)

    def later_queue(self, root: Path) -> tuple[dict, dict]:
        historical = validator.validate_historical_handoff(self.history)
        completed = copy.deepcopy(next(row for row in historical["items"]
                                       if row["id"] == validator.ITEM))
        completed["priority"] = 2
        for relative in set(completed["evidence_refs"] + completed["closure"]["evidence_refs"]):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        for relative in ("CONSTITUTION.md", "docs/RESEARCH_WORKFLOW.md", "plan.md", "evidence.txt"):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Later bounded frontier evidence.\n")
        def item(identifier, priority, status="READY"):
            value = {name: "Bounded later work" for name in (
                "title", "target", "action", "expected_value", "rank_rationale",
                "entry_gate", "completion", "stop_condition")}
            value.update(id=identifier, priority=priority, kind="EXPERIMENT", status=status,
                         depends_on=[], budget={"max_sessions": 1, "session_minutes": 60,
                                                "checker_launches": 0},
                         evidence_refs=["evidence.txt"], issue_urls=[], blocked_reason="",
                         closure=None)
            if status == "COMPLETE":
                value["closure"] = {"outcome": "SUCCESS", "evidence_refs": ["evidence.txt"],
                                    "recommendation": "Retain the completed evidence."}
            return value
        queue = {"schema_version": 3, "frontier_id": "F-LATER", "plan": "plan.md",
                 "updated_at": "2026-09-20", "selected_item": "LATER",
                 "handoff": {"status": "EXECUTABLE", "reason": "", "required_decision": "",
                             "evidence_refs": []},
                 "items": [item("LATER", 1), completed,
                           item("KIOTA-CTOR-INDEX-COVERAGE-1", 3, "COMPLETE"),
                           item("SURVIVOR-THREAD-ONE-DETERMINISM-1", 4)]}
        self.write_queue(root, queue)
        return historical, queue

    def write_queue(self, root: Path, queue: dict) -> None:
        candidates = [{"item_id": item["id"], "disposition": "FEASIBLE",
                       "rationale": "A bounded available alternative.",
                       "evidence_refs": [item["evidence_refs"][0]], "blockers": []}
                      for item in queue["items"] if item["status"] == "READY"]
        paths = {"CONSTITUTION.md", "docs/RESEARCH_WORKFLOW.md", "plan.md"}
        paths.update(path for row in candidates for path in row["evidence_refs"])
        review = {"schema_version": 1, "scope": "PROJECT_WIDE", "phase": "CLOSURE",
                  "reviewed_at": queue["updated_at"], "stopped_item": "KIOTA-CTOR-INDEX-COVERAGE-1",
                  "selected_item": queue["selected_item"], "queue_sha256": validator.queue_digest(queue),
                  "decision": "Select a later bounded item without starting it.",
                  "categories": [{"category": category, "assessment": "Compare bounded alternatives.",
                                  "candidate_ids": [row["item_id"] for row in candidates]}
                                 for category in sorted(CATEGORIES)],
                  "candidates": candidates,
                  "evidence_bindings": [{"path": path,
                                         "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
                                        for path in sorted(paths)]}
        encoded = json.dumps(review).encode()
        (root / "review.json").write_bytes(encoded)
        queue["strategic_review"] = {"path": "review.json", "sha256": hashlib.sha256(encoded).hexdigest()}
        (root / "config").mkdir(exist_ok=True)
        (root / "config/research-queue.json").write_text(json.dumps(queue))
        (root / "docs/RESEARCH_STATUS.md").write_text(
            "### Active\nF-LATER plan.md\nSelected next item: `LATER`.\n"
            "Queue handoff: EXECUTABLE.\n### Waiting\n")

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(VALIDATOR), "--root", str(root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def copy_fixture(self, destination: Path) -> None:
        paths = [
            "config/research-queue.json",
            "corpus/generated/nanoda-gen-a59d7fa2cfb3-valid-control.ndjson",
            "corpus/generated/nanoda-gen-a59d7fa2cfb3-valid-ctor-index.ndjson",
            "results/research/external-contributions.json",
            "results/action-recommendations/drafts/kiota-constructor-index-regression-pr.md",
        ]
        for relative in paths:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        shutil.copytree(
            ROOT / "results/research/kiota-ctor-index-test-1",
            destination / "results/research/kiota-ctor-index-test-1",
        )

    def test_live_closure_passes(self) -> None:
        completed = self.run_validator(ROOT)
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(completed.stdout.strip(), "PASS")

    def test_changed_exact_message_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.copy_fixture(root)
            path = root / "results/research/kiota-ctor-index-test-1/result.json"
            value = json.loads(path.read_text())
            value["observations"]["candidate"]["exact_message"] = "generic rejection"
            path.write_text(json.dumps(value, indent=2) + "\n")
            completed = self.run_validator(root)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("exact message changed", completed.stdout)

    def test_later_valid_frontier_preserves_historical_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            historical, _ = self.later_queue(root)
            validator.validate_current_handoff(root, historical)

    def test_later_frontier_cannot_reopen_completed_kiota_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            historical, queue = self.later_queue(root)
            item = next(row for row in queue["items"] if row["id"] == validator.ITEM)
            item.update(status="READY", closure=None)
            self.write_queue(root, queue)
            with self.assertRaisesRegex(ValueError, "queue item not closed SUCCESS"):
                validator.validate_current_handoff(root, historical)

    def test_later_frontier_cannot_change_completed_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            historical, queue = self.later_queue(root)
            item = next(row for row in queue["items"] if row["id"] == validator.ITEM)
            item["budget"]["session_minutes"] += 1
            self.write_queue(root, queue)
            with self.assertRaisesRegex(ValueError, "completed Kiota queue record changed"):
                validator.validate_current_handoff(root, historical)

    def test_altered_historical_review_is_rejected(self) -> None:
        review_path = json.loads(self.history("config/research-queue.json"))["strategic_review"]["path"]
        def changed(path):
            if path == review_path:
                value = json.loads(self.history(path))
                value["selected_item"] = "LATER"
                return json.dumps(value).encode()
            return self.history(path)
        with self.assertRaisesRegex(ValueError, "historical strategic review binding mismatch"):
            validator.validate_historical_handoff(changed)

    def test_original_tooling_remains_bound(self) -> None:
        def changed(path):
            data = self.history(path)
            return data + b"\n" if path == "scripts/validate-kiota-ctor-index-test-closure" else data
        with self.assertRaisesRegex(ValueError, "historical tooling binding mismatch"):
            validator.validate_historical_handoff(changed)


if __name__ == "__main__":
    unittest.main()
