"""Exact result and evidence checks for the completed binder pilot."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from lib import binder_model_closure


ROOT = Path(__file__).resolve().parents[1]


class BinderModelClosureTests(unittest.TestCase):
    def test_committed_result_replays_exactly(self):
        self.assertEqual(binder_model_closure.validate(ROOT), {
            "status": "PASS", "vectors": 10000, "distinct_structural_inputs": 5091,
            "stage_outputs": 30000, "mismatches": 0, "host_launches": 0,
        })

    def test_changed_reported_stage_count_is_rejected(self):
        original = binder_model_closure._json

        def changed(path):
            document = original(path)
            if path == ROOT / binder_model_closure.BASE / "result.json":
                document = copy.deepcopy(document)
                document["scope"]["stage_outputs_total"] = 29999
            return document

        with patch.object(binder_model_closure, "_json", side_effect=changed):
            with self.assertRaisesRegex(binder_model_closure.ClosureError,
                                        "reported scope differs"):
                binder_model_closure.validate(ROOT)

    def test_changed_profile_stage_count_is_rejected(self):
        original = binder_model_closure._json

        def changed(path):
            document = original(path)
            if path == ROOT / binder_model_closure.BASE / "result.json":
                document = copy.deepcopy(document)
                document["observations"]["kiota-2d2a9fa"]["stage_outputs"] = 14999
            return document

        with patch.object(binder_model_closure, "_json", side_effect=changed):
            with self.assertRaisesRegex(binder_model_closure.ClosureError,
                                        "reported profile accounting differs"):
                binder_model_closure.validate(ROOT)


if __name__ == "__main__":
    unittest.main()
