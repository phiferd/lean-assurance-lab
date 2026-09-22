"""Adversarial tests for the acceptance-impact boundary closure validator."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from lib import acceptance_impact_closure as closure


class AcceptanceImpactClosureTests(unittest.TestCase):
    def write_json(self, root: Path, relative: Path | str, value: object) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def copy(self, root: Path, relative: str) -> None:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((closure.ROOT / relative).read_bytes())

    def fixture(self, root: Path) -> None:
        paths = {row["path"] for row in closure.FIXED_BINDINGS.values()}
        run = json.loads((closure.ROOT / closure.FIXED_BINDINGS["stage2_run"]["path"]).read_text())
        for cell in run["cells"]:
            paths.add(cell["receipt"]["raw_stdout_path"])
            paths.add(cell["receipt"]["raw_stderr_path"])
        for relative in paths:
            self.copy(root, relative)
        for relative in closure.EXPECTED_RESULT_PATHS.values():
            self.copy(root, relative)

        bindings = {
            role: closure.binding(root / relative, root)
            for role, relative in closure.EXPECTED_RESULT_PATHS.items()
        }
        overall = {
            "schema_version": 1,
            "item_id": closure.ITEM,
            "status": "COMPLETE",
            "outcome": closure.BOUNDARY,
            "observed_matrix": closure.OBSERVED_MATRIX,
            "conclusion": "The frozen matrix boundary cannot be promoted after observation.",
            "evidence": bindings,
            "frozen_expected_official_candidate": "INTENDED_RECURSOR_REJECT",
            "falsified_expectation": "OFFICIAL_REJECTS_BEFORE_APPENDED_USE",
            "scoped_support": [
                "Kiota accepted both fixed uses; the official control accepted, while official Lean reached LALNest.rec_1_impact and exposed the fifth-argument LALNest versus LALWrap LALNest mismatch."
            ],
            "claim_limits": [
                "The frozen outcome is not relabeled after observation; no external report is authorized."
            ],
            "adaptive_replacement": False,
            "scientific_relaunches_after_observation": 0,
            "external_actions": 0,
            "recommendation": f"Select {closure.SUCCESSOR} without rerunning this pilot.",
        }
        self.write_json(root, closure.OVERALL_RESULT, overall)
        closure_value = {
            "schema_version": 1,
            "item_id": closure.ITEM,
            "status": "COMPLETE",
            "outcome": closure.BOUNDARY,
            "completion_boundary": "The official candidate reached the fifth application rather than the preregistered diagnostic.",
            "result": closure.OVERALL_RESULT.as_posix(),
            "report": closure.REPORT.as_posix(),
            "falsified_expectation": "OFFICIAL_REJECTS_BEFORE_APPENDED_USE",
            "post_hoc_promotion": "FORBIDDEN",
            "adaptive_replacement": False,
            "scientific_relaunches_after_observation": 0,
            "external_actions": 0,
            "successor": closure.SUCCESSOR,
        }
        self.write_json(root, closure.CLOSURE, closure_value)
        report = f"""# Acceptance impact result

Outcome: **{closure.BOUNDARY}**

The frozen ordering expectation was falsified. The expected
`INTENDED_RECURSOR_REJECT` was observed as `SEMANTIC_REJECT` at
`LALNest.rec_1_impact`: `LALNest` did not match `LALWrap LALNest`.
Relabeling the item after seeing the result or rerunning under a revised outcome rule is
forbidden. No external report is authorized. Successor: `{closure.SUCCESSOR}`.
"""
        report_path = root / closure.REPORT
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")

        work = {
            "item_id": closure.ITEM,
            "status": "COMPLETE",
            "current_phase": "COMPLETE",
            "scientific_scope": {"outcome_guided_replacement": False},
            "authority": {"external_writes": False},
            "observations": {"source_requests": 0, "build_attempts": 1,
                             "checker_attempts": 8,
                             "process_seconds": 17.952792873000362},
            "evidence_refs": [closure.OVERALL_RESULT.as_posix(), closure.CLOSURE.as_posix(),
                              closure.REPORT.as_posix(), closure.VALIDATOR.as_posix(),
                              closure.TEST.as_posix()],
        }
        self.write_json(root, closure.WORK, work)
        protocol = {
            "item_id": closure.ITEM,
            "status": "COMPLETE",
            "current_phase": "COMPLETE",
            "stage_2_observation": {"observed_matrix": closure.OBSERVED_MATRIX,
                                    "decision": closure.BOUNDARY},
        }
        self.write_json(root, closure.PROTOCOL, protocol)

        item_refs = list(work["evidence_refs"])
        closure_refs = item_refs + [closure.VALIDATOR.as_posix(), closure.TEST.as_posix()]
        queue_item = {
            "id": closure.ITEM, "status": "COMPLETE", "issue_urls": [],
            "blocked_reason": "", "evidence_refs": item_refs,
            "closure": {"outcome": "BOUNDED_UNRESOLVED", "evidence_refs": closure_refs,
                        "recommendation": f"Do not relabel; no external action. Select {closure.SUCCESSOR}."},
        }
        successor = {"id": closure.SUCCESSOR, "status": "READY"}
        review_path = "review.json"
        queue = {
            "schema_version": 4,
            "selected_item": closure.SUCCESSOR,
            "items": [queue_item, successor],
            "handoff": {"status": "EXECUTABLE"},
            "strategic_review": {"path": review_path, "sha256": "0" * 64},
        }
        review = {"phase": "CLOSURE", "stopped_item": closure.ITEM,
                  "selected_item": closure.SUCCESSOR,
                  "queue_sha256": closure._queue_digest(queue)}
        self.write_json(root, review_path, review)
        queue["strategic_review"]["sha256"] = closure.sha256(root / review_path)
        self.write_json(root, closure.QUEUE, queue)

    def test_exact_boundary_closure_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            result = closure.validate(root, require_committed=False)
            self.assertEqual(result["outcome"], closure.BOUNDARY)
            self.assertEqual(result["scientific_relaunches_after_observation"], 0)

    def test_exact_official_stderr_is_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            path = root / closure.FIXED_BINDINGS["official_candidate_stderr"]["path"]
            path.write_bytes(path.read_bytes().replace(b"LALWrap", b"Other__", 1))
            with self.assertRaisesRegex(closure.ClosureError, "binding differs"):
                closure.validate(root, require_committed=False)

    def test_post_hoc_promotion_and_relaunch_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            path = root / closure.CLOSURE
            value = json.loads(path.read_text())
            value["outcome"] = "CONSEQUENTIAL_WITHIN_FIXED_USE"
            value["scientific_relaunches_after_observation"] = 1
            self.write_json(root, closure.CLOSURE, value)
            with self.assertRaisesRegex(closure.ClosureError, "closure boundary"):
                closure.validate(root, require_committed=False)

    def test_adaptation_external_action_and_wrong_successor_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            path = root / closure.CLOSURE
            value = json.loads(path.read_text())
            value["adaptive_replacement"] = True
            value["external_actions"] = 1
            value["successor"] = "DIFFERENT"
            self.write_json(root, closure.CLOSURE, value)
            with self.assertRaisesRegex(closure.ClosureError, "non-adaptation"):
                closure.validate(root, require_committed=False)

    def test_final_work_and_queue_state_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            queue_path = root / closure.QUEUE
            queue = json.loads(queue_path.read_text())
            queue["items"][0]["status"] = "ACTIVE"
            self.write_json(root, closure.QUEUE, queue)
            with self.assertRaisesRegex(closure.ClosureError, "queue item"):
                closure.validate(root, require_committed=False)

    def test_receipt_safety_requires_positive_rss_and_cleanup(self):
        receipt = {"timed_out": False, "memory_exceeded": False,
                   "memory_monitor_error": None, "memory_monitor_samples": 1,
                   "maximum_observed_rss_bytes": 4096, "cleanup_complete": True}
        closure._safe_receipt(receipt)
        for key, bad in (("memory_monitor_samples", 0),
                         ("maximum_observed_rss_bytes", 0),
                         ("cleanup_complete", False), ("timed_out", True)):
            changed = copy.deepcopy(receipt)
            changed[key] = bad
            with self.assertRaisesRegex(closure.ClosureError, "unsafe"):
                closure._safe_receipt(changed)


if __name__ == "__main__":
    unittest.main()
