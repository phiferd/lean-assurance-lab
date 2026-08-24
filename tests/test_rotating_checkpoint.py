import json
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from rotating_checkpoint import CheckpointError, RotatingCheckpoint  # noqa: E402


FILES = [
    {"name": "small", "sha256": "a" * 64, "bytes": 10},
    {"name": "large", "sha256": "b" * 64, "bytes": 20},
]
BINDINGS = {f"binding-{index}": {"path": f"file-{index}", "sha256": str(index) * 64} for index in range(8)}
BINDINGS.update({
    "candidate": {"path": "candidate", "sha256": "e" * 64},
    "positive_control": {"path": "control", "sha256": "f" * 64},
})


def result(outcome: str, seconds: float = 1.0) -> dict:
    return {
        "normalized_outcome": outcome,
        "exit_code": 0,
        "seconds": seconds,
        "stdout_sha256": "c" * 64,
        "stderr_sha256": "d" * 64,
    }


class RotatingCheckpointTests(unittest.TestCase):
    def create(self, directory: str) -> RotatingCheckpoint:
        return RotatingCheckpoint.create(
            Path(directory) / "checkpoint.json",
            experiment_id="experiment",
            fold_id="fold",
            bindings=BINDINGS,
            files=FILES,
            started_at="2026-08-24T12:00:00+00:00",
        )

    def test_checkpoint_is_atomic_and_schema_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = self.create(directory)
            schema = json.loads((ROOT / "schemas" / "rotating-fold-checkpoint.schema.json").read_text())
            value = json.loads(checkpoint.path.read_text())
            jsonschema.Draft202012Validator(schema).validate(value)
            self.assertFalse(checkpoint.path.with_name(f".{checkpoint.path.name}.tmp").exists())

    def test_resume_reuses_completed_baseline_side(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = self.create(directory)
            checkpoint.start_session()
            checkpoint.begin_unit("original", "small", "a" * 64, 10)
            checkpoint.begin_attempt("baseline")
            checkpoint.finish_attempt("baseline", result("ACCEPT"))
            checkpoint.save()
            resumed = RotatingCheckpoint.resume(checkpoint.path, bindings=BINDINGS, files=FILES)
            self.assertEqual(resumed.next_side(), "mutant")
            self.assertEqual(resumed.data["costs"]["checker_results_recorded"], 1)
            self.assertEqual(resumed.data["sessions"][0]["status"], "INTERRUPTED")

    def test_resume_records_abandoned_attempt_and_retries_that_side(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = self.create(directory)
            checkpoint.start_session()
            checkpoint.begin_unit("candidate", "candidate", "e" * 64, 30)
            checkpoint.begin_attempt("baseline")
            checkpoint.save()
            resumed = RotatingCheckpoint.resume(checkpoint.path, bindings=BINDINGS, files=FILES)
            self.assertEqual(resumed.next_side(), "baseline")
            self.assertEqual(resumed.data["costs"]["abandoned_checker_attempts"], 1)
            self.assertIsNone(resumed.data["inflight"]["active_attempt"])

    def test_resume_rejects_changed_bindings(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = self.create(directory)
            changed = dict(BINDINGS)
            changed["binding-0"] = {"path": "different", "sha256": "0" * 64}
            with self.assertRaisesRegex(CheckpointError, "bindings differ"):
                RotatingCheckpoint.resume(checkpoint.path, bindings=changed, files=FILES)

    def test_resume_rejects_tampered_candidate_result(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = self.create(directory)
            checkpoint.data["candidate_evaluation"] = {"artifact_sha256": "0" * 64}
            checkpoint.save()
            with self.assertRaisesRegex(CheckpointError, "candidate_evaluation differs"):
                RotatingCheckpoint.resume(checkpoint.path, bindings=BINDINGS, files=FILES)

    def test_resume_rejects_unreconciled_attempt_count(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = self.create(directory)
            checkpoint.data["costs"]["checker_attempts_started"] = 1
            checkpoint.save()
            with self.assertRaisesRegex(CheckpointError, "accounting does not reconcile"):
                RotatingCheckpoint.resume(checkpoint.path, bindings=BINDINGS, files=FILES)

    def test_completed_original_rows_must_be_the_frozen_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = self.create(directory)
            checkpoint.data["original_tests"] = [{
                "name": "large", "artifact_sha256": "b" * 64, "bytes": 20,
            }]
            checkpoint.data["progress"]["completed_original_tests"] = 1
            checkpoint.save()
            with self.assertRaisesRegex(CheckpointError, "prefix diverges"):
                RotatingCheckpoint.resume(checkpoint.path, bindings=BINDINGS, files=FILES)


if __name__ == "__main__":
    unittest.main()
