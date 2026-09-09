import copy
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from lib import portfolio_historical_snapshot as history

ROOT = Path(__file__).resolve().parents[1]


class PortfolioHistoricalSnapshotTests(unittest.TestCase):
    def test_exact_module_selection_and_live_transition(self):
        self.assertEqual(history.historical_modules(ROOT), {
            "test_survivor_cache_predicate_transfer",
            "test_nanoda_zero_thread_upstream_closure",
            "test_survivor_thread_config_regression_historical",
            "test_survivor_universe_diff",
        })

    def test_frozen_test_or_scientific_input_drift_is_rejected(self):
        for path in ("tests/test_survivor_cache_predicate_transfer.py",
                     "results/research/survivor-cache-predicate-transfer-1/result.json"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "frozen portfolio input changed"):
                history._compare_bytes(path, b"changed", b"frozen")

    def test_custody_failure_cannot_silently_remove_tests(self):
        with mock.patch.object(history, "validate_live_transition", side_effect=ValueError("missing frozen test")):
            with self.assertRaisesRegex(ValueError, "missing frozen test"):
                history.historical_modules(ROOT)

    def test_registry_allows_only_preserved_prefix(self):
        history._compare_bytes("results/mutants/registry.jsonl", b"old\nnew\n", b"old\n")
        with self.assertRaisesRegex(ValueError, "append-only prefix changed"):
            history._compare_bytes("results/mutants/registry.jsonl", b"changed\nnew\n", b"old\n")

    def test_completed_record_can_only_be_reranked(self):
        old = {"items": [{"id": "old", "status": "COMPLETE", "priority": 1, "closure": {"outcome": "SUCCESS"}}]}
        current = {"selected_item": "next", "items": [
            {"id": "old", "status": "COMPLETE", "priority": 9, "closure": {"outcome": "SUCCESS"}},
            {"id": "next", "status": "READY", "priority": 1}]}
        history._compare_queue(old, current)
        damaged = copy.deepcopy(current)
        damaged["items"][0]["closure"]["outcome"] = "NO_GO"
        with self.assertRaisesRegex(ValueError, "completed predecessor queue record changed"):
            history._compare_queue(old, damaged)
        current["selected_item"] = "old"
        with self.assertRaisesRegex(ValueError, "selection is not executable"):
            history._compare_queue(old, current)

    def test_payload_cannot_replace_tracked_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, snapshot = Path(temporary, "root"), Path(temporary, "snapshot")
            (root / "external").mkdir(parents=True)
            snapshot.mkdir()
            with self.assertRaisesRegex(ValueError, "tracked historical path"):
                history._attach_payloads(root, snapshot, {"external/frozen"})

    def test_original_receipt_failure_propagates_without_path_rewrite(self):
        snapshot = Path("/private/tmp/frozen-content")
        original = Path("/original/execution/root")
        evidence = mock.Mock(side_effect=ValueError("checker command drift"))
        adapter = history._operational_evidence(evidence, snapshot, original)
        with self.assertRaisesRegex(ValueError, "checker command drift"):
            adapter(snapshot)
        evidence.assert_called_once_with(original)
        with self.assertRaisesRegex(ValueError, "unexpected snapshot evidence caller"):
            adapter(Path("/unrelated/root"))
        self.assertEqual(evidence.call_count, 1)

    def test_historical_process_failure_propagates(self):
        from contextlib import contextmanager

        @contextmanager
        def snapshot(_root):
            yield ROOT

        with mock.patch.object(history, "historical_modules", return_value=set(history.MODULES)), \
             mock.patch.object(history, "_snapshot", snapshot), \
             mock.patch.object(history.subprocess, "run", return_value=mock.Mock(returncode=1)):
            self.assertFalse(history.run_historical_tests(ROOT))


if __name__ == "__main__":
    unittest.main()
